# DNA - Disease Diagnosis Using Random Forest

DNA is an educational HCV laboratory classifier with a local web interface and an eight-page report. HCV is the only active disease module. More disease modules are planned after this model is understood.

## Start on this computer

From PowerShell in `D:\FML PROJECT`:

```powershell
.\.venv\Scripts\python.exe app.py
```

Open http://127.0.0.1:5000. Select Research sample 599, click **Load sample**, then **Analyze test panel**. Expected output: **Cirrhosis**, score **83.8%**. Sample 271 returns **Blood donor**, score **92.5%**. Scores are not calibrated clinical probabilities. Stop with Ctrl+C.

## Fresh installation

Use Python 3.12 and run:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe train.py
.\.venv\Scripts\python.exe -m unittest test_model.py -v
.\.venv\Scripts\python.exe app.py
```

The official dataset is included in `data/hcv/hcvdat0.csv`, so training and inference work offline after dependency installation. Retrain locally if the dependency versions change. Load only trusted model artifacts.

## Model and results

- Source: UCI HCV data, 615 records, age/sex and 10 lab predictors.
- Five original classes retained: blood donor, suspected blood donor, hepatitis, fibrosis, cirrhosis.
- Stratified 80/20 split with seed 42: 492 training, 123 testing.
- Five-fold validation on training records only. Median imputation and one-hot encoding are fitted inside the pipeline for every fold.
- 400 trees, minimum leaf size 2, square-root feature sampling, balanced_subsample weights.
- Test accuracy 95.12%; macro F1 0.612; balanced accuracy 58.67%.
- Majority baseline accuracy 86.99%. Accuracy alone obscures weak rare-class performance.
- The saved pipeline is the exact evaluated model. It is not refitted on test records.

## Explain and Explore

The explanation changes one observed lab value to its training median and measures the resulting change in the current winning class score. It is a local sensitivity probe, not SHAP or a causal medical explanation. Pin an output, change inputs, and run again to compare. Export result downloads the supplied panel and results as JSON.

Age and recorded sex are required. Up to three blank lab inputs are imputed and disclosed; four or more are rejected. This is a demo policy, not a clinical rule. The 65% review flag is illustrative and unvalidated. UCI does not document lab units in its variable table: use original dataset-scale inputs and sample cases. No clinical ranges are inferred. The app does not store submitted panels.

## Project files

- `modules.py`: HCV input contract and module registry.
- `train.py`: reproducible training and evaluation.
- `app.py`, `templates/`, `static/`: DNA local interface and API.
- `artifacts/hcv/`: evaluated model, metrics, charts, held-out examples and test predictions.
- `data/hcv/`: official original dataset, archive and attribution.
- `report/DNA_HCV_Report.pdf`: final project report.
- `report/DNA_HCV_Report.html`: editable report content, with embedded figures.
- `report/build_report.py`: regenerates the report from metrics; requires reportlab in an authoring environment.
- `test_model.py`: integration checks, including every saved test prediction and explanation math.
- `prototypes/breast_cancer/`: earlier experiment outputs, retained for reference and unused by DNA.

## Adding disease modules later

Do not concatenate unrelated disease datasets. Each module needs a separate dataset, target definition, verified input units, preprocessing pipeline, model, held-out evaluation, and interface contract. The registry and `/api/<module_id>/predict` routes provide structure, but new dataset-specific training and validation code is still needed. Check licenses, overlap, label quality and domain shift before exposing a new module. Different disease modules need not be mutually exclusive. No additional disease dataset has been downloaded.

## Dataset attribution

Lichtinghagen, R., Klawonn, F., and Hoffmann, G. (2020). HCV data. UCI Machine Learning Repository. https://doi.org/10.24432/C5D612. CC BY 4.0. Dataset rows are unchanged; preprocessing is applied by the training pipeline. The original publication is Hoffmann et al. (2018), https://doi.org/10.21037/jlpm.2018.06.01.
