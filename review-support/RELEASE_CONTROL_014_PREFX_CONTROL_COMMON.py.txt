#!/usr/bin/env python3
import json,re
from pathlib import Path
CONFIG_PATH=Path('/home/dragon/ai-film-runtime/config/release-control.json')
REQUIRED={'schema_version','kind','release_name','implementation_version','source_commit','source_digest','test_digest','contract_digest','package_name','package_sha256','wheel_name','wheel_sha256','app_file_count','runtime_root','rebuild_root','host_backup_root','offhost_export_root','offhost_export_name','authority_evidence_root','authority_model','verify_service','verify_timer','expected_timer_count','native_authority','native_execution_started'}
H64=re.compile(r'^[0-9a-f]{64}$'); H40=re.compile(r'^[0-9a-f]{40}$')
def load_control(path=None):
    p=Path(path) if path is not None else CONFIG_PATH
    x=json.loads(p.read_text(encoding='utf-8'))
    if not isinstance(x,dict) or set(x)!=REQUIRED: raise RuntimeError('release-control-schema')
    if x['schema_version']!=1 or x['kind']!='AIFILM_P00_RELEASE_CONTROL': raise RuntimeError('release-control-kind')
    if not re.fullmatch(r'dev[0-9]+',x['release_name']): raise RuntimeError('release-control-release')
    if not H40.fullmatch(x['source_commit']): raise RuntimeError('release-control-source')
    for k in ('source_digest','test_digest','contract_digest','package_sha256','wheel_sha256'):
        if not H64.fullmatch(x[k]): raise RuntimeError('release-control-digest:'+k)
    if not isinstance(x['app_file_count'],int) or x['app_file_count']<1: raise RuntimeError('release-control-app-count')
    if x['authority_model']!='LOCAL_OPERATOR_SAME_WSL_TRUST_DOMAIN': raise RuntimeError('release-control-authority-model')
    if x['native_authority'] is not False or x['native_execution_started'] is not False: raise RuntimeError('release-control-native-boundary')
    for k in ('runtime_root','rebuild_root','host_backup_root','offhost_export_root','authority_evidence_root'):
        if not Path(x[k]).is_absolute(): raise RuntimeError('release-control-path:'+k)
    if x['expected_timer_count']!=11: raise RuntimeError('release-control-timer-count')
    return x
