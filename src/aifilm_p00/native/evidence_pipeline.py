"""Concrete E00 capture -> protected immutable snapshot -> scoped publication.

Collects only authorized native observations and authenticated document/proof
records. support-bundle does not launch a guest. Unavailable/failed collectors
stay explicit and do not abort unrelated collection or become synthetic PASS.
The E17 proposal is separate from its E16 bundle and never accepts a phase gate.
"""
from copy import deepcopy
from datetime import datetime,timezone
from pathlib import PureWindowsPath
import os,time

from .. import CONTRACT_DIGEST
from ..codec import digest,canonical,loads,sha256,instant,token
from ..errors import require,P00Error
from ..evidence import (Collected,Sanitizer,assemble,requiredness,COLLECTOR_CAP,PATHS,
                        bundle_integrity,record_check)
from ..evidence_catalog import Stage,CATALOG,new_body,group_check,evaluated,pending
from ..authority import authorize,qualification
from ..policy import terminal,budget_check,c3_postconditions
from ..resume import completed_steps
from ..evidence_stage import scoped_stage,require_bundle_context
from .artifacts import SnapshotWriter,committed_snapshot
from .snapshot import extract_record,logical_ref,strict_safe_scan,NativeBundlePublisher


def _actual_guest(result):
    """Select actual captures from fixed operation outputs, never from bindings."""
    if not result:return None,None
    if 'guest_final' in result:return result['guest_final']['actual'],result.get('assertion_evidence',{}).get('profile',{}).get('guest',{}).get('admin',{}).get('actual')
    g=result.get('guest') or result.get('after')
    if type(g) is dict and 'inventory' in g:
        return g['inventory']['actual'],g.get('admin',{}).get('actual')
    if type(g) is dict and g.get('status')=='OBSERVED':return g['actual'],None
    return None,None


def stage_for(plan,fresh,result):
    s=plan['semantic'];purpose=s['purpose'];existing=fresh.observed.get('target') is not None
    if purpose=='SITE_VERIFY' and s['execution_class']=='SITE':name='GATE'
    elif purpose in ('ENGINE','HOST_RESTART'):name='C3'
    elif purpose=='DISCOVERY':name='DISCOVERY'
    elif purpose in ('PASSIVE','SUPPORT_BUNDLE','RECONCILIATION_ONLY'):name='C0'
    else:name='APPLY'
    return Stage(name,purpose,s['execution_class'],existing,True,bool(_actual_guest(result)[0]),
                 name=='C3',bool(s.get('endpoints')),purpose in ('RESTORE_IMPORT','RESTORE_VERIFY'),
                 s['source_class']=='ADOPT_NONSENSITIVE_QUIESCED')


def selected_events(rows,kind,plan_digest=None):
    return [deepcopy(r['event']) for r in rows if r['event'].get('kind')==kind
            and (plan_digest is None or r['event'].get('plan_digest')==plan_digest)]


def _history_plan_digests(plan,result):
    """Only exact durable source sessions named by this execution history."""
    values=[plan['plan_digest']]
    history=result.get('history',{}) if type(result) is dict else {}
    entries=history.get('entries',{}) if type(history) is dict else {}
    for row in entries.values():
        if type(row) is dict and type(row.get('plan_digest')) is str:
            values.append(row['plan_digest'])
    # preserve order while rejecting an unbounded/ambiguous source graph
    out=[]
    for value in values:
        if value not in out:out.append(value)
    require(len(out)<=8,15,'PRIOR_EVIDENCE_PLAN_CAP')
    return tuple(out)


