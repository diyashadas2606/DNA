"""DNA local application with independent disease model contracts."""
import json,math,joblib
import numpy as np
import pandas as pd
from flask import Flask,jsonify,render_template,request,send_from_directory
from modules import MODULES,ROOT

def validate(body,spec):
    if not isinstance(body,dict) or set(body)!=set(spec['features']): raise ValueError('Provide Age, Sex and exactly the ten named laboratory fields.')
    if body['Sex'] not in ('f','m'): raise ValueError('Choose the recorded sex category: f or m.')
    values=dict(body)
    for key in spec['numeric']:
        value=body[key]
        if value is None and key in spec['labs']: values[key]=np.nan;continue
        if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or value<0 or value>1e9: raise ValueError(f'{key}: enter a finite non-negative number (up to 1 billion).')
        if key=='Age' and (value<1 or value>120 or int(value)!=value): raise ValueError('Age must be a whole number from 1 to 120.')
    missing=[k for k in spec['labs'] if pd.isna(values[k])]
    if len(missing)>3: raise ValueError('Enter at least 7 of the 10 lab values. More than 3 missing results is outside this demo input policy.')
    return values,missing

def create_app():
    app=Flask(__name__);app.config['MAX_CONTENT_LENGTH']=64*1024
    bundles={}
    for key,spec in MODULES.items():
        path=spec['artifact_dir']/'model.joblib'
        if not path.exists(): raise RuntimeError('Run python train.py first.')
        bundles[key]=joblib.load(path) # Trusted project-generated files only.
    @app.get('/')
    def home():
        spec=MODULES['hcv']
        return render_template('index.html',spec=spec,metrics=json.loads((spec['artifact_dir']/'metrics.json').read_text()),examples=json.loads((spec['artifact_dir']/'examples.json').read_text()))
    @app.get('/api/modules')
    def module_list(): return jsonify(modules=[{'id':s['id'],'name':s['name'],'labels':s['labels']} for s in MODULES.values()])
    @app.get('/artifacts/<module_id>/<name>')
    def artifact(module_id,name):
        if module_id not in MODULES or name not in {'confusion_matrix.png','class_performance.png','feature_importance.png','example_inputs.csv'}: return jsonify(error='File not available'),404
        return send_from_directory(MODULES[module_id]['artifact_dir'],name)
    @app.get('/report')
    def report(): return send_from_directory(ROOT/'report','DNA_HCV_Report.pdf')
    @app.post('/api/<module_id>/predict')
    def predict(module_id):
        if module_id not in MODULES: return jsonify(error='Unknown disease module'),404
        spec=MODULES[module_id];bundle=bundles[module_id]
        try: values,missing=validate(request.get_json(silent=True),spec)
        except ValueError as error: return jsonify(error=str(error)),400
        model=bundle['pipeline'];frame=pd.DataFrame([values],columns=spec['features']);scores=model.predict_proba(frame)[0]
        winner=int(np.argmax(scores));class_id=int(model.classes_[winner]);score=float(scores[winner])
        warnings=[k for k in spec['numeric'] if pd.notna(values[k]) and not bundle['minimum'][k]<=values[k]<=bundle['maximum'][k]]
        variants=[];keys=[]
        for key in spec['labs']:
            if key in missing: continue
            variant=dict(values);variant[key]=bundle['medians'][key];variants.append(variant);keys.append(key)
        replacements=model.predict_proba(pd.DataFrame(variants,columns=spec['features']))[:,winner]
        effects=[{'feature':k,'effect_pp':float((score-p)*100),'reference':bundle['medians'][k]} for k,p in zip(keys,replacements)]
        effects.sort(key=lambda item:abs(item['effect_pp']),reverse=True)
        return jsonify(module=module_id,prediction=spec['labels'][class_id],score=score,scores=[{'label':spec['labels'][int(c)],'score':float(p)} for c,p in zip(model.classes_,scores)],missing=missing,imputed_values={k:bundle['medians'][k] for k in missing},out_of_range=warnings,needs_review=bool(missing or warnings or score<.65),effects=effects[:5],explanation='Score change when one observed lab value is replaced with its training median. Not a causal explanation or medical threshold.',note='Educational dataset classification. Scores are uncalibrated; donor labels do not establish absence of disease.')
    return app
if __name__=='__main__': create_app().run(host='127.0.0.1',port=5000,debug=False)
