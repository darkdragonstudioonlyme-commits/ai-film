"""Authenticated proof normalization; never manufacture native observations.

The host-owner HKLM anchor is the trust root specified by the native adapter.
Receipts are read, not issued. Owner assertions are explicitly distinguished from
native measurements. A receipt cannot turn a workspace fixture into a native run.
"""
from datetime import timedelta
from copy import deepcopy
from .. import CONTRACT_DIGEST
from ..codec import instant,digest,hash_value
from ..errors import require,P00Error


class ProofReader:
    def __init__(self,store,host_id,owner_sid,now):
        self.store=store;self.host_id=host_id;self.owner_sid=owner_sid;self.now=now

    def selected(self,role,scope,*,owner_assertion=False,not_before=None):
        """Select exactly one current pinned receipt for an immutable scope.

        A future postcheck cannot have its bytes hashed before execution. Its
        slot is bound by role + exact subject/parent scope, and the actual pinned
        digest is recorded on consumption. Ambiguous or withdrawn slots block.
        """
        candidates=[]
        for ref in sorted(self.store.pins.get(role,frozenset())-self.store.withdrawn):
            item=self.store.get(role,ref)
            if all(item.get('scope',{}).get(k)==v for k,v in scope.items()):candidates.append((ref,item))
        require(len(candidates)==1,20 if not candidates else 15,
                'AWAITING_OWNER_VERIFICATION' if not candidates else 'PROOF_SELECTION_AMBIGUOUS')
        return self.receipt(role,candidates[0][0],scope,owner_assertion=owner_assertion,not_before=not_before)

    def receipt(self,role,ref,scope,*,owner_assertion=False,not_before=None):
        item=self.store.get(role,ref)
        require(item.get('schema_version')==1 and item.get('withdrawn') is False
                and item.get('fixture_only') is not True,15,'PROOF_RECEIPT_SCHEMA')
        require(item.get('contract_digest')==CONTRACT_DIGEST,16,'PROOF_CONTRACT')
        require(type(item.get('scope')) is dict and all(item['scope'].get(k)==v for k,v in scope.items()),
                16,'PROOF_SUBJECT_MISMATCH')
        issued=instant(item['issued_at']);expires=instant(item['expires_at'])
        require(issued<=self.now<=expires and issued<=expires,11,'PROOF_EXPIRED')
        require(not_before is None or issued>=not_before,16,'PROOF_PRECEDES_OPERATION')
        authorizer=self.store.get('resource_owner',item['authorizer_ref'])
        require(authorizer.get('withdrawn') is False and authorizer.get('fixture_only') is not True
                and authorizer.get('owner_sid')==item.get('owner_sid')
                and role in authorizer.get('receipt_roles',[]),12,'PROOF_OWNER_AUTHORITY')
        host=scope.get('host_id',self.host_id)
        require(host in authorizer.get('host_ids',[]),12,'PROOF_OWNER_HOST_SCOPE')
        actuals=item.get('measurements')
        require(type(actuals) is list and 0<len(actuals)<=128 and len(actuals)==len(set(actuals)),15,'PROOF_MEASUREMENTS_REQUIRED')
        checked=[]
        for actual_ref in actuals:
            m=self.store.get('measurement',actual_ref)
            require(m.get('fixture_only') is not True and m.get('source_kind') in ('SITE','LAB','OWNER_ASSERTION'),
                    15,'WORKSPACE_PROOF_FORBIDDEN')
            require(m.get('source_kind')!='OWNER_ASSERTION' or owner_assertion,15,'NATIVE_PROOF_REQUIRED')
            require(m.get('status')=='OBSERVED' and m.get('contract_digest')==CONTRACT_DIGEST
                    and type(m.get('actual')) is dict and bool(m['actual']),15,'PROOF_MEASUREMENT_SCHEMA')
            require(m.get('host_id')==host and m.get('subject_digest')==digest(item['scope']),16,'PROOF_MEASUREMENT_SUBJECT')
            require(instant(m['timestamp_utc'])<=issued,15,'PROOF_MEASUREMENT_TIME')
            require(m.get('collector_ref') is not None and m.get('raw_artifact_ref') is not None,15,'PROOF_PROVENANCE_REQUIRED')
            collector=self.store.get('collector_release',m['collector_ref'])
            require(collector.get('withdrawn') is False and collector.get('review_verdict')=='PASS'
                    and collector.get('build_digest')==m.get('collector_digest'),15,'PROOF_COLLECTOR_UNREVIEWED')
            # Exact raw artifact is independently pinned, not a hash echoed back
            # alongside an unchecked `actual` object.
            raw=self.store.get('measurement_artifact',m['raw_artifact_ref'])
            require(raw.get('measurement_actual_digest')==digest(m['actual'])
                    and raw.get('subject_digest')==m['subject_digest'] and raw.get('withdrawn') is False,
                    15,'PROOF_RAW_BINDING')
            checked.append({'ref':actual_ref,'actual':deepcopy(m['actual']),'source_kind':m['source_kind'],
                            'timestamp_utc':m['timestamp_utc']})
        claim=item.get('claim')
        require(type(claim) is dict and bool(claim),15,'PROOF_CLAIM_SCHEMA')
        # The root specifies exact pointers to facts. Coverage for every claim
        # prevents a single unrelated measurement from blessing arbitrary flags.
        mapping=item.get('claim_map')
        require(type(mapping) is dict and set(mapping)==set(claim),15,'PROOF_CLAIM_COVERAGE')
        for key,bound in mapping.items():
            require(type(bound) is dict and set(bound)=={'measurement_ref','actual_key'},15,'PROOF_CLAIM_MAP')
            rows=[m for m in checked if m['ref']==bound['measurement_ref']]
            require(len(rows)==1 and bound['actual_key'] in rows[0]['actual']
                    and rows[0]['actual'][bound['actual_key']]==claim[key],15,'PROOF_CLAIM_NOT_MEASURED')
        return {'ref':ref,'claim':deepcopy(claim),'measurements':checked,'issued_at':item['issued_at'],
                'scope':deepcopy(item['scope']),'owner_sid':item['owner_sid']}
