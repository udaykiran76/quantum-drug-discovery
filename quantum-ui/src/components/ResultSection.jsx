import React, { useState } from 'react';
import MoleculeViewer from './MoleculeViewer';
import QuantumVisual from './QuantumVisual';

function ResultSection({ result }) {
  const [activeTab, setActiveTab] = useState('overview');

  if (!result) {
    return (
      <div className="no-result">
        <div className="no-result-icon">🔬</div>
        <h2>No Prediction Yet</h2>
        <p>Go to Predict tab and enter a SMILES string to see results here.</p>
      </div>
    );
  }

  const isActive = result.prediction === 'ACTIVE';

  const tabs = ['overview', 'molecule', 'quantum', 'properties', 'lipinski'];

  return (
    <div className="section">

      {/* Result Banner */}
      <div className={`result-banner ${isActive ? 'active' : 'inactive'}`}>
        <div className="result-icon">{isActive ? '✅' : '❌'}</div>
        <div className="result-text">
          <h2>{isActive ? 'ACTIVE — BACE-1 Inhibitor' : 'INACTIVE — Not a BACE-1 Inhibitor'}</h2>
          <p>
            {isActive
              ? `This molecule shows ${result.confidence}% confidence of inhibiting BACE-1 — promising Alzheimer's drug candidate!`
              : `This molecule shows ${result.confidence}% confidence of NOT inhibiting BACE-1.`
            }
          </p>
        </div>
      </div>

      {/* Model Cards */}
      <div className="model-cards">
        <div className="model-card blue">
          <div className="model-icon">🔵</div>
          <h3>Classical XGBoost</h3>
          <div className="model-prob">{result.classical_prob}%</div>
          <p>ACTIVE probability</p>
          <div className="prob-bar">
            <div className="prob-fill blue" style={{ width: `${result.classical_prob}%` }}></div>
          </div>
        </div>
        <div className="model-card purple">
          <div className="model-icon">🟣</div>
          <h3>Quantum Kernel SVM</h3>
          <div className="model-prob">{result.quantum_prob}%</div>
          <p>ACTIVE probability</p>
          <div className="prob-bar">
            <div className="prob-fill purple" style={{ width: `${result.quantum_prob}%` }}></div>
          </div>
        </div>
        <div className="model-card green">
          <div className="model-icon">🟢</div>
          <h3>Hybrid Combined</h3>
          <div className="model-prob">{result.hybrid_prob}%</div>
          <p>ACTIVE probability</p>
          <div className="prob-bar">
            <div className="prob-fill green" style={{ width: `${result.hybrid_prob}%` }}></div>
          </div>
        </div>
      </div>

      {/* BACE-1 Explanation */}
      <div className={`bace-explanation ${isActive ? 'active' : 'inactive'}`}>
        <div className="bace-left">
          <h3>{isActive ? '🧬 Potential BACE-1 Inhibitor' : '🔬 Not a BACE-1 Inhibitor'}</h3>
          <p>{isActive
            ? 'This molecule shows structural features compatible with BACE-1 active site binding. It may block BACE-1 from cutting APP protein, reducing Amyloid-Beta production.'
            : 'This molecule lacks structural features required for BACE-1 active site binding. It will not block the enzyme from creating Amyloid-Beta plaques.'
          }</p>
        </div>
        <div className="bace-right">
          <h3>🔭 Research Impact</h3>
          <p>{isActive
            ? 'Recommended for in-vitro testing against BACE-1. If confirmed, could slow Alzheimer\'s progression by reducing plaque formation.'
            : 'Consider structural modification to improve binding affinity. Current form not suitable as Alzheimer\'s drug candidate.'
          }</p>
        </div>
      </div>

      {/* Sub Tabs */}
      <div className="sub-tab-bar">
        {tabs.map(tab => (
          <button
            key={tab}
            className={`sub-tab-btn ${activeTab === tab ? 'active' : ''}`}
            onClick={() => setActiveTab(tab)}
          >
            {tab === 'overview'    && '📊 Overview'}
            {tab === 'molecule'    && '🧪 3D Molecule'}
            {tab === 'quantum'     && '⚛️ Quantum'}
            {tab === 'properties'  && '🔬 Properties'}
            {tab === 'lipinski'    && '💊 Drug-likeness'}
          </button>
        ))}
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div className="tab-content">
          <h3 className="section-title">📊 Prediction Breakdown</h3>
          <div className="breakdown-table">
            <div className="breakdown-row header">
              <span>Model</span>
              <span>Probability</span>
              <span>Verdict</span>
            </div>
            {[
              { name: '🔵 Classical XGBoost',       prob: result.classical_prob },
              { name: '🟣 Quantum Kernel SVM',       prob: result.quantum_prob },
              { name: '🟢 Hybrid Classical+Quantum', prob: result.hybrid_prob },
            ].map((row, i) => (
              <div key={i} className="breakdown-row">
                <span>{row.name}</span>
                <span>{row.prob}%</span>
                <span className={row.prob >= 50 ? 'verdict-active' : 'verdict-inactive'}>
                  {row.prob >= 50 ? '✅ ACTIVE' : '❌ INACTIVE'}
                </span>
              </div>
            ))}
          </div>

          <h3 className="section-title">🔥 Fingerprint Heatmap</h3>
          <p className="section-desc">1024-bit Morgan fingerprint — bright = molecular pattern present</p>
          <div className="heatmap">
            {result.fingerprint.slice(0, 512).map((bit, i) => (
              <div
                key={i}
                className="heatmap-cell"
                style={{ backgroundColor: bit === 1 ? '#9467bd' : '#1a1a2e' }}
                title={`Bit ${i}: ${bit}`}
              />
            ))}
          </div>
        </div>
      )}

      {/* Molecule Tab */}
      {activeTab === 'molecule' && (
        <div className="tab-content">
          <MoleculeViewer smiles={result.smiles} />
        </div>
      )}

      {/* Quantum Tab */}
      {activeTab === 'quantum' && (
        <div className="tab-content">
          <QuantumVisual
            scaledFeatures={result.scaled_features}
            pcaFeatures={result.pca_features}
          />
        </div>
      )}

      {/* Properties Tab */}
      {activeTab === 'properties' && (
        <div className="tab-content">
          <h3 className="section-title">🔬 Molecular Properties</h3>
          <div className="properties-grid">
            {result.properties && Object.entries(result.properties).map(([key, val]) => (
              <div key={key} className="property-card">
                <div className="property-value">{val}</div>
                <div className="property-name">{key}</div>
              </div>
            ))}
          </div>

          <h3 className="section-title">📉 PCA Feature Analysis</h3>
          <p className="section-desc">1024 fingerprint bits compressed to 8 quantum rotation angles</p>
          <div className="pca-bars">
            {result.scaled_features && result.scaled_features.map((val, i) => (
              <div key={i} className="pca-bar-row">
                <span className="pca-label">Q{i + 1}</span>
                <div className="pca-bar-bg">
                  <div
                    className="pca-bar-fill"
                    style={{ width: `${(val / Math.PI) * 100}%` }}
                  />
                </div>
                <span className="pca-value">{val.toFixed(3)}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Lipinski Tab */}
      {activeTab === 'lipinski' && (
        <div className="tab-content">
          <h3 className="section-title">💊 Lipinski Rule of 5 — Drug-likeness Analysis</h3>
          {result.lipinski && (
            <>
              <div className={`lipinski-score ${result.lipinski.passed >= 5 ? 'good' : result.lipinski.passed >= 3 ? 'medium' : 'bad'}`}>
                {result.lipinski.passed}/{result.lipinski.total} Rules Passed —
                {result.lipinski.passed >= 5 ? ' ✅ Excellent Drug Candidate' : result.lipinski.passed >= 3 ? ' ⚠️ Moderate Drug-likeness' : ' ❌ Poor Drug-likeness'}
              </div>
              <div className="lipinski-grid">
                {Object.entries(result.lipinski.rules).map(([rule, data]) => (
                  <div key={rule} className={`lipinski-card ${data.passed ? 'pass' : 'fail'}`}>
                    <span className="lipinski-icon">{data.passed ? '✅' : '❌'}</span>
                    <span className="lipinski-rule">{rule}</span>
                    <span className="lipinski-value">{data.value}</span>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      )}

    </div>
  );
}

export default ResultSection;
