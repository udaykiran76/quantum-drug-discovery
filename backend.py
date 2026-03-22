from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
import joblib
import sys
import os

sys.path.append("src")

from features import smiles_to_fingerprint, get_molecule_properties, check_lipinski

app = FastAPI(title="Quantum Drug Discovery API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load models once at startup
print("Loading models...")
xgb_model  = joblib.load("models/classical_model.pkl")
qsvm_model = joblib.load("models/quantum_svm.pkl")
pca        = joblib.load("models/pca.pkl")
scaler     = joblib.load("models/scaler.pkl")
print("All models loaded!")


class PredictRequest(BaseModel):
    smiles: str


@app.get("/")
def root():
    return {"message": "Quantum Drug Discovery API is running!"}


@app.post("/predict")
def predict(request: PredictRequest):
    smiles = request.smiles

    # Get fingerprint
    fp = smiles_to_fingerprint(smiles)
    if fp is None:
        return {"error": "Invalid SMILES string"}

    fp_2d = fp.reshape(1, -1)

    # Classical prediction
    classical_prob = float(xgb_model.predict_proba(fp_2d)[0][1])

    # Quantum prediction
    fp_pca    = pca.transform(fp_2d)
    fp_scaled = scaler.transform(fp_pca)
    quantum_prob = float(qsvm_model.predict_proba(fp_scaled)[0][1])

    # Hybrid combination
    hybrid_prob = (0.6 * classical_prob) + (0.4 * quantum_prob)
    prediction  = "ACTIVE" if hybrid_prob >= 0.5 else "INACTIVE"
    confidence  = hybrid_prob if prediction == "ACTIVE" else 1 - hybrid_prob

    # Molecule properties
    props = get_molecule_properties(smiles)

    # Lipinski rules
    rules, passed = check_lipinski(smiles)
    lipinski = {
        "passed": passed,
        "total" : 6,
        "rules" : {
            rule: {"value": disp, "passed": ok}
            for rule, (val, ok, disp) in rules.items()
        }
    }

    # PCA features for visualization
    pca_features    = fp_pca[0].tolist()
    scaled_features = fp_scaled[0].tolist()
    fingerprint     = fp.tolist()

    return {
        "prediction"      : prediction,
        "confidence"      : round(confidence * 100, 2),
        "classical_prob"  : round(classical_prob * 100, 2),
        "quantum_prob"    : round(quantum_prob * 100, 2),
        "hybrid_prob"     : round(hybrid_prob * 100, 2),
        "properties"      : props,
        "lipinski"        : lipinski,
        "pca_features"    : pca_features,
        "scaled_features" : scaled_features,
        "fingerprint"     : fingerprint,
    }


@app.get("/benchmark")
def benchmark():
    return {
        "models": [
            {"name": "Classical XGBoost",        "accuracy": 82.2, "roc_auc": 0.9225},
            {"name": "Quantum Kernel SVM",        "accuracy": 74.0, "roc_auc": 0.8487},
            {"name": "Hybrid Classical+Quantum",  "accuracy": 83.0, "roc_auc": 0.9301},
        ]
    }


@app.get("/examples")
def examples():
    return {
        "molecules": [
            {"name": "Known BACE Inhibitor", "smiles": "Fc1ncccc1-c1cc(ccc1)C1(N=C(N2C1=NCC(F)(F)C2)N)c1ccc(OC(F)F)cc1"},
            {"name": "Aspirin",              "smiles": "CC(=O)Oc1ccccc1C(=O)O"},
            {"name": "Ibuprofen",            "smiles": "CC(C)Cc1ccc(cc1)C(C)C(=O)O"},
            {"name": "Caffeine",             "smiles": "Cn1c(=O)c2c(ncn2C)n(c1=O)C"},
        ]
    }