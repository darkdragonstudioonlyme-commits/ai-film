"""Concrete Windows command execution component used by NativeDriver routes.

Requires an already-authorized session, held global guard and durable INTENT.
Does not declare service-side completion, clear a fence or issue HOST_READY;
NativeDriver owns pre/postconditions, resume and evidence integration.
"""
from contextlib import ExitStack
from ..codec import canonical,windows_path,hash_value,sha256
from ..errors import require,P00Error
from ..plans import check_plan
from ..windows_commands import compile_wsl,compile_feature,compile_features,compile_runtime
from .process import Command
from .trust import NativeStore,validate_payload_graph

SUPPORTED_ACTIONS=frozenset({'ENABLE_PREREQUISITES','INSTALL_RUNTIME','INSTALL_DISTRO',
                            'EXPORT_CHECKPOINT','IMPORT_NEW_CLONE','STOP_RETAIN_CLONE'})

class NativeActuator:
    def __init__(self,supervisor,paths,store,system_directory,environment):
        require(type(store) is NativeStore,12,'NATIVE_AUTHORITY_ADAPTER_REQUIRED')
        self.supervisor=supervisor;self.paths=paths;self.store=store
        self.system_directory=windows_path(system_directory);self.environment=environment

    def execute(self,action,plan,coordinator,native_binding):
        s=check_plan(plan)
        require(coordinator.held and coordinator.admission is not None and coordinator.fence is not None,12,'ADMITTED_INTENT_REQUIRED')
        require(coordinator.admission.plan_digest==plan['plan_digest'] and coordinator.fence['action']==action
                and action in {o['action'] for o in s['operations']},12,'ACTUATOR_SCOPE')
        require(action in SUPPORTED_ACTIONS,11,'ACTION_COMPONENT_NOT_IMPLEMENTED')
        # The full route driver must retrieve this exact blob through refs; check
        # again at this boundary instead of trusting an arbitrary dictionary.
        ref=s['refs'].get('native_binding');require(ref is not None,12,'NATIVE_BINDING_REQUIRED')
        trusted=self.store.get('native_binding',ref)
        require(trusted==native_binding and trusted.get('host_id')==s['host_id']
                and trusted.get('owner_sid')==s['owner_sid'],12,'NATIVE_BINDING_SCOPE')
        require(trusted.get('withdrawn') is False,12,'NATIVE_BINDING_WITHDRAWN')
        timeout=trusted.get('timeout_seconds',{}).get(action)
        require(type(timeout) is int and 1<=timeout<=7200,10,'ACTION_TIMEOUT_BINDING')
        target=s['target']['name'];commands=[];results=[]
        with ExitStack() as stack:
            if action in ('INSTALL_RUNTIME','INSTALL_DISTRO','IMPORT_NEW_CLONE'):
                role='payload' if action!='IMPORT_NEW_CLONE' else 'checkpoint_payload'
                pref=s['refs'].get(role);require(pref is not None,15,'PAYLOAD_TRUST_MISSING')
                if role=='payload':p=validate_payload_graph(self.store,pref,s['payload_digest'])
                else:
                    p=self.store.get(role,pref)
                    require(p.get('payload_digest')==s.get('expected_checkpoint') and p.get('withdrawn') is False,15,'CHECKPOINT_BINDING')
                stack.enter_context(self.paths.pinned_payload(p['path'],p['payload_digest'],p['bytes']))
            if action=='ENABLE_PREREQUISITES':
                features=trusted.get('features')
                require(type(features) is list and features and len(set(features))==len(features)
                        and set(features)<={'VirtualMachinePlatform','Microsoft-Windows-Subsystem-Linux'},10,'FEATURE_SCOPE')
                commands=[compile_features(features,self.system_directory,
                    log_path=trusted['dism_log_path'],scratch_directory=trusted['scratch_directory'])]
            elif action=='INSTALL_RUNTIME':commands=[compile_runtime(p['path'],self.system_directory)]
            elif action=='INSTALL_DISTRO':commands=[compile_wsl(action,system_directory=self.system_directory,target=target,payload=p['path'],base_path=s['target']['base_path'])]
            elif action=='IMPORT_NEW_CLONE':commands=[compile_wsl(action,system_directory=self.system_directory,target=target,payload=p['path'],base_path=s['target']['base_path'])]
            elif action=='EXPORT_CHECKPOINT':commands=[compile_wsl(action,system_directory=self.system_directory,target=target,payload=trusted['export_path'])]
            elif action=='STOP_RETAIN_CLONE':commands=[compile_wsl(action,system_directory=self.system_directory,target=target)]
            for index,argv in enumerate(commands):
                def persist(witness):
                    if coordinator.fence['state']=='INTENT':coordinator.native_started(witness)
                    else:coordinator.native_child_started(witness)
                command=Command(tuple(argv),action+'-'+str(index),timeout,b'',True)
                result=self.supervisor.run(command,before_resume=persist,environment=self.environment,cwd=self.system_directory)
                results.append({'native_exit':result.exit_code,'stdout_digest':sha256(result.stdout),
                    'stderr_digest':sha256(result.stderr),'stdout_eof':result.stdout_eof,'stderr_eof':result.stderr_eof,
                    'truncated':result.truncated,'duration_ms':result.duration_ms,
                    'native_witness':result.native_witness,'tree_terminal':result.tree_terminal,'service_terminal':False})
                coordinator.storage.append_event({'kind':'NATIVE_PROCESS_COMPLETED',
                    'plan_digest':plan['plan_digest'],'action':action,
                    'native_witness':result.native_witness,'native_exit':result.exit_code,
                    'tree_terminal':result.tree_terminal,'service_terminal':False})
                # MSI/DISM success-with-restart is not mapped to full success.
                if result.exit_code==3010 and action in ('INSTALL_RUNTIME','ENABLE_PREREQUISITES'):
                    return {'exit':20,'state':'AWAITING_REBOOT','results':results,'service_terminal':False}
                require(result.exit_code==0,18,'NATIVE_ACTION_FAILED')
        return {'exit':0,'state':'NATIVE_PROCESS_COMPLETED','results':results,'service_terminal':False,
                'postconditions_observed':False,'host_ready':False}
