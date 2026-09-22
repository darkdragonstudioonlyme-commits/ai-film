#!/usr/bin/env python3
"""Serialized file-backed model of reviewed V03 policy publication. Never writes HKLM."""
from __future__ import annotations
import argparse,fcntl,hashlib,json,os
from pathlib import Path
from v03_binding_producer_common import V03Error,canonical,hash_value,require

class PublishError(RuntimeError):pass

RUNTIME_ADD_ROLES=frozenset({
    'lab_authority_lineage','lab_stage_state_handoff','execution_plan','approval','native_binding','checkpoint_payload',
    'checkpoint_copy_receipt','recovery_request','source_manifest','protection','restore_envelope','user_init_receipt',
    'c3_postchecks','operation_postcheck','run_revocation','read_absence_observation','restore_result'
})

def req(c,r):
    if not c:raise PublishError(r)
def sha(raw):return hashlib.sha256(raw).hexdigest()

def strict_policy(raw):
    try:p=json.loads(raw.decode())
    except Exception as e:raise PublishError('POLICY_JSON') from e
    need={'schema_version','host_id','operator_sids','role_pins','blobs','withdrawn_refs','generation'}
    req(type(p) is dict and set(p)==need and p['schema_version']==1 and type(p['generation']) is int and p['generation']>=1,'POLICY_SCHEMA')
    req(type(p['role_pins']) is dict and type(p['blobs']) is dict and type(p['withdrawn_refs']) is list,'POLICY_SCHEMA')
    for role,refs in p['role_pins'].items():
        req(isinstance(role,str) and type(refs) is list,'POLICY_PINS')
        for ref in refs:req(ref in p['blobs'] and sha(p['blobs'][ref].encode())==ref,'POLICY_BLOB')
    return p

def build_next(parent_raw,additions,withdrawals=()):
    parent=strict_policy(parent_raw);p=json.loads(json.dumps(parent));refs=[]
    req(type(additions) is list,'ADDITIONS')
    for obj in additions:
        req(type(obj) is dict and isinstance(obj.get('role'),str),'ADDITION_SCHEMA')
        raw=canonical(obj);ref=sha(raw);role=obj['role'];existing=p['blobs'].get(ref)
        req(existing is None or existing.encode()==raw,'ADDITION_COLLISION')
        p['blobs'][ref]=raw.decode();p['role_pins'].setdefault(role,[])
        if ref not in p['role_pins'][role]:p['role_pins'][role].append(ref);p['role_pins'][role].sort()
        refs.append({'role':role,'ref':ref})
    for ref in withdrawals:
        hash_value(ref);req(ref in p['blobs'],'WITHDRAW_UNKNOWN')
        if ref not in p['withdrawn_refs']:p['withdrawn_refs'].append(ref)
    p['withdrawn_refs']=sorted(p['withdrawn_refs']);p['generation']=parent['generation']+1
    raw=canonical(p);strict_policy(raw);return raw,sorted(refs,key=lambda x:(x['role'],x['ref']))

def read_events(path):
    p=Path(path)
    if not p.exists():return []
    rows=[]
    for line in p.read_bytes().splitlines():
        try:v=json.loads(line)
        except Exception as e:raise PublishError('PUBLICATION_JOURNAL_INVALID') from e
        req(type(v) is dict,'PUBLICATION_JOURNAL_INVALID');rows.append(v)
    return rows

def event_key(event):
    return tuple(event[k] for k in ('new_policy_digest','suite_ref','case_id','stage_index','slot_ref'))

