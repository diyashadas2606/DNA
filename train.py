"""Train DNA clinical diagnostic models with leakage-free cross-validation."""
import argparse
import hashlib
import json
import joblib
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
from sklearn.metrics import (
    accuracy_score, balanced_accuracy_score, classification_report,
    confusion_matrix, ConfusionMatrixDisplay, f1_score, roc_auc_score
)
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from modules import MODULES, ROOT


def train_module(module_id: str):
    if module_id not in MODULES:
        raise ValueError(f"Unknown module {module_id}. Choose from: {list(MODULES.keys())}")

    spec = MODULES[module_id]
    out = spec['artifact_dir']
    out.mkdir(parents=True, exist_ok=True)
    print(f"\n========================================================")
    print(f"Training [{spec['short_name']}] ({module_id})")
    print(f"========================================================")

    # 1. Load data
    raw = pd.read_csv(spec['data_path'])
    if module_id == 'hcv':
        raw = pd.read_csv(spec['data_path'], index_col=0)
        label_map = dict(zip(spec['raw_labels'], range(len(spec['labels']))))
        y = raw[spec['target_col']].map(label_map)
        X = raw[spec['features']].copy()
    elif module_id == 'heart':
        raw['target'] = (raw['target'] > 0).astype(int)
        y = raw['target'].copy()
        X = raw[spec['features']].copy()
    elif module_id == 'diabetes':
        y = raw[spec['target_col']].astype(int)
        X = raw[spec['features']].copy()
    elif module_id == 'breast_cancer':
        # In raw sklearn data: 0 = malignant, 1 = benign.
        # We align: 0 = Benign (Non-Cancerous), 1 = Malignant (Cancerous).
        y = (raw['target'] == 0).astype(int)
        X = raw[spec['features']].copy()
    else:
        raise ValueError(f"Unsupported module {module_id}")

    # 2. Stratified train/test split
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

    # 3. Preprocessing pipeline
    transformers = []
    if spec['numeric']:
        transformers.append(('numeric', SimpleImputer(strategy='median'), spec['numeric']))
    if spec['categorical']:
        cat_pipe = Pipeline([
            ('imputer', SimpleImputer(strategy='most_frequent')),
            ('encoder', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
        ])
        transformers.append(('categorical', cat_pipe, spec['categorical']))

    prep = ColumnTransformer(transformers)

    # 4. Model estimator
    n_classes = len(spec['labels'])
    class_weight = 'balanced_subsample' if n_classes > 2 else 'balanced'
    rf = RandomForestClassifier(
        n_estimators=400,
        min_samples_leaf=2,
        class_weight=class_weight,
        max_features='sqrt',
        random_state=42,
        n_jobs=1
    )
    model = Pipeline([('preprocess', prep), ('forest', rf)])

    # 5. Cross-validation on training fold
    scoring = ['accuracy', 'balanced_accuracy', 'f1_macro']
    cv = cross_validate(
        model, Xtr, ytr,
        cv=StratifiedKFold(5, shuffle=True, random_state=42),
        scoring=scoring,
        error_score='raise'
    )

    # 6. Fit and evaluate on held-out test fold
    model.fit(Xtr, ytr)
    pred = model.predict(Xte)
    scores = model.predict_proba(Xte)
    base = DummyClassifier(strategy='most_frequent').fit(Xtr, ytr).predict(Xte)

    report = classification_report(
        yte, pred,
        labels=list(range(n_classes)),
        target_names=spec['labels'],
        output_dict=True,
        zero_division=0
    )
    cm = confusion_matrix(yte, pred, labels=list(range(n_classes)))

    # Compute baseline and test metrics
    acc = accuracy_score(yte, pred)
    b_acc = balanced_accuracy_score(yte, pred)
    f1 = f1_score(yte, pred, average='macro')
    base_acc = accuracy_score(yte, base)
    base_f1 = f1_score(yte, base, average='macro')

    roc_auc = None
    if n_classes == 2:
        try:
            roc_auc = float(roc_auc_score(yte, scores[:, 1]))
        except Exception:
            pass

    # Collect numeric medians and categorical modes
    medians = {}
    mins = {}
    maxs = {}
    for col in spec['numeric']:
        series = pd.to_numeric(Xtr[col], errors='coerce')
        medians[col] = float(series.median()) if pd.notna(series.median()) else 0.0
        mins[col] = float(series.min()) if pd.notna(series.min()) else 0.0
        maxs[col] = float(series.max()) if pd.notna(series.max()) else 0.0

    modes = {}
    for col in spec['categorical']:
        mode_val = Xtr[col].mode()
        modes[col] = mode_val.iloc[0] if len(mode_val) > 0 else None

    metrics = {
        'module': module_id,
        'test_name': spec['test_name'],
        'samples': len(X),
        'features': X.shape[1],
        'train_samples': len(Xtr),
        'test_samples': len(Xte),
        'labels': spec['labels'],
        'class_counts': {spec['labels'][i]: int((y == i).sum()) for i in range(n_classes)},
        'missing_counts': X.isna().sum().to_dict(),
        'accuracy': float(acc),
        'balanced_accuracy': float(b_acc),
        'macro_f1': float(f1),
        'roc_auc': roc_auc,
        'baseline_accuracy': float(base_acc),
        'baseline_macro_f1': float(base_f1),
        'classification_report': report,
        'confusion_matrix': cm.tolist(),
        'cv': {
            k[5:]: {'mean': float(v.mean()), 'std': float(v.std()), 'folds': v.tolist()}
            for k, v in cv.items() if k.startswith('test_')
        },
        'train_indices': [int(i) for i in Xtr.index.tolist()],
        'test_indices': [int(i) for i in Xte.index.tolist()],
        'sklearn_version': sklearn.__version__,
        'parameters': rf.get_params(),
        'sha256': hashlib.sha256(spec['data_path'].read_bytes()).hexdigest(),
        'source': spec['source'],
        'seed': 42
    }

    (out / 'metrics.json').write_text(json.dumps(metrics, indent=2))

    # Save model bundle
    bundle = {
        'pipeline': model,
        'module': module_id,
        'features': spec['features'],
        'numeric': spec['numeric'],
        'categorical': spec['categorical'],
        'medians': medians,
        'modes': modes,
        'minimum': mins,
        'maximum': maxs,
        'labels': spec['labels']
    }
    joblib.dump(bundle, out / 'model.joblib')

    # Save test predictions
    evaluation = Xte.copy()
    evaluation['actual'] = yte.values
    evaluation['predicted'] = pred
    for i in range(n_classes):
        evaluation[f'score_{i}'] = scores[:, i]
    evaluation.to_csv(out / 'test_predictions.csv', index_label='sample_id')

    # Select representative held-out examples for the web UI
    examples = []
    for i in range(n_classes):
        matching_indices = yte[yte == i].index
        for idx in matching_indices[:2]:  # Take up to 2 representative examples per class
            row_dict = Xte.loc[idx].to_dict()
            clean_features = {}
            for k, v in row_dict.items():
                if pd.isna(v):
                    clean_features[k] = None
                elif isinstance(v, (np.integer, int)):
                    clean_features[k] = int(v)
                elif isinstance(v, (np.floating, float)):
                    clean_features[k] = round(float(v), 4)
                else:
                    clean_features[k] = v

            pred_class = int(pred[list(Xte.index).index(idx)])
            examples.append({
                'sample_id': int(idx),
                'actual_class': spec['labels'][i],
                'predicted_class': spec['labels'][pred_class],
                'case_label': f"Patient Case {len(examples) + 1}: {spec['labels'][i]}",
                'features': clean_features
            })

    (out / 'examples.json').write_text(json.dumps(examples, indent=2))
    example_ids = [s['sample_id'] for s in examples]
    Xte.loc[example_ids].to_csv(out / 'example_inputs.csv', index=False)

    # 7. Generate Evaluation Figures
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'axes.spines.top': False, 'axes.spines.right': False})

    # A. Confusion Matrix
    fig, ax = plt.subplots(figsize=(6 + n_classes * 0.5, 4.5 + n_classes * 0.4))
    disp_labels = [l.split('(')[0].strip() for l in spec['labels']]
    ConfusionMatrixDisplay(cm, display_labels=disp_labels).plot(
        ax=ax, colorbar=False, cmap='Blues', xticks_rotation=20
    )
    ax.set_title(f"{spec['short_name']} | Test Set ({len(Xte)} samples)", pad=15, fontsize=12, fontweight='bold')
    fig.tight_layout()
    fig.savefig(out / 'confusion_matrix.png', dpi=180)
    plt.close(fig)

    # B. Per-class performance
    fig, ax = plt.subplots(figsize=(7 + n_classes * 0.5, 4.2))
    pos = np.arange(n_classes)
    precisions = [report[spec['labels'][i]]['precision'] for i in range(n_classes)]
    recalls = [report[spec['labels'][i]]['recall'] for i in range(n_classes)]
    ax.bar(pos - 0.18, precisions, width=0.36, label='Precision', color='#227d89')
    ax.bar(pos + 0.18, recalls, width=0.36, label='Recall', color='#a3c8c1')
    ax.set_xticks(pos, disp_labels)
    ax.set_ylim(0, 1.15)
    ax.legend(frameon=False)
    supports = [str(int(report[spec['labels'][i]]['support'])) for i in range(n_classes)]
    ax.set_title(f"Class-Level Metrics | Support: {', '.join(supports)}", fontsize=11, fontweight='bold')
    fig.tight_layout()
    fig.savefig(out / 'class_performance.png', dpi=180)
    plt.close(fig)

    # C. Feature Importance
    try:
        prep_step = model.named_steps['preprocess']
        feature_names = []
        if spec['numeric']:
            feature_names.extend(spec['numeric'])
        if spec['categorical']:
            cat_encoder = prep_step.named_transformers_['categorical'].named_steps['encoder']
            cat_names = cat_encoder.get_feature_names_out(spec['categorical'])
            feature_names.extend(cat_names)

        importances = rf.feature_importances_
        if len(feature_names) == len(importances):
            imp_series = pd.Series(importances, index=feature_names).sort_values()
            top_imp = imp_series.tail(15)  # Show top 15 most predictive features
            fig, ax = plt.subplots(figsize=(8, max(4.0, len(top_imp) * 0.28)))
            ax.barh(top_imp.index, top_imp.values, color='#227d89')
            ax.set_xlabel('Mean Decrease in Impurity (Gini Importance)')
            ax.set_title(f"Top Predictors | {spec['short_name']}", fontsize=11, fontweight='bold')
            fig.tight_layout()
            fig.savefig(out / 'feature_importance.png', dpi=180)
            plt.close(fig)
    except Exception as e:
        print(f"Feature importance plot skipped: {e}")

    print(f"Results for {spec['test_name']}:")
    print(f"  Test Accuracy:     {acc * 100:.2f}% (Baseline: {base_acc * 100:.2f}%)")
    print(f"  Balanced Accuracy: {b_acc * 100:.2f}%")
    print(f"  Macro F1:          {f1:.3f}")
    if roc_auc is not None:
        print(f"  ROC-AUC:           {roc_auc:.3f}")
    print(f"  Artifacts saved to: {out}")


def train_all():
    for mod in MODULES.keys():
        train_module(mod)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Train DNA Clinical Diagnostic Models")
    parser.add_argument('--module', choices=list(MODULES.keys()) + ['all'], default='all', help="Module to train")
    args = parser.parse_args()

    if args.module == 'all':
        train_all()
    else:
        train_module(args.module)
