"""Field-level E00-01..17 catalog and stage applicability (D00-14).

This validates evidence DATA, not its origin. Production inputs are read through
native protected adapters. Workspace fixtures never gain authority by passing a
schema. Missing actual fields stay missing, including within an otherwise present
group. E16 and E17 are downstream outputs, not prerequisites for E01..15 capture.
"""
from dataclasses import dataclass
from copy import deepcopy
from .codec import digest,instant,hash_value,token,fields,canonical
from .errors import require,P00Error

PROTECTED_PATHS={
 'E00-01':'observations/host.json','E00-02':'observations/runtime.json',
 'E00-03':'observations/distros.json','E00-04':'observations/guest.json',
 'E00-05':'observations/resources.json','E00-06':'observations/storage.json',
 'E00-07':'observations/config.json','E00-08':'observations/network.json',
 'E00-09':'recovery/source_manifest.json','E00-10':'governance/execution_binding.json',
 'E00-11':'execution/admission_journal.json','E00-12':'recovery/c3_protection.json',
 'E00-13':'qualification/release_receipt.json','E00-14':'verification/terminal.json',
 'E00-15':'recovery/restore_session.json','E00-16':'support/collection_report.json',
 'E00-17':'governance/gate_assessment.json'}
# Every cell has its own state/provenance. These are subsets of the normative
# record groups, not a list of optional labels that can replace actual evidence.
CATALOG={
 'E00-01':{'host':dict,'principal':dict,'support':dict},
 'E00-02':{'runtime':dict,'features':list,'virtualization':bool,'capability':dict,'pending_reboot':dict},
 'E00-03':{'own_context':dict,'target':(dict,type(None)),'cross_owner_coverage':dict},
 'E00-04':{'identity':dict,'home_admin':dict,'startup':dict,'init':dict},
 'E00-05':{'host':dict,'guest':dict,'measurement_context':dict},
 'E00-06':{'volumes':dict,'budgets':list,'path_acl':dict,'retained_allocations':dict},
 'E00-07':{'host_config':dict,'guest_config':dict,'default_transition':dict,'effective_assertions':dict},
 'E00-08':{'endpoint_matrix':list,'measurements':list,'context_applicability':dict},
 'E00-09':{'source_class':str,'authority':dict,'critical_list':list,'checkpoint_scope':dict,'retention':dict},
 'E00-10':{'design':dict,'code':dict,'content':dict,'plan':dict,'approval':dict,'trust':dict,'actor_class':dict},
 'E00-11':{'admission':dict,'events':list,'fence':(dict,type(None)),'reservations':list,'uncertainty':dict},
 'E00-12':{'impact':dict,'pre_c3':list,'pre_post':list,'owner_coverage':dict},
 'E00-13':{'receipt':dict,'profile_rows':list,'test_results':dict,'issued_expiry':dict,'withdrawal':dict},
 'E00-14':{'report':dict,'assertion_evidence':dict,'invalidation':dict},
 'E00-15':{'source':dict,'checkpoint':dict,'destination':dict,'envelope':dict,'actual_restore':dict,'pre_c3_refs':list},
 'E00-16':{'scope':str,'outcome':dict,'collectors':list,'member_manifest':dict,'sanitizer_scan':dict},
 'E00-17':{'proposal':dict,'as_of':str,'e14':dict,'e16':dict,'blockers':list}}
ACTUAL={'OBSERVED','PASS','ABSENT'}
FUTURE={'NOT_YET_CREATED','REQUIRES_ACTIVE_PROBE'}
STATUSES=ACTUAL|FUTURE|{'UNKNOWN','UNAVAILABLE','NOT_APPLICABLE','FAIL','BLOCKED','NOT_RUN'}


@dataclass(frozen=True)
class Stage:
    name:str
    route:str
    execution_class:str
    existing_target:bool
    persistent_output:bool=True
    after_probe:bool=False
    c3:bool=False
    network_required:bool=False
    restore:bool=False
    data_bearing:bool=False

    def validate(self):
        require(self.name in ('C0','DISCOVERY','APPLY','C3','GATE'),10,'EVIDENCE_STAGE')
        require(self.execution_class in ('SITE','LAB'),10,'EVIDENCE_EXECUTION_CLASS')
        token(self.route)
        for k in ('existing_target','persistent_output','after_probe','c3','network_required','restore','data_bearing'):
            require(type(getattr(self,k)) is bool,10,'EVIDENCE_STAGE_FLAG')


