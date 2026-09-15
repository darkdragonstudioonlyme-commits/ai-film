"""Protected C0 measurements -> an unapproved deterministic plan proposal.

The C0 source is a committed journal event, not a caller's observations object.
Requested after-state remains labelled intention and is never copied to actuals.
No approval, qualification, ownership or guest identity is created here.
"""
from copy import deepcopy
from dataclasses import dataclass
from datetime import timedelta

from .codec import digest, instant, hash_value, canonical
from .errors import require, P00Error
from .plans import make_plan, REQUIRED, OPTIONAL, semantic_diff
from .policy import host_profile, runtime_profile, floors, budget_check
from .native.observations import target_row

CAPTURE_CAP = 1024 * 1024
OBSERVED_KEYS = {'host_id','owner_sid','execution_class','contract_digest','build_digest',
                 'test_set_digest','profile','before'}


@dataclass(frozen=True)
class C0Capture:
    body: dict
    digest: str


def load_capture(rows, selected_digest, *, host_id, owner_sid, build_digest):
    hash_value(selected_digest)
    matches = [r['event'] for r in rows if r.get('event',{}).get('kind')=='C0_CAPTURE_COMMITTED'
               and r['event'].get('capture_digest')==selected_digest]
    require(len(matches)==1,15,'C0_CAPTURE_NOT_UNIQUE')
    capture = matches[0]['capture']
    require(digest(capture)==selected_digest,15,'C0_CAPTURE_INTEGRITY')
    for key,value in [('host_id',host_id),('owner_sid',owner_sid),('build_digest',build_digest)]:
        require(capture.get(key)==value,16,'C0_CAPTURE_SCOPE')
    intents=[r['event'] for r in rows if r.get('event',{}).get('kind')=='C0_CAPTURE_INTENT'
             and r['event'].get('capture_id')==capture.get('capture_id')]
    require(len(intents)==1 and intents[0]['request_digest']==capture['request_digest'],
            15,'C0_CAPTURE_INTENT_LINK')
    require(capture.get('source_kind') in ('SITE','LAB') and capture.get('schema_version')==1,
            15,'C0_CAPTURE_SCHEMA')
    return C0Capture(deepcopy(capture),selected_digest)


def compose(selection, capture, now):
    """Pure proposal builder. Only native entry loads actuals from protected log.

    Returns NON_APPLICABLE for incomplete observations or unsafe transition;
    schema/trust/identity errors remain errors, not defaults or synthetic facts.
    """
    require(type(capture) is C0Capture,15,'C0_CAPTURE_ADAPTER_TYPE')
    require(digest(capture.body)==capture.digest,15,'C0_CAPTURE_INTEGRITY')
    require(type(selection) is dict and selection.get('schema_version')==1
            and selection.get('withdrawn') is False and selection.get('fixture_only') is not True,
            15,'BINDING_SELECTION_SCHEMA')
    intent=selection.get('binding');require(type(intent) is dict,10,'BINDING_SELECTION_SCHEMA')
    allowed=(REQUIRED-OBSERVED_KEYS)|OPTIONAL
    require(set(intent)<=allowed and (REQUIRED-OBSERVED_KEYS)<=set(intent),
            10,'BINDING_INTENT_FIELD_SET')
    body=capture.body
    require(selection.get('scope')=={'host_id':body['host_id'],'owner_sid':body['owner_sid'],
            'capture_digest':capture.digest},12,'BINDING_SELECTION_SCOPE')
    ended=instant(body['ended_at'])
    blockers=[]
    def blocked(reason):
        if reason not in blockers:blockers.append(reason)
    if ended>now:blocked('C0_CAPTURE_FROM_FUTURE')
    if now-ended>timedelta(hours=24):blocked('C0_CAPTURE_STALE')
    if body.get('stable_material') is not True:blocked('C0_MATERIAL_NOT_STABLE')
    observed=body.get('observed',{})
    if observed.get('collection_errors'):blocked('C0_COLLECTION_INCOMPLETE')
    if observed.get('profile_verified') is not True:blocked('C0_PROFILE_NOT_OBSERVED')
    material=observed.get('material')
    if type(material) is not dict:blocked('C0_MATERIAL_UNAVAILABLE')
    plan=None
    if not blockers:
        candidate=deepcopy(intent)
        candidate.update({k:body[k] for k in OBSERVED_KEYS-{'profile','before','execution_class'}})
        candidate.update({'execution_class':body['source_kind'], 'profile':deepcopy(body['profile']),
                          'before':deepcopy(material)})
        # This is a code eligibility check against measured resources, never an
        # activation probe or a side effect to make the selection eligible.
        try:
            host_profile(observed['host'],now)
            floors(observed['resources'])
            budget_check(candidate['budgets'],observed['free_bytes'])
            row=target_row(material,candidate['target'])
            purpose=candidate['purpose']
            if purpose in ('CREATE','RESTORE_IMPORT'):
                require(row is None,16,'TARGET_ALREADY_EXISTS')
            elif purpose not in ('ENGINE','PASSIVE','SUPPORT_BUNDLE','RECONCILIATION_ONLY'):
                require(row is not None,11,'TARGET_NOT_PRESENT')
                # The observed registration is bound to an explicitly selected
                # name/path; it is never inferred from the default distro.
                candidate['target']['registration_id']=row['registration_id']
            if purpose not in ('ENGINE','PASSIVE','SUPPORT_BUNDLE','RECONCILIATION_ONLY'):
                runtime_profile(material['runtime'])
            plan=make_plan(candidate,now.isoformat())
        except P00Error as error:
            if error.code not in (11,13,16):raise
            blocked(error.reason)
    return {'source_kind':'DOCUMENT', 'state':'NON_APPLICABLE' if blockers else 'PLAN_PROPOSED',
            'capture_digest':capture.digest, 'capture_as_of':body['ended_at'],
            'selection_digest':digest(selection), 'blockers':blockers, 'plan':plan,
            'diff':semantic_diff(plan['semantic']['before'],plan['semantic']['expected_after']) if plan else [],
            'requires_current_revalidation':True, 'requires_exact_approval':True,
            'native_eligibility_proven':False, 'qualification_issued':False,'host_ready':False}


