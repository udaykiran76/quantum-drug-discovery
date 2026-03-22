import React from 'react';

const EXAMPLES = [
  { name: "Known BACE Inhibitor", smiles: "Fc1ncccc1-c1cc(ccc1)C1(N=C(N2C1=NCC(F)(F)C2)N)c1ccc(OC(F)F)cc1" },
  { name: "Aspirin",              smiles: "CC(=O)Oc1ccccc1C(=O)O" },
  { name: "Ibuprofen",            smiles: "CC(C)Cc1ccc(cc1)C(C)C(=O)O" },
  { name: "Caffeine",             smiles: "Cn1c(=O)c2c(ncn2C)n(c1=O)C" },
];

function InputSection({ smiles, setSmiles, loading, error, onPredict, onExample }) {
  return (
    <div className="section">

      {/* Hero */}
      <div className="hero">
        <h2 className="hero-title">
          Find Alzheimer's Drug Candidates
        </h2>
        <p className="hero-subtitle">
          Enter a molecule SMILES string below. Our Hybrid Quantum-Classical AI
          will predict whether it can inhibit BACE-1 — the enzyme responsible
          for Alzheimer's disease.
        </p>
      </div>

      {/* How it works */}
      <div className="pipeline-cards">
        <div className="pipeline-card blue">
          <div className="pipeline-icon">🔬</div>
          <h3>Input</h3>
          <p>Enter SMILES string of any drug molecule</p>
        </div>
        <div className="pipeline-arrow">→</div>
        <div className="pipeline-card purple">
          <div className="pipeline-icon">⚛️</div>
          <h3>Quantum</h3>
          <p>ZZFeatureMap encodes molecule into 8 qubits</p>
        </div>
        <div className="pipeline-arrow">→</div>
        <div className="pipeline-card green">
          <div className="pipeline-icon">🎯</div>
          <h3>Predict</h3>
          <p>Hybrid model gives ACTIVE or INACTIVE verdict</p>
        </div>
      </div>

      {/* Input box */}
      <div className="input-card">
        <label className="input-label">
          🧪 Enter SMILES String
        </label>
        <div className="input-row">
          <input
            className="smiles-input"
            type="text"
            value={smiles}
            onChange={e => setSmiles(e.target.value)}
            placeholder="e.g. CC(=O)Oc1ccccc1C(=O)O"
            onKeyPress={e => e.key === 'Enter' && onPredict()}
          />
          <button
            className={`predict-btn ${loading ? 'loading' : ''}`}
            onClick={onPredict}
            disabled={loading}
          >
            {loading ? '⏳ Analyzing...' : '🚀 Predict'}
          </button>
        </div>
        {error && <p className="error-msg">❌ {error}</p>}
      </div>

      {/* Example molecules */}
      <div className="examples-section">
        <h3 className="examples-title">💊 Try Example Molecules</h3>
        <div className="examples-grid">
          {EXAMPLES.map((ex, i) => (
            <button
              key={i}
              className="example-btn"
              onClick={() => onExample(ex.smiles)}
            >
              <span className="example-name">{ex.name}</span>
              <span className="example-smiles">{ex.smiles.substring(0, 30)}...</span>
            </button>
          ))}
        </div>
      </div>

      {/* Info cards */}
      <div className="info-grid">
        <div className="info-card">
          <h3>🧬 About BACE-1</h3>
          <p>
            BACE-1 is an enzyme that cuts APP protein in the wrong place,
            creating Amyloid-Beta fragments that form plaques in the brain —
            the root cause of Alzheimer's disease.
          </p>
        </div>
        <div className="info-card">
          <h3>⚛️ Quantum Advantage</h3>
          <p>
            Our Quantum Kernel maps molecules into high-dimensional Hilbert
            space using Qiskit's ZZFeatureMap with 8 qubits — capturing
            patterns invisible to classical ML models.
          </p>
        </div>
        <div className="info-card">
          <h3>🎯 Hybrid Pipeline</h3>
          <p>
            We combine Classical XGBoost (82.2%) with Quantum Kernel SVM
            (74.0%) using a 60/40 weighted ensemble to achieve 83.0%
            accuracy and 0.9301 ROC-AUC.
          </p>
        </div>
      </div>

    </div>
  );
}

export default InputSection;
