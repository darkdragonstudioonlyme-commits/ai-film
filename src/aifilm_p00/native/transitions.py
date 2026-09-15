"""Exact native after-state matching with narrowly bound generated identities.

Native binding is authenticated and its digest is in the immutable plan. A
capture declares where Windows allocates an identity, not a wildcard for unknown
facts. Captured values always come from the fresh native observation and are
retained verbatim in the journal. No existing registration can be recaptured.
"""
from copy import deepcopy
import re
from ..codec import digest
from ..errors import require

CAPTURES={'TARGET_REGISTRATION','FIRST_DEFAULT','INITIAL_UID'}


def resolve_expected(expected, actual, initial, target, captures):
    """Compare full material states, resolving only the declared generated slots.

    Slots use {"capture": "TARGET_REGISTRATION"}, etc. and are allowed ONLY at
    fields of the newly created target or the first-default field. The caller
    binds the exact allowed slot names for this action, never from observations.
    """
    require(type(expected) is dict and type(actual) is dict and type(initial) is dict,
            10,'MATERIAL_SCHEMA')
    require(type(captures) is list and len(captures)==len(set(captures)) and
            set(captures)<=CAPTURES,10,'IDENTITY_CAPTURE_SCOPE')
    out=deepcopy(expected); used=set(); observed={}
    oldrows=initial.get('distros',{}).get('rows',[])
    newrows=actual.get('distros',{}).get('rows',[])
    target_rows=[r for r in newrows if r.get('name')==target['name']]
    target_actual=target_rows[0] if len(target_rows)==1 else None
    fresh=(target.get('registration_id') is None and not any(r.get('name')==target['name'] for r in oldrows))
    for row in out.get('distros',{}).get('rows',[]):
        for key,name in (('registration_id','TARGET_REGISTRATION'),('default_uid','INITIAL_UID')):
            if type(row.get(key)) is not dict: continue
            require(row[key]=={'capture':name} and name in captures and fresh
                    and target_actual is not None and row.get('name')==target['name']
                    and row.get('base_path')==target['base_path'],10,'IDENTITY_CAPTURE_LOCATION')
            value=target_actual[key]
            if key=='registration_id':
                require(type(value) is str and re.fullmatch(r'\{[0-9A-Fa-f]{8}(?:-[0-9A-Fa-f]{4}){3}-[0-9A-Fa-f]{12}\}',value)
                        and value not in {r['registration_id'] for r in oldrows},16,'REGISTRATION_NOT_NEW')
            else: require(type(value) is int and value>=0,16,'UID_NOT_OBSERVED')
            require(name not in used,10,'DUPLICATE_IDENTITY_CAPTURE')
            row[key]=value;used.add(name);observed[name]=value
    if type(out.get('distros',{}).get('default')) is dict:
        require(out['distros']['default']=={'capture':'FIRST_DEFAULT'} and 'FIRST_DEFAULT' in captures
                and fresh and not oldrows and initial['distros']['default'] is None
                and target_actual is not None,10,'DEFAULT_CAPTURE_SCOPE')
        require(actual['distros']['default']==target_actual['registration_id'],16,'FIRST_DEFAULT_NOT_TARGET')
        out['distros']['default']=actual['distros']['default'];used.add('FIRST_DEFAULT')
        observed['FIRST_DEFAULT']=actual['distros']['default']
    require(used==set(captures),10,'IDENTITY_CAPTURE_UNUSED')
    # Registry enumeration order may change. Ordering is not an identity change.
    for state in (out,):
        if 'distros' in state:
            state['distros']['rows']=sorted(state['distros']['rows'],key=lambda r:r['registration_id'])
    require(out==actual,16,'NATIVE_AFTER_STATE_MISMATCH')
    return {'material_after':deepcopy(actual),'captures':observed,'material_digest':digest(actual)}


def operation_expected(binding, plan, action, actual):
    s=plan['semantic']; rows=binding.get('after_by_action')
    require(type(rows) is dict and action in rows,10,'AFTER_STATE_BINDING_MISSING')
    row=rows[action]
    require(type(row) is dict and set(row)=={'material','captures'},10,'AFTER_STATE_BINDING_SCHEMA')
    return resolve_expected(row['material'],actual,s['before'],s['target'],row['captures'])


def final_expected(binding, plan, actual):
    s=plan['semantic']; captures=binding.get('final_captures',[])
    return resolve_expected(s['expected_after'],actual,s['before'],s['target'],captures)
