"""Read-only native authority adapter with an out-of-band HKLM trust anchor.

Nothing here enrolls a host, writes the anchor, issues approvals/qualification,
or treats a fixture file as authority. Host-owner provisioning is external;
missing authority blocks. Each read_anchor call obtains a fresh policy/ACL snapshot.
The production NativeDriver refreshes this authority before each admitted step.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import timedelta
import os
from pathlib import Path
from .. import CONTRACT_DIGEST
from ..authority import PinnedStore
from ..codec import loads,canonical,sha256,digest,hash_value,instant,fields
from ..errors import P00Error,require
from .security import ADMIN_OWNERS,check_security,sid

ANCHOR_KEY=r'SOFTWARE\AI-FILM-SERVER\Phase00\Trust'
ANCHOR_VALUE='Policy'
ANCHOR_CAP=10*1024**2


@dataclass(frozen=True)
class MetadataPermit:
    host_id:str
    owner_sid:str
    build_digest:str
    approval_digest:str


def normalize_design(raw,contract_directory):
    """Normalize the actual uppercase review artifact; do not fabricate a review."""
    require(raw.get('APPROVAL_TYPE')=='DESIGN_REVIEW_PASS' and raw.get('VERDICT')=='PASS'
            and raw.get('REVIEW_ID')=='REVIEW-P00-002',15,'DESIGN_CHAIN_INVALID')
    rows=raw.get('NORMATIVE_CONTRACT_SET')
    require(type(rows) is list and len(rows)==4 and raw.get('NORMATIVE_CONTRACT_SET_DIGEST')==CONTRACT_DIGEST,
            15,'DESIGN_CONTRACT_SET_INVALID')
    expected={'PHASE00_INFRA_DESIGN_V2.md','PHASE00_ACCEPTANCE_MATRIX_V2.md',
              'PHASE00_FAILURE_RECOVERY_PLAN_V2.md','PHASE00_EVIDENCE_AND_RESEARCH_REGISTER_V2.md'}
    require({r.get('path') for r in rows}==expected,15,'DESIGN_CONTRACT_SET_INVALID')
    require(digest(sorted(rows,key=lambda r:r['path']))==CONTRACT_DIGEST,15,'DESIGN_CONTRACT_SET_HASH')
    for row in rows:
        path=Path(contract_directory)/row['path']
        require(path.is_file() and not path.is_symlink(),15,'CONTRACT_FILE_MISSING')
        blob=path.read_bytes()
        require(len(blob)==row['bytes'] and sha256(blob)==row['sha256'],15,'CONTRACT_FILE_CHANGED')
    require(raw.get('IMPLEMENTATION_AUTHORING_ENTRY_OPEN') is True and raw.get('OPEN_REQUIRED_CHANGES')==[],15,'DESIGN_ENTRY_CLOSED')
    return {'role':'design','verdict':'PASS','contract_digest':CONTRACT_DIGEST,
            'withdrawn':False,'raw_review_id':raw['REVIEW_ID']}


class NativeStore:
    def __init__(self,policy_bytes,contract_directory):
        policy=loads(policy_bytes)
        fields(policy,{'schema_version','host_id','operator_sids','role_pins','blobs','withdrawn_refs','generation'})
        require(policy['schema_version']==1 and type(policy['generation']) is int and policy['generation']>=1,15,'ANCHOR_SCHEMA')
        require(type(policy['operator_sids']) is list and bool(policy['operator_sids']),15,'ANCHOR_OPERATORS')
        self.operators=frozenset(sid(s) for s in policy['operator_sids'])
        require(type(policy['role_pins']) is dict and type(policy['blobs']) is dict and type(policy['withdrawn_refs']) is list,15,'ANCHOR_SCHEMA')
        self.host_id=policy['host_id']; self.generation=policy['generation']
        self.policy_digest=sha256(policy_bytes); self.withdrawn=frozenset(policy['withdrawn_refs'])
        for ref in self.withdrawn: hash_value(ref)
        self.pins={role:frozenset(refs) for role,refs in policy['role_pins'].items()}
        self.blobs={ref:value.encode('utf-8') for ref,value in policy['blobs'].items() if type(value) is str}
        require(len(self.blobs)==len(policy['blobs']),15,'ANCHOR_BLOB_TYPE')
        for refs in self.pins.values():
            for ref in refs:
                hash_value(ref)
                require(ref in self.blobs and sha256(self.blobs[ref])==ref,15,'ANCHOR_BLOB_HASH')
        self.contract_directory=contract_directory
        self.provenance='WINDOWS_HKLM_ACL_ANCHOR'

    def get(self,role,ref):
        hash_value(ref)
        require(ref in self.pins.get(role,frozenset()),15,'UNTRUSTED_DOCUMENT')
        require(ref not in self.withdrawn,11,'AUTHORITY_WITHDRAWN')
        blob=self.blobs.get(ref)
        require(blob is not None and sha256(blob)==ref,15,'DOCUMENT_INTEGRITY')
        data=loads(blob)
        require(type(data) is dict,15,'DOCUMENT_SCHEMA')
        if role=='design' and 'APPROVAL_TYPE' in data:
            return normalize_design(data,self.contract_directory)
        require(data.get('role')==role,15,'DOCUMENT_ROLE_MISMATCH')
        require(data.get('fixture_only') is not True or role=='lab_fixture_spec',
                15,'WORKSPACE_AUTHORITY_FORBIDDEN')
        return data

    def one(self,role):
        refs=self.pins.get(role,frozenset())-self.withdrawn
        require(len(refs)==1,15,'AUTHORITY_SELECTION_AMBIGUOUS')
        ref=next(iter(refs)); return ref,self.get(role,ref)

    def metadata_permit(self,principal,build_digest,now):
        require(principal['execution_sid'] in self.operators,12,'OPERATOR_NOT_REGISTERED')
        dref,_=self.one('design'); cref,code=self.one('code')
        require(code.get('verdict')=='PASS' and code.get('withdrawn') is False and code.get('build_digest')==build_digest
                and code.get('contract_digest')==CONTRACT_DIGEST,11,'CODE_REVIEW_REQUIRED')
        ref,value=self.one('metadata_initialization')
        require(value.get('host_id')==self.host_id and value.get('owner_sid')==principal['execution_sid']
                and value.get('build_digest')==build_digest and value.get('class')=='C0'
                and value.get('design_ref')==dref and value.get('code_ref')==cref
                and value.get('withdrawn') is False,12,'METADATA_APPROVAL_SCOPE')
        issued=instant(value['issued_at']); expires=instant(value['expires_at'])
        require(issued<=now<=expires and expires-issued<=timedelta(hours=24),12,'METADATA_APPROVAL_EXPIRED')
        return MetadataPermit(self.host_id,principal['execution_sid'],build_digest,ref)


def read_anchor(api,contract_directory):
    require(os.name=='nt',11,'WINDOWS_X64_REQUIRED')
    import winreg
    try:
        # The entire read handle is validated; a user-writable child key cannot
        # become authority merely because its path begins with HKLM.
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,ANCHOR_KEY,0,winreg.KEY_READ|winreg.KEY_WOW64_64KEY) as key:
            check_security(api.security(int(key),4),owners=ADMIN_OWNERS,writers=ADMIN_OWNERS,
                           readers=ADMIN_OWNERS,confidential=False,registry=True)
            value,kind=winreg.QueryValueEx(key,ANCHOR_VALUE)
            require(kind==winreg.REG_SZ and type(value) is str,15,'ANCHOR_VALUE_TYPE')
            data=value.encode('utf-8'); require(len(data)<=ANCHOR_CAP,15,'ANCHOR_TOO_LARGE')
        return NativeStore(data,contract_directory)
    except P00Error: raise
    except (OSError,UnicodeError): raise P00Error(12,'TRUST_ANCHOR_UNAVAILABLE') from None


def validate_payload_graph(store,ref,expected_digest):
    p=store.get('payload',ref)
    require(p.get('payload_digest')==expected_digest and p.get('withdrawn') is False,15,'PAYLOAD_TRUST_INVALID')
    require(type(p.get('bytes')) is int and p['bytes']>0 and isinstance(p.get('path'),str),15,'PAYLOAD_BINDING_INCOMPLETE')
    metadata=store.get('release_metadata',p['trusted_metadata_digest'])
    require(metadata.get('authenticated') is True and metadata.get('trust_anchor')==p.get('trust_anchor')
            and metadata.get('withdrawn') is False,15,'RELEASE_METADATA_UNTRUSTED')
    row={'filename':p.get('filename'),'bytes':p['bytes'],'sha256':expected_digest,'version':p.get('version')}
    require(row in metadata.get('artifacts',[]),15,'PAYLOAD_NOT_IN_RELEASE_METADATA')
    return p
