// Compatibility probe only. No evaluator reads, scenario execution or Terminal writes.
import { readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { createHash } from 'node:crypto';
const here=fileURLToPath(new URL('.',import.meta.url));
const terminal='/Users/chenzehao/Projects/DND Terminal';
const entry=terminal+'/src/application/calculator-corpus.js';
const {loadCalculatorCorpus,CORPUS_API_REVISION}=await import(pathToFileURL(entry));
const corpus=JSON.parse(readFileSync(here+'input/knowledge.json','utf8'));
const result=loadCalculatorCorpus(corpus);
if(result.status!=='data_error'||!result.issues?.some(x=>x.code==='unsupported_corpus_environment'))throw new Error('Unexpected compatibility result; inspect before proceeding');
const report={kind:'read_only_old_consumer_compatibility_probe',input_format:corpus.format_revision,consumer_api:CORPUS_API_REVISION,
 consumer_source_sha256:createHash('sha256').update(readFileSync(entry)).digest('hex'),input_sha256:createHash('sha256').update(readFileSync(here+'input/knowledge.json')).digest('hex'),
 actual:result,interpretation:'Old consumer safely rejects the explicit new format. This is not a new 48-case run or a source-data correctness failure.',
 schema_adaptation_required:true,per_case_execution:'Not Run',consumer_acceptance:'Pending',terminal_modified:false};
writeFileSync(here+'reports/consumer-compatibility.json',JSON.stringify(report,null,2)+'\n');
process.stdout.write(JSON.stringify(report,null,2)+'\n');
