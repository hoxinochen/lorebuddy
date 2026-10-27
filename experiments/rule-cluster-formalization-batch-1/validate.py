"""Validate the formalization preparation without granting authority."""
from pathlib import Path
import argparse
import copy
import importlib.util
import json
import tempfile
from collections import Counter
from jsonschema import Draft202012Validator
from build import HERE, ROOT, PREVIOUS, build, load, sha, encoded

SUBJECT_SCHEMA = {
 '$schema': 'https://json-schema.org/draft/2020-12/schema', '$id': 'm2.rule-review-subject@0.1.0',
 'type': 'object', 'additionalProperties': False,
 'required': ['schema','id','subject_kind','title','language','module','rules_context_id','review_status','body','source_binding','full_fidelity','candidate_snapshot','review_record_id','dependency_ids','uncompiled_semantics_retained'],
 'properties': {
  'schema': {'const':'m2.rule-review-subject@0.1.0'}, 'id':{'$ref':'#/$defs/id'},
  'subject_kind':{'enum':['creature','ability','spell','shared_reference']},
  'title':{'type':'string','minLength':1}, 'language':{'const':'zh-Hans'},
  'module':{'enum':['creatures','spells','common']}, 'rules_context_id':{'$ref':'#/$defs/id'},
  'review_status':{'const':'in_review'}, 'full_fidelity':{'const':'not_claimed'},
  'candidate_snapshot':{'type':'object'}, 'review_record_id':{'$ref':'#/$defs/id'},
  'dependency_ids':{'type':'array','uniqueItems':True,'items':{'$ref':'#/$defs/id'}},
  'uncompiled_semantics_retained':{'const':True},
  'body':{'type':'object','additionalProperties':False,'required':['path','digest','encoding'],
          'properties':{'path':{'type':'string','minLength':1},'digest':{'$ref':'#/$defs/digest'},'encoding':{'const':'utf-8'}}},
  'source_binding':{'type':'object','additionalProperties':False,
     'required':['entry_id','artifact_id','fragment_id','mapping_id','derived_evidence_id','derived_note_utf8_range'],
     'properties':{**{k:{'$ref':'#/$defs/id'} for k in ['entry_id','artifact_id','fragment_id','mapping_id']},
       'derived_evidence_id':{'oneOf':[{'$ref':'#/$defs/id'},{'type':'null'}]},
       'derived_note_utf8_range':{'type':'object','additionalProperties':False,'required':['start','end'],
           'properties':{'start':{'type':'integer','minimum':0},'end':{'type':'integer','minimum':1}}}}}},
 '$defs':{'id':{'type':'string','pattern':'^urn:uuid:[0-9a-f-]{36}$'},'digest':{'type':'string','pattern':'^sha256:[0-9a-f]{64}$'}}}

REVIEW_SCHEMA = {
 '$schema':'https://json-schema.org/draft/2020-12/schema','$id':'m2.rule-review-record@0.1.0',
 'type':'object','additionalProperties':False,
 'required':['schema','id','subject_id','subject_digest','status','ai_precheck','human_decision','reviewer','checks','source_fidelity_gate'],
 'properties':{'schema':{'const':'m2.rule-review-record@0.1.0'},
               **{k:{'$ref':'#/$defs/id'} for k in ['id','subject_id']},
               'subject_digest':{'$ref':'#/$defs/digest'},'status':{'const':'awaiting_review'},
               'ai_precheck':{'type':'string','minLength':1},'human_decision':{'type':'null'},'reviewer':{'type':'null'},
               'checks':{'type':'array','minItems':4,'uniqueItems':True,'items':{'type':'string'}},
               'source_fidelity_gate':{'const':'pending_normative_raw_to_library_coverage'}},
 '$defs':SUBJECT_SCHEMA['$defs']}


