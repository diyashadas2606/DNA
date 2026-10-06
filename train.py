"""Train DNA HCV with preprocessing fitted independently inside each fold."""
import hashlib,json,joblib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sklearn
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score,balanced_accuracy_score,classification_report,confusion_matrix,ConfusionMatrixDisplay,f1_score
from sklearn.model_selection import StratifiedKFold,cross_validate,train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from modules import MODULES,RAW_LABELS,LABELS

def train():
    spec=MODULES['hcv']; out=spec['artifact_dir']; out.mkdir(parents=True,exist_ok=True)
    raw=pd.read_csv(spec['data_path'],index_col=0)
    if set(raw.Category.unique()) != set(RAW_LABELS): raise ValueError('Unexpected labels')
    X=raw[spec['features']].copy(); y=raw.Category.map(dict(zip(RAW_LABELS,range(5))))
    Xtr,Xte,ytr,yte=train_test_split(X,y,test_size=.2,stratify=y,random_state=42)
    if len(Xtr.fillna(-999).merge(Xte.fillna(-999),on=spec['features'])): raise ValueError('Cross-partition duplicate rows; use group splitting')
    prep=ColumnTransformer([('numeric',SimpleImputer(strategy='median'),spec['numeric']),('sex',OneHotEncoder(handle_unknown='error',sparse_output=False),['Sex'])])
    rf=RandomForestClassifier(n_estimators=400,min_samples_leaf=2,class_weight='balanced_subsample',max_features='sqrt',random_state=42,n_jobs=1)
    model=Pipeline([('preprocess',prep),('forest',rf)])
    cv=cross_validate(model,Xtr,ytr,cv=StratifiedKFold(5,shuffle=True,random_state=42),scoring=['accuracy','balanced_accuracy','f1_macro'],error_score='raise')
    model.fit(Xtr,ytr); pred=model.predict(Xte); scores=model.predict_proba(Xte)
    base=DummyClassifier(strategy='most_frequent').fit(Xtr,ytr).predict(Xte)
    report=classification_report(yte,pred,labels=list(range(5)),target_names=LABELS,output_dict=True,zero_division=0)
    cm=confusion_matrix(yte,pred,labels=list(range(5)))
    metrics={'module':'hcv','samples':len(X),'features':X.shape[1],'train_samples':len(Xtr),'test_samples':len(Xte),'labels':LABELS,'class_counts':{LABELS[i]:int((y==i).sum()) for i in range(5)},'missing_counts':X.isna().sum().to_dict(),'accuracy':accuracy_score(yte,pred),'balanced_accuracy':balanced_accuracy_score(yte,pred),'macro_f1':f1_score(yte,pred,average='macro'),'baseline_accuracy':accuracy_score(yte,base),'baseline_macro_f1':f1_score(yte,base,average='macro'),'classification_report':report,'confusion_matrix':cm.tolist(),'cv':{k[5:]:{'mean':float(v.mean()),'std':float(v.std()),'folds':v.tolist()} for k,v in cv.items() if k.startswith('test_')},'train_indices':Xtr.index.tolist(),'test_indices':Xte.index.tolist(),'sklearn_version':sklearn.__version__,'parameters':rf.get_params(),'sha256':hashlib.sha256(spec['data_path'].read_bytes()).hexdigest(),'source':spec['source'],'seed':42}
    (out/'metrics.json').write_text(json.dumps(metrics,indent=2))
    joblib.dump({'pipeline':model,'module':'hcv','features':spec['features'],'medians':Xtr[spec['numeric']].median().to_dict(),'minimum':Xtr[spec['numeric']].min().to_dict(),'maximum':Xtr[spec['numeric']].max().to_dict()},out/'model.joblib')
    evaluation=Xte.assign(actual=yte,predicted=pred)
    for i in range(5): evaluation['score_'+str(i)]=scores[:,i]
    evaluation.to_csv(out/'test_predictions.csv',index_label='sample_id')
    examples=[]
    for i in range(5):
        idx=yte[yte==i].index[0]
        values={k:None if pd.isna(v) else v for k,v in Xte.loc[idx].to_dict().items()}
        examples.append({'sample_id':int(idx),'features':values})
    (out/'examples.json').write_text(json.dumps(examples,indent=2))
    Xte.loc[[s['sample_id'] for s in examples]].to_csv(out/'example_inputs.csv',index=False)
    plt.rcParams.update({'font.family':'DejaVu Sans','axes.spines.top':False,'axes.spines.right':False})
    short=['Donor','Suspected donor','Hepatitis','Fibrosis','Cirrhosis']
    fig,ax=plt.subplots(figsize=(8,6));ConfusionMatrixDisplay(cm,display_labels=short).plot(ax=ax,colorbar=False,cmap='Blues',xticks_rotation=20)
    ax.set_title('HCV held-out test set | 123 records',pad=15);fig.tight_layout();fig.savefig(out/'confusion_matrix.png',dpi=180);plt.close(fig)
    fig,ax=plt.subplots(figsize=(8,4));pos=np.arange(5)
    ax.bar(pos-.18,[report[n]['precision'] for n in LABELS],width=.36,label='Precision',color='#227d89');ax.bar(pos+.18,[report[n]['recall'] for n in LABELS],width=.36,label='Recall',color='#a3c8c1')
    ax.set_xticks(pos,short);ax.set_ylim(0,1.12);ax.legend();ax.set_title('Per-class results | support: '+', '.join(str(int(report[n]['support'])) for n in LABELS));fig.tight_layout();fig.savefig(out/'class_performance.png',dpi=180);plt.close(fig)
    names=[*spec['numeric'],*model.named_steps['preprocess'].named_transformers_['sex'].get_feature_names_out(['Sex'])]
    importance=pd.Series(rf.feature_importances_,index=names).sort_values()
    fig,ax=plt.subplots(figsize=(8,4));ax.barh(importance.index,importance.values,color='#227d89');ax.set_xlabel('Mean decrease in impurity');ax.set_title('Training feature importance');fig.tight_layout();fig.savefig(out/'feature_importance.png',dpi=180);plt.close(fig)
    print(json.dumps({k:metrics[k] for k in ['class_counts','missing_counts','accuracy','balanced_accuracy','macro_f1','baseline_accuracy','classification_report','cv']},indent=2))
if __name__=='__main__': train()
