"""Pure admission authority verification; the native adapter is ACL anchored.
PinnedStore requires out-of-band role/digest pins. No input document can pin itself.
Workspace tests inject synthetic pins; they are never native execution authority.
"""
from dataclasses import dataclass
from datetime import timedelta
from . import CONTRACT_DIGEST
from .codec import loads,sha256,instant,hash_value,digest,token
from .plans import interface_check
from .errors import require,P00Error

@dataclass(frozen=True)
class PinnedStore:
    pins: dict[str,frozenset[str]]
    blobs: dict[str,bytes]
    provenance: str

    def get(self,role:str,ref:str)->dict:
        hash_value(ref)
        require(ref in self.pins.get(role,frozenset()),15,'UNTRUSTED_DOCUMENT')
        blob=self.blobs.get(ref)
        require(blob is not None and sha256(blob)==ref,15,'DOCUMENT_INTEGRITY')
        data=loads(blob)
        require(type(data) is dict and data.get('role')==role,15,'DOCUMENT_ROLE_MISMATCH')
        return data

@dataclass(frozen=True)
class Context:
    host_id: str
    execution_sid: str
    registered_class: str
    build_digest: str
    test_set_digest: str
    profile: dict
    elevated: bool
    now: object

@dataclass(frozen=True)
class Admission:
    plan_digest: str
    run_id: str
    host_id: str
    owner_sid: str
    classes: frozenset[str]
    execution_class: str
    purpose: str
    authority_document_digests: tuple[str,...]


def authorize(interface:str,plan:dict,ctx:Context,store:PinnedStore)->Admission:
    s=interface_check(interface,plan)
    require(ctx.host_id==s['host_id'] and ctx.execution_sid==s['owner_sid'],12,'WRONG_HOST_OR_PRINCIPAL')
    require(ctx.registered_class==s['execution_class'],12,'EXECUTION_CLASS_NOT_REGISTERED')
    refs=s['refs']; classes=frozenset(o['class'] for o in s['operations']); active=bool(classes-{'C0'})
    require({'registration','design','code'}<=refs.keys() and 'approval_ref' in plan,12,'AUTHORITY_REFERENCES_MISSING')
    registration=store.get('registration',refs['registration'])
    require(registration.get('host_id')==ctx.host_id and registration.get('execution_class')==ctx.registered_class and ctx.execution_sid in registration.get('operator_sids',[]),12,'HOST_REGISTRATION_MISMATCH')
    require(registration.get('withdrawn') is False,12,'HOST_REGISTRATION_WITHDRAWN')
    approval=store.get('approval',plan['approval_ref'])
    require(approval.get('plan_digest')==plan['plan_digest'] and approval.get('owner_sid')==ctx.execution_sid,12,'APPROVAL_SCOPE')
    require(approval.get('interface')==interface and approval.get('purpose')==s['purpose'] and approval.get('withdrawn') is False,12,'APPROVAL_SCOPE')
    require(set(approval.get('classes',[]))==classes,12,'APPROVAL_CLASS')
    issued=instant(approval['issued_at']); expires=instant(approval['expires_at'])
    require(issued<=ctx.now<=expires and expires-issued<=timedelta(hours=24),12,'APPROVAL_EXPIRED')
    require(instant(approval['maintenance_start'])<=ctx.now<=instant(approval['maintenance_end']),12,'OUTSIDE_MAINTENANCE')
    if 'C3' in classes: require(ctx.elevated,12,'ELEVATION_REQUIRED')
    require(ctx.build_digest==s['build_digest'] and ctx.test_set_digest==s['test_set_digest'],16,'EXECUTABLE_CONTENT_MISMATCH')
    design=store.get('design',refs['design']); code=store.get('code',refs['code'])
    require(design.get('verdict')=='PASS' and design.get('contract_digest')==CONTRACT_DIGEST and design.get('withdrawn') is False,15,'DESIGN_CHAIN_INVALID')
    require(code.get('verdict')=='PASS' and code.get('withdrawn') is False,11,'CODE_REVIEW_REQUIRED')
    require(code.get('build_digest')==ctx.build_digest and code.get('test_set_digest')==ctx.test_set_digest and code.get('contract_digest')==CONTRACT_DIGEST,16,'CODE_REVIEW_CONTENT_MISMATCH')
    if s['payload_digest'] is not None:
        require('payload' in refs,15,'PAYLOAD_TRUST_MISSING')
        payload=store.get('payload',refs['payload'])
        require(payload.get('payload_digest')==s['payload_digest'] and payload.get('trusted_metadata_digest') is not None and payload.get('trust_anchor') is not None and payload.get('withdrawn') is False,15,'PAYLOAD_TRUST_INVALID')
    if ctx.registered_class=='LAB':
        # controller_external is an explicit authority-mode claim, not a containment prerequisite.
        # True preserves independently controlled LABs; False permits owner-selected local-operator
        # LAB authority. Both modes retain the same disposable/no-credential/no-production barriers.
        require(type(registration.get('controller_external')) is bool,12,'LAB_CONTROLLER_MODE')
        require(registration.get('disposable') is True and registration.get('no_real_credentials') is True
                and registration.get('no_production_mappings') is True,12,'LAB_REGISTRATION_INCOMPLETE')
        require('lab_plan' in refs,12,'LAB_PLAN_REQUIRED')
        lab=store.get('lab_plan',refs['lab_plan'])
        require(lab.get('host_id')==ctx.host_id and lab.get('build_digest')==ctx.build_digest and lab.get('approved') is True and lab.get('withdrawn') is False and s['purpose'] in lab.get('purposes',[]),12,'LAB_PLAN_INVALID')
        # LAB is allowed to create regression evidence; no qualification prerequisite.
    elif active:
        require('qualification' in refs,11,'QUALIFICATION_MISSING')
        qualification(store,refs['qualification'],s,ctx)
    require(ctx.profile==s['profile'],16,'LIVE_PROFILE_MISMATCH')
    return Admission(plan['plan_digest'],s['run_id'],ctx.host_id,ctx.execution_sid,classes,ctx.registered_class,s['purpose'],tuple(sorted([*refs.values(),plan['approval_ref']])))