def _prior_guest_from_events(rows,plan,result):
    """Select prior guest facts only from hash-linked operation observations.

    This is used by C3/gate stages where the source guest was quiesced before the
    current operation.  We never boot the guest merely to fill an evidence cell,
    and never infer guest facts from a binding or a PASS envelope.
    """
    plans=set(_history_plan_digests(plan,result));candidates=[]
    for row in rows:
        event=row.get('event',{})
        if event.get('kind')!='OPERATION_AFTER_OBSERVED' or event.get('plan_digest') not in plans:continue
        evidence=event.get('evidence')
        require(type(evidence) is dict and event.get('evidence_digest')==digest(evidence),15,'PRIOR_GUEST_EVENT_INTEGRITY')
        details=evidence.get('details',{});actual=details.get('actual_result') if type(details) is dict else None
        guest,admin=_actual_guest(actual if type(actual) is dict else {})
        if guest:
            candidates.append((event.get('step_id',''),event['plan_digest'],deepcopy(guest),deepcopy(admin),event['evidence_digest']))
    if not candidates:return None,None,None
    # Step IDs are deterministic within a plan.  The latest durable event in the
    # journal is authoritative for that exact source graph; duplicates for the
    # same plan/step with different evidence are integrity errors.
    seen={}
    for row in candidates:
        key=(row[1],row[0])
        if key in seen:require(seen[key][4]==row[4],15,'PRIOR_GUEST_EVENT_AMBIGUOUS')
        seen[key]=row
    chosen=candidates[-1]
    return chosen[2],chosen[3],{'plan_digest':chosen[1],'step_id':chosen[0],'evidence_digest':chosen[4]}