class C0CaptureRunner:
    """One admission; journal before children; never active guest discovery.

    This inventory entry intentionally tolerates missing eligibility facts.
    Missing metadata remains typed UNAVAILABLE and makes a downstream selection
    NON_APPLICABLE, not a reason to install/bootstrap while collecting inventory.
    """
    def __init__(self,session):self.s=session;self.d=session.driver;self.c=session.coordinator

    def execute(self,request):
        from .authority import authorize
        from .plans import interface_check
        from uuid import uuid4
        semantic=interface_check('preflight',request)
        require(semantic['purpose']=='PASSIVE',12,'C0_CAPTURE_SCOPE')
        first,auth=self.s._fresh('preflight',request)
        with self.c.acquire(auth):
            self.d.reserve_c0_capture(request,self.c)
            capture_id='c0-'+uuid4().hex
            self.c.storage.append_event({'kind':'C0_CAPTURE_INTENT','capture_id':capture_id,
                'request_digest':request['plan_digest'], 'host_id':auth.host_id,'owner_sid':auth.owner_sid})
            start=self.d.capture_c0(request,self.c)
            end=self.d.capture_c0(request,self.c)
            authority=self.d.refresh(request,coordinator=None)
            current=authorize('preflight',request,authority.context,authority.store)
            require(current==auth and first.generation<=start.generation<=end.generation<=authority.generation,
                    16,'C0_AUTHORITY_CHANGED')
            require(start.collection_kind==end.collection_kind=='WINDOWS_NATIVE_METADATA'
                    or self.d.source_kind=='WORKSPACE_TEST',15,'C0_NATIVE_COLLECTION_REQUIRED')
            from .native.read_recovery import pending_reads
            require(not pending_reads(self.c.storage.read_events()) and self.c.storage.load_fence() is None,
                    21,'C0_READS_UNRESOLVED')
            stable=(type(start.observed.get('material')) is dict
                    and start.observed['material']==end.observed.get('material')
                    and (start.observed.get('host') or {}).get('boot_utc')==(end.observed.get('host') or {}).get('boot_utc'))
            body={'schema_version':1,'capture_id':capture_id,'request_digest':request['plan_digest'],
                'host_id':auth.host_id,'owner_sid':auth.owner_sid,'source_kind':semantic['execution_class'],
                'contract_digest':semantic['contract_digest'],'build_digest':semantic['build_digest'],
                'test_set_digest':semantic['test_set_digest'],'profile':deepcopy(end.context.profile),
                'started_at':start.context.now.isoformat(),'ended_at':end.context.now.isoformat(),
                'stable_material':stable,'observed':deepcopy(end.observed),
                'guest_state':'REQUIRES_ACTIVE_PROBE','host_ready':False}
            require(len(canonical(body))<=CAPTURE_CAP,22,'C0_CAPTURE_CAP')
            self.c.storage.append_event({'kind':'C0_CAPTURE_COMMITTED','capture_digest':digest(body),'capture':body})
            return {'exit':0,'state':'INVENTORY_CAPTURED','source_kind':semantic['execution_class'],
                    'capture_digest':digest(body),'stable_material':stable,
                    'guest_state':'REQUIRES_ACTIVE_PROBE','host_ready':False,'qualification_issued':False,
                    'completeness':'INCOMPLETE' if end.observed.get('collection_errors') else 'METADATA_COLLECTED'}
