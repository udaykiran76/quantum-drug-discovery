.

🧬 Quantum Drug Discovery Platform

A production-oriented web application that integrates classical machine learning, quantum-inspired models, and cheminformatics to predict molecular activity and assist in early-stage drug discovery.

🚀 Overview

This project provides an end-to-end pipeline for analyzing chemical compounds using SMILES representation and predicting their biological activity. It combines:
Classical ML models
Quantum-inspired learning techniques
Molecular feature engineering
Interactive web interface
The goal is to simulate a modern drug discovery workflow in a scalable and user-friendly way.

🧠 Key Features
🔬 Molecular Input via SMILES strings
📊 Activity Prediction (Active / Inactive)
⚛️ Quantum-inspired Modeling using Qiskit
🤖 Classical ML Models using XGBoost
🧬 Feature Engineering with RDKit
📈 Model Benchmarking & Comparison
🌐 Interactive UI built with Streamlit

⚙️ Tech Stack


Programming Language: Python
ML Libraries: scikit-learn, XGBoost
Quantum Computing: Qiskit
Cheminformatics: RDKit
Frontend/UI: Streamlit
Visualization: Matplotlib, Seaborn


📊 Workflow


Data Collection
Dataset sourced from MoleculeNet (BACE dataset)
Feature Engineering
Convert SMILES → Molecular fingerprints
Dimensionality reduction using PCA
Model Training
Classical model (XGBoost)
Quantum model (Qiskit kernel-based SVM)
Evaluation
Accuracy, ROC-AUC, and comparison
Deployment
Interactive UI using Streamlit
▶️ Getting Started
1. Clone Repository
git clone <your-repo-link>
cd quantum-drug-discovery
2. Create Virtual Environment
python -m venv venv
venv\Scripts\activate
3. Install Dependencies
pip install -r requirements.txt
4. Run Application
cd app
streamlit run streamlit_app.py
🧪 Example Usage
Input: CCO
Output:
Prediction: Active / Inactive
Confidence Score


Molecular Visualization

🔮 Future Enhancements
🧠 Graph Neural Networks for better molecular representation
⚛️ Advanced hybrid quantum-classical models
📡 API integration using FastAPI
🗄️ Database integration (PostgreSQL / MongoDB)
🧬 Molecule generation using generative models
📊 Explainability using SHAP
