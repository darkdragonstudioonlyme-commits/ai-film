"""Observe interrupted create-only publication without mutating retained outputs.

Publication uses a deterministic protected staging path recorded in write-ahead
intent before any file write. Recovery never renames, deletes, overwrites or
re-publishes. Final-only exact bytes may complete; temp-only is a verified output
failure retained for owner diagnostics; both is ambiguous/drift.
"""
from pathlib import PureWindowsPath
from copy import deepcopy
from ..codec import digest, hash_value, windows_path
from ..errors import require,P00Error
from ..evidence import bundle_integrity, BUNDLE_CAP
from .observations import file_presence


def staged_output_path(final_path,plan_digest,payload_sha,kind):
    final_path=windows_path(final_path);hash_value(plan_digest);hash_value(payload_sha)
    require(kind in ('bundle','assessment'),10,'PUBLISH_STAGE_KIND')
    parent=PureWindowsPath(final_path).parent
    name='p00-pending-'+kind+'-'+plan_digest[:16]+'-'+payload_sha[:32]+'.bin'
    return windows_path(str(parent/name))


def _intent_rows(coordinator,plan_digest):
    return [r['event'] for r in coordinator.storage.read_events()
            if r['event'].get('kind')=='BUNDLE_PUBLISH_INTENT'
            and r['event'].get('plan_digest')==plan_digest]


def _validate_intent(event,plan,binding):
    body=event.get('publication');require(type(body) is dict,15,'PUBLISH_INTENT_SCHEMA')
    require(event.get('publication_digest')==digest(body),15,'PUBLISH_INTENT_INTEGRITY')
    expected={'path','temp_path','sha256','bytes','exit','outcome','archive_expected','component_eligible'}
    require(set(body)==expected,15,'PUBLISH_INTENT_SCHEMA')
    allowed={0:'COMPLETE',2:'PARTIAL_OPTIONAL',15:'FAILED_INTEGRITY',22:'INCOMPLETE_MANDATORY',23:'BLOCKED_REDACTION'}
    require(body['exit'] in allowed and body['outcome']==allowed[body['exit']]
            and type(body['archive_expected']) is bool and type(body['component_eligible']) is bool,
            15,'PUBLISH_OUTCOME_SCHEMA')
    output=binding['incomplete_bundle_output'] if body['exit']==22 else binding['bundle_output']
    require(body['path']==output,16,'PUBLISH_PATH_DRIFT')
    if body['archive_expected']:
        require(body['exit'] in (0,2,22) and type(body['bytes']) is int and 1<=body['bytes']<=BUNDLE_CAP,
                15,'PUBLISH_SIZE')
        hash_value(body['sha256'])
        expected_temp=staged_output_path(output,plan['plan_digest'],body['sha256'],'bundle')
        require(body['temp_path']==expected_temp,16,'PUBLISH_TEMP_PATH_DRIFT')
    else:
        require(body['exit'] in (15,22,23) and body['sha256'] is None and body['bytes']==0
                and body['temp_path'] is None and body['component_eligible'] is False,
                15,'PUBLISH_NO_ARCHIVE_SCHEMA')
    return body,output


def _read_bundle(paths,path,body):
    raw=paths.read_blob(path,expected=body['sha256'],cap=BUNDLE_CAP)
    require(len(raw)==body['bytes'],15,'PUBLISH_SIZE_MISMATCH')
    checked=bundle_integrity(raw);require(checked['sha256']==body['sha256'],15,'PUBLISH_READBACK_MISMATCH')
    return checked


def observed_publication(paths,coordinator,plan,binding):
    require(coordinator.held and coordinator.fence is not None
            and coordinator.fence['action']=='PUBLISH_SAFE_BUNDLE',12,'PUBLISH_RECOVERY_SCOPE')
    require(coordinator.fence['plan_digest']==plan['plan_digest'],12,'PUBLISH_RECOVERY_SCOPE')
    intents=_intent_rows(coordinator,plan['plan_digest']);require(len(intents)==1,21,'PUBLISH_INTENT_NOT_UNIQUE')
    event=intents[0];body,output=_validate_intent(event,plan,binding);temp=body['temp_path']
    final_present=file_presence(paths,output)
    if not body['archive_expected']:
        require(not final_present,16,'PUBLISH_UNEXPECTED_FINAL')
        result={'exit':body['exit'],'outcome':body['outcome'],'published':False,
                'archive_expected':False,'component_eligible':False,'host_ready':False,
                'recovered_no_archive_decision':True}
        coordinator.storage.append_event({'kind':'BUNDLE_NO_ARCHIVE_REOBSERVED',
            'plan_digest':plan['plan_digest'],'intent_digest':event['publication_digest'],
            'result':deepcopy(result),'observation_digest':digest(result)})
        return result
    temp_present=file_presence(paths,temp)
    require(not (final_present and temp_present),16,'PUBLISH_OUTPUT_AMBIGUOUS')
    if final_present:
        checked=_read_bundle(paths,output,body)
        result={'exit':body['exit'],'outcome':body['outcome'],'published':True,
                'bundle_digest':checked['sha256'],'archive_expected':True,
                'component_eligible':body['component_eligible'],'host_ready':False,
                'recovered_existing_bytes':True}
        coordinator.storage.append_event({'kind':'BUNDLE_PUBLICATION_REOBSERVED',
            'plan_digest':plan['plan_digest'],'intent_digest':event['publication_digest'],
            'result':deepcopy(result),'observation_digest':digest(result)})
        return result
    if temp_present:
        checked=_read_bundle(paths,temp,body)
        retained={'temp_path':temp,'sha256':checked['sha256'],'bytes':body['bytes'],
                  'intent_digest':event['publication_digest'],'published':False,'host_ready':False}
        coordinator.storage.append_event({'kind':'BUNDLE_PUBLICATION_TEMP_RETAINED',
            'plan_digest':plan['plan_digest'],'observation':retained,'observation_digest':digest(retained)})
        raise P00Error(18,'PUBLISH_TEMP_RETAINED')
    raise P00Error(18,'PUBLISH_OUTPUT_MISSING')
