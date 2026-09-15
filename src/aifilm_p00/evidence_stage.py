"""Serialize observed stage, never infer eligibility from an envelope's status."""
from dataclasses import asdict,fields,replace
from .codec import digest
from .errors import require
from .evidence_catalog import Stage


def encode_stage(stage):
    require(isinstance(stage,Stage),15,'STAGE_CONTEXT_REQUIRED')
    stage.validate();return asdict(stage)


def decode_stage(value):
    require(type(value) is dict and set(value)=={f.name for f in fields(Stage)},15,'STAGE_CONTEXT_SCHEMA')
    result=Stage(**value);result.validate();return result


def scoped_stage(descriptor,index,scope,record):
    """Use the capture's immutable stage and allow only an explicit projection.

    A GATE request is not permission to upgrade an APPLY, LAB or partial record.
    Inventory projects only requiredness, retaining the original subject/flags.
    """
    value=index.get('stage_context');stage=decode_stage(value)
    require(value==descriptor.get('stage_context') and digest(value)==descriptor.get('stage_digest'),
            15,'SNAPSHOT_STAGE_BINDING')
    require(stage.name==descriptor['stage'] and stage.execution_class==descriptor['source_kind']
            and stage.route==record['route'] and stage.name==record['stage']
            and stage.execution_class==record['source_kind'],15,'SNAPSHOT_STAGE_SCOPE')
    require(scope in ('GATE_HANDOFF','INVENTORY','FAILED_RUN'),10,'BUNDLE_SCOPE')
    if scope=='GATE_HANDOFF':
        require(stage.name=='GATE' and stage.execution_class=='SITE' and stage.after_probe
                and stage.existing_target,22,'GATE_SOURCE_STAGE_INCOMPLETE')
    elif scope=='INVENTORY':stage=replace(stage,name='C0')
    return stage


def require_bundle_context(context,descriptor,source_fences):
    """Derive attempted action classes from durable intents, not caller flags."""
    keys={'persistent_output','mutation_attempted','c3_attempted','restore_attempted'}
    require(type(context) is dict and set(context)==keys and all(type(x) is bool for x in context.values()),10,'BUNDLE_CONTEXT_SCHEMA')
    stage=decode_stage(descriptor.get('stage_context'))
    restore_actions={'EXPORT_CHECKPOINT','IMPORT_NEW_CLONE','VERIFY_CLONE','STOP_RETAIN_CLONE'}
    c3_actions={'ENABLE_PREREQUISITES','INSTALL_RUNTIME','AWAIT_OWNER_RESTART'}
    actual={'persistent_output':stage.persistent_output,
            'mutation_attempted':bool(source_fences),
            'c3_attempted':any(x['action'] in c3_actions for x in source_fences),
            'restore_attempted':any(x['action'] in restore_actions for x in source_fences)}
    require(context==actual,16,'BUNDLE_CONTEXT_DRIFT');return actual