def publish(parent_path,current_path,expected_parent_sha,additions,event_fields,journal_path,guard_path,withdrawals=(),fault=None):
    parent_raw=Path(parent_path).read_bytes();req(sha(parent_raw)==expected_parent_sha,'EXPECTED_PARENT_DIGEST')
    parent=strict_policy(parent_raw);req(type(additions) is list,'ADDITIONS')
    for obj in additions:req(type(obj) is dict and obj.get('role') in RUNTIME_ADD_ROLES,'RUNTIME_ROLE_NOT_AUTHORIZED')
    base_refs=set()
    for mref in parent['role_pins'].get('lab_base_manifest',[]):
        try:m=json.loads(parent['blobs'][mref])
        except Exception as e:raise PublishError('BASE_MANIFEST_INVALID') from e
        base_refs.add(mref);base_refs.update(x.get('ref') for x in m.get('entries',[]) if type(x) is dict)
    req(not(base_refs & set(withdrawals)),'IMMUTABLE_BASE_WITHDRAWAL')
    # First apply reviewed runtime objects, then add a content-addressed generation record that excludes its own ref/new policy hash.
    provisional_raw,added=build_next(parent_raw,additions,withdrawals);provisional=json.loads(provisional_raw)
    grouped={}
    for row in added:grouped.setdefault(row['role'],[]).append(row['ref'])
    generation_record={'role':'lab_authority_generation','schema_version':1,'withdrawn':False,
        'parent_policy_digest':expected_parent_sha,'parent_generation':parent['generation'],'generation':parent['generation']+1,
        'immutable_partition_digest':event_fields['immutable_partition_digest'],'added_refs':{k:sorted(v) for k,v in sorted(grouped.items())},
        'event_identity':{k:event_fields[k] for k in ('suite_ref','case_id','stage_index','slot_ref')}}
    grow=canonical(generation_record);gref=sha(grow);provisional['blobs'][gref]=grow.decode();provisional['role_pins'].setdefault('lab_authority_generation',[]);provisional['role_pins']['lab_authority_generation'].append(gref);provisional['role_pins']['lab_authority_generation']=sorted(set(provisional['role_pins']['lab_authority_generation']))
    candidate_raw=canonical(provisional);strict_policy(candidate_raw);candidate_sha=sha(candidate_raw)
    added_with_generation=sorted([*added,{'role':'lab_authority_generation','ref':gref}],key=lambda x:(x['role'],x['ref']))
    event={'kind':'AUTHORITY_GENERATION_PUBLISHED','parent_policy_digest':expected_parent_sha,'parent_generation':parent['generation'],
           'new_policy_digest':candidate_sha,'new_generation':parent['generation']+1,'generation_record_ref':gref,'added_refs':added_with_generation,**event_fields}
    for k in ('suite_ref','slot_ref','immutable_partition_digest','lineage_ref','plan_ref'):hash_value(event[k],k.upper())
    req(isinstance(event['case_id'],str) and type(event['stage_index']) is int,'PUBLICATION_SCOPE')
    guard=Path(guard_path);guard.parent.mkdir(parents=True,exist_ok=True)
    with open(guard,'a+b') as gh:
        fcntl.flock(gh.fileno(),fcntl.LOCK_EX)
        cur=Path(current_path).read_bytes() if Path(current_path).exists() else parent_raw;cur_sha=sha(cur)
        if fault=='BEFORE_WRITE':raise PublishError('FAULT_BEFORE_WRITE')
        wrote=False
        if cur_sha==expected_parent_sha:
            tmp=Path(str(current_path)+'.tmp');tmp.parent.mkdir(parents=True,exist_ok=True);tmp.write_bytes(candidate_raw)
            with open(tmp,'rb') as fh:os.fsync(fh.fileno())
            os.replace(tmp,current_path);wrote=True
            if fault=='AFTER_WRITE_BEFORE_READBACK':raise PublishError('FAULT_AFTER_WRITE_BEFORE_READBACK')
        elif cur_sha!=candidate_sha:raise PublishError('UNKNOWN_CURRENT_POLICY')
        readback=Path(current_path).read_bytes();req(readback==candidate_raw,'POLICY_READBACK')
        if fault=='AFTER_READBACK_BEFORE_EVENT':raise PublishError('FAULT_AFTER_READBACK_BEFORE_EVENT')
        rows=read_events(journal_path);same=[r for r in rows if all(k in r for k in ('new_policy_digest','suite_ref','case_id','stage_index','slot_ref')) and event_key(r)==event_key(event)]
        if same:req(len(same)==1 and same[0]==event,'PUBLICATION_EVENT_CONFLICT')
        else:
            Path(journal_path).parent.mkdir(parents=True,exist_ok=True)
            with open(journal_path,'ab') as f:f.write(canonical(event)+b'\n');f.flush();os.fsync(f.fileno())
        if fault=='AFTER_EVENT':raise PublishError('FAULT_AFTER_EVENT')
        return {'schema_version':1,'kind':'V03_POLICY_PUBLICATION','status':'PASS','parent_policy_digest':expected_parent_sha,
                'new_policy_digest':candidate_sha,'parent_generation':parent['generation'],'new_generation':parent['generation']+1,
                'added_refs':added_with_generation,'generation_record_ref':gref,'rewrote_policy':wrote,'publication_event_reused':bool(same),
                'guard_released_before_request_entry':True,'hklm_written':False,'signing_performed':False,'native_execution_started':False}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--parent-policy',required=True);ap.add_argument('--current-policy',required=True)
    ap.add_argument('--expected-parent-sha256',required=True);ap.add_argument('--additions',required=True);ap.add_argument('--event',required=True)
    ap.add_argument('--journal',required=True);ap.add_argument('--guard-file',required=True);ap.add_argument('--withdrawals');a=ap.parse_args()
    try:
        additions=json.loads(Path(a.additions).read_text());event=json.loads(Path(a.event).read_text())
        withdrawals=json.loads(Path(a.withdrawals).read_text()) if a.withdrawals else []
        o=publish(a.parent_policy,a.current_policy,a.expected_parent_sha256,additions,event,a.journal,a.guard_file,withdrawals);rc=0
    except (PublishError,V03Error,OSError,ValueError,json.JSONDecodeError,KeyError) as e:
        o={'schema_version':1,'kind':'V03_POLICY_PUBLICATION','status':'FAIL','reason':str(e),
           'hklm_written':False,'signing_performed':False,'native_execution_started':False};rc=1
    print(json.dumps(o,sort_keys=True,separators=(',',':')));return rc
if __name__=='__main__':raise SystemExit(main())