CLAIM_SCHEMA = {
 '$schema':'https://json-schema.org/draft/2020-12/schema','$id':'m2.publication-claim@0.1.0',
 'type':'object','additionalProperties':False,
 'required':['schema','id','kind','title_claim','identity_status','basis','review_status','rights'],
 'properties':{'schema':{'const':'m2.publication-claim@0.1.0'}, 'id':{'$ref':'#/$defs/id'},
               'kind':{'enum':['work','edition']}, 'title_claim':{'type':'string','minLength':1},
               'identity_status':{'const':'claimed'}, 'basis':{'type':'string','minLength':1},
               'review_status':{'const':'in_review'}, 'rights':{'const':'unknown'},
               'work_id':{'$ref':'#/$defs/id'}, 'language':{'const':'zh-Hans'},
               'translation_authority':{'const':'unknown'}},
 'allOf':[{'if':{'properties':{'kind':{'const':'edition'}}},'then':{'required':['work_id','language','translation_authority']}}],
 '$defs':SUBJECT_SCHEMA['$defs']}
EVIDENCE_SCHEMA = {
 '$schema':'https://json-schema.org/draft/2020-12/schema','$id':'m2.derived-text-evidence@0.1.0',
 'type':'object','additionalProperties':False,
 'required':['schema','id','original_record','raw_fragment_id','derived_artifact_path','derived_artifact_digest','coordinate_basis','raw_to_derived_fidelity'],
 'properties':{'schema':{'const':'m2.derived-text-evidence@0.1.0'}, 'id':{'$ref':'#/$defs/id'},
               'original_record':{'type':'object'}, 'raw_fragment_id':{'$ref':'#/$defs/id'},
               'derived_artifact_path':{'type':'string'},'derived_artifact_digest':{'$ref':'#/$defs/digest'},
               'coordinate_basis':{'const':'derived_note_utf8_not_raw_entry'},
               'raw_to_derived_fidelity':{'const':'not_proven_by_this_record'}},
 '$defs':SUBJECT_SCHEMA['$defs']}


