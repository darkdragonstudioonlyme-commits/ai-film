import importlib.util,unittest
from pathlib import Path
TOOL=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('fx',TOOL/'v03-fixture-preparation-controller.py');fx=importlib.util.module_from_spec(spec);spec.loader.exec_module(fx)
CAT=TOOL.parents[1]/'test-governance/P00_V03_AUTHORITY_BINDING_PRODUCER_RECIPE_CATALOG_V1.json'
class FixtureTests(unittest.TestCase):
 def test_reviewed_population(self):
  c=fx.load_recipe_catalog(CAT);self.assertEqual(len(c['preparations']),78);self.assertEqual(c['counts']['native_cases'],85);self.assertEqual(c['counts']['native_requests'],133)
 def observations(self,c):
  out={}
  for r in c['preparations']:
   out[r['token']]={'before_digest':'a','after_digest':'b' if r['mode']=='ARRANGE' else 'a','actual':{'causal_effect_observed':True} if r['mode']=='ARRANGE' else {'observed_existing_condition':True}}
  return out
 def test_records_are_observation_only(self):
  c=fx.load_recipe_catalog(CAT);rows=fx.materialize_records(c,self.observations(c));self.assertEqual(len(rows),78);self.assertTrue(all(x['native_execution_started'] is False for x in rows))
 def test_arrange_without_effect_rejected(self):
  c=fx.load_recipe_catalog(CAT);obs=self.observations(c);r=next(x for x in c['preparations'] if x['mode']=='ARRANGE');obs[r['token']]['after_digest']='a'
  with self.assertRaises(Exception):fx.materialize_records(c,obs)
if __name__=='__main__':unittest.main()
