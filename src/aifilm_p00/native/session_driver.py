"""Concrete native Phase00 driver. Construction is Windows-only and ACL anchored.

No fixture ports, arbitrary commands, expected-state observations or qualification
issuance are accepted by its factory. Guest commands are fixed, bounded agents.
Every actuation remains under the SessionRunner's single guard and durable fence.
All assertions come from Win32/WSL observations or explicitly typed owner receipts.
"""
from __future__ import annotations
from copy import deepcopy
from contextlib import ExitStack
from datetime import datetime,timezone
from pathlib import Path,PureWindowsPath
import ctypes as C
import hashlib

from .. import CONTRACT_DIGEST
from ..authority import Context,authorize
from ..admission import Coordinator
from ..codec import digest,sha256,instant,hash_value,windows_path
from ..errors import require,P00Error
from ..plans import check_plan
from ..session import Refresh,Completion,SessionRunner
from ..policy import (host_profile,runtime_profile,guest_profile,floors,budget_check,
                       protection,c3_postconditions,restore_envelope)
from ..resume import completed_steps
from ..windows_commands import compile_wsl
from .entry import _entry
from .coordination import NativeGuard,NativeJournal
from .filesystem import WindowsPaths,same_path
from .process import NativeSupervisor,Command
from .actuator import NativeActuator,SUPPORTED_ACTIONS
from .guest import GuestTransport
from .observations import (ReadBroker,normalize_host,normalize_distros,match_profile,
                           target_row,config_observation,volume_observations,file_presence)
from .system_state import NativeSystemState
from .transitions import operation_expected,final_expected
from .proofs import ProofReader

INTERFACES={'PASSIVE':'preflight','DISCOVERY':'preflight','SITE_VERIFY':'verify',
 'TARGET_LIFECYCLE':'verify','HOST_RESTART':'verify','RESTORE_VERIFY':'verify',
 'RECONCILIATION_ONLY':'verify','SUPPORT_BUNDLE':'support-bundle'}


def interface_for(plan):return INTERFACES.get(plan['semantic']['purpose'],'apply')


def _binding(store,s):
    ref=s['refs'].get('native_binding');require(ref is not None,12,'NATIVE_BINDING_REQUIRED')
    b=store.get('native_binding',ref)
    require(b.get('schema_version')==1 and b.get('withdrawn') is False
            and b.get('host_id')==s['host_id'] and b.get('owner_sid')==s['owner_sid'],12,'NATIVE_BINDING_SCOPE')
    require(type(b.get('volume_paths')) is dict and type(b.get('after_by_action')) is dict,
            10,'NATIVE_BINDING_SCHEMA')
    from .bindings import validate_binding
    return validate_binding(b,s)


def remaining_budgets(s,b,completed):
    """Stop counting permanent bytes as future allocation after committed steps.

    A cutoff is plan-bound. Only hash-verified TERMINAL+CLEAR progress can remove
    it. Retained bytes already reduce measured free space. No refund on INTENT,
    subprocess exit, uncertain writes, or an uncommitted checkpoint.
    """
    lifetimes=b.get('allocation_lifetimes')
    require(type(lifetimes) is dict and set(lifetimes)=={v['volume_id'] for v in s['budgets']},
            10,'ALLOCATION_LIFETIMES_REQUIRED')
    result=deepcopy(s['budgets'])
    for volume in result:
        bound=lifetimes[volume['volume_id']]
        require(type(bound) is dict and set(bound)==set(volume['allocations']),10,'ALLOCATION_LIFETIME_SET')
        for name,cutoff in bound.items():
            require(cutoff is None or type(cutoff) is int and 0<=cutoff<len(s['operations']),10,'ALLOCATION_LIFETIME')
            if cutoff is not None and cutoff in completed:volume['allocations'][name]=0
    return result


