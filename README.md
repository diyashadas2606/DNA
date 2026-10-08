# DNA - Clinical Diagnostic Intelligence Platform

**DNA** is a multi-investigation clinical machine learning platform designed around real-world patient diagnostic investigations. Rather than selecting an arbitrary disease from a dropdown menu, clinicians or researchers select the **Diagnostic Test or Laboratory Panel** performed on the patient.

---

## Supported Clinical Diagnostic Investigations

| Investigation Panel | Clinical Purpose | Biomarkers / Parameters | Target Pathology | Test Accuracy |
| :--- | :--- | :--- | :--- | :--- |
| 🧪 **Comprehensive Liver Function Panel (LFT)** | Hepatic blood chemistry & enzyme activity | Albumin, Bilirubin, ALT, AST, GGT, ALP, Cholinesterase, Total Protein, Cholesterol, Creatinine, Age, Sex | Blood Donor (Healthy), Hepatitis, Fibrosis, Cirrhosis | **95.12%** |
| 🫀 **Cardiovascular Stress & Diagnostic Workup** | Hemodynamics, lipid profile & treadmill stress ECG | Resting BP, Serum Cholesterol, Fasting Blood Sugar, Resting ECG, Max Heart Rate, Exercise Angina, ST Depression, ST Slope, Fluoroscopy Vessels, Thallium Scan | Absence vs. Presence of Heart Disease | **90.16%** |
| 🩸 **Glycemic & Metabolic Profile** | Endocrine challenge & insulin resistance | Fasting Plasma Glucose, Serum Insulin, BMI, Diastolic BP, Skinfold Thickness, Pedigree Function, Age, Pregnancies | Non-Diabetic vs. Diabetic | **73.38%** |
| 🔬 **Fine Needle Aspiration (FNA) Cytology** | Microscopic digital nuclear morphometry of lesion | 30 Nuclear Morphology measurements (Mean, SE, Worst: Radius, Texture, Perimeter, Area, Smoothness, Compactness, Concavity, Concave Points, Symmetry, Fractal Dimension) | Benign vs. Malignant Lesion | **96.49%** |

---

## Quickstart

From PowerShell in the project directory:

```powershell
.\.venv\Scripts\python.exe app.py
```

Then open your browser to **http://127.0.0.1:5000**.

1. Select any of the **Diagnostic Workup Cards** at the top (`🧪 Liver Panel`, `🫀 Cardiac Workup`, `🩸 Glycemic Profile`, or `🔬 FNA Biopsy`).
2. Click **Load Case ↗** to load verified held-out clinical patient cases, or enter custom biomarker values.
3. Click **Analyze Diagnostic Panel →**.
4. View predicted pathology categories, confidence scores, sensitivity deltas against population medians, and model evaluation benchmarks.

---

## Re-training All Models & Running Tests

To retrain all clinical diagnostic pipelines from scratch:

```powershell
# Train all 4 diagnostic models
.\.venv\Scripts\python.exe train.py --module all

# Or train a specific test:
.\.venv\Scripts\python.exe train.py --module heart
.\.venv\Scripts\python.exe train.py --module diabetes
.\.venv\Scripts\python.exe train.py --module breast_cancer
.\.venv\Scripts\python.exe train.py --module hcv

# Run full integration test suite
.\.venv\Scripts\python.exe -m unittest test_model.py -v
```

---

## Architectural Layout

- [**`modules.py`**](modules.py): Master clinical registry defining diagnostic test schemas, medical units, clinical reference ranges, valid categories, and model configurations.
- [**`train.py`**](train.py): Reproducible machine learning training pipelines with stratified 80/20 train/test splits, 5-fold cross-validation inside pipelines, and automated artifact generation.
- [**`app.py`**](app.py): Flask application powering the API (`/api/modules`, `/api/<module_id>/predict`) and local web server.
- [**`templates/index.html`**](templates/index.html): Responsive user interface with diagnostic test selection cards, dynamic patient panels, and evaluation dashboards.
- [**`static/app.js`**](static/app.js): Client-side reactive controller for test switching, form building, predictions, and sensitivity explanations.
- [**`static/style.css`**](static/style.css): Modern styling and responsive layout.
- [**`data/`**](data/): Contains official datasets for Liver (`data/hcv/`), Heart (`data/heart/`), Diabetes (`data/diabetes/`), and Breast Cancer (`data/breast_cancer/`).
- [**`artifacts/`**](artifacts/): Trained model bundles (`model.joblib`), evaluation metrics (`metrics.json`), confusion matrices, and feature importance charts for each investigation.
- [**`test_model.py`**](test_model.py): End-to-end integration and data leakage test suite.

---

## Interpretability & Sensitivity

The platform features a local sensitivity probe for every diagnostic test:
- Each observed biomarker is temporarily replaced with its population training median, calculating the net shift in the winning category's likelihood ($\pm\text{pp}$).
- Flags out-of-range inputs that exceed observed training extremes.
- Allows clinicians to **Pin for Comparison** to observe how specific biomarker interventions shift diagnostic outcomes.

---

## Attribution & Clinical Notice

- **HCV Liver Data**: Lichtinghagen, R., Klawonn, F., and Hoffmann, G. (2020). UCI Machine Learning Repository.
- **Heart Disease**: Janosi, Steinbrunn, Pfisterer, Detrano. (1988). Cleveland Heart Disease, UCI Machine Learning Repository.
- **Diabetes**: National Institute of Diabetes and Digestive and Kidney Diseases (NIDDK), Pima Indians Diabetes Dataset.
- **Breast Cancer**: Street, W.N., Wolberg, W.H., and Mangasarian, O.L. (1995). Wisconsin Diagnostic Breast Cancer (WDBC), UCI.

*Note: This platform is designed for research and educational purposes. Model scores are empirical probabilities and not calibrated clinical decisions.*