class NativeCatalogProducer:
    def __init__(self,driver,plan,fresh,coordinator,result=None,failure=None):
        self.d=driver;self.plan=plan;self.s=plan['semantic'];self.f=fresh;self.c=coordinator
        self.result=result or {};self.failure=failure;self.stage=stage_for(plan,fresh,self.result)
        self.at=fresh.context.now.isoformat();self.guest,self.admin=_actual_guest(self.result)
        self.events=coordinator.storage.read_events();self.prior_guest_ref=None
        if self.guest is None and (self.stage.name in ('C3','GATE') or self.stage.c3):
            self.guest,self.admin,self.prior_guest_ref=_prior_guest_from_events(self.events,plan,self.result)
        self.capture_ref='journal:'+plan['plan_digest']+':'+digest(self.result)

    def _source(self):
        if 'source' in self.d.proofs:return self.d.proofs['source']
        if self.f.observed.get('target') is None:return None
        return self.d._source(self.plan,self.f)

    def _terminal(self):
        value=self.result.get('terminal')
        require(type(value) is dict,11,'TERMINAL_NOT_COLLECTED')
        # The execution path already evaluated actual native assertions. Recheck
        # content-addressed assertion children before consuming this record.
        actual=self.result['assertion_evidence']
        require(set(value['assertions'])==set(actual),15,'TERMINAL_DETAIL_SET')
        require(all(v['evidence_digest']==digest(actual[k]) for k,v in value['assertions'].items()),15,'TERMINAL_DETAIL_HASH')
        return value,actual

    def values(self,eid):
        d=self.d;s=self.s;f=self.f;o=f.observed;b=d.binding;store=f.store
        if eid=='E00-01':
            return {'host':o['host'],'principal':o['principal'],
                    'support':{'support_end':o['host']['support_end'],'profile':f.context.profile}}
        if eid=='E00-02':
            return {'runtime':o['material']['runtime'],'features':o['material']['features'],
                'virtualization':o['host']['virtualization'],
                'capability':{'actual_version_capture':o['material']['runtime'],
                              'profile_catalog_ref':b['profile_catalog_ref']},'pending_reboot':d.system.pending_reboot()}
        if eid=='E00-03':
            value={'own_context':o['material']['distros'],'target':o['target']}
            protection=d.proofs.get('protection')
            if protection:value['cross_owner_coverage']={'protection_ref':protection['ref'],'coverage':protection['claim']}
            elif 'history' in self.result:
                restart=self.result['history']['entries']['host_restart']['observation']['details']['affected_resources']
                value['cross_owner_coverage']={'postchecks':restart}
            return value
        if eid=='E00-04':
            value={};g=self.guest
            if g:
                value.update({'identity':{k:g[k] for k in ('uid','gid','user','home','os_id','version_id','architecture')},
                    'init':{k:g[k] for k in ('kernel','kernel_boot_id','pid1_start_ticks','pid1_comm')}})
                if self.admin:value['home_admin']={'home_access_writable':g['home_access_writable'],'admin':self.admin}
            source=self._source()
            if source:value['startup']=source
            elif self.prior_guest_ref:value['startup']={'prior_guest_source':self.prior_guest_ref}
            return value
        if eid=='E00-05':
            value={'host':o['resources'],'measurement_context':{'host_id':s['host_id'],'target':o['target'],
                       'host_time':self.at,'guest_collected':self.guest is not None,
                       'prior_guest_source':self.prior_guest_ref}}
            if self.guest:value['guest']=self.guest['resources']
            return value
        if eid=='E00-06':
            validations={}
            candidates={'coordination_root':d.paths.root,'snapshot_root':str(PureWindowsPath(d.paths.root)/'records'),
                        'scratch':b['scratch_directory']}
            if o['target']:candidates['target_parent']=str(PureWindowsPath(o['target']['base_path']).parent)
            for name,path in candidates.items():
                with d.paths.pin(path,directory=True,protected=name!='target_parent',confidential=name!='target_parent') as p:
                    validations[name]={'identity':p.identity,'volume':p.volume,'path':path}
            return {'volumes':o['volumes'],'budgets':o['remaining_budgets'],'path_acl':validations,
                    'retained_allocations':{'registered_distros':o['material']['distros']['rows'],
                                            'volume_free_observed':o['free_bytes']}}
        if eid=='E00-07':
            value={'host_config':o['material']['wslconfig'],
                'default_transition':{'before':s['before'].get('distros'),'actual':o['material']['distros']}}
            if self.guest:value['guest_config']={'wsl_conf_sha256':self.guest['wsl_conf_sha256']}
            if 'terminal' in self.result:value['effective_assertions']=self._terminal()[1]['config_preserved']
            return value
        if eid=='E00-08':
            if 'terminal' in self.result:
                actual=self._terminal()[1]['network']
                return {'endpoint_matrix':s['endpoints'],'measurements':actual['matrix'],
                    'context_applicability':{'roles':actual['roles'],'windows_download_required':actual['windows_download_required'],
                                            'offline_payload_refs':b.get('offline_payload_refs',[])}}
            if 'network' in self.result:return self.result['network']
            return {}
        if eid=='E00-09':
            source=self._source();value={}
            if source:
                claim=source['claim']
                value={'source_class':claim['source_class'],'authority':source}
                for key in ('critical_list','checkpoint_scope','retention'):
                    if key in claim:value[key]=claim[key]
                if 'critical_list' in value:require(value['critical_list']==b.get('critical_files'),16,'CRITICAL_LIST_AUTHORITY')
            return value
        if eid=='E00-10':
            refs=s['refs'];return {'design':store.get('design',refs['design']),'code':store.get('code',refs['code']),
                'content':{'build_digest':s['build_digest'],'test_set_digest':s['test_set_digest'],'contract_digest':CONTRACT_DIGEST},
                'plan':self.plan,'approval':store.get('approval',self.plan['approval_ref']),
                'trust':{'generation':store.generation,'authority_refs':list(self.c.admission.authority_document_digests)},
                'actor_class':{'context':s['execution_class'],'principal':o['principal'],
                               'registration':store.get('registration',refs['registration'])}}
        if eid=='E00-11':
            from dataclasses import asdict
            # Each source journal frame remains hash checked by NativeJournal;
            # raw commands/content are protected, never included in safe output.
            relevant=[r for r in self.events if r['event'].get('plan_digest') in (self.plan['plan_digest'],None)]
            return {'admission':asdict(self.c.admission)|{'classes':sorted(self.c.admission.classes)},
                'events':relevant,'fence':deepcopy(self.c.fence),
                'reservations':deepcopy(self.c.fence['reservations']) if self.c.fence else [],
                'uncertainty':{'own_current_intent_accounted':self.c.fence is not None,
                    'state':self.c.fence['state'] if self.c.fence else 'TERMINAL',
                    'no_other_fence':True,'failure':self.failure}}
        if eid=='E00-12':
            plans={self.plan['plan_digest']}
            if 'history' in self.result:plans.add(self.result['history']['entries']['host_restart']['plan_digest'])
            pre=[r['event'] for r in self.events if r['event'].get('kind')=='PRE_C3_PROOF_OBSERVED' and r['event'].get('plan_digest') in plans]
            require(bool(pre),11,'PRE_C3_EVIDENCE_UNAVAILABLE')
            old=pre[-1];reader=d._reader(f)
            # Preserve original precondition time while checking current trust.
            from .proofs import ProofReader
            proof=ProofReader(store,s['host_id'],s['owner_sid'],instant(old['checked_at'])).receipt('protection',old['proof_ref'],old['scope'],owner_assertion=True)
            post=[]
            if 'history' in self.result:post.append(self.result['assertion_evidence']['affected_resources'])
            elif self.result.get('affected_resources'):post.append(self.result['affected_resources'])
            return {'impact':proof['claim'],'pre_c3':pre,'pre_post':post,
                    'owner_coverage':{'scope':proof['scope'],'owner_sid':proof['owner_sid'],'measurements':proof['measurements']}}
        if eid=='E00-13':
            require('qualification' in s['refs'],11,'QUALIFICATION_NOT_ESTABLISHED')
            # Uses actual pinned LAB records via native trust; not a receipt
            # created by this package or by a workspace test.
            q=qualification(store,s['refs']['qualification'],s,f.context)
            tests={case:store.get('test_result',ref) for case,ref in q['results'].items()}
            return {'receipt':q,'profile_rows':q['profile_rows'],'test_results':tests,
                'issued_expiry':{'issued_at':q['issued_at'],'valid_days':30},
                'withdrawal':{'withdrawn':q['withdrawn'],'generation':store.generation}}
        if eid=='E00-14':
            report,actual=self._terminal()
            return {'report':report,'assertion_evidence':actual,
                    'invalidation':{'last_source_effect':self.result['last_source_effect'],
                        'start_witness':report['start_witness'],'end_witness':report['end_witness']}}
        if eid=='E00-15':
            if 'terminal' in self.result:
                actual=self._terminal()[1]['clone_stopped_retained'];claim=actual['claim']
                return {'source':{'host_id':claim['source_host_id'],'target_registration':claim['source_target_registration'],
                                  'source_class':s['source_class']},
                    'checkpoint':{'sha256':claim['checkpoint_digest']},
                    'destination':{'host_id':claim['destination_host_id'],'registration':claim['destination_registration']},
                    'envelope':{'receipt':actual,'preboot_verified':claim['preboot_envelope_verified']},
                    'actual_restore':actual,'pre_c3_refs':[self.result['history']['entries']['host_restart']['evidence_digest']]}
            envelope=d.proofs.get('envelope');source=d.proofs.get('source')
            value={}
            if envelope:value.update({'checkpoint':{'sha256':envelope['claim']['checkpoint_digest']},'envelope':envelope,
                'destination':{'host_id':s['host_id'],'target':o['target']}})
            if source:value['source']=source
            if self.result.get('content'):value['actual_restore']=self.result
            return value
        raise P00Error(10,'CATALOG_NOT_SOURCE_INPUT')

    def collect(self):
        groups={};envelopes={};outcomes=[]
        for eid in PATHS:
            begin=time.monotonic();error=None;values={}
            try:values=self.values(eid)
            except P00Error as e:error=e.safe()
            except (KeyError,ValueError,TypeError,OSError):error={'exit':18,'reason':'COLLECTOR_SCHEMA_OR_IO'}
            elapsed=int((time.monotonic()-begin)*1000)
            body=new_body(eid,values,at=self.at,source_ref=self.capture_ref,source_kind=self.s['execution_class'])
            from ..evidence_catalog import required_fields
            modes=required_fields(self.stage)[eid]
            for name,c in body['fields'].items():
                if name not in values and modes[name]=='S':
                    status='NOT_YET_CREATED' if not self.stage.existing_target else 'REQUIRES_ACTIVE_PROBE'
                    body['fields'][name]=pending(status,'FUTURE_ACTUAL_NOT_COLLECTED',self.at)
                elif name not in values and modes[name]=='N':body['fields'][name]=pending('NOT_RUN','NOT_REQUIRED_AT_THIS_STAGE',self.at)
            result=group_check(eid,body,self.stage)
            # A new GATE body has no evaluation record yet. Validate mandatory
            # actual fields first, then attach the result of the actual native
            # execution path, and finally validate the complete envelope.
            missing=[x for x in result['missing_fields'] if x!='evaluations']
            valid=not missing and error is None and elapsed<=30000
            if self.stage.name=='GATE':
                valid=valid and self.failure is None and 'terminal' in self.result
                if eid=='E00-12':valid=valid and bool(values.get('pre_post'))
                if eid=='E00-11':valid=valid and self.c.fence['state'] not in ('UNCERTAIN','AWAITING_REBOOT','AWAITING_USER_INIT')
            if valid:
                body=evaluated(body,'ACTUAL_FIELDS_AND_NATIVE_PREDICATES',True,'contract:'+CONTRACT_DIGEST+'#'+eid)
                require(group_check(eid,body,self.stage)['complete_for_stage'],15,'GENERATED_CATALOG_INVALID')
            status=('PASS' if self.stage.name=='GATE' else 'OBSERVED') if valid else 'UNAVAILABLE'
            # A group containing typed future fields is structurally complete for
            # inventory, but not a future guest/network PASS.
            if eid in ('E00-04','E00-08','E00-09') and not values and self.stage.name=='C0':
                status='NOT_YET_CREATED' if not self.stage.existing_target else 'REQUIRES_ACTIVE_PROBE'
            rid='r_'+eid.replace('-','_')
            step_id=self.c.fence['witness']['step_id'] if self.c.fence else 'step-none'
            envelope={'schema_version':1,'evidence_id':eid,'record_id':rid,'status':status,
                'source_kind':self.s['execution_class'],'work_item':self.s['work_item'],'run_id':self.s['run_id'],
                'step_id':step_id,'operation':self.c.fence['action'] if self.c.fence else 'OBSERVE_HOST',
                'host_alias':self.s['host_id'],'target_alias':'target-'+digest(self.s['target'])[:24],
                'collector_digest':self.s['build_digest'],'build_digest':self.s['build_digest'],
                'contract_digest':CONTRACT_DIGEST,'timestamp_utc':self.at,'stage':self.stage.name,'route':self.s['purpose'],
                'expected_ref':'contract:'+CONTRACT_DIGEST+'#'+eid,'actual_ref':None,'native_exit':None,
                'normalized_exit':0 if valid else 22,'epoch_ref':None,'protected_ref':None,'protected_digest':'0'*64,
                'safe_summary':{'status':status,'complete':valid,'count':len(values),
                    'duration_ms':elapsed,'digest':digest(body)},'sensitivity':'PROTECTED'}
            groups[eid]=body;envelopes[eid]=envelope
            outcomes.append({'evidence_id':eid,'complete':valid,'duration_ms':elapsed,'missing':result['missing_fields'],
                             'error':error,'status':status})
        return groups,envelopes,outcomes


