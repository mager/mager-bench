import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import bench_v1_2 as runner

spec=importlib.util.spec_from_file_location('export_v12','web/scripts/sync-everyday-data.py')
exporter=importlib.util.module_from_spec(spec)
spec.loader.exec_module(exporter)

class RunnerTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory()
  self.output=Path(self.temp.name)/'attempt.json'
 def tearDown(self): self.temp.cleanup()
 def answers(self):
  return [Path('tests/fixtures/v1_2',t['id']+'.js').read_text() for t in runner.TASKS]
 @patch('providers.has_key',return_value=True)
 @patch('providers.CodexCLIProvider')
 def test_complete_validates_and_tampering_is_rejected(self,provider,login):
  provider.return_value.complete.side_effect=self.answers()
  self.assertEqual(runner.run('codex-cli/test',self.output,'low',['low','high']),0)
  data=json.loads(self.output.read_text());exporter.validate(data)
  self.assertEqual(data['score'],{'passed':36,'total':36})
  data['tasks'][0]['score']['passed']=0
  with self.assertRaises(AssertionError): exporter.validate(data)
 @patch('providers.has_key',return_value=True)
 @patch('providers.CodexCLIProvider')
 def test_provider_failure_stops_and_preserves_partial(self,provider,login):
  provider.return_value.complete.side_effect=[self.answers()[0],RuntimeError('test provider failure')]
  self.assertEqual(runner.run('codex-cli/test',self.output,'low',['low']),1)
  data=json.loads(self.output.read_text());exporter.validate(data)
  self.assertIsNone(data['score']);self.assertEqual(data['tasks'][0]['score']['passed'],12)
  self.assertEqual(provider.return_value.complete.call_count,2)
 @patch('providers.has_key',return_value=True)
 @patch('providers.CodexCLIProvider')
 def test_interrupt_is_saved_unscored(self,provider,login):
  provider.return_value.complete.side_effect=KeyboardInterrupt
  self.assertEqual(runner.run('codex-cli/test',self.output,'low',['low']),1)
  data=json.loads(self.output.read_text());exporter.validate(data)
  self.assertIsNone(data['score']);self.assertEqual(data['tasks'][0]['status'],'interrupted')
 @patch('providers.has_key',return_value=True)
 @patch('providers.CodexCLIProvider')
 def test_existing_file_cannot_be_overwritten(self,provider,login):
  self.output.write_text('preserved')
  with self.assertRaises(FileExistsError): runner.run('codex-cli/test',self.output,'low',['low'])
  self.assertEqual(self.output.read_text(),'preserved');provider.assert_not_called()
 @patch('pathlib.Path.read_text')
 def test_effort_is_minimum_not_default(self,read):
  read.return_value=json.dumps({'models':[{'slug':'test','default_reasoning_level':'high','supported_reasoning_levels':[{'effort':'high'},{'effort':'low'},{'effort':'minimal'}]}]})
  self.assertEqual(runner.lowest_effort('codex-cli/test')[0],'minimal')
 @patch('pathlib.Path.read_text')
 def test_unknown_effort_is_rejected(self,read):
  read.return_value=json.dumps({'models':[{'slug':'test','supported_reasoning_levels':[{'effort':'turbo'}]}]})
  with self.assertRaises(ValueError): runner.lowest_effort('codex-cli/test')

if __name__=='__main__':unittest.main()
