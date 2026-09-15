"""Write-ahead E17 proposal publication and read-only crash recovery.

The gate assessment is a separate JSON artifact, never part of E16 and never a
HOST_READY authority. Intent binds both exact staged and final paths before any
write. Recovery recognizes exact existing bytes only; it never renames, deletes,
replaces or creates missing assessment output.
"""
from copy import deepcopy
from ..codec import canonical,digest,sha256,loads
from ..errors import require,P00Error
from .observations import file_presence
from .publication_recovery import staged_output_path

ASSESSMENT_CAP=1024*1024


def _intent_rows(coordinator,plan_digest):
    return [r['event'] for r in coordinator.storage.read_events()
            if r['event'].get('kind')=='ASSESSMENT_PUBLISH_INTENT'
            and r['event'].get('plan_digest')==plan_digest]


def assessment_intent_count(coordinator,plan_digest):
    return len(_intent_rows(coordinator,plan_digest))


def _validate_intent(event,plan_digest,path):
    require(event.get('kind')=='ASSESSMENT_PUBLISH_INTENT',15,'ASSESSMENT_INTENT_KIND')
    body=event.get('publication');require(type(body) is dict,15,'ASSESSMENT_INTENT_SCHEMA')
    require(event.get('publication_digest')==digest(body),15,'ASSESSMENT_INTENT_INTEGRITY')
    require(set(body)=={'path','temp_path','sha256','bytes','assessment_digest','accepted_by_master'},15,'ASSESSMENT_INTENT_SCHEMA')
    require(body['path']==path and body['accepted_by_master'] is False,16,'ASSESSMENT_PATH_OR_AUTHORITY_DRIFT')
    require(type(body['bytes']) is int and 1<=body['bytes']<=ASSESSMENT_CAP,15,'ASSESSMENT_SIZE')
    require(body['temp_path']==staged_output_path(path,plan_digest,body['sha256'],'assessment'),
            16,'ASSESSMENT_TEMP_PATH_DRIFT')
    return body


def _read_assessment(paths,path,body):
    raw=paths.read_blob(path,expected=body['sha256'],cap=ASSESSMENT_CAP)
    require(len(raw)==body['bytes'],15,'ASSESSMENT_SIZE_MISMATCH')
    value=loads(raw)
    require(type(value) is dict and digest(value)==body['assessment_digest'],15,'ASSESSMENT_READBACK_MISMATCH')
    require(value.get('status')=='PROPOSAL' and value.get('accepted_by_master') is False
            and value.get('host_ready') is False,15,'ASSESSMENT_AUTHORITY_FORBIDDEN')
    return value


class AssessmentPublisher:
    def __init__(self,paths,coordinator):self.paths=paths;self.c=coordinator

    def publish(self,plan,assessment,path):
        c=self.c
        require(c.held and c.fence is not None and c.admission is not None,12,'ASSESSMENT_ADMISSION_REQUIRED')
        require(c.admission.plan_digest==plan['plan_digest'] and c.fence['plan_digest']==plan['plan_digest'],12,'ASSESSMENT_SCOPE')
        require(assessment.get('status')=='PROPOSAL' and assessment.get('accepted_by_master') is False
                and assessment.get('host_ready') is False,15,'ASSESSMENT_AUTHORITY_FORBIDDEN')
        raw=canonical(assessment);require(len(raw)<=ASSESSMENT_CAP,22,'ASSESSMENT_CAP')
        payload_sha=sha256(raw);temp=staged_output_path(path,plan['plan_digest'],payload_sha,'assessment')
        publication={'path':path,'temp_path':temp,'sha256':payload_sha,'bytes':len(raw),
                     'assessment_digest':digest(assessment),'accepted_by_master':False}
        c.storage.append_event({'kind':'ASSESSMENT_PUBLISH_INTENT','plan_digest':plan['plan_digest'],
                                'publication':publication,'publication_digest':digest(publication)})
        try:self.paths.publish_new(path,raw,pending_path=temp)
        except P00Error as e:
            if e.code in (12,15,16):raise
            return {'exit':18,'status':'FAILED_OUTPUT','published':False,'accepted_by_master':False,'host_ready':False}
        c.storage.append_event({'kind':'ASSESSMENT_OUTPUT_OBSERVED','plan_digest':plan['plan_digest'],
                                'path':path,'sha256':publication['sha256'],'assessment_digest':publication['assessment_digest']})
        return {'exit':0,'status':'PROPOSAL','published':True,'assessment_digest':publication['assessment_digest'],
                'output_sha256':publication['sha256'],'accepted_by_master':False,'host_ready':False}


def recover_assessment(paths,coordinator,plan,path):
    require(coordinator.held and coordinator.fence is not None and coordinator.admission is not None,12,'ASSESSMENT_RECOVERY_ADMISSION')
    require(coordinator.admission.plan_digest==plan['plan_digest'] and coordinator.fence['plan_digest']==plan['plan_digest'],12,'ASSESSMENT_RECOVERY_SCOPE')
    rows=_intent_rows(coordinator,plan['plan_digest']);require(len(rows)==1,21,'ASSESSMENT_INTENT_NOT_UNIQUE')
    body=_validate_intent(rows[0],plan['plan_digest'],path);temp=body['temp_path']
    final_present=file_presence(paths,path);temp_present=file_presence(paths,temp)
    require(not (final_present and temp_present),16,'ASSESSMENT_OUTPUT_AMBIGUOUS')
    if final_present:
        _read_assessment(paths,path,body)
        result={'exit':0,'status':'PROPOSAL','published':True,'recovered_existing_bytes':True,
                'assessment_digest':body['assessment_digest'],'output_sha256':body['sha256'],
                'accepted_by_master':False,'host_ready':False}
        coordinator.storage.append_event({'kind':'ASSESSMENT_OUTPUT_REOBSERVED','plan_digest':plan['plan_digest'],
            'intent_digest':rows[0]['publication_digest'],'result':deepcopy(result),'observation_digest':digest(result)})
        return result
    if temp_present:
        _read_assessment(paths,temp,body)
        retained={'temp_path':temp,'sha256':body['sha256'],'bytes':body['bytes'],
                  'intent_digest':rows[0]['publication_digest'],'published':False,'host_ready':False}
        coordinator.storage.append_event({'kind':'ASSESSMENT_TEMP_RETAINED','plan_digest':plan['plan_digest'],
            'observation':retained,'observation_digest':digest(retained)})
        raise P00Error(18,'ASSESSMENT_TEMP_RETAINED')
    raise P00Error(18,'ASSESSMENT_OUTPUT_MISSING')
