"""Bounded DIRECT HTTPS measurement component. No config writes or TLS bypass.

The native route driver must bind/authorize context and confirm DIRECT matches the
observed proxy policy. No host/guest cross-substitution. Tests inject a transport;
no real network calls are made by workspace regression.
"""
from __future__ import annotations
from dataclasses import dataclass
from urllib.parse import urlsplit
import hashlib
import http.client
import socket
import ssl
import time
import threading
from .codec import fields,hash_value,sha256,token
from .errors import require,P00Error

CAP=10*1024**2


def endpoint(spec):
    fields(spec,{'endpoint_id','url','context','proxy_mode','expected_status','body_prefix_hex','maximum_bytes','redirect_allowlist'})
    token(spec['endpoint_id']);require(spec['context'] in ('WINDOWS','GUEST'),10,'NETWORK_CONTEXT')
    require(spec['proxy_mode']=='DIRECT',11,'PROXY_PROFILE_REQUIRES_ADAPTER')
    require(type(spec['maximum_bytes']) is int and 1<=spec['maximum_bytes']<=CAP,10,'RESPONSE_CAP')
    require(type(spec['expected_status']) is int and 200<=spec['expected_status']<300,10,'HTTP_EXPECTATION')
    require(type(spec['body_prefix_hex']) is str and 0<len(spec['body_prefix_hex'])<=1024,10,'RESPONSE_EXPECTATION')
    try:bytes.fromhex(spec['body_prefix_hex'])
    except ValueError:raise P00Error(10,'RESPONSE_EXPECTATION') from None
    require(type(spec['redirect_allowlist']) is list and len(spec['redirect_allowlist'])<=3,10,'REDIRECT_SCOPE')
    for value in [spec['url'],*spec['redirect_allowlist']]:
        require(type(value) is str and len(value)<=2048 and not any(ord(c)<32 for c in value),10,'URL_SYNTAX')
        try:
            parsed=urlsplit(value);port=parsed.port
        except ValueError:raise P00Error(10,'URL_SYNTAX') from None
        require(parsed.scheme=='https' and parsed.hostname and not parsed.username and not parsed.password
                and not parsed.fragment and port in (None,443),10,'HTTPS_REQUIRED')
    return spec


def proxy_policy(spec,actual):
    """Validate observed context for the approved DIRECT-only P00 probe.

    Reviewed V2 does not authorize a proxy/VPN/CA remediation adapter. A configured
    proxy is therefore an observed network-context failure (14), never something
    silently ignored by the fixed DIRECT transport.
    """
    endpoint(spec)
    require(type(actual) is dict and actual.get('context')==spec['context'],15,'NETWORK_PROXY_OBSERVATION_REQUIRED')
    env=actual.get('environment_overrides')
    names=('http_proxy','https_proxy','all_proxy','HTTP_PROXY','HTTPS_PROXY','ALL_PROXY')
    require(type(env) is dict and set(env)==set(names) and all(type(env[k]) is bool for k in names),
            15,'NETWORK_PROXY_OBSERVATION_REQUIRED')
    require(not any(env.values()),14,'NETWORK_PROXY_CONTEXT')
    if spec['context']=='WINDOWS':
        winhttp=actual.get('winhttp');user=actual.get('user')
        require(type(winhttp) is dict and set(winhttp)=={'access_type','proxy_present','bypass_present'}
                and type(user) is dict and set(user)=={'status','auto_detect','auto_config_url_present','proxy_present'},
                15,'NETWORK_PROXY_OBSERVATION_REQUIRED')
        require(winhttp['access_type']==1 and not winhttp['proxy_present']
                and user['status'] in ('OBSERVED','ABSENT') and not user['auto_detect']
                and not user['auto_config_url_present'] and not user['proxy_present'],
                14,'NETWORK_PROXY_CONTEXT')
    return actual


def _dns_bounded(host,timeout):
    result=[];failure=[]
    def call():
        try:result.extend(socket.getaddrinfo(host,443,type=socket.SOCK_STREAM))
        except OSError:failure.append(True)
    worker=threading.Thread(target=call,daemon=True);worker.start();worker.join(timeout)
    require(not worker.is_alive(),14,'DNS_TIMEOUT')
    require(not failure and bool(result),14,'DNS_FAILURE')
    return result


