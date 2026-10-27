from pathlib import Path
import tempfile,subprocess,sys,json,hashlib
HERE=Path(__file__).resolve().parent
files=['intake.json','migration.json','input/knowledge.json','input/完整规则簇.md','input/regression-questions.json','input/new-questions.json','input/测试题.md','evaluator/regression-gold.json','evaluator/new-gold.json','evaluator/results-template.json','reports/issues.json','reports/question-production.json']
with tempfile.TemporaryDirectory(prefix='buddy-contract-rebuild-') as folder:
 target=Path(folder)
 for script in ['produce.py','prepare_questions.py']:
  subprocess.run([sys.executable,str(HERE/script),str(target)],check=True,capture_output=True,text=True)
 differences=[p for p in files if (HERE/p).read_bytes()!=(target/p).read_bytes()]
 assert not differences,differences
report={'status':'Passed','canonical_files_compared':len(files),'byte_identical':True,'source_fidelity_is_separately_checked':True,'model_or_consumer_calls':False}
(HERE/'reports/rebuild-check.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
