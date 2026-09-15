"""Write-ahead E17 proposal publication and read-only crash recovery.

The gate assessment is a separate JSON artifact, never part of E16 and never a
HOST_READY authority.  Intent is durable before create-only publication.  A
recovery path may only recognize exact already-existing bytes; it cannot rewrite,
replace, delete, or infer acceptance from the file name.
"""
from copy import deepcopy
from ..codec import canonical,digest,sha256
from ..errors import require,P00Error
from .observations import file_presence

ASSESSMENT_CAP=1024*1024


def _intent_rows(coordinator,plan_digest):
    return [r['event'] for r in coordinator.storage.read_events()
            if r['event'].get('kind')=='ASSESSMENT_PUBLISH_INTENT'
            and r['event'].get('plan_digest')==plan_digest]


def _validate_intent(event,path):
    require(event.get('kind')=='ASSESSMENT_PUBLISH_INTENT',15,'ASSESSMENT_INTENT_KIND')
    body=event.get('publication');require(type(body) is dict,15,'ASSESSMENT_INTENT_SCHEMA')
    require(event.get('publication_digest')==digest(body),15,'ASSESSMENT_INTENT_INTEGRITY')
    require(set(body)=={'path','sha256','bytes','assessment_digest','accepted_by_master'},15,'ASSESSMENT_INTENT_SCHEMA')
    require(body['path']==path and body['accepted_by_master'] is False,16,'ASSESSMENT_PATH_OR_AUTHORITY_DRIFT')
    require(type(body['bytes']) is int and 1<=body['bytes']<=ASSESSMENT_CAP,15,'ASSESSMENT_SIZE')
    return body


class AssessmentPublisher:
    def __init__(self,paths,coordinator):self.paths=paths;self.c=coordinator

    def publish(self,plan,assessment,path):
        c=self.c
        require(c.held and c.fence is not None and c.admission is not None,12,'ASSESSMENT_ADMISSION_REQUIRED')
        require(c.admission.plan_digest==plan['plan_digest'] and c.fence['plan_digest']==plan['plan_digest'],12,'ASSESSMENT_SCOPE')
        require(assessment.get('status')=='PROPOSAL' and assessment.get('accepted_by_master') is False
                and assessment.get('host_ready') is False,15,'ASSESSMENT_AUTHORITY_FORBIDDEN')
        raw=canonical(assessment);require(len(raw)<=ASSESSMENT_CAP,22,'ASSESSMENT_CAP')
        publication={'path':path,'sha256':sha256(raw),'bytes':len(raw),'assessment_digest':digest(assessment),'accepted_by_master':False}
        c.storage.append_event({'kind':'ASSESSMENT_PUBLISH_INTENT','plan_digest':plan['plan_digest'],
                                'publication':publication,'publication_digest':digest(publication)})
        try:self.paths.publish_new(path,raw)
        except P00Error as e:
            if e.code in (12,15,16):raise
            return {'exit':18,'status':'FAILED_OUTPUT','published':False,'accepted_by_master':False,'host_ready':False}
        # Success is based on create-only write completion.  A later recovery may
        # re-observe bytes after an interrupted controller before this event.
        c.storage.append_event({'kind':'ASSESSMENT_OUTPUT_OBSERVED','plan_digest':plan['plan_digest'],
                                'path':path,'sha256':publication['sha256'],'assessment_digest':publication['assessment_digest']})
        return {'exit':0,'status':'PROPOSAL','published':True,'assessment_digest':publication['assessment_digest'],
                'output_sha256':publication['sha256'],'accepted_by_master':False,'host_ready':False}


def recover_assessment(paths,coordinator,plan,path):
    require(coordinator.held and coordinator.fence is not None and coordinator.admission is not None,12,'ASSESSMENT_RECOVERY_ADMISSION')
    require(coordinator.admission.plan_digest==plan['plan_digest'] and coordinator.fence['plan_digest']==plan['plan_digest'],12,'ASSESSMENT_RECOVERY_SCOPE')
    rows=_intent_rows(coordinator,plan['plan_digest']);require(len(rows)==1,21,'ASSESSMENT_INTENT_NOT_UNIQUE')
    body=_validate_intent(rows[0],path)
    require(file_presence(paths,path),18,'ASSESSMENT_FINAL_NOT_PRESENT')
    raw=paths.read_blob(path,expected=body['sha256'],cap=ASSESSMENT_CAP)
    require(len(raw)==body['bytes'],15,'ASSESSMENT_SIZE_MISMATCH')
    from ..codec import loads
    value=loads(raw)
    require(type(value) is dict and digest(value)==body['assessment_digest'],15,'ASSESSMENT_READBACK_MISMATCH')
    require(value.get('status')=='PROPOSAL' and value.get('accepted_by_master') is False
            and value.get('host_ready') is False,15,'ASSESSMENT_AUTHORITY_FORBIDDEN')
    return {'exit':0,'status':'PROPOSAL','published':True,'recovered_existing_bytes':True,
            'assessment_digest':body['assessment_digest'],'output_sha256':body['sha256'],
            'accepted_by_master':False,'host_ready':False}