class DirectTransport:
    def attempt(self,spec,url,deadline,clock=time.monotonic):
        def remaining():
            left=deadline-clock();require(left>0,14,'NETWORK_DEADLINE');return left
        u=urlsplit(url);addresses=_dns_bounded(u.hostname,remaining())
        context=ssl.create_default_context();tcp=None;tls=None
        try:
            for family,kind,proto,_,address in addresses[:16]:
                try:
                    tcp=socket.socket(family,kind,proto);tcp.settimeout(remaining());tcp.connect(address);break
                except OSError:
                    if tcp:tcp.close();tcp=None
            require(tcp is not None,14,'TCP_FAILURE')
            peer=tcp.getpeername()
            tcp.settimeout(remaining());tls=context.wrap_socket(tcp,server_hostname=u.hostname)
            certificate=tls.getpeercert(binary_form=True);version=tls.version()
            target=u.path or '/'
            if u.query:target+='?'+u.query
            # URL ascii requirement avoids ambiguous HTTP request encodings. IDNA
            # host is used for Host; TLS still checks the requested DNS hostname.
            try:request=('GET '+target+' HTTP/1.1\r\nHost: '+u.hostname.encode('idna').decode()+
                         '\r\nConnection: close\r\nAccept-Encoding: identity\r\nUser-Agent: AI-Film-P00\r\n\r\n').encode('ascii')
            except UnicodeError:raise P00Error(10,'URL_ENCODING') from None
            tls.settimeout(remaining());tls.sendall(request)
            response=http.client.HTTPResponse(tls);response.begin()
            if response.status in (301,302,303,307,308):
                return {'redirect':response.getheader('Location'),'http_status':response.status}
            require(response.status==spec['expected_status'],14,'HTTP_STATUS')
            require(response.getheader('Content-Encoding','identity').lower()=='identity',14,'UNEXPECTED_CONTENT_ENCODING')
            total=0;h=hashlib.sha256();prefix=bytearray();expected=bytes.fromhex(spec['body_prefix_hex'])
            while total<=spec['maximum_bytes']:
                tls.settimeout(remaining())
                chunk=response.read(min(65536,spec['maximum_bytes']+1-total))
                if not chunk:break
                total+=len(chunk);h.update(chunk)
                prefix.extend(chunk[:max(0,len(expected)-len(prefix))])
            require(total<=spec['maximum_bytes'],14,'HTTP_BODY_CAP')
            require(bytes(prefix)==expected,14,'HTTP_BODY_EXPECTATION')
            return {'dns':True,'tcp':True,'tls_chain_hostname':True,'https':True,'http_status':response.status,
                    'bytes':total,'body_sha256':h.hexdigest(),'certificate_sha256':sha256(certificate),
                    'tls_version':version,'peer':str(peer[0]),'eof':True}
        except P00Error:raise
        except ssl.SSLError:raise P00Error(14,'TLS_FAILURE') from None
        except (OSError,http.client.HTTPException):raise P00Error(14,'NETWORK_IO') from None
        finally:
            if tls:tls.close()
            elif tcp:tcp.close()


def measure(spec,*,transport=None,clock=time.monotonic,sleep=time.sleep):
    endpoint(spec);transport=transport or DirectTransport();started=clock();collector_deadline=started+30
    failures=[]
    for attempt in range(3):
        if attempt:
            delay=(2,5)[attempt-1]
            if clock()+delay>=collector_deadline:break
            sleep(delay)
        deadline=min(clock()+10,collector_deadline)
        if deadline<=clock():break
        current=spec['url'];seen=set()
        try:
            for _ in range(4):
                require(current not in seen,14,'REDIRECT_LOOP');seen.add(current)
                result=transport.attempt(spec,current,deadline,clock)
                if 'redirect' not in result:
                    return {'status':'OBSERVED','endpoint_id':spec['endpoint_id'],'context':spec['context'],
                            'attempts':attempt+1,'duration_ms':int((clock()-started)*1000),
                            'measurements':result,'failures':failures,'host_ready':False}
                require(result['redirect'] in spec['redirect_allowlist'],14,'UNAPPROVED_REDIRECT')
                current=result['redirect']
            raise P00Error(14,'REDIRECT_LIMIT')
        except P00Error as e:
            if e.code!=14:raise
            failures.append({'attempt':attempt+1,'reason':e.reason})
    return {'status':'FAIL','endpoint_id':spec['endpoint_id'],'context':spec['context'],
            'attempts':len(failures),'duration_ms':int((clock()-started)*1000),
            'failures':failures,'normalized_exit':14,'host_ready':False}
