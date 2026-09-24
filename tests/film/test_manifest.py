import unittest
from film.manifest import make_manifest, validate_manifest

class ManifestTests(unittest.TestCase):
    def sample(self):
        return dict(
            asset_id="a1",kind="image",model="bench",model_version="v1",
            model_hash="sha256:abc",prompt="p",negative_prompt="n",seed=7,
            references=[],workflow_version="1",config={"aspect":"9:16"},
            worker="local",gpu="none",generation_time="2026-09-24T00:00:00Z",
            parent_assets=[]
        )

    def test_digest_is_deterministic(self):
        a=make_manifest(**self.sample())
        b=make_manifest(**self.sample())
        self.assertEqual(a["manifest_sha256"],b["manifest_sha256"])
        self.assertTrue(validate_manifest(a))

    def test_tamper_detected(self):
        a=make_manifest(**self.sample())
        a["prompt"]="changed"
        with self.assertRaises(ValueError):
            validate_manifest(a)

if __name__=="__main__":
    unittest.main()