def check(bundle, *, records=None):
 manifest = load(bundle/'intake.json')
 actual_files = {str(p.relative_to(bundle)) for p in bundle.rglob('*') if p.is_file()}
 assert actual_files == set(manifest['file_digests']) | {'intake.json'}, 'bundle file closure'
 for p, digest in manifest['file_digests'].items():
  assert sha((bundle/p).read_bytes()) == digest, 'bundle file digest: '+p
 spec = importlib.util.spec_from_file_location('accepted_corpus_validation', PREVIOUS/'validate.py')
 previous = importlib.util.module_from_spec(spec); spec.loader.exec_module(previous)
 corpus = load(PREVIOUS/'input/knowledge.json')
 previous.validate_corpus(corpus)  # All 45 abilities/254 extractions/calls, not question-selected facts.
 assert manifest['toolchain']['generator_digest']==sha((HERE/'build.py').read_bytes()), 'generator lock'
 assert manifest['toolchain']['validator_digest']==sha(Path(__file__).read_bytes()), 'validator lock'
 for relative,digest in manifest['toolchain']['normative_inputs'].items():
  assert sha((ROOT/relative).read_bytes())==digest, 'normative lock'
 assert manifest['input_digest'] == sha((PREVIOUS/'input/knowledge.json').read_bytes()), 'input identity'
 assert manifest['p6_decision_digest'] == sha((PREVIOUS/'reports/batch-acceptance.json').read_bytes()), 'P6 identity'
 recs = {p:load(bundle/p) for p in manifest['file_digests'] if p.endswith('.json')}
 if records is not None: recs = records
 subjects = [r for p,r in recs.items() if p.startswith('metadata/review-subjects/')]
 assert Counter(s['subject_kind'] for s in subjects) == {'creature':8,'ability':45,'spell':11,'shared_reference':6}, 'complete subjects'
 original = {o['id']:o for c in corpus['cards'] for o in [c]+c['abilities']}
 original.update({o['id']:o for o in corpus['spells']+corpus['shared_rules']})
 assert len({s['id'] for s in subjects}) == 70 and {s['id'] for s in subjects} == set(original), 'subject identity closure'
 all_records = {r['id']:r for r in recs.values() if isinstance(r,dict) and 'id' in r}
 queue = recs['metadata/review-queue.json']
 assert len(queue)==70 and {r['subject_id'] for r in queue} == set(original), 'review queue closure'
 lock = recs['metadata/evidence/source-lock.json']
 assert load(Path(lock['artifact_record_path']))==lock['artifact_record'], 'artifact record identity'
 assert sha(Path(lock['preserved_container_path']).read_bytes())==lock['artifact_record']['digest'], 'artifact container bytes'
 assert sha(Path(lock['inventory_path']).read_bytes()) == lock['inventory_sha256'], 'full inventory lock'
 entry_by_id={e['entry_id']:e for e in lock['selected_entries']}
 inventory={r['id']:r for r in map(json.loads,Path(lock['inventory_path']).read_text().splitlines())}
 for entry in entry_by_id.values():
  assert entry['inventory_record']==inventory[entry['entry_id']], 'inventory record identity'
 for entry in entry_by_id.values():
  raw=Path(entry['raw_path']).read_bytes()
  assert sha(raw) == entry['inventory_record']['digest'], 'raw source bytes'
  assert sha(Path(entry['note_path']).read_bytes()) == entry['note_sha256'], 'derived source bytes'
  for typ, name in [('fragments','fragment.schema.json'),('source-mappings','source-mapping.schema.json'),('boundaries','boundary-record.schema.json')]:
   for p,r in recs.items():
    if p.startswith('metadata/'+typ+'/'):
     Draft202012Validator(load(ROOT/'schemas'/name)).validate(r)
  frag, mapping=all_records[entry['fragment_id']],all_records[entry['source_mapping_id']]
  assert frag['entry_id']==mapping['source']['id']==entry['entry_id'], 'source chain'
  assert frag['locator']=={'kind':'byte-range','start':0,'end':len(raw),'parser':'raw-bytes-no-parser@1'}, 'raw coordinate'
  assert frag['fragment_digest']==frag['entry_digest']==sha(raw), 'raw fragment bytes'
  assert mapping['mapping_status']=='claimed' and mapping['review_status']=='pending', 'source identity promotion'
  for target in ['work_id','edition_id']:
   claim=all_records[mapping['target'][target]]
   Draft202012Validator(CLAIM_SCHEMA).validate(claim)
   assert claim['identity_status']=='claimed' and claim['rights']=='unknown', 'publication authority'
  assert all_records[mapping['target']['edition_id']]['work_id']==mapping['target']['work_id'], 'edition work chain'
 original_evidence={e['id']:e for e in corpus['evidence']}
 staged_evidence=[r for p,r in recs.items() if p.startswith('metadata/evidence/records/')]
 assert len(staged_evidence)==94 and {r['id'] for r in staged_evidence}==set(original_evidence), 'evidence closure'
 for record in staged_evidence:
  Draft202012Validator(EVIDENCE_SCHEMA).validate(record)
  assert record['original_record']==original_evidence[record['id']], 'evidence identity'
  sid=record['original_record']['source_entry_id']
  assert record['raw_fragment_id']==entry_by_id[sid]['fragment_id'], 'evidence fragment'
 for s in subjects:
  Draft202012Validator(SUBJECT_SCHEMA).validate(s)
  assert s['candidate_snapshot']==original[s['id']], 'candidate fact drift'
  assert s['rules_context_id']==corpus['rules_context']['id'], 'rules context'
  binding=s['source_binding'];entry=entry_by_id[binding['entry_id']]
  assert binding['fragment_id']==entry['fragment_id'] and binding['mapping_id']==entry['source_mapping_id'], 'source binding'
  body_path=(bundle/s['body']['path']).resolve()
  assert body_path.is_relative_to(bundle.resolve()), 'body path escape'
  body=body_path.read_bytes();span=binding['derived_note_utf8_range']
  expected_body=original[s['id']].get('verbatim_text') if s['subject_kind']!='shared_reference' else original[s['id']]['content']['text']
  assert body==expected_body.encode(), 'body versus approved-input candidate'
  assert span['end']>span['start'] and Path(entry['note_path']).read_bytes()[span['start']:span['end']]==body, 'derived range'
  assert sha(body)==s['body']['digest'], 'body digest'
  review=all_records[s['review_record_id']]
  Draft202012Validator(REVIEW_SCHEMA).validate(review)
  assert review['subject_id']==s['id'] and review['subject_digest']==sha(encoded(s)), 'review identity'
  assert set(s['dependency_ids']) <= set(all_records) | set(original) | {corpus['rules_context']['id']}, 'dependency closure'
  if s['subject_kind']=='ability':
   owner=original[s['candidate_snapshot']['owner_id']]
   assert any(a['id']==s['id'] for a in owner['abilities']), 'ability owner'
 plan=recs['metadata/package-plan.json']; by_name={p['name']:p for p in plan['packages']}
 def visit(name, path=()):
  assert name not in path, 'package dependency cycle'
  for dep in by_name[name]['content_dependencies']+by_name[name]['build_dependencies']:
   assert dep in by_name, 'missing package'
   visit(dep,path+(name,))
 for name in by_name:visit(name)
 assert plan['rights']=='unknown' and plan['status']=='proposed_for_review', 'package promotion'
 issues=recs['metadata/issues/open.json']
 assert {i['code'] for i in issues}=={'HUMAN_RULE_REVIEW_PENDING','CLAIMED_MAPPING_REVIEW_PENDING','NORMATIVE_FIDELITY_COVERAGE_NOT_IMPLEMENTED','PACKAGE_PLAN_PENDING'}, 'missing approval blockers'
 return recs


