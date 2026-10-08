"""Integration tests for DNA clinical diagnostic models, inference, and explanations."""
import json
import unittest
import numpy as np
import pandas as pd
import joblib
from app import create_app
from modules import MODULES


class ModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = create_app().test_client()

    def test_module_list_and_assets(self):
        resp = self.client.get('/api/modules')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn('modules', data)
        mod_ids = [m['id'] for m in data['modules']]
        for expected in ['hcv', 'heart', 'diabetes', 'breast_cancer']:
            self.assertIn(expected, mod_ids)

        for mod_id in ['hcv', 'heart', 'diabetes', 'breast_cancer']:
            for asset in ['confusion_matrix.png', 'class_performance.png', 'feature_importance.png']:
                with self.client.get(f'/artifacts/{mod_id}/{asset}') as r:
                    self.assertEqual(r.status_code, 200, f"Failed for {mod_id}/{asset}")

    def test_all_modules_prediction_and_consistency(self):
        for mod_id, spec in MODULES.items():
            out = spec['artifact_dir']
            examples = json.loads((out / 'examples.json').read_text())
            self.assertGreater(len(examples), 0)

            # Test prediction on first example
            sample = examples[0]['features']
            resp = self.client.post(f'/api/{mod_id}/predict', json=sample)
            self.assertEqual(resp.status_code, 200, f"Prediction failed for {mod_id}: {resp.get_data(as_text=True)}")
            data = resp.get_json()
            self.assertIn('prediction', data)
            self.assertIn('score', data)
            self.assertAlmostEqual(sum(s['score'] for s in data['scores']), 1.0, places=4)

    def test_saved_predictions_sample(self):
        # Verify first 10 saved test predictions for each module
        for mod_id, spec in MODULES.items():
            out = spec['artifact_dir']
            df_preds = pd.read_csv(out / 'test_predictions.csv').head(10)
            for _, row in df_preds.iterrows():
                payload = {}
                for k in spec['features']:
                    val = row[k]
                    payload[k] = None if pd.isna(val) else val
                resp = self.client.post(f'/api/{mod_id}/predict', json=payload)
                self.assertEqual(resp.status_code, 200)
                data = resp.get_json()
                self.assertEqual(data['prediction'], spec['labels'][int(row['predicted'])])

    def test_validation_errors(self):
        # Empty body
        self.assertEqual(self.client.post('/api/hcv/predict', json={}).status_code, 400)
        # Unknown module
        self.assertEqual(self.client.post('/api/unknown/predict', json={}).status_code, 404)

        # Invalid categorical
        hcv_sample = json.loads((MODULES['hcv']['artifact_dir'] / 'examples.json').read_text())[0]['features']
        self.assertEqual(self.client.post('/api/hcv/predict', json=dict(hcv_sample, Sex='invalid')).status_code, 400)

        # Invalid numeric
        self.assertEqual(self.client.post('/api/hcv/predict', json=dict(hcv_sample, Age=-5)).status_code, 400)
        self.assertEqual(self.client.post('/api/hcv/predict', json=dict(hcv_sample, ALT='not_a_number')).status_code, 400)

    def test_no_data_leakage_across_all_modules(self):
        for mod_id, spec in MODULES.items():
            metrics = json.loads((spec['artifact_dir'] / 'metrics.json').read_text())
            tr = set(metrics['train_indices'])
            te = set(metrics['test_indices'])
            self.assertFalse(tr & te, f"Data leakage detected in {mod_id}!")
            self.assertEqual(len(tr | te), metrics['samples'])


if __name__ == '__main__':
    unittest.main()
