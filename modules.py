"""Independent clinical diagnostic module specifications and registry."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# ============================================================================
# 1. LIVER FUNCTION TEST (HCV / Hepatic Biomarkers)
# ============================================================================
HCV_LABS = ['ALB', 'ALP', 'ALT', 'AST', 'BIL', 'CHE', 'CHOL', 'CREA', 'GGT', 'PROT']
HCV_LAB_NAMES = [
    'Albumin', 'Alkaline Phosphatase', 'Alanine Aminotransferase',
    'Aspartate Aminotransferase', 'Bilirubin', 'Cholinesterase',
    'Cholesterol', 'Creatinine', 'Gamma-Glutamyl Transferase', 'Total Protein'
]
HCV_UNITS = {
    'Age': 'years', 'Sex': 'category', 'ALB': 'g/L', 'ALP': 'IU/L',
    'ALT': 'U/L', 'AST': 'U/L', 'BIL': 'μmol/L', 'CHE': 'kU/L',
    'CHOL': 'mmol/L', 'CREA': 'μmol/L', 'GGT': 'U/L', 'PROT': 'g/L'
}
HCV_RANGES = {
    'ALB': '35 - 52 g/L', 'ALP': '30 - 120 IU/L', 'ALT': '7 - 56 U/L',
    'AST': '10 - 40 U/L', 'BIL': '3.4 - 20.5 μmol/L', 'CHE': '5.3 - 12.9 kU/L',
    'CHOL': '3.0 - 5.2 mmol/L', 'CREA': '53 - 106 μmol/L', 'GGT': '9 - 48 U/L', 'PROT': '64 - 83 g/L'
}
HCV_LABELS = ['Blood donor', 'Suspected blood donor', 'Hepatitis', 'Fibrosis', 'Cirrhosis']
HCV_RAW_LABELS = ['0=Blood Donor', '0s=suspect Blood Donor', '1=Hepatitis', '2=Fibrosis', '3=Cirrhosis']

# ============================================================================
# 2. CARDIAC STRESS & DIAGNOSTIC WORKUP (Heart Disease / Cleveland)
# ============================================================================
HEART_FEATURES = ['age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg', 'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal']
HEART_LABELS = ['No Disease Detected', 'Heart Disease Present']

HEART_FIELDS = [
    {
        'key': 'age', 'name': 'Age', 'unit': 'years', 'type': 'number',
        'ref_range': '20 - 90 yrs', 'min': 1, 'max': 120, 'step': 1,
        'category': 'Patient Vitals', 'hint': 'Patient chronological age in years.'
    },
    {
        'key': 'sex', 'name': 'Biological Sex', 'unit': 'category', 'type': 'select',
        'options': [{'value': 1, 'label': 'Male'}, {'value': 0, 'label': 'Female'}],
        'category': 'Patient Vitals', 'hint': 'Recorded biological sex.'
    },
    {
        'key': 'cp', 'name': 'Chest Pain Type', 'unit': 'category', 'type': 'select',
        'options': [
            {'value': 1, 'label': 'Typical Angina'},
            {'value': 2, 'label': 'Atypical Angina'},
            {'value': 3, 'label': 'Non-anginal Pain'},
            {'value': 4, 'label': 'Asymptomatic'}
        ],
        'category': 'Clinical Symptoms', 'hint': 'Nature of precordial pain or discomfort during exertion.'
    },
    {
        'key': 'trestbps', 'name': 'Resting Blood Pressure', 'unit': 'mm Hg', 'type': 'number',
        'ref_range': '90 - 120 mm Hg', 'min': 60, 'max': 250, 'step': 1,
        'category': 'Patient Vitals', 'hint': 'Resting systemic arterial blood pressure upon admission.'
    },
    {
        'key': 'chol', 'name': 'Serum Cholesterol', 'unit': 'mg/dL', 'type': 'number',
        'ref_range': '< 200 mg/dL', 'min': 80, 'max': 600, 'step': 1,
        'category': 'Lipid Profile', 'hint': 'Total serum cholesterol concentration.'
    },
    {
        'key': 'fbs', 'name': 'Fasting Blood Sugar > 120 mg/dL', 'unit': 'category', 'type': 'select',
        'options': [
            {'value': 0, 'label': '≤ 120 mg/dL (Normal fasting)'},
            {'value': 1, 'label': '> 120 mg/dL (Elevated)'}
        ],
        'category': 'Metabolic Vitals', 'hint': 'Fasting blood glucose above diagnostic threshold.'
    },
    {
        'key': 'restecg', 'name': 'Resting ECG Results', 'unit': 'category', 'type': 'select',
        'options': [
            {'value': 0, 'label': 'Normal'},
            {'value': 1, 'label': 'ST-T Wave Abnormality'},
            {'value': 2, 'label': 'Left Ventricular Hypertrophy'}
        ],
        'category': 'Electrocardiogram', 'hint': 'Baseline electrocardiographic tracing at rest.'
    },
    {
        'key': 'thalach', 'name': 'Maximum Heart Rate Achieved', 'unit': 'bpm', 'type': 'number',
        'ref_range': '100 - 200 bpm', 'min': 50, 'max': 230, 'step': 1,
        'category': 'Stress Exercise', 'hint': 'Peak heart rate achieved during treadmill stress testing.'
    },
    {
        'key': 'exang', 'name': 'Exercise-Induced Angina', 'unit': 'category', 'type': 'select',
        'options': [
            {'value': 0, 'label': 'No Angina on Exercise'},
            {'value': 1, 'label': 'Exercise Angina Present'}
        ],
        'category': 'Stress Exercise', 'hint': 'Precordial chest tightness provoked during exertion.'
    },
    {
        'key': 'oldpeak', 'name': 'ST Depression (Exercise vs Rest)', 'unit': 'mm', 'type': 'number',
        'ref_range': '< 1.0 mm', 'min': 0.0, 'max': 10.0, 'step': 0.1,
        'category': 'Stress Exercise', 'hint': 'Electrocardiographic ST segment depression provoked by exercise relative to rest.'
    },
    {
        'key': 'slope', 'name': 'Slope of Peak Exercise ST', 'unit': 'category', 'type': 'select',
        'options': [
            {'value': 1, 'label': 'Upsloping'},
            {'value': 2, 'label': 'Flat'},
            {'value': 3, 'label': 'Downsloping'}
        ],
        'category': 'Stress Exercise', 'hint': 'Geometric trajectory of ST segment during peak stress.'
    },
    {
        'key': 'ca', 'name': 'Major Vessels Colored (Fluoroscopy)', 'unit': 'vessels', 'type': 'number',
        'ref_range': '0 vessels', 'min': 0, 'max': 3, 'step': 1,
        'category': 'Coronary Angiography', 'hint': 'Count of major coronary vessels with visualized radiopaque dye (0-3).'
    },
    {
        'key': 'thal', 'name': 'Thallium Stress Scintigraphy', 'unit': 'category', 'type': 'select',
        'options': [
            {'value': 3, 'label': 'Normal Perfusion (3)'},
            {'value': 6, 'label': 'Fixed Perfusion Defect (6)'},
            {'value': 7, 'label': 'Reversible Ischemia Defect (7)'}
        ],
        'category': 'Coronary Angiography', 'hint': 'Myocardial thallium-201 nuclear perfusion scan findings.'
    }
]

# ============================================================================
# 3. GLYCEMIC & METABOLIC PROFILE (Diabetes Mellitus / Pima)
# ============================================================================
DIABETES_FEATURES = [
    'Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness',
    'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age'
]
DIABETES_LABELS = ['Non-Diabetic', 'Diabetic']

DIABETES_FIELDS = [
    {
        'key': 'Glucose', 'name': 'Plasma Glucose (2-Hr Tolerance)', 'unit': 'mg/dL', 'type': 'number',
        'ref_range': '70 - 140 mg/dL', 'min': 40, 'max': 300, 'step': 1,
        'category': 'Glycemic Status', 'hint': 'Plasma glucose concentration 2 hours post-oral glucose load.'
    },
    {
        'key': 'Insulin', 'name': 'Serum Insulin (2-Hr)', 'unit': 'μU/mL', 'type': 'number',
        'ref_range': '16 - 166 μU/mL', 'min': 5, 'max': 900, 'step': 1,
        'category': 'Glycemic Status', 'hint': '2-hour postprandial serum insulin concentration.'
    },
    {
        'key': 'BMI', 'name': 'Body Mass Index (BMI)', 'unit': 'kg/m²', 'type': 'number',
        'ref_range': '18.5 - 24.9 kg/m²', 'min': 10.0, 'max': 70.0, 'step': 0.1,
        'category': 'Anthropometry', 'hint': 'Body mass index (weight in kg / height in meters squared).'
    },
    {
        'key': 'BloodPressure', 'name': 'Diastolic Blood Pressure', 'unit': 'mm Hg', 'type': 'number',
        'ref_range': '60 - 80 mm Hg', 'min': 40, 'max': 160, 'step': 1,
        'category': 'Vitals', 'hint': 'Diastolic systemic arterial blood pressure.'
    },
    {
        'key': 'SkinThickness', 'name': 'Triceps Skinfold Thickness', 'unit': 'mm', 'type': 'number',
        'ref_range': '10 - 30 mm', 'min': 5, 'max': 100, 'step': 1,
        'category': 'Anthropometry', 'hint': 'Subcutaneous adipose caliper measure at triceps.'
    },
    {
        'key': 'DiabetesPedigreeFunction', 'name': 'Diabetes Pedigree Function', 'unit': 'score', 'type': 'number',
        'ref_range': '0.08 - 1.20', 'min': 0.01, 'max': 3.0, 'step': 0.001,
        'category': 'Genetic History', 'hint': 'Scored genetic familial risk metric based on genealogical history.'
    },
    {
        'key': 'Age', 'name': 'Patient Age', 'unit': 'years', 'type': 'number',
        'ref_range': '18 - 90 yrs', 'min': 18, 'max': 120, 'step': 1,
        'category': 'Patient Profile', 'hint': 'Patient chronological age.'
    },
    {
        'key': 'Pregnancies', 'name': 'Number of Pregnancies', 'unit': 'count', 'type': 'number',
        'ref_range': '0 - 15', 'min': 0, 'max': 25, 'step': 1,
        'category': 'Obstetric History', 'hint': 'Total lifetime pregnancies.'
    }
]

# ============================================================================
# 4. FINE NEEDLE ASPIRATION (FNA) CYTOLOGY (Breast Cancer / WDBC)
# ============================================================================
BC_CORE_NAMES = [
    ('mean radius', 'Mean Nuclear Radius', 'μm', '6.0 - 30.0 μm', 'Mean distance from center to points on the cell perimeter.'),
    ('mean texture', 'Mean Nuclear Texture', 'score', '9.0 - 40.0', 'Standard deviation of gray-scale intensity values across nucleus.'),
    ('mean perimeter', 'Mean Nuclear Perimeter', 'μm', '40.0 - 200.0 μm', 'Mean nuclear outer contour length.'),
    ('mean area', 'Mean Nuclear Area', 'μm²', '140.0 - 2600.0 μm²', 'Mean cross-sectional area of cell nuclei.'),
    ('mean smoothness', 'Mean Nuclear Smoothness', 'score', '0.05 - 0.17', 'Local variation in radius lengths of nuclear membrane.'),
    ('mean compactness', 'Mean Nuclear Compactness', 'ratio', '0.01 - 0.35', 'Perimeter² / area - 1.0 (shape irregularity index).'),
    ('mean concavity', 'Mean Nuclear Concavity', 'severity', '0.0 - 0.45', 'Severity of concave indentations in nuclear contour.'),
    ('mean concave points', 'Mean Concave Points', 'count', '0.0 - 0.21', 'Frequency of concave contour indentations.'),
    ('mean symmetry', 'Mean Nuclear Symmetry', 'score', '0.10 - 0.31', 'Nuclear structural bilateral symmetry index.'),
    ('mean fractal dimension', 'Mean Fractal Dimension', 'index', '0.04 - 0.10', 'Coastline approximation index - 1 (boundary complexity).')
]

BC_ERROR_NAMES = [
    ('radius error', 'Radius SE', 'μm', '0.1 - 3.0 μm', 'Standard error for nuclear radius.'),
    ('texture error', 'Texture SE', 'score', '0.3 - 5.0', 'Standard error for texture intensity.'),
    ('perimeter error', 'Perimeter SE', 'μm', '0.7 - 22.0 μm', 'Standard error for nuclear perimeter.'),
    ('area error', 'Area SE', 'μm²', '6.0 - 550.0 μm²', 'Standard error for nuclear area.'),
    ('smoothness error', 'Smoothness SE', 'score', '0.001 - 0.03', 'Standard error for nuclear smoothness.'),
    ('compactness error', 'Compactness SE', 'ratio', '0.002 - 0.14', 'Standard error for nuclear compactness.'),
    ('concavity error', 'Concavity SE', 'severity', '0.0 - 0.4', 'Standard error for nuclear concavity.'),
    ('concave points error', 'Concave Points SE', 'count', '0.0 - 0.06', 'Standard error for concave contour points.'),
    ('symmetry error', 'Symmetry SE', 'score', '0.007 - 0.08', 'Standard error for symmetry.'),
    ('fractal dimension error', 'Fractal Dimension SE', 'index', '0.0008 - 0.03', 'Standard error for fractal dimension.')
]

BC_WORST_NAMES = [
    ('worst radius', 'Worst Nuclear Radius', 'μm', '7.0 - 36.0 μm', 'Largest / most atypical nuclear radius observed in biopsy specimen.'),
    ('worst texture', 'Worst Nuclear Texture', 'score', '12.0 - 50.0', 'Maximum texture heterogeneity observed in specimen.'),
    ('worst perimeter', 'Worst Nuclear Perimeter', 'μm', '50.0 - 255.0 μm', 'Largest nuclear perimeter contour observed.'),
    ('worst area', 'Worst Nuclear Area', 'μm²', '180.0 - 4250.0 μm²', 'Maximum nuclear cross-sectional area observed.'),
    ('worst smoothness', 'Worst Nuclear Smoothness', 'score', '0.07 - 0.23', 'Highest membrane roughness observed.'),
    ('worst compactness', 'Worst Nuclear Compactness', 'ratio', '0.02 - 1.1', 'Most irregular nuclear compactness observed.'),
    ('worst concavity', 'Worst Nuclear Concavity', 'severity', '0.0 - 1.3', 'Most severe nuclear invagination observed.'),
    ('worst concave points', 'Worst Concave Points', 'count', '0.0 - 0.30', 'Highest concentration of nuclear boundary indentations.'),
    ('worst symmetry', 'Worst Nuclear Symmetry', 'score', '0.15 - 0.67', 'Highest nuclear asymmetry observed.'),
    ('worst fractal dimension', 'Worst Fractal Dimension', 'index', '0.05 - 0.21', 'Highest nuclear border complexity observed.')
]

BC_FIELDS = []
for k, n, u, r, h in BC_CORE_NAMES:
    BC_FIELDS.append({'key': k, 'name': n, 'unit': u, 'type': 'number', 'ref_range': r, 'min': 0, 'max': 5000, 'step': 'any', 'category': 'Mean Nuclear Morphology', 'hint': h})
for k, n, u, r, h in BC_ERROR_NAMES:
    BC_FIELDS.append({'key': k, 'name': n, 'unit': u, 'type': 'number', 'ref_range': r, 'min': 0, 'max': 1000, 'step': 'any', 'category': 'Nuclear Variation (SE)', 'hint': h})
for k, n, u, r, h in BC_WORST_NAMES:
    BC_FIELDS.append({'key': k, 'name': n, 'unit': u, 'type': 'number', 'ref_range': r, 'min': 0, 'max': 6000, 'step': 'any', 'category': 'Worst / Extreme Cells', 'hint': h})

BC_FEATURES = [f['key'] for f in BC_FIELDS]
BC_LABELS = ['Benign (Non-Cancerous)', 'Malignant (Cancerous)']


# ============================================================================
# MASTER MODULE REGISTRY
# ============================================================================
MODULES = {
    'hcv': {
        'id': 'hcv',
        'test_name': 'Comprehensive Liver Function Panel (LFT)',
        'short_name': 'Liver Function (LFT)',
        'tagline': 'Hepatic Enzymes & Blood Chemistry',
        'icon': '🧪',
        'organ': 'Liver / Hepatic System',
        'clinical_focus': 'Measures liver enzyme activity (ALT, AST, ALP, GGT), bilirubin metabolism, and protein synthesis to detect viral hepatitis, hepatic fibrosis, and end-stage cirrhosis.',
        'target_label': 'Hepatic Pathology Status',
        'features': ['Age', 'Sex', *HCV_LABS],
        'numeric': ['Age', *HCV_LABS],
        'categorical': ['Sex'],
        'labs': HCV_LABS,
        'labels': HCV_LABELS,
        'raw_labels': HCV_RAW_LABELS,
        'target_col': 'Category',
        'fields': [
            {
                'key': 'Age', 'name': 'Patient Age', 'unit': 'years', 'type': 'number',
                'ref_range': '19 - 77 yrs', 'min': 1, 'max': 120, 'step': 1,
                'category': 'Patient Demographics', 'hint': 'Patient chronological age.'
            },
            {
                'key': 'Sex', 'name': 'Recorded Sex', 'unit': 'category', 'type': 'select',
                'options': [{'value': 'm', 'label': 'Male'}, {'value': 'f', 'label': 'Female'}],
                'category': 'Patient Demographics', 'hint': 'Biological sex category.'
            },
            *[
                {
                    'key': k, 'name': n, 'unit': HCV_UNITS[k], 'type': 'number',
                    'ref_range': HCV_RANGES[k], 'min': 0, 'max': 100000, 'step': 'any',
                    'category': 'Blood Serum Chemistry',
                    'hint': f'Serum concentration of {n.lower()}.'
                }
                for k, n in zip(HCV_LABS, HCV_LAB_NAMES)
            ]
        ],
        'max_missing': 3,
        'source': 'https://archive.ics.uci.edu/dataset/571/hcv+data',
        'artifact_dir': ROOT / 'artifacts' / 'hcv',
        'data_path': ROOT / 'data' / 'hcv' / 'hcvdat0.csv'
    },
    'heart': {
        'id': 'heart',
        'test_name': 'Cardiovascular Stress & Diagnostic Workup',
        'short_name': 'Cardiac Workup',
        'tagline': 'Vitals, Lipid Profile & Stress ECG',
        'icon': '🫀',
        'organ': 'Cardiovascular System',
        'clinical_focus': 'Integrates resting arterial blood pressure, total serum cholesterol, ECG tracings, exercise treadmill tolerance, and angiographic vessel markers to identify ischemic coronary heart disease.',
        'target_label': 'Cardiovascular Disease Risk',
        'features': HEART_FEATURES,
        'numeric': ['age', 'trestbps', 'chol', 'thalach', 'oldpeak', 'ca'],
        'categorical': ['sex', 'cp', 'fbs', 'restecg', 'exang', 'slope', 'thal'],
        'labs': ['trestbps', 'chol', 'thalach', 'oldpeak', 'ca'],
        'labels': HEART_LABELS,
        'target_col': 'target',
        'fields': HEART_FIELDS,
        'max_missing': 3,
        'source': 'https://archive.ics.uci.edu/dataset/45/heart+disease',
        'artifact_dir': ROOT / 'artifacts' / 'heart',
        'data_path': ROOT / 'data' / 'heart' / 'heart.csv'
    },
    'diabetes': {
        'id': 'diabetes',
        'test_name': 'Glycemic & Metabolic Profile',
        'short_name': 'Glycemic Profile',
        'tagline': 'Endocrine & Glucose Regulation',
        'icon': '🩸',
        'organ': 'Endocrine / Pancreatic System',
        'clinical_focus': 'Evaluates post-challenge plasma glucose, serum insulin, body mass index, and familial genetic susceptibility to screen for insulin resistance and Type 2 diabetes.',
        'target_label': 'Metabolic Diagnosis',
        'features': DIABETES_FEATURES,
        'numeric': DIABETES_FEATURES,
        'categorical': [],
        'labs': ['Glucose', 'Insulin', 'BMI', 'BloodPressure', 'SkinThickness', 'DiabetesPedigreeFunction'],
        'labels': DIABETES_LABELS,
        'target_col': 'Outcome',
        'fields': DIABETES_FIELDS,
        'max_missing': 4,
        'source': 'https://archive.ics.uci.edu/dataset/34/diabetes',
        'artifact_dir': ROOT / 'artifacts' / 'diabetes',
        'data_path': ROOT / 'data' / 'diabetes' / 'diabetes.csv'
    },
    'breast_cancer': {
        'id': 'breast_cancer',
        'test_name': 'Fine Needle Aspiration (FNA) Cytology',
        'short_name': 'FNA Biopsy Cytology',
        'tagline': 'Cellular Histopathology & Nuclear Geometry',
        'icon': '🔬',
        'organ': 'Breast Tissue / Oncology',
        'clinical_focus': 'Analyzes digitized nuclear morphometry (radius, contour irregularity, texture variation, and concavity) from fine needle aspiration biopsies to distinguish benign lesions from malignant carcinomas.',
        'target_label': 'Cytopathological Classification',
        'features': BC_FEATURES,
        'numeric': BC_FEATURES,
        'categorical': [],
        'labs': BC_FEATURES,
        'labels': BC_LABELS,
        'target_col': 'target',
        'fields': BC_FIELDS,
        'max_missing': 5,
        'source': 'https://archive.ics.uci.edu/dataset/17/breast+cancer+wisconsin+diagnostic',
        'artifact_dir': ROOT / 'artifacts' / 'breast_cancer',
        'data_path': ROOT / 'data' / 'breast_cancer' / 'breast_cancer.csv'
    }
}
