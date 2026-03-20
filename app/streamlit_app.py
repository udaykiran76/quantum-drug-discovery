import streamlit as st
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch
import matplotlib.gridspec as gridspec
from rdkit import Chem
from rdkit.Chem import Draw, AllChem, Descriptors
from rdkit.Chem import rdMolDescriptors
import joblib
from PIL import Image
import io
import base64

sys.path.append("src")

st.set_page_config(
    page_title="Quantum Drug Discovery",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #1f77b4, #9467bd, #2ca02c);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding: 1rem 0;
    }
    .sub-header {
        text-align: center;
        color: #666;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #1f77b4, #9467bd);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .result-active {
        background: linear-gradient(135deg, #2ca02c, #98df8a);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        font-size: 1.5rem;
        font-weight: bold;
    }
    .result-inactive {
        background: linear-gradient(135deg, #d62728, #ff9896);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        font-size: 1.5rem;
        font-weight: bold;
    }
    .quantum-card {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        padding: 1.5rem;
        border-radius: 12px;
        color: #00d4ff;
        border: 1px solid #9467bd;
    }
    .lipinski-pass {
        background: linear-gradient(135deg, #2ca02c, #98df8a);
        padding: 0.8rem;
        border-radius: 8px;
        color: white;
        text-align: center;
        margin: 0.3rem 0;
    }
    .lipinski-fail {
        background: linear-gradient(135deg, #d62728, #ff9896);
        padding: 0.8rem;
        border-radius: 8px;
        color: white;
        text-align: center;
        margin: 0.3rem 0;
    }
    .bace-card {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        padding: 1.5rem;
        border-radius: 12px;
        color: #ffffff;
        border: 1px solid #2ca02c;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_models():
    xgb_model  = joblib.load("models/classical_model.pkl")
    qsvm_model = joblib.load("models/quantum_svm.pkl")
    pca        = joblib.load("models/pca.pkl")
    scaler     = joblib.load("models/scaler.pkl")
    return xgb_model, qsvm_model, pca, scaler


def smiles_to_fingerprint(smiles, n_bits=1024):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    fp = AllChem.GetMorganFingerprintAsBitVect(mol, radius=2, nBits=n_bits)
    return np.array(fp)


def get_molecule_properties(smiles):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    return {
        "Molecular Weight"    : round(Descriptors.MolWt(mol), 2),
        "LogP (Lipophilicity)": round(Descriptors.MolLogP(mol), 2),
        "H-Bond Donors"       : rdMolDescriptors.CalcNumHBD(mol),
        "H-Bond Acceptors"    : rdMolDescriptors.CalcNumHBA(mol),
        "Rotatable Bonds"     : rdMolDescriptors.CalcNumRotatableBonds(mol),
        "Aromatic Rings"      : rdMolDescriptors.CalcNumAromaticRings(mol),
        "Heavy Atoms"         : mol.GetNumHeavyAtoms(),
        "Ring Count"          : rdMolDescriptors.CalcNumRings(mol),
    }


def smiles_to_2d_image(smiles, size=(400, 300)):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    img = Draw.MolToImage(mol, size=size)
    return img


def get_3d_html(smiles):
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return None
        mol = Chem.AddHs(mol)
        AllChem.EmbedMolecule(mol, randomSeed=42)
        AllChem.MMFFOptimizeMolecule(mol)
        mol_block = Chem.MolToMolBlock(mol)
        html = f"""
        <script src="https://3dmol.org/build/3Dmol-min.js"></script>
        <div id="viewer" style="width:100%;height:400px;border-radius:12px;
             background:#0a0a0a;border:1px solid #9467bd;"></div>
        <script>
            let viewer = $3Dmol.createViewer("viewer", {{backgroundColor: "#0a0a0a"}});
            let molData = `{mol_block}`;
            viewer.addModel(molData, "mol");
            viewer.setStyle({{}}, {{
                stick: {{colorscheme: "RasmolAA", radius: 0.15}},
                sphere: {{colorscheme: "RasmolAA", scale: 0.3}}
            }});
            viewer.zoomTo();
            viewer.spin(true);
            viewer.render();
        </script>
        """
        return html
    except:
        return None


def run_hybrid_prediction(smiles, xgb_model, qsvm_model, pca, scaler):
    fp = smiles_to_fingerprint(smiles)
    if fp is None:
        return None
    fp_2d            = fp.reshape(1, -1)
    classical_prob   = xgb_model.predict_proba(fp_2d)[0][1]
    fp_pca           = pca.transform(fp_2d)
    fp_scaled        = scaler.transform(fp_pca)
    quantum_prob     = qsvm_model.predict_proba(fp_scaled)[0][1]
    hybrid_prob      = (0.6 * classical_prob) + (0.4 * quantum_prob)
    prediction       = "ACTIVE" if hybrid_prob >= 0.5 else "INACTIVE"
    return {
        "prediction"     : prediction,
        "hybrid_prob"    : hybrid_prob,
        "classical_prob" : classical_prob,
        "quantum_prob"   : quantum_prob,
        "confidence"     : hybrid_prob if prediction == "ACTIVE" else 1 - hybrid_prob,
        "fp"             : fp,
        "fp_pca"         : fp_pca,
        "fp_scaled"      : fp_scaled,
    }


def create_benchmark_chart():
    results = {
        "Classical\nXGBoost"        : {"accuracy": 0.8224, "roc_auc": 0.9225},
        "Quantum\nKernel SVM"       : {"accuracy": 0.7400, "roc_auc": 0.8487},
        "Hybrid\nClassical+Quantum" : {"accuracy": 0.8300, "roc_auc": 0.9301},
    }
    models   = list(results.keys())
    accuracy = [results[m]["accuracy"] * 100 for m in models]
    roc_auc  = [results[m]["roc_auc"] for m in models]
    colors   = ["#1f77b4", "#9467bd", "#2ca02c"]
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    fig.patch.set_facecolor("#0a0a0a")
    for ax in axes:
        ax.set_facecolor("#1a1a2e")
        ax.tick_params(colors="white")
        ax.yaxis.label.set_color("white")
        ax.title.set_color("white")
        for spine in ax.spines.values():
            spine.set_edgecolor("#9467bd")
    bars1 = axes[0].bar(models, accuracy, color=colors, alpha=0.85, width=0.5)
    axes[0].set_title("Accuracy (%)", fontweight="bold")
    axes[0].set_ylim(0, 105)
    for bar, val in zip(bars1, accuracy):
        axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height()+1,
                     f"{val:.1f}%", ha="center", color="white", fontweight="bold", fontsize=10)
    bars2 = axes[1].bar(models, roc_auc, color=colors, alpha=0.85, width=0.5)
    axes[1].set_title("ROC-AUC Score", fontweight="bold")
    axes[1].set_ylim(0, 1.1)
    for bar, val in zip(bars2, roc_auc):
        axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height()+0.01,
                     f"{val:.4f}", ha="center", color="white", fontweight="bold", fontsize=10)
    plt.tight_layout()
    return fig


def create_probability_chart(classical_prob, quantum_prob, hybrid_prob):
    fig, ax = plt.subplots(figsize=(8, 3))
    fig.patch.set_facecolor("#0a0a0a")
    ax.set_facecolor("#1a1a2e")
    models = ["Classical", "Quantum", "Hybrid"]
    probs  = [classical_prob, quantum_prob, hybrid_prob]
    colors = ["#1f77b4", "#9467bd", "#2ca02c"]
    bars   = ax.barh(models, probs, color=colors, alpha=0.85, height=0.4)
    ax.set_xlim(0, 1)
    ax.axvline(x=0.5, color="red", linestyle="--", alpha=0.7)
    ax.set_title("Prediction Probabilities (ACTIVE)", color="white", fontweight="bold")
    ax.tick_params(colors="white")
    for spine in ax.spines.values():
        spine.set_edgecolor("#9467bd")
    for bar, val in zip(bars, probs):
        ax.text(val + 0.02, bar.get_y() + bar.get_height()/2,
                f"{val:.3f}", va="center", color="white", fontweight="bold")
    plt.tight_layout()
    return fig


def create_bloch_sphere(fp_scaled):
    """Visualize qubit states on Bloch sphere."""
    fig = plt.figure(figsize=(12, 4))
    fig.patch.set_facecolor("#0a0a0a")

    angles = fp_scaled[0][:8]

    for i in range(8):
        ax = fig.add_subplot(2, 4, i+1, projection='3d')
        ax.set_facecolor("#1a1a2e")

        # Draw sphere wireframe
        u = np.linspace(0, 2*np.pi, 30)
        v = np.linspace(0, np.pi, 30)
        x = np.outer(np.cos(u), np.sin(v))
        y = np.outer(np.sin(u), np.sin(v))
        z = np.outer(np.ones(np.size(u)), np.cos(v))
        ax.plot_wireframe(x, y, z, color="#9467bd", alpha=0.1, linewidth=0.3)

        # Draw axes
        ax.plot([-1,1],[0,0],[0,0], color="#444", linewidth=0.5)
        ax.plot([0,0],[-1,1],[0,0], color="#444", linewidth=0.5)
        ax.plot([0,0],[0,0],[-1,1], color="#444", linewidth=0.5)

        # Draw qubit state vector
        theta = angles[i]
        phi   = angles[i] * 2
        qx    = np.sin(theta) * np.cos(phi)
        qy    = np.sin(theta) * np.sin(phi)
        qz    = np.cos(theta)
        ax.quiver(0, 0, 0, qx, qy, qz,
                  color="#00d4ff", linewidth=2, arrow_length_ratio=0.2)

        # Labels
        ax.text(0, 0, 1.2,  "|0⟩", color="white", fontsize=7, ha="center")
        ax.text(0, 0, -1.3, "|1⟩", color="white", fontsize=7, ha="center")
        ax.set_title(f"Q{i+1}\nθ={theta:.2f}", color="#00d4ff", fontsize=7)
        ax.set_xlim([-1,1])
        ax.set_ylim([-1,1])
        ax.set_zlim([-1,1])
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_zticks([])
        ax.grid(False)
        ax.xaxis.pane.fill = False
        ax.yaxis.pane.fill = False
        ax.zaxis.pane.fill = False

    fig.suptitle("Qubit States on Bloch Sphere (8 Qubits)",
                 color="white", fontsize=12, fontweight="bold")
    plt.tight_layout()
    return fig


def create_quantum_circuit_diagram():
    """Draw quantum circuit gate diagram."""
    fig, ax = plt.subplots(figsize=(12, 5))
    fig.patch.set_facecolor("#0a0a0a")
    ax.set_facecolor("#0a0a0a")
    ax.set_xlim(0, 10)
    ax.set_ylim(-0.5, 8.5)
    ax.axis("off")

    n_qubits = 8
    colors   = {"H": "#1f77b4", "Rz": "#9467bd", "CNOT": "#2ca02c", "ZZ": "#d62728"}

    # Draw qubit lines
    for i in range(n_qubits):
        y = n_qubits - 1 - i
        ax.plot([0.2, 9.8], [y, y], color="#444", linewidth=1, zorder=1)
        ax.text(-0.05, y, f"q{i}", color="#00d4ff",
                fontsize=9, ha="right", va="center", fontweight="bold")

    # H gates (Hadamard)
    for i in range(n_qubits):
        y = n_qubits - 1 - i
        rect = plt.Rectangle((0.3, y-0.2), 0.6, 0.4,
                               color=colors["H"], zorder=2, alpha=0.9)
        ax.add_patch(rect)
        ax.text(0.6, y, "H", color="white",
                fontsize=8, ha="center", va="center", fontweight="bold")

    # Rz gates (rotation)
    for i in range(n_qubits):
        y = n_qubits - 1 - i
        rect = plt.Rectangle((1.2, y-0.2), 0.8, 0.4,
                               color=colors["Rz"], zorder=2, alpha=0.9)
        ax.add_patch(rect)
        ax.text(1.6, y, f"Rz(x{i})", color="white",
                fontsize=7, ha="center", va="center", fontweight="bold")

    # ZZ entanglement gates
    zz_positions = [2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5]
    entangle_pairs = [(0,1),(1,2),(2,3),(3,4),(4,5),(5,6),(6,7)]

    for pos, (q1, q2) in zip(zz_positions[:len(entangle_pairs)], entangle_pairs):
        y1 = n_qubits - 1 - q1
        y2 = n_qubits - 1 - q2
        ax.plot([pos, pos], [y1, y2], color=colors["ZZ"],
                linewidth=2, zorder=2)
        for y in [y1, y2]:
            circle = plt.Circle((pos, y), 0.12,
                                  color=colors["ZZ"], zorder=3)
            ax.add_patch(circle)
            ax.text(pos, y, "ZZ", color="white",
                    fontsize=5, ha="center", va="center", fontweight="bold")

    # Second Rz layer
    for i in range(n_qubits):
        y = n_qubits - 1 - i
        rect = plt.Rectangle((9.0, y-0.2), 0.6, 0.4,
                               color=colors["Rz"], zorder=2, alpha=0.9)
        ax.add_patch(rect)
        ax.text(9.3, y, "Rz", color="white",
                fontsize=8, ha="center", va="center", fontweight="bold")

    # Legend
    legend_items = [
        plt.Rectangle((0,0), 1, 1, color=colors["H"],    label="Hadamard (H)"),
        plt.Rectangle((0,0), 1, 1, color=colors["Rz"],   label="Rotation Rz"),
        plt.Rectangle((0,0), 1, 1, color=colors["ZZ"],   label="ZZ Entanglement"),
    ]
    ax.legend(handles=legend_items, loc="upper right",
              facecolor="#1a1a2e", labelcolor="white", fontsize=9)
    ax.set_title("ZZFeatureMap Quantum Circuit (8 Qubits)",
                 color="white", fontsize=12, fontweight="bold", pad=15)
    plt.tight_layout()
    return fig


def create_feature_importance(xgb_model, fp):
    """Show which fingerprint bits matter most."""
    importances = xgb_model.feature_importances_
    top_idx     = np.argsort(importances)[::-1][:20]
    top_imp     = importances[top_idx]
    mol_bits    = fp[top_idx]

    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor("#0a0a0a")
    ax.set_facecolor("#1a1a2e")

    colors = ["#2ca02c" if mol_bits[i] == 1 else "#d62728"
              for i in range(len(top_idx))]

    bars = ax.bar(range(20), top_imp, color=colors, alpha=0.85)
    ax.set_xticks(range(20))
    ax.set_xticklabels([f"Bit\n{idx}" for idx in top_idx],
                        color="white", fontsize=7)
    ax.set_title("Top 20 Most Important Fingerprint Bits",
                  color="white", fontsize=12, fontweight="bold")
    ax.set_ylabel("Importance Score", color="white")
    ax.tick_params(colors="white")
    for spine in ax.spines.values():
        spine.set_edgecolor("#9467bd")

    legend_items = [
        mpatches.Patch(color="#2ca02c", label="Present in molecule"),
        mpatches.Patch(color="#d62728", label="Absent in molecule"),
    ]
    ax.legend(handles=legend_items, facecolor="#1a1a2e",
              labelcolor="white", fontsize=9)
    plt.tight_layout()
    return fig


def create_pca_analysis(fp_pca, fp_scaled):
    """Visualize PCA reduced features."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    fig.patch.set_facecolor("#0a0a0a")

    for ax in axes:
        ax.set_facecolor("#1a1a2e")
        ax.tick_params(colors="white")
        for spine in ax.spines.values():
            spine.set_edgecolor("#9467bd")

    # PCA values before scaling
    axes[0].bar(range(8), fp_pca[0], color="#9467bd", alpha=0.85)
    axes[0].set_title("PCA Features (Before Scaling)",
                       color="white", fontweight="bold")
    axes[0].set_xlabel("PCA Component", color="white")
    axes[0].set_ylabel("Value", color="white")
    axes[0].set_xticks(range(8))
    axes[0].set_xticklabels([f"PC{i+1}" for i in range(8)], color="white")

    # PCA values after scaling (quantum angles)
    axes[1].bar(range(8), fp_scaled[0], color="#00d4ff", alpha=0.85)
    axes[1].set_title("Quantum Rotation Angles [0, π]",
                       color="white", fontweight="bold")
    axes[1].set_xlabel("Qubit", color="white")
    axes[1].set_ylabel("Rotation Angle (radians)", color="white")
    axes[1].set_xticks(range(8))
    axes[1].set_xticklabels([f"Q{i+1}" for i in range(8)], color="white")
    axes[1].axhline(y=np.pi, color="red", linestyle="--",
                     alpha=0.5, label=f"π = {np.pi:.2f}")
    axes[1].legend(facecolor="#1a1a2e", labelcolor="white")

    fig.suptitle("PCA Feature Analysis — 1024 bits → 8 Quantum Features",
                  color="white", fontsize=12, fontweight="bold")
    plt.tight_layout()
    return fig


def create_fingerprint_heatmap(fp):
    """Visualize Morgan fingerprint as heatmap."""
    fig, ax = plt.subplots(figsize=(12, 3))
    fig.patch.set_facecolor("#0a0a0a")
    ax.set_facecolor("#0a0a0a")

    fp_matrix = fp.reshape(32, 32)
    im = ax.imshow(fp_matrix, cmap="plasma", aspect="auto", interpolation="nearest")
    plt.colorbar(im, ax=ax, label="Bit Value")
    ax.set_title("Morgan Fingerprint Heatmap (1024 bits → 32×32 grid)",
                  color="white", fontsize=12, fontweight="bold")
    ax.set_xlabel("Bit Position (column)", color="white")
    ax.set_ylabel("Bit Position (row)", color="white")
    ax.tick_params(colors="white")
    plt.tight_layout()
    return fig


def check_lipinski(smiles):
    """Check Lipinski Rule of 5 for drug-likeness."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None

    mw   = Descriptors.MolWt(mol)
    logp = Descriptors.MolLogP(mol)
    hbd  = rdMolDescriptors.CalcNumHBD(mol)
    hba  = rdMolDescriptors.CalcNumHBA(mol)
    tpsa = Descriptors.TPSA(mol)
    rb   = rdMolDescriptors.CalcNumRotatableBonds(mol)

    rules = {
        "Molecular Weight < 500 Da"       : (mw,   mw < 500,     f"{mw:.1f} Da"),
        "LogP < 5 (lipophilicity)"        : (logp, logp < 5,     f"{logp:.2f}"),
        "H-Bond Donors ≤ 5"               : (hbd,  hbd <= 5,     str(hbd)),
        "H-Bond Acceptors ≤ 10"           : (hba,  hba <= 10,    str(hba)),
        "TPSA < 140 Å² (permeability)"    : (tpsa, tpsa < 140,   f"{tpsa:.1f} Å²"),
        "Rotatable Bonds ≤ 10 (flexible)" : (rb,   rb <= 10,     str(rb)),
    }

    passed = sum(1 for _, (val, passed, disp) in rules.items() if passed)
    return rules, passed


def create_confidence_breakdown(classical_prob, quantum_prob, hybrid_prob):
    """Detailed confidence score visualization."""
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    fig.patch.set_facecolor("#0a0a0a")

    models = ["Classical\nXGBoost", "Quantum\nKernel SVM", "Hybrid\nCombined"]
    probs  = [classical_prob, quantum_prob, hybrid_prob]
    colors = ["#1f77b4", "#9467bd", "#2ca02c"]

    for i, (ax, model, prob, color) in enumerate(zip(axes, models, probs, colors)):
        ax.set_facecolor("#1a1a2e")

        # Gauge chart using pie
        active   = prob
        inactive = 1 - prob

        wedge_colors = [color, "#333333"]
        ax.pie(
            [active, inactive],
            colors=wedge_colors,
            startangle=90,
            counterclock=False,
            wedgeprops={"width": 0.4, "edgecolor": "#0a0a0a"}
        )

        verdict = "ACTIVE" if prob >= 0.5 else "INACTIVE"
        v_color = "#2ca02c" if prob >= 0.5 else "#d62728"

        ax.text(0, 0.1,  f"{prob*100:.1f}%",
                color="white",     fontsize=16, ha="center", fontweight="bold")
        ax.text(0, -0.2, verdict,
                color=v_color,     fontsize=10, ha="center", fontweight="bold")
        ax.set_title(model,
                     color="white", fontsize=10, fontweight="bold")

    fig.suptitle("Confidence Score Breakdown — All Models",
                  color="white", fontsize=12, fontweight="bold")
    plt.tight_layout()
    return fig


def show_bace1_explanation(prediction, hybrid_prob):
    """Show BACE-1 binding explanation based on prediction."""
    if prediction == "ACTIVE":
        return {
            "verdict"    : "✅ Potential BACE-1 Inhibitor",
            "color"      : "#2ca02c",
            "mechanism"  : "This molecule shows structural features compatible with BACE-1 active site binding.",
            "impact"     : f"With {hybrid_prob*100:.1f}% confidence, this molecule may block BACE-1 from cutting APP protein.",
            "next_steps" : "Recommended for in-vitro testing against BACE-1 enzyme.",
            "disease"    : "If confirmed, could reduce Amyloid-Beta production and slow Alzheimer's progression.",
            "icon"       : "🧬"
        }
    else:
        return {
            "verdict"    : "❌ Not a BACE-1 Inhibitor",
            "color"      : "#d62728",
            "mechanism"  : "This molecule lacks structural features required for BACE-1 active site binding.",
            "impact"     : f"With {(1-hybrid_prob)*100:.1f}% confidence, this molecule will NOT block BACE-1.",
            "next_steps" : "Consider structural modification to improve binding affinity.",
            "disease"    : "Not suitable as Alzheimer's drug candidate in current form.",
            "icon"       : "🔬"
        }


# ─── SIDEBAR ────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🧬 About This Tool")
    st.markdown("""
    Predicts whether a drug molecule inhibits
    **BACE-1** — enzyme linked to **Alzheimer's**.

    **Hybrid Quantum-Classical Pipeline:**
    - 🔵 Classical XGBoost — 82.2%
    - 🟣 Quantum Kernel SVM — 74.0%
    - 🟢 Hybrid Combined — 83.0%
    """)

    st.divider()
    st.markdown("## 💊 Example Molecules")
    examples = {
        "Aspirin"        : "CC(=O)Oc1ccccc1C(=O)O",
        "Ibuprofen"      : "CC(C)Cc1ccc(cc1)C(C)C(=O)O",
        "Caffeine"       : "Cn1c(=O)c2c(ncn2C)n(c1=O)C",
        "Known Inhibitor": "Fc1ncccc1-c1cc(ccc1)C1(N=C(N2C1=NCC(F)(F)C2)N)c1ccc(OC(F)F)cc1",
    }
    selected       = st.selectbox("Select example:", list(examples.keys()))
    example_smiles = examples[selected]

    st.divider()
    st.markdown("## ⚛️ Quantum Config")
    st.markdown("""
    - **Qubits:** 8
    - **Feature map:** ZZFeatureMap
    - **Entanglement:** Linear
    - **Kernel:** Fidelity Quantum
    - **Simulator:** Qiskit Aer
    """)

    st.divider()
    st.markdown("## 📊 Dataset")
    st.markdown("""
    - **Source:** MoleculeNet BACE
    - **Molecules:** 1,522
    - **Target:** BACE-1 inhibition
    - **Disease:** Alzheimer's
    """)


# ─── MAIN ───────────────────────────────────────────────────────
st.markdown('<div class="main-header">🧬 Quantum Drug Discovery Assistant</div>',
            unsafe_allow_html=True)
st.markdown('<div class="sub-header">Alzheimer\'s BACE-1 Inhibitor Prediction — Hybrid Quantum-Classical AI</div>',
            unsafe_allow_html=True)

st.markdown("### 🔬 Enter Molecule SMILES")
col1, col2 = st.columns([3, 1])
with col1:
    smiles_input = st.text_input("SMILES String:", value=example_smiles)
with col2:
    st.write("")
    st.write("")
    predict_btn = st.button("🚀 Predict", type="primary", use_container_width=True)

st.divider()

if predict_btn and smiles_input:
    mol = Chem.MolFromSmiles(smiles_input)
    if mol is None:
        st.error("❌ Invalid SMILES string!")
    else:
        with st.spinner("🔄 Running Hybrid Quantum-Classical Pipeline..."):
            try:
                xgb_model, qsvm_model, pca, scaler = load_models()
                results = run_hybrid_prediction(
                    smiles_input, xgb_model, qsvm_model, pca, scaler
                )
            except Exception as e:
                st.error(f"Error: {e}")
                st.stop()

        # ── Result Banner ──────────────────────────────────────
        st.markdown("### 🎯 Prediction Result")
        css_class = "result-active" if results["prediction"] == "ACTIVE" else "result-inactive"
        icon      = "✅" if results["prediction"] == "ACTIVE" else "❌"
        st.markdown(f"""
        <div class="{css_class}">
            {icon} {results['prediction']} — BACE-1 Inhibitor Prediction<br>
            <span style="font-size:1rem">
            Confidence: {results['confidence']*100:.1f}%
            </span>
        </div>
        """, unsafe_allow_html=True)

        st.write("")

        # ── Metric Cards ───────────────────────────────────────
        st.markdown("### 📊 Model Predictions Breakdown")
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f"""<div class="metric-card">
                <h3>🔵 Classical</h3><h2>{results['classical_prob']*100:.1f}%</h2>
                <p>XGBoost ACTIVE probability</p></div>""", unsafe_allow_html=True)
        with m2:
            st.markdown(f"""<div class="metric-card">
                <h3>🟣 Quantum</h3><h2>{results['quantum_prob']*100:.1f}%</h2>
                <p>Quantum Kernel ACTIVE probability</p></div>""", unsafe_allow_html=True)
        with m3:
            st.markdown(f"""<div class="metric-card">
                <h3>🟢 Hybrid</h3><h2>{results['hybrid_prob']*100:.1f}%</h2>
                <p>Combined ACTIVE probability</p></div>""", unsafe_allow_html=True)

        st.write("")

        # ── Confidence Breakdown ───────────────────────────────
        st.markdown("### 🎯 Confidence Score Breakdown")
        conf_fig = create_confidence_breakdown(
            results["classical_prob"],
            results["quantum_prob"],
            results["hybrid_prob"]
        )
        st.pyplot(conf_fig)

        st.divider()

        # ── Probability Chart ──────────────────────────────────
        st.markdown("### 📉 Probability Comparison")
        prob_fig = create_probability_chart(
            results["classical_prob"],
            results["quantum_prob"],
            results["hybrid_prob"]
        )
        st.pyplot(prob_fig)

        st.divider()

        # ── BACE-1 Explanation ─────────────────────────────────
        st.markdown("### 🧬 BACE-1 Binding Explanation")
        explanation = show_bace1_explanation(
            results["prediction"],
            results["hybrid_prob"]
        )
        b1, b2 = st.columns(2)
        with b1:
            st.markdown(f"""
            <div class="bace-card">
                <h4>{explanation['icon']} {explanation['verdict']}</h4>
                <p><b>Mechanism:</b> {explanation['mechanism']}</p>
                <p><b>Impact:</b> {explanation['impact']}</p>
            </div>""", unsafe_allow_html=True)
        with b2:
            st.markdown(f"""
            <div class="bace-card">
                <h4>🔭 Research Implications</h4>
                <p><b>Next Steps:</b> {explanation['next_steps']}</p>
                <p><b>Disease Impact:</b> {explanation['disease']}</p>
            </div>""", unsafe_allow_html=True)

        st.divider()

        # ── Molecule Visualization ─────────────────────────────
        st.markdown("### 🧪 Molecule Visualization")
        tab1, tab2 = st.tabs(["🔷 3D Interactive", "🔹 2D Structure"])
        with tab1:
            st.markdown("**Rotate:** Left drag | **Zoom:** Scroll | **Pan:** Right drag")
            html_3d = get_3d_html(smiles_input)
            if html_3d:
                st.components.v1.html(html_3d, height=420)
            else:
                st.warning("3D view not available for this molecule.")
        with tab2:
            img_2d = smiles_to_2d_image(smiles_input)
            if img_2d:
                st.image(img_2d, caption=f"2D Structure", width=400)

        st.divider()

        # ── Drug-likeness Lipinski ─────────────────────────────
        st.markdown("### 💊 Drug-likeness Analysis (Lipinski Rule of 5)")
        rules, passed = check_lipinski(smiles_input)
        score_color   = "#2ca02c" if passed >= 5 else "#d62728" if passed <= 3 else "#ff7f0e"
        st.markdown(f"""
        <div style="background:{score_color};padding:1rem;border-radius:10px;
                    color:white;text-align:center;font-size:1.2rem;font-weight:bold;">
            Drug-likeness Score: {passed}/6 Rules Passed
            {"✅ Excellent Drug Candidate" if passed >= 5
             else "⚠️ Moderate Drug-likeness" if passed >= 3
             else "❌ Poor Drug-likeness"}
        </div>""", unsafe_allow_html=True)

        st.write("")
        r1, r2, r3 = st.columns(3)
        cols        = [r1, r2, r3, r1, r2, r3]

        for i, (rule, (val, ok, display)) in enumerate(rules.items()):
            with cols[i]:
                css = "lipinski-pass" if ok else "lipinski-fail"
                icon = "✅" if ok else "❌"
                st.markdown(f"""
                <div class="{css}">
                    {icon} {rule}<br>
                    <b>Value: {display}</b>
                </div>""", unsafe_allow_html=True)

        st.divider()

        # ── Molecular Properties ───────────────────────────────
        st.markdown("### 🔬 Molecular Properties")
        props = get_molecule_properties(smiles_input)
        if props:
            p1, p2, p3, p4 = st.columns(4)
            pcols = [p1, p2, p3, p4]
            for i, (key, val) in enumerate(props.items()):
                with pcols[i % 4]:
                    st.metric(label=key, value=val)

        st.divider()

        # ── Fingerprint Heatmap ────────────────────────────────
        st.markdown("### 🔥 Morgan Fingerprint Heatmap")
        st.markdown("Each cell = one bit of the 1024-bit molecular fingerprint. Bright = present, Dark = absent.")
        heatmap_fig = create_fingerprint_heatmap(results["fp"])
        st.pyplot(heatmap_fig)

        st.divider()

        # ── Feature Importance ─────────────────────────────────
        st.markdown("### 📊 Feature Importance Analysis")
        st.markdown("Green = bit present in this molecule. Red = bit absent. Height = importance for prediction.")
        fi_fig = create_feature_importance(xgb_model, results["fp"])
        st.pyplot(fi_fig)

        st.divider()

        # ── PCA Analysis ───────────────────────────────────────
        st.markdown("### 📉 PCA Feature Analysis")
        st.markdown("How 1024 fingerprint bits are compressed into 8 quantum rotation angles.")
        pca_fig = create_pca_analysis(results["fp_pca"], results["fp_scaled"])
        st.pyplot(pca_fig)

        st.divider()

        # ── Quantum Circuit ────────────────────────────────────
        st.markdown("### ⚛️ Quantum Circuit Diagram")
        st.markdown("Actual gate-level view of the ZZFeatureMap circuit used for this prediction.")
        circuit_fig = create_quantum_circuit_diagram()
        st.pyplot(circuit_fig)

        st.divider()

        # ── Bloch Sphere ───────────────────────────────────────
        st.markdown("### 🔵 Qubit State Visualization (Bloch Sphere)")
        st.markdown("Each sphere shows the quantum state of one qubit after encoding molecular features.")
        bloch_fig = create_bloch_sphere(results["fp_scaled"])
        st.pyplot(bloch_fig)

        st.divider()

        # ── Benchmark ─────────────────────────────────────────
        st.markdown("### 📈 Model Benchmark Comparison")
        bench_fig = create_benchmark_chart()
        st.pyplot(bench_fig)

        st.divider()

        # ── Pipeline Summary ───────────────────────────────────
        st.markdown("### 🔄 Pipeline Summary")
        st.markdown("""
```
        SMILES Input
             ↓
        RDKit Morgan Fingerprint (1024 bits)
             ↓
        ┌──────────────────┐    ┌────────────────────────┐
        │ Classical Path   │    │ Quantum Path            │
        │ XGBoost          │    │ PCA → 8 features        │
        │ Full 1024 bits   │    │ ZZFeatureMap (8 qubits) │
        │ Accuracy: 82.2%  │    │ Quantum Kernel SVM      │
        │                  │    │ Accuracy: 74.0%         │
        └────────┬─────────┘    └───────────┬─────────────┘
                 │                           │
                 └─────────────┬─────────────┘
                               ↓
                      Hybrid Ensemble
                  (60% Classical + 40% Quantum)
                  Accuracy: 83.0% | ROC-AUC: 0.9301
                               ↓
                     ACTIVE / INACTIVE
```
        """)

else:
    st.markdown("### 👆 Enter a SMILES string above and click Predict")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""<div class="metric-card">
            <h3>🔵 Classical</h3><h2>82.2%</h2>
            <p>XGBoost Accuracy</p></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""<div class="metric-card">
            <h3>🟣 Quantum</h3><h2>74.0%</h2>
            <p>Quantum Kernel SVM</p></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown("""<div class="metric-card">
            <h3>🟢 Hybrid</h3><h2>83.0%</h2>
            <p>Best Combined</p></div>""", unsafe_allow_html=True)
    st.write("")
    st.markdown("### 📈 Model Benchmark")
    st.pyplot(create_benchmark_chart())