def run(bundle):
 for name,schema in [('review-subject.schema.json',SUBJECT_SCHEMA),('review-record.schema.json',REVIEW_SCHEMA),
                     ('publication-claim.schema.json',CLAIM_SCHEMA),('derived-text-evidence.schema.json',EVIDENCE_SCHEMA)]:
  Draft202012Validator.check_schema(schema)
  p=HERE/'schemas'/name;p.parent.mkdir(exist_ok=True);p.write_bytes(encoded(schema))
 records=check(bundle)
 faults=[]
 def mutate_subject(data, **kw):
  subject=next(r for p,r in data.items() if p.startswith('metadata/review-subjects/'))
  subject.update(kw)
  next(r for p,r in data.items() if p.startswith('metadata/reviews/') and r['subject_id']==subject['id'])['subject_digest']=sha(encoded(subject))
 mutations=[
  ('missing_untested_subject',lambda d:d.pop(next(p for p in d if p.startswith('metadata/review-subjects/')))),
  ('fake_approval',lambda d:mutate_subject(d,review_status='approved')),
  ('fake_full_fidelity',lambda d:mutate_subject(d,full_fidelity='full')),
  ('source_identity_upgrade',lambda d:next(r for p,r in d.items() if p.startswith('metadata/source-mappings/')).update(mapping_status='verified')),
  ('publication_rights_upgrade',lambda d:next(r for p,r in d.items() if p.startswith('sources/catalog/')).update(rights='allowed')),
  ('unknown_dependency',lambda d:mutate_subject(d,dependency_ids=['urn:uuid:00000000-0000-5000-8000-000000000001'])),
  ('raw_and_derived_coordinate_confusion',lambda d:next(r for p,r in d.items() if p.startswith('metadata/fragments/'))['locator'].update(end=1)),
  ('missing_fidelity_blocker',lambda d:d['metadata/issues/open.json'].pop(2)),
  ('package_cycle',lambda d:d['metadata/package-plan.json']['packages'][0]['content_dependencies'].append('creatures'))]
 for name,mutate in mutations:
  data=copy.deepcopy(records);mutate(data)
  try:check(bundle,records=data)
  except Exception as exc:faults.append({'fault':name,'blocked':True,'by':str(exc).splitlines()[0][:120]})
  else:raise AssertionError('Fault escaped: '+name)
 with tempfile.TemporaryDirectory() as tmp:
  rebuilt=Path(tmp)/'rebuilt';build(rebuilt)
  left={str(p.relative_to(bundle)):p.read_bytes() for p in bundle.rglob('*') if p.is_file()}
  right={str(p.relative_to(rebuilt)):p.read_bytes() for p in rebuilt.rglob('*') if p.is_file()}
  assert left==right,'non-deterministic rebuild'
 report={'schema':'m2.formalization-preparation-validation@0.1.0','status':'passed_with_explicit_formal_approval_blockers',
         'counts':load(bundle/'intake.json')['counts'],'bundle_files':len(left),
         'all_candidate_facts_preserved':True,'raw_and_derived_coordinate_separated':True,
         'deterministic_rebuild':True,'faults':faults,'formal_approved_subjects':0,
         'full_fidelity':'not_run_not_claimed','source_mapping_review':'pending','human_rule_review':'pending',
         'terminal_changes':False,'new_llm_calls':False}
 path=HERE/'reports/validation.json';path.parent.mkdir(exist_ok=True);path.write_bytes(encoded(report))
 print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--bundle',type=Path,default=HERE/'review-bundle')
 run(parser.parse_args().bundle)
