"""Independent disease module contracts."""
from pathlib import Path
ROOT = Path(__file__).resolve().parent
LABS = ['ALB','ALP','ALT','AST','BIL','CHE','CHOL','CREA','GGT','PROT']
NAMES = ['Albumin','Alkaline phosphatase','Alanine aminotransferase','Aspartate aminotransferase','Bilirubin','Cholinesterase','Cholesterol','Creatinine','Gamma-glutamyl transferase','Total protein']
LABELS = ['Blood donor','Suspected blood donor','Hepatitis','Fibrosis','Cirrhosis']
RAW_LABELS = ['0=Blood Donor','0s=suspect Blood Donor','1=Hepatitis','2=Fibrosis','3=Cirrhosis']
MODULES = {'hcv': {'id':'hcv','name':'HCV laboratory study','features':['Age','Sex',*LABS], 'numeric':['Age',*LABS], 'labs':LABS,'labels':LABELS,'fields':[{'key':k,'name':n} for k,n in zip(LABS,NAMES)],'source':'https://archive.ics.uci.edu/dataset/571/hcv+data','artifact_dir':ROOT/'artifacts'/'hcv','data_path':ROOT/'data'/'hcv'/'hcvdat0.csv'}}
