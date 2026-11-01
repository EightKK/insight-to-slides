import json,sys,copy,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'scripts'))
from evaluate_decision_quality import evaluate
D=json.loads((R/'tests'/'fixtures'/'sandvik-2026-q3-argumentation.json').read_text(encoding='utf-8'))
class ContractTests(unittest.TestCase):
    def test_good_contract(self):self.assertEqual(evaluate(D)['status'],'PASS')
    def test_no_governing_answer(self):
        x=copy.deepcopy(D);x['questions'][0]['governing']=False
        self.assertIn('GOVERNING_NOT_COVERED',[z['code'] for z in evaluate(x)['errors']])
    def test_causal_overclaim(self):
        x=copy.deepcopy(D);x['claims'][0]['causal_basis']='hypothesis'
        self.assertIn('CAUSAL_OVERCLAIM',[z['code'] for z in evaluate(x)['errors']])
    def test_unknown_evidence(self):
        x=copy.deepcopy(D);x['claims'][0]['evidence_ids']=['MISSING']
        self.assertIn('UNKNOWN_EVIDENCE',[z['code'] for z in evaluate(x)['errors']])
    def test_false_choice(self):
        x=copy.deepcopy(D);x['decision']['options'][1]['tradeoff']=''
        self.assertIn('SCHEMA',[z['code'] for z in evaluate(x)['errors']])
        x['decision']['options'][1]['tradeoff']='TBD 後で検討する'
        self.assertIn('HOLLOW_OPTION',[z['code'] for z in evaluate(x)['errors']])
    def test_no_falsifier(self):
        x=copy.deepcopy(D);x['hypotheses'][0]['falsifier']=''
        self.assertIn('SCHEMA',[z['code'] for z in evaluate(x)['errors']])
        x['hypotheses'][0]['falsifier']='TODO: define falsifier'
        self.assertIn('PLACEHOLDER_TEXT',[z['code'] for z in evaluate(x)['errors']])
    def test_missing_key_message(self):
        x=copy.deepcopy(D);x['slides']=[s for s in x['slides'] if s['id']!='S11']
        self.assertIn('KEY_CLAIM_NOT_SHOWN',[z['code'] for z in evaluate(x)['errors']])
    def codes(self,x):return [z['code'] for z in evaluate(x)['errors']]
    def test_all_examples_pass(self):
        for f in ['../tests/fixtures/asml-2026-q3-argumentation.json','../tests/fixtures/factory-monthly-argumentation-basic.json','../tests/fixtures/sandvik-2026-q3-argumentation.json','factory-monthly-synthetic/contracts/argumentation-contract.json']:
            r=evaluate(json.loads((R/'examples'/f).read_text(encoding='utf-8')))
            self.assertEqual(r['status'],'PASS',(f,r['errors']))
    def test_duplicate_hypothesis_ids(self):
        x=copy.deepcopy(D);x['hypotheses'][1]['id']=x['hypotheses'][0]['id']
        self.assertIn('DUPLICATE_HYPOTHESIS',self.codes(x))
    def test_support_counter_overlap(self):
        x=copy.deepcopy(D);h=x['hypotheses'][0];h['counter_evidence_ids']=h['counter_evidence_ids']+[h['supporting_evidence_ids'][0]]
        self.assertIn('SUPPORT_COUNTER_OVERLAP',self.codes(x))
    def test_duplicate_option_names(self):
        x=copy.deepcopy(D);x['decision']['options'][1]['name']=x['decision']['options'][0]['name'].upper()
        self.assertIn('DUPLICATE_OPTION',self.codes(x))
    def test_schema_minlength(self):
        x=copy.deepcopy(D);x['evidence'][0]['summary']=''
        self.assertIn('SCHEMA',self.codes(x))
    def test_malformed_input_reports_not_crashes(self):
        x=copy.deepcopy(D);x['questions']=['q']
        self.assertIn('SCHEMA',self.codes(x))
    def test_coherent_but_empty_contract_fails(self):
        filler='TBD - to be decided later'
        x={'schema_version':'1.0.0','audience':'Plant management','governing_question':'TBD governing question here',
           'current_answer':'TBD; answer will follow after review',
           'evidence':[{'id':'e1','source':'n/a','summary':'TODO add summary'},{'id':'e2','source':'xxx','summary':'TODO add summary'}],
           'claims':[{'id':'c1','text':filler,'kind':'fact','evidence_ids':['e1'],'causal_basis':'not_causal','prominence':'key'},
                     {'id':'c2','text':filler,'kind':'interpretation','evidence_ids':['e2'],'causal_basis':'not_causal'}],
           'questions':[{'id':'q1','text':'Main question','status':'answered','answer':filler,'supporting_claim_ids':['c1'],'governing':True}],
           'hypotheses':[{'id':'h1','text':filler,'supporting_evidence_ids':['e1'],'counter_evidence_ids':['e1'],'falsifier':filler,'confidence':'high'},
                         {'id':'h1','text':filler,'supporting_evidence_ids':['e1'],'counter_evidence_ids':['e1'],'falsifier':filler,'confidence':'high'}],
           'decision':{'question':'TBD decision question','working_assessment':filler,
                       'options':[{'name':'Option','merit':filler,'tradeoff':filler},{'name':'option','merit':filler,'tradeoff':filler}],
                       'reversal_conditions':[filler]},
           'slides':[{'id':'s1','claim_ids':['c1'],'purpose':'main'}]}
        r=evaluate(x)
        self.assertEqual(r['status'],'FAIL')
        got=set(self.codes(x))
        for code in ('PLACEHOLDER_TEXT','DUPLICATE_HYPOTHESIS','SUPPORT_COUNTER_OVERLAP','DUPLICATE_OPTION','HOLLOW_OPTION','NO_REVERSAL_CONDITION','DUPLICATE_HYPOTHESIS_TEXT'):
            self.assertIn(code,got)
if __name__=='__main__':unittest.main()
