#!/usr/bin/env python3
"""Pure fixture preparation recorder; it never executes ARRANGE/OBSERVE actions itself."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from v03_binding_producer_common import V03Error,canonical,digest,load_json,require

EXPECTED={'arrange_tokens':65,'observe_tokens':13,'native_preparation_tokens':78,'native_cases':85,'native_requests':133,'document_only_cases':1}

def load_recipe_catalog(path):
    x=load_json(path);require(type(x) is dict and x.get('schema_version')==1,'RECIPE_SCHEMA')
    counts=x.get('counts');require(type(counts) is dict,'RECIPE_COUNTS')
    for k,v in EXPECTED.items(): require(counts.get(k)==v,'RECIPE_COUNT:'+k)
    rows=x.get('preparations');require(type(rows) is list and len(rows)==78,'PREPARATION_COUNT')
    tokens=[];arr=obs=0
    for r in rows:
        require(type(r) is dict and isinstance(r.get('token'),str) and r['token'] not in tokens,'PREPARATION_TOKEN')
        require(r.get('mode') in ('ARRANGE','OBSERVE'),'PREPARATION_MODE')
        require(r.get('runtime_inference_forbidden') is True,'RUNTIME_INFERENCE')
        tokens.append(r['token']);arr+=r['mode']=='ARRANGE';obs+=r['mode']=='OBSERVE'
    require((arr,obs)==(65,13),'PREPARATION_MODE_COUNTS');return x

def materialize_records(catalog,observations):
    require(type(observations) is dict,'OBSERVATIONS_SCHEMA');out=[]
    for recipe in catalog['preparations']:
        token=recipe['token'];require(token in observations,'OBSERVATION_MISSING:'+token);o=observations[token]
        require(type(o) is dict and set(o)=={'before_digest','after_digest','actual'},'OBSERVATION_SCHEMA')
        before=o['before_digest'];after=o['after_digest'];actual=o['actual'];require(type(actual) is dict,'OBSERVATION_ACTUAL')
        if recipe['mode']=='ARRANGE':
            require(before!=after and actual.get('causal_effect_observed') is True,'ARRANGE_CAUSALITY')
        else:
            require(actual.get('observed_existing_condition') is True,'OBSERVE_CAUSALITY')
        out.append({'schema_version':1,'kind':'V03_FIXTURE_PREPARATION_RECORD','token':token,'mode':recipe['mode'],
                    'recipe_family':recipe['recipe_family'],'before_digest':before,'after_digest':after,'actual':actual,
                    'record_digest':digest({'token':token,'mode':recipe['mode'],'before_digest':before,'after_digest':after,'actual':actual}),
                    'native_execution_started':False})
    return out

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--recipe-catalog',required=True);ap.add_argument('--observations',required=True);ap.add_argument('--out',required=True);a=ap.parse_args()
    try:
        c=load_recipe_catalog(a.recipe_catalog);obs=load_json(a.observations);rows=materialize_records(c,obs)
        result={'schema_version':1,'kind':'V03_FIXTURE_PREPARATION_SET','status':'PASS','records':rows,
                'arrange_count':65,'observe_count':13,'native_case_count':85,'native_request_count':133,'native_execution_started':False}
        Path(a.out).write_bytes(canonical(result)+b'\n');rc=0
    except (V03Error,OSError,ValueError,json.JSONDecodeError) as e:
        result={'schema_version':1,'kind':'V03_FIXTURE_PREPARATION_SET','status':'FAIL','reason':str(e),'native_execution_started':False};rc=1
    print(json.dumps(result,sort_keys=True,separators=(',',':')));return rc
if __name__=='__main__':raise SystemExit(main())
