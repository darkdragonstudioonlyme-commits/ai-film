"""Observe a publish interrupted after create-only file output, without rewriting it.

A journaled intended hash alone is not completion. The final path must be read
under protected handles, checked byte-for-byte, and its ZIP manifest validated.
No temp-file rename, deletion, overwrite, resanitization or auto retry occurs.
"""
from pathlib import PureWindowsPath
from copy import deepcopy
from ..codec import digest, sha256
from ..errors import require
from ..evidence import bundle_integrity, BUNDLE_CAP
from .observations import file_presence


def observed_publication(paths,coordinator,plan,binding):
    require(coordinator.held and coordinator.fence is not None
            and coordinator.fence['action']=='PUBLISH_SAFE_BUNDLE',12,'PUBLISH_RECOVERY_SCOPE')
    s=plan['semantic'];require(coordinator.fence['plan_digest']==plan['plan_digest'],12,'PUBLISH_RECOVERY_SCOPE')
    intents=[r['event'] for r in coordinator.storage.read_events()
             if r['event'].get('kind')=='BUNDLE_PUBLISH_INTENT'
             and r['event'].get('plan_digest')==plan['plan_digest']]
    require(len(intents)==1,21,'PUBLISH_INTENT_NOT_UNIQUE')
    event=intents[0];body=event['publication']
    require(event.get('publication_digest')==digest(body),15,'PUBLISH_INTENT_INTEGRITY')
    require(body.get('archive_expected') is True,21,'PUBLISH_NO_ARCHIVE_REQUIRES_DIAGNOSTICS')
    output=binding['incomplete_bundle_output'] if body['exit']==22 else binding['bundle_output']
    require(body['path']==output,16,'PUBLISH_PATH_DRIFT')
    require(body['exit'] in (0,2,22),15,'PUBLISH_OUTCOME_SCHEMA')
    require(file_presence(paths,output),18,'PUBLISH_FINAL_NOT_PRESENT')
    raw=paths.read_blob(output,expected=body['sha256'],cap=BUNDLE_CAP)
    require(len(raw)==body['bytes'],15,'PUBLISH_SIZE_MISMATCH')
    checked=bundle_integrity(raw)
    require(checked['sha256']==body['sha256'],15,'PUBLISH_READBACK_MISMATCH')
    result={'exit':body['exit'],'outcome':body['outcome'],'published':True,
            'bundle_digest':checked['sha256'],'archive_expected':True,
            'component_eligible':body['component_eligible'],'host_ready':False,
            'recovered_existing_bytes':True}
    coordinator.storage.append_event({'kind':'BUNDLE_PUBLICATION_REOBSERVED',
        'plan_digest':plan['plan_digest'],'intent_digest':event['publication_digest'],
        'result':deepcopy(result),'observation_digest':digest(result)})
    return result
