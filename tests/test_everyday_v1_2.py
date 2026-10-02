import unittest
from pathlib import Path
from everyday_v1_2.tasks import TASKS, CASES
from everyday_v1_2.grader import grade, equal

class EverydayTests(unittest.TestCase):
 def test_literal_cases_against_reference_implementations(self):
  for task in TASKS:
   with self.subTest(task=task['id']):
    result=grade(task['id'],Path('tests/fixtures/v1_2',task['id']+'.js').read_text())
    self.assertEqual(result['passed'],12,[c for c in result['cases'] if not c['passed']])
 def test_wrong_program_does_not_pass(self):
  self.assertEqual(grade('split-bill','function solve(){return null;}')['passed'],0)
 def test_no_host_capabilities(self):
  code='function solve(){return [typeof process,typeof require,typeof fetch,typeof std,typeof os];}'
  self.assertEqual(grade('split-bill',code)['cases'][0]['actual'],['undefined']*5)
 def test_infinite_loop_is_bounded(self):
  self.assertEqual(grade('split-bill','function solve(){while(true){}}')['passed'],0)
 def test_memory_is_bounded(self):
  result=grade('split-bill','function solve(){return new Array(100000000).fill("x")}')
  self.assertTrue(all('error' in c for c in result['cases']))
 def test_source_format_failure_is_unscored(self):
  with self.assertRaises(ValueError): grade('split-bill','')
 def test_booleans_are_not_numbers(self): self.assertFalse(equal(True,1))
 def test_object_order_does_not_matter(self): self.assertTrue(equal({'a':1,'b':2},{'b':2,'a':1}))
 def test_budget(self): self.assertEqual(sum(map(len,CASES.values())),36)

if __name__=='__main__': unittest.main()
