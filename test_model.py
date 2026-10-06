"""Integration tests for DNA HCV data, inference, and explanations."""
import json,unittest
import numpy as np
import pandas as pd
import joblib
from app import create_app
from modules import MODULES

class ModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client=create_app().test_client();cls.spec=MODULES['hcv'];cls.out=cls.spec['artifact_dir']
        cls.sample=json.loads((cls.out/'examples.json').read_text())[0]['features']
    def post(self,data): return self.client.post('/api/hcv/predict',json=data)
    def test_page_assets_and_routes(self):
        for url in ['/','/static/style.css','/static/app.js','/api/modules','/artifacts/hcv/confusion_matrix.png']:
            with self.client.get(url) as response: self.assertEqual(response.status_code,200)
        self.assertEqual(self.client.get('/artifacts/hcv/model.joblib').status_code,404)
        self.assertEqual(self.client.post('/api/unknown/predict',json=self.sample).status_code,404)
    def test_all_saved_predictions(self):
        for _,row in pd.read_csv(self.out/'test_predictions.csv').iterrows():
            payload={k:None if pd.isna(row[k]) else row[k] for k in self.spec['features']}
            response=self.post(payload);self.assertEqual(response.status_code,200);data=response.get_json()
            self.assertEqual(data['prediction'],self.spec['labels'][int(row.predicted)])
            self.assertAlmostEqual(sum(s['score'] for s in data['scores']),1)
            for i,s in enumerate(data['scores']): self.assertAlmostEqual(s['score'],row['score_'+str(i)])
    def test_validation(self):
        for key,value in [('Age',None),('Age',True),('Age',121),('Age',30.5),('Sex','x'),('ALT',-1),('ALT','20'),('ALT',float('nan')),('ALT',float('inf')),('ALT',1e10)]:
            self.assertEqual(self.post(dict(self.sample,**{key:value})).status_code,400,(key,value))
        for payload in [{},[],dict(self.sample,extra=1)]: self.assertEqual(self.post(payload).status_code,400)
    def test_missing_data(self):
        payload=dict(self.sample,ALB=None,ALP=None,ALT=None)
        result=self.post(payload);self.assertEqual(result.status_code,200)
        self.assertEqual(set(result.get_json()['missing']),{'ALB','ALP','ALT'})
        self.assertTrue(result.get_json()['needs_review'])
        payload['AST']=None;self.assertEqual(self.post(payload).status_code,400)
    def test_sensitivity_matches_direct_inference(self):
        bundle=joblib.load(self.out/'model.joblib');model=bundle['pipeline']
        data=self.post(self.sample).get_json();winner=self.spec['labels'].index(data['prediction'])
        for effect in data['effects']:
            changed=dict(self.sample);changed[effect['feature']]=effect['reference']
            frame=pd.DataFrame([changed],columns=self.spec['features']).replace({None:np.nan})
            score=model.predict_proba(frame)[0,winner]
            self.assertAlmostEqual(effect['effect_pp'],100*(data['score']-score))
        self.assertIn('ALT',self.post(dict(self.sample,ALT=100000)).get_json()['out_of_range'])
    def test_no_leakage_and_metrics(self):
        m=json.loads((self.out/'metrics.json').read_text());tr=set(m['train_indices']);te=set(m['test_indices'])
        self.assertFalse(tr&te);self.assertEqual(len(tr|te),615)
        raw=pd.read_csv(self.spec['data_path'],index_col=0)
        bundle=joblib.load(self.out/'model.joblib')
        for key,value in bundle['medians'].items(): self.assertAlmostEqual(value,raw.loc[list(tr),key].median())
        cm=np.array(m['confusion_matrix']);self.assertEqual(cm.sum(),123)
        self.assertAlmostEqual(np.trace(cm)/cm.sum(),m['accuracy'])
if __name__=='__main__': unittest.main()