class CatalogSnapshotReader:
    """Continue optional/ordinary missing collectors; retain integrity precedence."""
    def __init__(self,paths,coordinator):self.paths=paths;self.c=coordinator
    def read(self,descriptor,index,scope,context,optional):
        wanted=requiredness(scope,**context)|set(optional)
        rows={r['evidence_id']:r for r in index['records']}
        require(len(rows)==len(index['records']) and set(rows)<=set(PATHS),15,'SNAPSHOT_GROUP_DUPLICATE')
        collected=[];bodies={}
        root=descriptor['root'];run_id=descriptor['run_id']
        with self.paths.pin(root,directory=True,protected=True):
            for eid in sorted(wanted):
                begin=time.monotonic();record=None
                try:
                    require(eid in rows,22,'SNAPSHOT_GROUP_MISSING');r=rows[eid]
                    from ..codec import relative
                    relative(r['relative_path']);token(r['record_id'])
                    blob=self.paths.read_blob(str(PureWindowsPath(root)/r['relative_path']),expected=r['sha256'],cap=COLLECTOR_CAP)
                    require(len(blob)==r['bytes'],15,'SNAPSHOT_MEMBER_SIZE')
                    record=extract_record(blob,r['record_id']);record_check(record)
                    require(record['run_id']==run_id and record['evidence_id']==eid,15,'SNAPSHOT_RECORD_SCOPE')
                    rr,path,rid=logical_ref(record['protected_ref']);require(rr==run_id,15,'SNAPSHOT_PROTECTED_RUN')
                    raw=self.paths.read_blob(str(PureWindowsPath(root)/path),expected=record['protected_digest'],cap=COLLECTOR_CAP)
                    body=extract_record(raw,rid)['body'];bodies[eid]=body
                    # Full field-level checks, not just the outer envelope.
                    stage=scoped_stage(descriptor,index,scope,record)
                    checked=group_check(eid,body,stage)
                    if scope in ('GATE_HANDOFF','INVENTORY'):require(checked['complete_for_stage'],22,'CATALOG_SCOPE_INCOMPLETE')
                    duration=int((time.monotonic()-begin)*1000)
                    collected.append(Collected(eid,record,sha256(canonical(record)),duration,len(blob)+len(raw),True,
                        'COMPLETE' if duration<=30000 else 'TIMEOUT',True,True))
                except P00Error as error:
                    if error.code in (15,16,23):
                        collected.append(Collected(eid,record,sha256(canonical(record)) if record else None,
                            int((time.monotonic()-begin)*1000),0,False,
                            'PRIVACY_FAILURE' if error.code==23 else 'INTEGRITY_FAILURE',False,False))
                        continue
                    collected.append(Collected(eid,None,None,int((time.monotonic()-begin)*1000),0,False,'INCOMPLETE',False,False))
        return collected,bodies


