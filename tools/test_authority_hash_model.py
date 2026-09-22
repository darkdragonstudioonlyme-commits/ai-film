#!/usr/bin/env python3
"""No-execution design witness; not an authority materializer or native proof."""
import hashlib
import json
import unittest


def order(dependencies):
    pending={k:set(v) for k,v in dependencies.items()};done=[]
    while pending:
        ready=sorted(k for k,v in pending.items() if not v-set(done))
        if not ready:raise ValueError('CYCLIC_OR_UNRESOLVED_DEPENDENCY')
        for name in ready:done.append(name);del pending[name]
    return done


class ModelTests(unittest.TestCase):
    def test_literal_reviewed_self_partition_rejected(self):
        with self.assertRaises(ValueError):order({'slot':{'partition'},'suite':{'slot'},'partition':{'suite','slot'}})
    def test_corrected_detached_root_order(self):
        graph={'descriptor':set(),'template':{'descriptor'},'slot':{'descriptor','template'},'suite':{'slot'},'manifest':{'suite','slot','template','descriptor'}}
        seq=order(graph);self.assertEqual(seq[-1],'manifest')
        values={}
        for name in seq:
            raw=json.dumps({'kind':name,'refs':[values[x] for x in sorted(graph[name])]},sort_keys=True,separators=(',',':')).encode()
            values[name]=hashlib.sha256(raw).hexdigest()
        self.assertEqual(len(set(values.values())),5)
    def test_runtime_lineage_self_policy_rejected(self):
        with self.assertRaises(ValueError):order({'lineage':{'new_policy'},'new_policy':{'lineage'}})
    def test_runtime_parent_order(self):
        self.assertEqual(order({'old_policy':set(),'derived':{'old_policy'},'lineage':{'old_policy','derived'},'generation':{'lineage','old_policy'},'new_policy':{'generation','lineage','derived','old_policy'}})[-1],'new_policy')
    def test_unresolved_reference_rejected(self):
        with self.assertRaises(ValueError):order({'slot':{'MISSING'}})
    def test_copy_identity_not_path_identity(self):
        data=b'SYNTHETIC_CHECKPOINT_ONLY';source=r'C:\source\export.tar';dest=r'D:\isolated\staging.tar'
        self.assertNotEqual(source,dest);self.assertEqual(hashlib.sha256(data).digest(),hashlib.sha256(bytes(data)).digest())

if __name__=='__main__':unittest.main(verbosity=2)
