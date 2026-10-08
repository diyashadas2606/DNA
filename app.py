"""DNA Clinical Diagnostic Web Application with Multi-Investigation Support."""
import json
import math
import joblib
import numpy as np
import pandas as pd
from flask import Flask, jsonify, render_template, request, send_from_directory
from modules import MODULES, ROOT


def validate(body, spec, bundle):
    if not isinstance(body, dict):
        raise ValueError('Invalid JSON request payload.')

    expected = set(spec['features'])
    received = set(body.keys())
    if expected != received:
        missing_keys = expected - received
        extra_keys = received - expected
        msg = []
        if missing_keys:
            msg.append(f"Missing fields: {', '.join(sorted(missing_keys))}")
        if extra_keys:
            msg.append(f"Unexpected fields: {', '.join(sorted(extra_keys))}")
        raise ValueError("; ".join(msg))

    values = dict(body)

    # Validate categoricals
    field_map = {f['key']: f for f in spec['fields']}
    for key in spec.get('categorical', []):
        val = body[key]
        field_def = field_map.get(key, {})
        allowed_options = [opt['value'] for opt in field_def.get('options', [])]
        if allowed_options:
            if val not in allowed_options:
                # Try integer casting if applicable
                try:
                    int_val = int(val)
                    if int_val in allowed_options:
                        values[key] = int_val
                        continue
                except (ValueError, TypeError):
                    pass
                raise ValueError(f"{field_def.get('name', key)}: select a valid option.")
        else:
            if key == 'Sex' and val not in ('f', 'm'):
                raise ValueError('Recorded sex must be "f" or "m".')

    # Validate numerics
    for key in spec['numeric']:
        value = body[key]
        if value is None or (isinstance(value, float) and math.isnan(value)):
            if key in spec.get('labs', spec['numeric']):
                values[key] = np.nan
                continue
            raise ValueError(f"{key}: required field cannot be empty.")

        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0 or value > 1e9:
            raise ValueError(f"{key}: enter a finite non-negative number.")

        if key in ('Age', 'age') and (value < 1 or value > 120 or int(value) != value):
            raise ValueError('Age must be a whole number between 1 and 120.')

        values[key] = float(value)

    # Missing fields policy
    missing = [k for k in spec.get('labs', spec['numeric']) if pd.isna(values.get(k))]
    max_missing = spec.get('max_missing', 3)
    if len(missing) > max_missing:
        raise ValueError(
            f"Too many missing lab results ({len(missing)}). "
            f"At most {max_missing} missing values can be imputed for this test panel."
        )

    return values, missing


def create_app():
    app = Flask(__name__)
    app.config['MAX_CONTENT_LENGTH'] = 64 * 1024

    bundles = {}
    metrics_cache = {}
    examples_cache = {}

    for key, spec in MODULES.items():
        path = spec['artifact_dir'] / 'model.joblib'
        if not path.exists():
            raise RuntimeError(f"Missing model artifact for {key}. Run python train.py first.")
        bundles[key] = joblib.load(path)

        metrics_file = spec['artifact_dir'] / 'metrics.json'
        if metrics_file.exists():
            metrics_cache[key] = json.loads(metrics_file.read_text())

        examples_file = spec['artifact_dir'] / 'examples.json'
        if examples_file.exists():
            examples_cache[key] = json.loads(examples_file.read_text())

    @app.get('/')
    def home():
        default_mod = 'hcv'
        return render_template(
            'index.html',
            modules=MODULES,
            active_id=default_mod,
            active_spec=MODULES[default_mod],
            metrics=metrics_cache.get(default_mod, {}),
            examples=examples_cache.get(default_mod, [])
        )

    @app.get('/api/modules')
    def module_list():
        data = []
        for s in MODULES.values():
            mod_id = s['id']
            data.append({
                'id': mod_id,
                'test_name': s['test_name'],
                'short_name': s['short_name'],
                'tagline': s['tagline'],
                'icon': s['icon'],
                'organ': s['organ'],
                'clinical_focus': s['clinical_focus'],
                'target_label': s['target_label'],
                'labels': s['labels'],
                'features': s['features'],
                'numeric': s['numeric'],
                'categorical': s.get('categorical', []),
                'fields': s['fields'],
                'max_missing': s.get('max_missing', 3),
                'metrics': metrics_cache.get(mod_id, {}),
                'examples': examples_cache.get(mod_id, [])
            })
        return jsonify(modules=data)

    @app.get('/artifacts/<module_id>/<name>')
    def artifact(module_id, name):
        allowed_files = {
            'confusion_matrix.png', 'class_performance.png',
            'feature_importance.png', 'example_inputs.csv'
        }
        if module_id not in MODULES or name not in allowed_files:
            return jsonify(error='File not available'), 404
        return send_from_directory(MODULES[module_id]['artifact_dir'], name)

    @app.get('/report')
    def report():
        return send_from_directory(ROOT / 'report', 'DNA_HCV_Report.pdf')

    @app.post('/api/<module_id>/predict')
    def predict(module_id):
        if module_id not in MODULES:
            return jsonify(error='Unknown diagnostic test module'), 404

        spec = MODULES[module_id]
        bundle = bundles[module_id]

        try:
            values, missing = validate(request.get_json(silent=True), spec, bundle)
        except ValueError as error:
            return jsonify(error=str(error)), 400

        model = bundle['pipeline']
        frame = pd.DataFrame([values], columns=spec['features'])
        scores = model.predict_proba(frame)[0]

        winner = int(np.argmax(scores))
        class_id = int(model.classes_[winner])
        score = float(scores[winner])

        # Check for values outside training min/max bounds
        warnings = [
            k for k in spec['numeric']
            if pd.notna(values[k]) and not (bundle['minimum'][k] <= values[k] <= bundle['maximum'][k])
        ]

        # Local sensitivity probe
        variants = []
        keys = []
        for key in spec['numeric']:
            if key in missing:
                continue
            variant = dict(values)
            variant[key] = bundle['medians'][key]
            variants.append(variant)
            keys.append(key)

        effects = []
        if variants:
            var_frame = pd.DataFrame(variants, columns=spec['features'])
            replacements = model.predict_proba(var_frame)[:, winner]
            for k, p in zip(keys, replacements):
                effects.append({
                    'feature': k,
                    'effect_pp': float((score - p) * 100),
                    'reference': bundle['medians'][k]
                })
            effects.sort(key=lambda item: abs(item['effect_pp']), reverse=True)

        return jsonify(
            module=module_id,
            test_name=spec['test_name'],
            target_label=spec['target_label'],
            prediction=spec['labels'][class_id],
            score=score,
            scores=[{'label': spec['labels'][int(c)], 'score': float(p)} for c, p in zip(model.classes_, scores)],
            missing=missing,
            imputed_values={k: bundle['medians'][k] for k in missing},
            out_of_range=warnings,
            needs_review=bool(missing or warnings or score < 0.65),
            effects=effects[:5],
            explanation='Score change when one observed lab value is replaced with its training median. Measures local sensitivity, not causality.',
            note=f'Educational research classifier ({spec["short_name"]}). Scores are uncalibrated and should not be used as clinical diagnostic substitutes.'
        )

    return app


if __name__ == '__main__':
    create_app().run(host='127.0.0.1', port=5000, debug=False)