class NativeEvidencePipeline:
    def __init__(self,driver):self.d=driver
    def capture(self,plan,coordinator,fresh,result=None,failure=None):
        producer=NativeCatalogProducer(self.d,plan,fresh,coordinator,result,failure)
        groups,envelopes,outcomes=producer.collect()
        require(sum(len(canonical(v)) for v in groups.values())+sum(len(canonical(v)) for v in envelopes.values())+65536
                <=self.d.binding['snapshot_maximum_bytes'],13,'SNAPSHOT_DECLARED_CAP')
        snapshot=SnapshotWriter(self.d.paths,coordinator).seal(plan,producer.stage,groups,envelopes)
        coordinator.storage.append_event({'kind':'COLLECTION_OUTCOMES','plan_digest':plan['plan_digest'],
            'snapshot_digest':snapshot['index_digest'],'collectors':outcomes})
        return snapshot

    def publish(self,plan,coordinator,fresh):
        d=self.d;s=plan['semantic'];b=d.binding
        require(s['purpose']=='SUPPORT_BUNDLE' and coordinator.fence['action']=='PUBLISH_SAFE_BUNDLE',12,'SUPPORT_SCOPE')
        descriptor,index=committed_snapshot(d.paths,coordinator,b['snapshot_selector'])
        scope=s['bundle_scope'];context=b['bundle_context'];optional=frozenset(b.get('optional_evidence_ids',[]))
        require(type(context) is dict and set(context)=={'persistent_output','mutation_attempted','c3_attempted','restore_attempted'}
                and all(type(v) is bool for v in context.values()),10,'BUNDLE_CONTEXT_SCHEMA')
        # Applicability is checked against the observed source journal, not flags
        # chosen after a collector failed. An attempted mutation may not be hidden.
        source_rows=selected_events(coordinator.storage.read_events(),'SET_FENCE',None)
        source_fences=[r['record'] for r in source_rows if r['record']['plan_digest']==descriptor['plan_digest']]
        require_bundle_context(context,descriptor,source_fences)
        collected,bodies=CatalogSnapshotReader(d.paths,coordinator).read(descriptor,index,scope,context,optional)
        sanitizer=Sanitizer(os.urandom(32))
        bundle=assemble(scope,collected,sanitizer,context=context,optional_ids=optional,scanner=strict_safe_scan)
        output=b['bundle_output'] if bundle.exit!=22 else b['incomplete_bundle_output']
        fresh=d.refresh(plan,coordinator=coordinator);authorize('support-bundle',plan,fresh.context,fresh.store)
        coordinator.storage.append_event({'kind':'PROTECTED_ALIAS_MAP','plan_digest':plan['plan_digest'],
            'bundle_digest':sha256(bundle.archive) if bundle.archive is not None else None,'map':sanitizer.alias_map})
        result=NativeBundlePublisher(d.paths,coordinator).publish(bundle,approved_path=output,
            budgets=fresh.observed['remaining_budgets'],free_by_volume=fresh.observed['free_bytes'])
        if result['exit']==18:
            raise P00Error(18,'BUNDLE_OUTPUT_FAILED')
        result['archive_expected']=bundle.archive is not None
        coordinator.storage.append_event({'kind':'BUNDLE_OBSERVED','plan_digest':plan['plan_digest'],
            'source_snapshot_digest':descriptor['index_digest'],'scope':scope,'result':result,
            'output_alias_digest':digest(output),'collection_report':bundle.report})
        # Never expose alias-map secrets in the public archive. It remains in the
        # protected native journal, under this original run's output reservation.
        if scope=='GATE_HANDOFF' and bundle.mandatory_complete and result.get('published'):
            result['assessment']=self.assess(plan,coordinator,fresh,descriptor,bodies,result,bundle.report)
        return result

    def assess(self,plan,coordinator,fresh,descriptor,bodies,published,collection_report):
        d=self.d;s=plan['semantic'];require(s['execution_class']=='SITE',19,'LAB_NOT_SITE_ASSESSMENT')
        source=bodies['E00-10']['fields']['plan']['actual'];old=source['semantic']
        require(source['plan_digest']==descriptor['plan_digest'] and old['purpose']=='SITE_VERIFY',15,'GATE_SOURCE_PLAN')
        complete=completed_steps(coordinator.storage.read_events(),source)
        require(len(complete)==len(old['operations']),19,'GATE_SOURCE_NOT_COMMITTED')
        actual=bodies['E00-14']['fields'];report=actual['report']['actual']
        expiry=fresh.context.now
        valid=terminal(report,expiry,s['host_id'],s['target']['registration_id'],s['build_digest'],CONTRACT_DIGEST,
            instant(actual['invalidation']['actual']['last_source_effect']),s['expected_checkpoint'])
        require(report['end_witness']['host_boot']==fresh.observed['host']['boot_utc']
                and report['end_witness']['runtime']==digest(fresh.observed['material']['runtime']),19,'GATE_HOST_EPOCH_CHANGED')
        assessment={'schema_version':1,'evidence_id':'E00-17','status':'PROPOSAL','accepted_by_master':False,
            'eligible_as_of':valid['eligible_as_of'],'sealed_at':expiry.isoformat(),
            'host_id':s['host_id'],'target_id':s['target']['registration_id'],'contract_digest':CONTRACT_DIGEST,
            'build_digest':s['build_digest'],'e14_digest':digest(report),'e16_digest':published['bundle_digest'],
            'snapshot_digest':descriptor['index_digest'],'source_session_digest':source['plan_digest'],
            'blockers':[],'host_ready':False,'qualification_issued':False}
        path=d.binding['assessment_output']
        require(path.endswith('.json') and '.zip' not in str(PureWindowsPath(path).name),10,'ASSESSMENT_OUTPUT_SEPARATE')
        from .assessment import AssessmentPublisher
        published_assessment=AssessmentPublisher(d.paths,coordinator).publish(plan,assessment,path)
        if published_assessment['exit']==18:raise P00Error(18,'ASSESSMENT_OUTPUT_FAILED')
        coordinator.storage.append_event({'kind':'ASSESSMENT_PROPOSED','plan_digest':plan['plan_digest'],
            'e14_digest':assessment['e14_digest'],'e16_digest':assessment['e16_digest'],
            'assessment_digest':digest(assessment),'output_sha256':published_assessment['output_sha256'],
            'accepted_by_master':False})
        return published_assessment