def required_fields(stage):
    """R actual; S typed future; N not needed at this stage (never false PASS)."""
    stage.validate();out={eid:{name:'N' for name in names} for eid,names in CATALOG.items()}
    def group(eid,mode='R'):
        for name in out[eid]:out[eid][name]=mode
    for eid in ('E00-01','E00-02','E00-03','E00-06','E00-10'):group(eid)
    group('E00-04','S');group('E00-05');out['E00-05']['guest']='S'
    group('E00-07');out['E00-07']['guest_config']='S';out['E00-07']['effective_assertions']='N'
    group('E00-08','S');group('E00-09','S')
    out['E00-03']['cross_owner_coverage']='N'
    if stage.persistent_output:group('E00-11')
    if stage.name=='C0':
        for field in ('design','code','plan','approval'):out['E00-10'][field]='S'
        return out
    group('E00-09');group('E00-11')
    if not stage.existing_target:
        out['E00-09']['critical_list']='S';out['E00-09']['checkpoint_scope']='S'
    if stage.execution_class=='SITE':group('E00-13')
    else:
        # Authenticated LAB registration/test-plan is in E10. There is no
        # dependency on the qualification receipt these tests will produce.
        group('E00-13','N')
    if stage.after_probe or stage.name=='APPLY' and stage.route=='ADOPT':
        group('E00-04');out['E00-05']['guest']='R';out['E00-07']['guest_config']='R'
    if stage.network_required:group('E00-08')
    else:group('E00-08','N')
    if stage.c3 or stage.name=='C3':
        group('E00-12');out['E00-03']['cross_owner_coverage']='R'
        if stage.existing_target or stage.data_bearing:group('E00-15')
        if stage.existing_target:
            # Previously collected, quiesced baseline; no new guest boot merely
            # to fill this cell after the source was checkpointed.
            group('E00-04');out['E00-05']['guest']='R';out['E00-07']['guest_config']='R'
    if stage.restore:group('E00-15')
    if stage.name=='GATE':
        for eid in out:group(eid)
    return out


def cell(value,source_ref,observed_at,*,source_kind,status='OBSERVED',reason=None):
    """Caller must have actually read/observed the value; this is no authority."""
    return {'status':status,'actual':deepcopy(value),'source_ref':source_ref,
            'observed_at':observed_at,'source_kind':source_kind,'reason':reason}


def pending(status,reason,at):
    require(status in FUTURE|{'UNKNOWN','UNAVAILABLE','NOT_APPLICABLE','BLOCKED','NOT_RUN'},10,'PENDING_STATUS')
    return cell(None,None,at,source_kind='DOCUMENT',status=status,reason=reason)


def check_cell(eid,name,value):
    fields(value,{'status','actual','source_ref','observed_at','source_kind','reason'})
    require(value['status'] in STATUSES and value['source_kind'] in ('SITE','LAB','DOCUMENT'),15,'CELL_STATUS')
    instant(value['observed_at'])
    if value['reason'] is not None:token(value['reason'])
    if value['status'] in ACTUAL:
        require(type(value['source_ref']) is str and bool(value['source_ref']),15,'CELL_ACTUAL_REFERENCE')
        wanted=CATALOG[eid][name];wanted=wanted if isinstance(wanted,tuple) else (wanted,)
        require(type(value['actual']) in wanted,15,'CELL_ACTUAL_TYPE')
        if eid not in ('E00-09','E00-10','E00-13','E00-15','E00-16','E00-17'):
            require(value['source_kind'] in ('SITE','LAB'),15,'DOCUMENT_NOT_NATIVE_ACTUAL')
    else:
        require(value['actual'] is None and value['reason'] is not None,15,'MISSING_CELL_NOT_TYPED')
        # N/A requires an actual applicability proof, not an unchecked waiver.
        if value['status']=='NOT_APPLICABLE':require(bool(value['source_ref']),15,'APPLICABILITY_PROOF_MISSING')