def qualification(store:PinnedStore,ref:str,s:dict,ctx:Context):
    q=store.get('qualification',ref)
    require(q.get('status')=='PASS' and q.get('withdrawn') is False and q.get('gate_blockers')==[],11,'QUALIFICATION_FAILED_OR_WITHDRAWN')
    issued=instant(q['issued_at']); require(issued<=ctx.now<=issued+timedelta(days=30),11,'QUALIFICATION_EXPIRED')
    for key,expected in [('contract_digest',CONTRACT_DIGEST),('build_digest',ctx.build_digest),('test_set_digest',ctx.test_set_digest)]:
        require(q.get(key)==expected,16,'QUALIFICATION_CONTENT_MISMATCH')
    require(q.get('source_kind')=='LAB' and q.get('issuer_role')=='VALIDATION' and q.get('master_recorded') is True,15,'QUALIFICATION_CHAIN_INVALID')
    require(q.get('code_review_ref')==s['refs']['code'],16,'QUALIFICATION_CODE_REVIEW_MISMATCH')
    rows=q.get('profile_rows',[])
    require(any(row.get('purpose')==s['purpose'] and row.get('profile')==ctx.profile and row.get('payload_digest')==s['payload_digest'] for row in rows),16,'PROFILE_NOT_QUALIFIED')
    require('test_set' in s['refs'],15,'TEST_SET_REFERENCE_MISSING')
    spec=store.get('test_set',s['refs']['test_set'])
    require(spec.get('test_set_digest')==ctx.test_set_digest,16,'TEST_SET_MISMATCH')
    mandatory=spec.get('mandatory_cases'); require(type(mandatory) is list and mandatory and len(set(mandatory))==len(mandatory),15,'MANDATORY_TEST_SET_INVALID')
    # Broad suites cannot disappear merely because a receipt uses a short test list.
    require({f'T00-{i:02d}' for i in range(1,15)}|{f'F00-{i:02d}' for i in range(1,17)}<=set(mandatory),15,'MANDATORY_SUITE_INCOMPLETE')
    results=q.get('results'); require(type(results) is dict and set(results)==set(mandatory),11,'REGRESSION_RESULTS_MISSING')
    for case in mandatory:
        result=store.get('test_result',results[case])
        require(result.get('test_id')==case and result.get('source_kind')=='LAB' and result.get('status')=='PASS' and result.get('actual_evidence_digest') is not None,11,'REGRESSION_RESULT_NOT_ACTUAL_PASS')
        require(result.get('build_digest')==ctx.build_digest and result.get('test_set_digest')==ctx.test_set_digest and result.get('contract_digest')==CONTRACT_DIGEST,16,'REGRESSION_CONTENT_MISMATCH')
        require(result.get('lab_id')==q.get('lab_id'),16,'REGRESSION_LAB_MISMATCH')
        if case in spec.get('native_required_cases',[]):
            require(result.get('environment_kind')=='WINDOWS_WSL_NATIVE',11,'NATIVE_REGRESSION_REQUIRED')
        actual=store.get('measurement',result['actual_evidence_digest'])
        require(actual.get('source_kind')=='LAB' and actual.get('lab_id')==q.get('lab_id') and actual.get('test_id')==case,15,'ACTUAL_EVIDENCE_MISMATCH')
    return q