class NativeDriver:
    source_kind='NATIVE_PENDING'
    def __init__(self,root,api,paths,supervisor,system,operators):
        self.root=Path(root);self.api=api;self.paths=paths;self.supervisor=supervisor
        self.system=system;self.operators=frozenset(operators)
        self.store=None;self.binding=None;self.broker=None;self.environment=None
        self.last=None;self.before_action={};self.proofs={};self.actual_steps={}
        self.current_interface=None

    def _authority_snapshot(self,plan):
        api,store,passive,identity,reg=_entry(self.root)
        s=check_plan(plan)
        require(store.operators==self.operators,16,'OPERATOR_POPULATION_CHANGED')
        require(passive['principal']['execution_sid']==s['owner_sid'] and store.host_id==s['host_id'],12,'NATIVE_PRINCIPAL_SCOPE')
        require(identity['source_content_digest']==s['build_digest'] and identity['test_content_digest']==s['test_set_digest'],16,'NATIVE_CONTENT_DRIFT')
        b=_binding(store,s);catalog=store.get('profile_catalog',b['profile_catalog_ref'])
        require(catalog.get('withdrawn') is False and catalog.get('contract_digest')==CONTRACT_DIGEST,
                15,'PROFILE_CATALOG_UNTRUSTED')
        # Every child process is checked against an independently trusted exact-byte
        # executable policy before CreateProcess/ResumeThread. Refreshing authority
        # also refreshes this policy; no cached path-only trust survives a step.
        from .executable_trust import ExecutableTrust
        executable_trust=ExecutableTrust.from_store(self.paths,store,b['executable_policy_ref'],
            host_id=s['host_id'],build_digest=s['build_digest'])
        self.supervisor.set_executable_trust(executable_trust)
        require(any(r.get('key')==s['profile'] for r in catalog.get('profiles',[])),16,'PROFILE_REQUEST_UNBOUND')
        from .source_pin import SourcePins
        self.source_pins=SourcePins(self.root,self.paths,identity,s['build_digest'])
        self.store=store;self.binding=b;self.source_kind=reg['execution_class']
        self.current_interface=interface_for(plan)
        ctx=Context(s['host_id'],s['owner_sid'],self.source_kind,identity['source_content_digest'],
                    identity['test_content_digest'],deepcopy(s['profile']),passive['principal']['elevated'],
                    datetime.now(timezone.utc))
        return ctx,passive,catalog

    def _environment(self,b):
        sysdir=self.api.system_directory();system_root=str(PureWindowsPath(sysdir).parent)
        temp=windows_path(b['scratch_directory'])
        # Scratch is an explicit, existing protected directory, not os.environ.
        # Creating it is a separately authorized metadata/output action.
        with self.paths.pin(temp,directory=True,protected=True):pass
        require(same_path(str(PureWindowsPath(temp).parent),self.paths.root),12,'SCRATCH_SCOPE')
        return {'SystemRoot':system_root,'WINDIR':system_root,'SystemDrive':PureWindowsPath(sysdir).drive,
                'PATH':sysdir,'TEMP':temp,'TMP':temp,'USERPROFILE':self.system.user_profile(),
                'LOCALAPPDATA':self.system.local_app_data()}

    def _packaged(self,live,catalog):
        rows=[]
        for p in live['runtime_packages']:
            require(p.get('name')=='MicrosoftCorporationII.WindowsSubsystemForLinux'
                    and p.get('publisher') in catalog.get('appx_publishers',[])
                    and p.get('signature_kind') in ('Store','System','Enterprise'),15,'RUNTIME_PACKAGE_TRUST')
            rows.append({'installed':True,'identity':p['identity'],'version':p['version'],'kind':'APPX'})
        for code in catalog.get('msi_product_codes',[]):
            value=self.system.product(code)
            if value['installed']:rows.append({**value,'kind':'MSI'})
        if not rows:return None
        versions={'.'.join(r['version'].split('.')[:3]) for r in rows}
        require(len(versions)==1,16,'RUNTIME_PACKAGING_AMBIGUOUS')
        require(next(iter(versions)) in catalog.get('stable_runtime_versions',[]),11,'RUNTIME_STABILITY_UNBOUND')
        return {'installed':True,'version':rows[0]['version'],
                'identity':digest(sorted(rows,key=lambda r:r['identity'])),'packages':rows}

    def refresh(self,plan,*,coordinator=None,step=None):
        ctx,passive,catalog=self._authority_snapshot(plan)
        if coordinator is None:
            # Only permission to request a profile, NOT evidence it is observed.
            return Refresh(ctx,self.store,{},self.store.generation,'REQUEST_AUTHORITY_ONLY')
        require(coordinator.held and coordinator.admission is not None,12,'ADMISSION_REQUIRED')
        authorize(interface_for(plan),plan,ctx,self.store)
        if plan['semantic']['purpose']=='RECONCILIATION_ONLY':
            from .recovery_driver import refresh_recovery
            return refresh_recovery(self,plan,ctx,passive,catalog,coordinator)
        self._reserve_journal(plan,coordinator)
        self.environment=self._environment(self.binding)
        if self.broker is None or self.broker.c is not coordinator:
            self.broker=ReadBroker(self.root,self.api,self.paths,self.supervisor,self.environment,coordinator,self.source_pins)
        else:
            self.broker.environment=self.environment;self.broker.sources=self.source_pins
        capture_start=len(self.broker.captures)
        live=self.broker.host('HOST');host=normalize_host(passive,live,catalog)
        # Authenticate the support document used by the matching catalogue row.
        for r in catalog['windows']:
            if (r.get('build'),r.get('release'),r.get('registry_edition')) == (host['build'],host['release'],passive['host']['EditionID']['value']):
                document=self.store.get('support_document',r['document_ref'])
                require(document.get('withdrawn') is False and document.get('publisher')=='Microsoft',15,'SUPPORT_DOCUMENT_TRUST')
        host_profile(host,ctx.now)
        packaged=self._packaged(live,catalog)
        if packaged is None:
            # Do not start the Windows wsl.exe install stub merely to ask a
            # version. This is absence of a supported PACKAGED runtime only.
            runtime={'status':'PACKAGED_ABSENT','version':None,'kernel':None,'package_identity':None}
            running=None
        else:
            runtime=self.broker.runtime(packaged);runtime_profile(runtime)
            running=self.broker.running()
        features=self.broker.host('FEATURES')
        rows=features['features']
        require(type(rows) is list and {r['name'] for r in rows}=={'VirtualMachinePlatform','Microsoft-Windows-Subsystem-Linux'}
                and len(rows)==2 and all(r['state'] in ('Enabled','Disabled','Absent') for r in rows),11,'FEATURE_OBSERVATION_UNKNOWN')
        config=config_observation(self.paths,self.system.user_profile()+'\\.wslconfig')
        material={'schema_version':1,'host':{k:host[k] for k in ('host_id','build','ubr','edition','release','architecture')},
                  'execution_sid':passive['principal']['execution_sid'],'runtime':runtime,
                  'features':sorted([{'name':r['name'],'state':r['state']} for r in rows],key=lambda r:r['name']),
                  'distros':normalize_distros(passive['distros']),'wslconfig':config}
        profile=match_profile(catalog,{'host':material['host'],'runtime':runtime,'config_digest':digest(config)})
        s=check_plan(plan)
        # Effective facts must match the exact reviewed/qualified plan profile in
        # the native driver itself, not only in the outer SessionRunner authorize
        # call. Direct native consumers (capture/recovery/evidence) can therefore
        # never receive an apparently valid Refresh with a mismatched profile.
        profile_verified=(profile==s['profile'])
        require(profile_verified,16,'LIVE_PROFILE_MISMATCH')
        ctx=Context(ctx.host_id,ctx.execution_sid,ctx.registered_class,ctx.build_digest,ctx.test_set_digest,
                    profile,ctx.elevated,datetime.now(timezone.utc))
        volumes=volume_observations(self.paths,self.binding['volume_paths'],s['budgets'])
        progress=completed_steps(coordinator.storage.read_events(),plan) if s['purpose']!='RECONCILIATION_ONLY' else {}
        afterbudgets=remaining_budgets(s,self.binding,progress)
        from .bindings import verify_volume_coverage
        physical_coverage=verify_volume_coverage(self.paths,self.api.system_directory(),self.binding,s,afterbudgets,
            pending_snapshots=0 if s['purpose']=='RECONCILIATION_ONLY' else len(s['operations'])-len(progress))
        observed={'physical_write_coverage':physical_coverage,'material':material,'resources':deepcopy(passive['resources']),
                  'free_bytes':{k:v['free_bytes'] for k,v in volumes.items()},'remaining_budgets':afterbudgets,
                  'volumes':volumes,'host':host,'principal':passive['principal'],'packaging':packaged,
                  'running':running,'timestamp_utc':ctx.now.isoformat(),'collection_kind':'WINDOWS_NATIVE_METADATA',
                  'read_captures':deepcopy(self.broker.captures[capture_start:]),'target':target_row(material,s['target']),
                  'profile_verified':profile_verified}
        floors(observed['resources']);budget_check(afterbudgets,observed['free_bytes'])
        self.last=Refresh(ctx,self.store,observed,self.store.generation,'WINDOWS_NATIVE_METADATA')
        return self.last

    def _reserve_journal(self,plan,coordinator):
        """Reserve all declared remaining journal bytes before any child read.

        The fixed native journal rejects quota expansion while held. Measuring
        actual free space is separate from its logical/log-capacity reservation.
        """
        limit=self.binding.get('journal_maximum_additional_bytes')
        require(type(limit) is int and limit>=4096,10,'JOURNAL_BUDGET_REQUIRED')
        vid=self.paths.volume(self.paths.root)['volume_id']
        budgets=[v for v in plan['semantic']['budgets'] if v['volume_id']==vid]
        require(len(budgets)==1 and sum(budgets[0]['allocations'].values()) >= limit,
                13,'JOURNAL_ALLOCATION_MISSING')
        volume=self.paths.volume(self.paths.root)
        budget_check(budgets,{vid:volume['free_bytes']})
        if coordinator.storage.reservation is None:
            coordinator.storage.reserve_capacity(limit,recovery=plan['semantic']['purpose']=='RECONCILIATION_ONLY')
        else:
            require(coordinator.storage.reservation.allowed_bytes==limit,16,'JOURNAL_RESERVATION_DRIFT')

    def _reader(self,fresh):return ProofReader(fresh.store,fresh.context.host_id,fresh.context.execution_sid,fresh.context.now)

    def _receipt(self,role,plan,fresh,scope,*,owner_assertion=False,not_before=None):
        ref=plan['semantic']['refs'].get(role)
        reader=self._reader(fresh)
        if ref is None:return reader.selected(role,scope,owner_assertion=owner_assertion,not_before=not_before)
        return reader.receipt(role,ref,scope,owner_assertion=owner_assertion,not_before=not_before)

    def _source(self,plan,fresh):
        s=plan['semantic'];row=fresh.observed['target']
        require(row is not None and row['wsl_version']==2,11,'TARGET_WSL2_REQUIRED')
        value=self._receipt('source_manifest',plan,fresh,
            {'host_id':s['host_id'],'target_registration':row['registration_id'],'source_class':s['source_class']},owner_assertion=True)
        claim=value['claim']
        require(claim.get('source_class')==s['source_class'] and claim.get('startup_known') is True
                and claim.get('quiesce_possible') is True,11,'SOURCE_STARTUP_UNKNOWN')
        require(s['source_class'] in ('CLEAN_P00','ADOPT_NONSENSITIVE_QUIESCED','SYNTHETIC_LAB'),11,'SOURCE_CLASS_FORBIDDEN')
        require(s['source_class']!='SYNTHETIC_LAB' or s['execution_class']=='LAB',12,'SYNTHETIC_SITE_FORBIDDEN')
        require(claim.get('config_digest')==digest(fresh.observed['material']['wslconfig']),16,'SOURCE_CONFIG_DRIFT')
        return value

    def _protection_boundary(self,fresh):
        # A consistency boundary covers source data/config, not the runtime
        # version that this exact approved C3 transaction intentionally changes.
        # Exclusive VHD handles prove the same-SID sources are not still open.
        material=fresh.observed['material'];rows=material['distros']['rows']
        require(not rows or fresh.observed['running'] is not None,11,'QUIESCE_NOT_OBSERVED')
        require(not rows or not fresh.observed['running'],20,'AFFECTED_DISTROS_MUST_BE_STOPPED')
        sources=[]
        for row in rows:
            closed=self._vhd_closed(row)
            sources.append({'registration':deepcopy(row),'file_identity':closed['file_identity'],
                            'volume_id':closed['volume_id']})
        return {'host_id':fresh.context.host_id,'owner_sid':fresh.context.execution_sid,
                'distros':sources,'default':material['distros']['default'],
                'wslconfig':deepcopy(material['wslconfig'])}

    def _protect(self,plan,fresh,coordinator):
        s=plan['semantic'];target=fresh.observed['target'];rid=target['registration_id'] if target else None
        boundary=self._protection_boundary(fresh)
        scope={'host_id':s['host_id'],'source_witness':digest(boundary)}
        receipt=self._receipt('protection',plan,fresh,scope,owner_assertion=True)
        protection(receipt['claim'],s['host_id'],rid,fresh.context.now,scope['source_witness'])
        actual={r['registration_id'] for r in fresh.observed['material']['distros']['rows']}
        covered={r['resource_id'] for r in receipt['claim']['rows']}
        require(actual<=covered,11,'IMPACT_OBSERVED_RESOURCE_MISSING')
        self.proofs['protection']=receipt
        coordinator.storage.append_event({'kind':'PRE_C3_PROOF_OBSERVED',
            'plan_digest':plan['plan_digest'],'scope':scope,'proof_ref':receipt['ref'],
            'checked_at':fresh.context.now.isoformat(),'boundary':boundary,
            'claim_digest':digest(receipt['claim'])})
        return receipt

    def _envelope(self,plan,fresh,*,require_unused=True):
        s=plan['semantic']
        receipt=self._receipt('restore_envelope',plan,fresh,
            {'host_id':s['host_id'],'checkpoint_digest':s.get('expected_checkpoint'),
             'envelope_digest':s.get('expected_envelope')})
        restore_envelope(receipt['claim'],s['source_class'],s['execution_class'],s['expected_checkpoint'],
                         fresh.context.now,s['expected_envelope'])
        require(receipt['claim'].get('destination_host_id')==s['host_id'],16,'ENVELOPE_DESTINATION')
        # This policy receipt includes outside-guest actual controller probes.
        # It is never inferred from a distro name or an in-guest ping failure.
        self.proofs['envelope']=receipt
        return receipt

    def preconditions(self,plan,step,fresh,coordinator):
        s=plan['semantic'];action=s['operations'][step]['action'];row=fresh.observed['target']
        self.before_action[step]=deepcopy(fresh.observed)
        if s['operations'][step]['class']=='C3':
            if action in ('ENABLE_PREREQUISITES','INSTALL_RUNTIME'):
                require(not any(self.system.pending_reboot().values()),20,'PREEXISTING_REBOOT_PENDING')
                self.system.installer_idle(action)
            self._protect(plan,fresh,coordinator)
        if action in ('INSTALL_DISTRO','IMPORT_NEW_CLONE'):
            require(row is None and not file_presence(self.paths,s['target']['base_path']),16,'TARGET_ALREADY_EXISTS')
            with self.paths.pin(str(PureWindowsPath(s['target']['base_path']).parent),directory=True,confidential=False):pass
            if action=='IMPORT_NEW_CLONE':self._envelope(plan,fresh)
        elif action=='INSTALL_RUNTIME':
            require(fresh.observed['material']['runtime']['status']!='PRESENT'
                    or self.binding.get('runtime_change_explicit') is True,12,'RUNTIME_CHANGE_NOT_APPROVED')
        elif action not in ('ENABLE_PREREQUISITES','AWAIT_OWNER_RESTART','OBSERVE_HOST','PUBLISH_SAFE_BUNDLE'):
            require(row is not None,11,'TARGET_NOT_CREATED')
        if action in ('PROBE_GUEST','CREATE_WORKSPACE','EXPORT_CHECKPOINT','STOP_START_TARGET','VERIFY_TERMINAL','VERIFY_CLONE','STOP_RETAIN_CLONE'):
            self.proofs['source']=self._source(plan,fresh)
        if action=='VERIFY_CLONE':self._envelope(plan,fresh,require_unused=False)
        if action=='EXPORT_CHECKPOINT':
            require(fresh.observed['running'] is not None and s['target']['name'] not in fresh.observed['running'],
                    20,'SOURCE_MUST_BE_QUIESCED_AND_STOPPED')
            require(not file_presence(self.paths,self.binding['export_path']),16,'CHECKPOINT_ALREADY_EXISTS')
        if action in ('INSTALL_RUNTIME','INSTALL_DISTRO'):
            from .trust import validate_payload_graph
            payload=validate_payload_graph(fresh.store,s['refs']['payload'],s['payload_digest'])
            if action=='INSTALL_RUNTIME':
                with self.paths.pinned_payload(payload['path'],payload['payload_digest'],payload['bytes']):
                    signature=self.broker.host('AUTHENTICODE',payload['path'])
                require(signature['status']=='Valid' and signature['thumbprint'] in self.binding.get('runtime_signers',[]),15,'RUNTIME_AUTHENTICODE')
        require(action in self.binding['after_by_action'],10,'AFTER_STATE_BINDING_MISSING')

    def witness(self,plan,step,fresh):
        return {'host_boot':fresh.observed['host']['boot_utc'],'controller_pid':self.api.get_current_pid(),
                'controller_start':str(self.api.process_start(self.api.get_current_process())),
                'build_digest':fresh.context.build_digest,'step_id':'step-'+str(step),
                'captured_at':fresh.context.now.isoformat(),'material_before_digest':digest(fresh.observed['material'])}

    def _guest(self,plan,operation,coordinator,extra=None):
        s=plan['semantic'];request={'operation':operation,'user':s['target']['user'],**(extra or {})}
        # Recheck immutable reviewed content before using agent bytes.
        from ..content import content_identity
        require(content_identity(self.root)['source_content_digest']==s['build_digest'],16,'GUEST_SOURCE_DRIFT')
        return GuestTransport(self.root,self.supervisor,self.api.system_directory(),self.environment,self.source_pins).run(
            s['target']['name'],s['target']['user'],request,coordinator)

    def _eligible_guest(self,plan,coordinator,source):
        inventory=self._guest(plan,'INVENTORY',coordinator)
        admin=self._guest(plan,'ADMIN',coordinator)
        g=inventory['capture']['actual'];a=admin['capture']['actual']
        row=self.last.observed['target'];claim=source['claim']
        normalized={'os_id':g['os_id'],'version_id':g['version_id'],'architecture':g['architecture'],
            'wsl_version':row['wsl_version'],'uid':g['uid'],'home_writable':g['home_access_writable'],
            'admin_ready':a['admin_ready'],'startup_known':claim['startup_known'],
            'quiesce_possible':claim['quiesce_possible'],'source_class':claim['source_class']}
        guest_profile(normalized);floors(g['resources'],guest=True)
        require(g['user']==plan['semantic']['target']['user'] and g['uid']==row['default_uid'],16,'GUEST_USER_BINDING')
        require(g['wsl_conf_sha256']==claim.get('wsl_conf_sha256'),16,'GUEST_STARTUP_CONFIG_DRIFT')
        return {'inventory':inventory['capture'],'admin':admin['capture'],'agent_digest':inventory['agent_digest']}

    def _execute_fixed(self,argv,action,coordinator,timeout=30):
        def before(w):
            if coordinator.fence['state']=='INTENT':coordinator.native_started(w)
            else:coordinator.native_child_started(w)
        result=self.supervisor.run(Command(tuple(argv),action,timeout,b'',True),before_resume=before,
                                   environment=self.environment,cwd=self.api.system_directory())
        coordinator.storage.append_event({'kind':'NATIVE_PROCESS_COMPLETED','plan_digest':coordinator.admission.plan_digest,
            'action':action,'native_witness':result.native_witness,'native_exit':result.exit_code,
            'tree_terminal':result.tree_terminal,'service_terminal':False})
        require(result.exit_code==0,18,'NATIVE_ACTION_FAILED')
        return result

    def run(self,plan,step,fresh,coordinator):
        s=plan['semantic'];action=s['operations'][step]['action']
        if action in SUPPORTED_ACTIONS:
            with ExitStack() as pins:
                if action in ('INSTALL_DISTRO','IMPORT_NEW_CLONE'):
                    pins.enter_context(self.paths.pin(str(PureWindowsPath(s['target']['base_path']).parent),directory=True,confidential=False))
                if action=='EXPORT_CHECKPOINT':
                    pins.enter_context(self.paths.pin(str(PureWindowsPath(self.binding['export_path']).parent),directory=True,protected=True))
                result=NativeActuator(self.supervisor,self.paths,fresh.store,self.api.system_directory(),self.environment).execute(
                    action,plan,coordinator,self.binding)
            if action in ('ENABLE_PREREQUISITES','INSTALL_RUNTIME') and result.get('state')!='AWAITING_REBOOT':
                from .lifecycle import classify_c3_process_result
                result=classify_c3_process_result(action,result,self.system.pending_reboot())
            return result
        if action=='AWAIT_OWNER_RESTART':return {'state':'AWAITING_REBOOT','exit':20}
        if action=='AWAIT_OWNER_USER_INIT':
            # A completed approved first-user setup can be observed without
            # prompting or replaying OOBE. Otherwise retain the original fence.
            row=fresh.observed.get('target')
            if row is not None and type(row.get('default_uid')) is int and row['default_uid']>0:
                try:
                    receipt=self._reader(fresh).selected('user_init_receipt',{'host_id':s['host_id'],
                        'plan_digest':plan['plan_digest'],'target_registration':row['registration_id'],'user':s['target']['user']})
                except P00Error as error:
                    if error.code==20:return {'state':'AWAITING_OWNER_VERIFICATION','exit':20}
                    raise
                return {'state':'OBSERVED','user_init':receipt}
            return {'state':'AWAITING_USER_INIT','exit':20}
        if action=='OBSERVE_HOST':return {'state':'OBSERVED','raw':deepcopy(fresh.observed)}
        if action=='PROBE_GUEST':return {'state':'OBSERVED','guest':self._guest(plan,'INVENTORY',coordinator)['capture']}
        if action=='CREATE_WORKSPACE':
            eligible=self._eligible_guest(plan,coordinator,self.proofs['source'])
            fresh2=self.refresh(plan,coordinator=coordinator,step=step)
            authorize(interface_for(plan),plan,fresh2.context,fresh2.store)
            require(fresh2.observed['material']==fresh.observed['material'],16,'MATERIAL_DRIFT')
            workspace=self.binding['workspace']
            result=self._guest(plan,'WORKSPACE',coordinator,workspace)
            return {'state':'OBSERVED','guest':eligible,'workspace':result['capture']}
        if action=='STOP_START_TARGET':
            eligible=self._eligible_guest(plan,coordinator,self.proofs['source'])
            before=self._guest(plan,'ASSERT_CONTENT',coordinator,{'critical_files':self.binding['critical_files']})
            self._execute_fixed(compile_wsl('STOP_TARGET',system_directory=self.api.system_directory(),target=s['target']['name']),action,coordinator)
            require(s['target']['name'] not in self.broker.running(),19,'TARGET_NOT_STOPPED')
            after=self._guest(plan,'INVENTORY',coordinator)
            content=self._guest(plan,'ASSERT_CONTENT',coordinator,{'critical_files':self.binding['critical_files']})
            old=eligible['inventory']['actual'];new=after['capture']['actual']
            require((old['kernel_boot_id'],old['pid1_start_ticks'])!=(new['kernel_boot_id'],new['pid1_start_ticks']),19,'TARGET_ACTIVATION_NOT_OBSERVED')
            require(before['capture']['actual']==content['capture']['actual'],19,'CONTENT_CHANGED_ACROSS_LIFECYCLE')
            return {'state':'OBSERVED','before':eligible,'after':after['capture'],'content':content['capture']}
        if action=='VERIFY_CLONE':
            self._envelope(plan,fresh,require_unused=False)
            eligible=self._eligible_guest(plan,coordinator,self.proofs['source'])
            content=self._guest(plan,'ASSERT_CONTENT',coordinator,{'critical_files':self.binding['critical_files']})
            return {'state':'OBSERVED','guest':eligible,'content':content['capture'],'envelope':self.proofs['envelope']}
        if action=='VERIFY_TERMINAL':
            from .terminal_sweep import NativeTerminalSweep
            return NativeTerminalSweep(self).run(plan,coordinator,fresh)
        if action=='PUBLISH_SAFE_BUNDLE':
            from .evidence_pipeline import NativeEvidencePipeline
            return NativeEvidencePipeline(self).publish(plan,coordinator,fresh)
        raise P00Error(10,'ACTION_NOT_IN_NATIVE_ROUTE')

    def _vhd_closed(self,row):
        path=str(PureWindowsPath(row['base_path'])/'ext4.vhdx')
        actual=self._checkpoint(path,confidential=False)
        return {'file_identity':actual['identity'],'volume_id':actual['volume_id'],
                'sha256':actual['sha256'],'exclusive_writer_excluded':True}

    def _checkpoint(self,path,*,confidential=True):
        from .winapi import DWORD
        with self.paths.pin(path,confidential=confidential) as pinned:
            expected_bytes=pinned.identity['bytes'];h=hashlib.sha256();total=0
            while True:
                buf=C.create_string_buffer(65536);n=DWORD()
                self.api.ok(self.api.read_file(pinned.handle,buf,len(buf),C.byref(n),None),'CHECKPOINT_READ')
                if n.value==0:break
                h.update(buf.raw[:n.value]);total+=n.value
            require(total==expected_bytes and total>0,15,'CHECKPOINT_SIZE_DRIFT')
            return {'sha256':h.hexdigest(),'bytes':total,'identity':deepcopy(pinned.identity),
                    'volume_id':pinned.volume['volume_id'],'exclusive_writer_excluded':True}

    def _post_c3(self,plan,fresh,coordinator):
        s=plan['semantic'];scope={'host_id':s['host_id'],'plan_digest':plan['plan_digest'],
                                'host_boot':fresh.observed['host']['boot_utc']}
        receipt=self._reader(fresh).selected('c3_postchecks',scope,owner_assertion=True,not_before=instant(fresh.observed['host']['boot_utc']))
        prior=self.proofs.get('protection')
        if prior is None:
            rows=[r['event'] for r in coordinator.storage.read_events()
                  if r['event'].get('kind')=='PRE_C3_PROOF_OBSERVED'
                  and r['event'].get('plan_digest')==plan['plan_digest']]
            require(bool(rows),15,'PRE_C3_JOURNAL_PROOF_MISSING')
            historic=rows[-1]
            require(digest(historic['boundary'])==historic['scope']['source_witness'],15,'PRE_C3_BOUNDARY_INTEGRITY')
            # Validate the original receipt at its recorded precondition time,
            # while honoring CURRENT pins/withdrawal. It is not reissued after C3.
            prior=ProofReader(fresh.store,s['host_id'],s['owner_sid'],instant(historic['checked_at'])).receipt(
                'protection',historic['proof_ref'],historic['scope'],owner_assertion=True)
            require(digest(prior['claim'])==historic['claim_digest'],15,'PRE_C3_PROOF_DRIFT')
        require(receipt['claim'].get('protection_ref')==prior['ref'],16,'C3_PROTECTION_PARENT')
        c3_postconditions(prior['claim']['rows'],receipt['claim']['rows'])
        return receipt

    def _after(self,plan,step,result,fresh,coordinator,*,reconciliation=False,resume_boundary=None):
        s=plan['semantic'];action=s['operations'][step]['action']
        # No caller-supplied completion bool. Read current process/job state,
        # current metadata and the action's data/service-level postconditions.
        writers=self.system.all_writers(coordinator.fence['native'])
        obs=fresh.observed;row=obs['target'];details={'writers':writers}
        if resume_boundary is not None:details['restart_boundary']=deepcopy(resume_boundary)
        if action=='ENABLE_PREREQUISITES':
            details['servicing']=self.system.installer_idle(action)
            require(all(r['state']=='Enabled' for r in obs['material']['features'] if r['name'] in self.binding['features']),19,'FEATURES_NOT_ENABLED')
            if resume_boundary is not None:details['affected_resources']=self._post_c3(plan,fresh,coordinator)
        elif action=='INSTALL_RUNTIME':
            details['servicing']=self.system.installer_idle(action);runtime_profile(obs['material']['runtime'])
            require(obs['material']['runtime']['version'] in self.binding['installed_runtime_versions'],19,'RUNTIME_NOT_EXPECTED')
            if resume_boundary is not None:details['affected_resources']=self._post_c3(plan,fresh,coordinator)
        elif action in ('INSTALL_DISTRO','IMPORT_NEW_CLONE'):
            require(row is not None and row['wsl_version']==2,19,'REGISTRATION_NOT_COMPLETE')
            require(obs['running'] is not None and s['target']['name'] not in obs['running'],19,'UNEXPECTED_AUTO_LAUNCH')
            details['vhd']=self._vhd_closed(row)
        elif action=='EXPORT_CHECKPOINT':
            require(s['target']['name'] not in obs['running'],19,'SOURCE_NOT_QUIESCENT')
            details['source_vhd']=self._vhd_closed(row)
            details['checkpoint']=self._checkpoint(self.binding['export_path'])
        elif action=='STOP_RETAIN_CLONE':
            require(s['target']['name'] not in obs['running'],19,'CLONE_STILL_RUNNING')
            details['vhd']=self._vhd_closed(row)
        elif action=='AWAIT_OWNER_RESTART':
            require(resume_boundary is not None,20,'REBOOT_NOT_OBSERVED')
            details['affected_resources']=self._post_c3(plan,fresh,coordinator)
        elif action=='AWAIT_OWNER_USER_INIT':
            require(row is not None and type(row['default_uid']) is int and row['default_uid']>0,20,'USER_INIT_NOT_OBSERVED')
            receipt=self._reader(fresh).selected('user_init_receipt',{'host_id':s['host_id'],
                'plan_digest':plan['plan_digest'],'target_registration':row['registration_id'],'user':s['target']['user']})
            require(receipt['claim'].get('uid')==row['default_uid'] and receipt['claim'].get('home_writable') is True
                    and receipt['claim'].get('os_id')=='ubuntu' and receipt['claim'].get('version_id')=='24.04',19,'USER_INIT_POSTCONDITION')
            details['user_init']=receipt
        elif action in ('CREATE_WORKSPACE','STOP_START_TARGET','VERIFY_CLONE','PROBE_GUEST','VERIFY_TERMINAL'):
            if reconciliation:
                # C0 reconciliation cannot silently launch a guest. It consumes
                # a previously sealed actual operation observation plus a fresh
                # owner/controller continuation record for this exact epoch.
                receipt=self._reader(fresh).selected('operation_postcheck',{'host_id':s['host_id'],
                    'plan_digest':plan['plan_digest'],'step_id':'step-'+str(step),
                    'target_registration':row['registration_id'],'host_boot':obs['host']['boot_utc']})
                details['actual_result']=receipt
            else:
                require(result.get('state')=='OBSERVED',19,'ACTUAL_OPERATION_OBSERVATION_REQUIRED')
                details['actual_result']=deepcopy(result)
        elif action=='OBSERVE_HOST':details['metadata']=deepcopy(obs)
        elif action=='PUBLISH_SAFE_BUNDLE':
            if reconciliation:
                from .publication_recovery import observed_publication
                result=observed_publication(self.paths,coordinator,plan,self.binding)
                from .assessment import assessment_intent_count,recover_assessment
                assessment_required=(s.get('bundle_scope')=='GATE_HANDOFF'
                                     and result.get('component_eligible') is True)
                count=assessment_intent_count(coordinator,plan['plan_digest'])
                if assessment_required:
                    require(count>0,18,'ASSESSMENT_INTENT_MISSING')
                    result['assessment']=recover_assessment(self.paths,coordinator,plan,self.binding['assessment_output'])
                else:
                    require(count==0,16,'ASSESSMENT_NOT_APPLICABLE')
            require(result.get('published') is True or result.get('archive_expected') is False,19,'PUBLISH_NOT_OBSERVED')
            details['bundle']=deepcopy(result)
        else:raise P00Error(10,'ACTION_AFTERSTATE_SCOPE')
        expected=operation_expected(self.binding,plan,action,obs['material'])
        evidence={'kind':'NATIVE_OPERATION_AFTER','action':action,'host_id':s['host_id'],
                  'plan_digest':plan['plan_digest'],'timestamp_utc':fresh.context.now.isoformat(),
                  'host_boot':obs['host']['boot_utc'],'details':details,'captures':expected['captures'],
                  'metadata':deepcopy(obs),'source_kind':self.source_kind}
        coordinator.storage.append_event({'kind':'OPERATION_AFTER_OBSERVED','plan_digest':plan['plan_digest'],
            'step_id':'step-'+str(step),'evidence':evidence,'evidence_digest':digest(evidence)})
        self.actual_steps[step]=evidence
        return Completion(deepcopy(obs['material']),evidence,True,True,deepcopy(coordinator.fence['native']))

    def observe(self,plan,step,result,fresh,coordinator):
        current=self.refresh(plan,coordinator=coordinator,step=step)
        authorize(interface_for(plan),plan,current.context,current.store)
        completed=self._after(plan,step,result,current,coordinator)
        from .evidence_pipeline import NativeEvidencePipeline
        snapshot=NativeEvidencePipeline(self).capture(plan,coordinator,current,result)
        from dataclasses import replace
        return replace(completed,raw_evidence={**completed.raw_evidence,
            'snapshot':{'index_digest':snapshot['index_digest'],'record_count':snapshot['record_count'],
                        'capture_source_plan':snapshot['plan_digest']}})

    def record_failure(self,plan,error,coordinator):
        """Capture known actuals, without hidden host/guest repair or promotion.

        The original exception always wins if authority, storage or collectors
        themselves fail. A failed attempt leaves its durable original fence.
        """
        if not coordinator.held or coordinator.fence is None:
            return None
        failure={'exit':int(error.code) if isinstance(error,P00Error) else 18,
                 'reason':error.reason if isinstance(error,P00Error) else 'CONTROLLER_INTERRUPTED'}
        if self.last is None:
            # Failure occurred after durable INTENT but before the first usable
            # observation snapshot. Preserve a bounded, non-authoritative journal
            # capsule rather than silently losing the event or inventing E00 facts.
            event={'kind':'EARLY_FAILURE_CAPTURED','plan_digest':plan['plan_digest'],
                   'run_id':plan['semantic']['run_id'],'action':coordinator.fence['action'],
                   'fence_state':coordinator.fence['state'],'failure':failure,
                   'host_ready':False,'qualification_issued':False}
            coordinator.storage.append_event(event)
            return {'status':'JOURNAL_ONLY','event_digest':digest(event),'host_ready':False}
        latest=self.refresh(plan,coordinator=None)
        authorize(interface_for(plan),plan,latest.context,latest.store)
        require(latest.generation>=self.last.generation,15,'AUTHORITY_ROLLBACK')
        from dataclasses import replace
        from .evidence_pipeline import NativeEvidencePipeline
        known=replace(self.last,store=latest.store,generation=latest.generation)
        return NativeEvidencePipeline(self).capture(plan,coordinator,known,failure=failure)

    def reserve_c0_capture(self,request,coordinator):
        self._reserve_journal(request,coordinator)

    def capture_c0(self,request,coordinator):
        from .recovery_driver import refresh_recovery
        ctx,passive,catalog=self._authority_snapshot(request)
        require(request['semantic']['purpose']=='PASSIVE',12,'C0_CAPTURE_SCOPE')
        return refresh_recovery(self,request,ctx,passive,catalog,coordinator)

    def refresh_read_recovery(self,request,coordinator):
        from .read_request_recovery import refresh
        return refresh(self,request,coordinator)

    def reserve_read_recovery(self,request,fresh,coordinator,count):
        from .read_request_recovery import reserve
        return reserve(self,request,fresh,coordinator,count)

    def read_run_revocation(self,original,request,fresh,disposition):
        from .read_request_recovery import run_revocation
        return run_revocation(self,original,request,fresh,disposition)

    def observe_detached_read(self,entry,fresh,diagnostic=False):
        from .read_request_recovery import observe
        return observe(self,entry,fresh,diagnostic)

    def diagnose(self,original,step,fresh,coordinator):
        from .recovery_driver import diagnose
        return diagnose(self,original,step,fresh,coordinator)

    def pause_observation(self,original,step,fresh,coordinator,*,request,disposition):
        from .recovery_driver import pause_observation
        return pause_observation(self,original,step,fresh,coordinator,
                                 request=request,disposition=disposition)

    def reconcile(self,original,step,fresh,coordinator):
        # Fresh context was authorized for read-only reconciliation. Resolve the
        # original immutable binding for after-state matching, not for actuation.
        require(type(fresh.observed.get('material')) is dict
                and fresh.observed.get('profile_verified') is True,11,'RECONCILIATION_FACTS_INCOMPLETE')
        from .read_recovery import reconcile_detached_reads
        reconcile_detached_reads(self.system,coordinator)
        request_binding=self.binding
        self.binding=_binding(fresh.store,original['semantic'])
        try:
            if coordinator.fence['witness'].get('execution_phase')=='LIVE_REVALIDATION':
                from .noop import reconcile
                return reconcile(self,original,fresh,coordinator)
            wait_context=coordinator.fence.get('wait_observation') or {}
            needs_reboot=(coordinator.fence.get('state')=='AWAITING_REBOOT'
                or (coordinator.fence.get('state')=='AWAITING_OWNER_VERIFICATION'
                    and wait_context.get('previous_state')=='AWAITING_REBOOT'))
            resume_boundary=None
            if needs_reboot:
                from .lifecycle import reboot_resume_boundary
                resume_boundary=reboot_resume_boundary(coordinator.fence,fresh.observed.get('host'),
                                                       self.system.pending_reboot())
            return self._after(original,step,{},fresh,coordinator,reconciliation=True,
                               resume_boundary=resume_boundary)
        finally:self.binding=request_binding

    def pre_noop(self,plan,fresh,coordinator,completed):
        from .noop import preconditions
        return preconditions(self,plan,fresh,coordinator,completed)

    def revalidate_committed(self,plan,fresh,coordinator,completed):
        from .noop import revalidate
        return revalidate(self,plan,fresh,coordinator,completed)

    def final_assertions(self,plan,fresh,coordinator,completed):
        expected=final_expected(self.binding,plan,fresh.observed['material'])
        s=plan['semantic'];purpose=s['purpose'];row=fresh.observed['target']
        require(len(completed)==len(s['operations']),19,'SESSION_STEPS_INCOMPLETE')
        # Direct final assertions cannot bypass the separate journaled live
        # revalidation path selected by SessionRunner for committed reruns.
        require(len(s['operations'])-1 in self.actual_steps,11,'LIVE_REVALIDATION_REQUIRED')
        # State is checked again after final metadata probes. Committed content
        # evidence remains linked; final report does not invent fresh guest tests.
        if purpose not in ('ENGINE','PASSIVE','SUPPORT_BUNDLE','RESTORE_EXPORT'):
            require(row is not None,19,'TARGET_NOT_PRESENT')
        if s['final_state']=='RUNNING' and row is not None:
            require(s['target']['name'] in fresh.observed['running'],19,'FINAL_TARGET_NOT_RUNNING')
        if s['final_state']=='STOPPED_RETAINED' and row is not None:
            require(s['target']['name'] not in fresh.observed['running'],19,'FINAL_TARGET_NOT_STOPPED')
        outcome={}
        if purpose=='SUPPORT_BUNDLE':
            actual=completed[len(s['operations'])-1]['observations']['details']['bundle']
            require(type(actual.get('exit')) is int and actual['exit'] in (0,2,15,18,22,23),19,'BUNDLE_OUTCOME_REQUIRED')
            outcome={'exit':actual['exit'],'state':actual['outcome']}
        return {'interface_outcome':outcome,'material_digest':expected['material_digest'],'completed_step_digests':
                 {str(k):v['evidence_digest'] for k,v in completed.items()},
                 'final_running':fresh.observed['running'],'timestamp_utc':fresh.context.now.isoformat(),
                 'source_kind':self.source_kind,'host_ready':False}


def native_session(root):
    """Only production factory. Never constructed by workspace CLI branches."""
    root=Path(root)
    api,store,_,_,_=_entry(root)
    paths=WindowsPaths(api,store.operators);guard=NativeGuard(api,store.operators)
    coordinator=Coordinator(guard,NativeJournal(paths,guard,store.host_id))
    supervisor=NativeSupervisor(api,paths,guard,require_executable_trust=True);system=NativeSystemState(api)
    return SessionRunner(NativeDriver(root,api,paths,supervisor,system,store.operators),coordinator)