def group_check(eid,body,stage,*,downstream=False):
    require(eid in CATALOG and type(body) is dict,15,'CATALOG_ID')
    fields(body,{'schema_version','evidence_id','fields','evaluations'})
    require(body['schema_version']==1 and body['evidence_id']==eid
            and type(body['fields']) is dict and set(body['fields'])==set(CATALOG[eid]),15,'CATALOG_FIELD_SET')
    require(type(body['evaluations']) is list,15,'CATALOG_EVALUATIONS')
    requirements=required_fields(stage)[eid];missing=[]
    for name,c in body['fields'].items():
        check_cell(eid,name,c);mode=requirements[name]
        if mode=='R' and c['status'] not in ACTUAL:missing.append(name)
        if mode=='S' and c['status'] not in ACTUAL|FUTURE:missing.append(name)
        # A GATE group must be measured in its actual source context. Lab test
        # receipts and destination proofs are expressly separate exceptions.
        if stage.name=='GATE' and eid not in ('E00-10','E00-13','E00-15','E00-16','E00-17') and c['status'] in ACTUAL:
            require(c['source_kind']=='SITE',15,'LAB_NOT_SITE_GATE')
    for evaluated in body['evaluations']:
        fields(evaluated,{'name','status','input_digest','expected_ref','reason'})
        token(evaluated['name']);hash_value(evaluated['input_digest'])
        require(evaluated['status'] in ('PASS','FAIL','BLOCKED'),15,'EVALUATION_STATUS')
        require(type(evaluated['expected_ref']) is str and bool(evaluated['expected_ref']),15,'EVALUATION_EXPECTATION')
        require(evaluated['input_digest']==digest(body['fields']),15,'EVALUATION_INPUT_CHANGED')
        if evaluated['status']!='PASS':missing.append('evaluation:'+evaluated['name'])
    if stage.name=='GATE' and not body['evaluations']:missing.append('evaluations')
    if eid in ('E00-16','E00-17') and not downstream:missing.append('DOWNSTREAM_OUTPUT_NOT_INPUT')
    return {'complete_for_stage':not missing,'missing_fields':missing,'stage':stage.name,
            'body_digest':digest(body),'host_ready':False}


def new_body(eid,values,*,at,source_ref,source_kind,field_sources=None,
             missing_status='UNAVAILABLE',missing_reason='NOT_COLLECTED'):
    require(eid in CATALOG and set(values)<=set(CATALOG[eid]),15,'CATALOG_FIELD_UNKNOWN')
    field_sources={} if field_sources is None else field_sources
    require(type(field_sources) is dict and set(field_sources)<=set(values),15,'CATALOG_FIELD_SOURCE_UNKNOWN')
    actual={}
    for name in CATALOG[eid]:
        if name not in values:
            actual[name]=pending(missing_status,missing_reason,at);continue
        meta=field_sources.get(name,{'source_ref':source_ref,'observed_at':at,'source_kind':source_kind})
        require(type(meta) is dict and set(meta)=={'source_ref','observed_at','source_kind'}
                and type(meta['source_ref']) is str and bool(meta['source_ref'])
                and meta['source_kind'] in ('SITE','LAB','DOCUMENT'),15,'CATALOG_FIELD_SOURCE_SCHEMA')
        instant(meta['observed_at'])
        actual[name]=cell(values[name],meta['source_ref'],meta['observed_at'],source_kind=meta['source_kind'])
    return {'schema_version':1,'evidence_id':eid,'fields':actual,'evaluations':[]}


def evaluated(body,name,passed,expected_ref,reason=None):
    """Attach a predicate result, not a substitute for running that predicate."""
    require(type(passed) is bool,15,'PREDICATE_RESULT_TYPE');token(name)
    result=deepcopy(body)
    result['evaluations'].append({'name':name,'status':'PASS' if passed else 'FAIL',
        'input_digest':digest(body['fields']),'expected_ref':expected_ref,'reason':reason})
    return result
