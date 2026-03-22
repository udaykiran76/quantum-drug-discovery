import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const data = [
  { name: 'Classical\nXGBoost',        accuracy: 82.2, roc_auc: 92.25 },
  { name: 'Quantum\nKernel SVM',       accuracy: 74.0, roc_auc: 84.87 },
  { name: 'Hybrid\nClassical+Quantum', accuracy: 83.0, roc_auc: 93.01 },
];

const COLORS = {
  classical : '#1f77b4',
  quantum   : '#9467bd',
  hybrid    : '#2ca02c',
};

function BenchmarkSection() {
  return (
    <div className="section">

      <div className="benchmark-header">
        <h2>📊 Model Benchmark Comparison</h2>
        <p>Classical vs Quantum vs Hybrid — Performance Analysis on MoleculeNet BACE Dataset</p>
      </div>

      {/* Summary Cards */}
      <div className="benchmark-cards">
        <div className="benchmark-card blue">
          <h3>🔵 Classical XGBoost</h3>
          <div className="bench-metric">
            <span className="bench-val">82.2%</span>
            <span className="bench-label">Accuracy</span>
          </div>
          <div className="bench-metric">
            <span className="bench-val">0.9225</span>
            <span className="bench-label">ROC-AUC</span>
          </div>
          <div className="bench-detail">
            <p>✅ Trained on 1,210 samples</p>
            <p>✅ Full 1,024-bit fingerprint</p>
            <p>✅ Fast training (~2 min)</p>
          </div>
        </div>

        <div className="benchmark-card purple">
          <h3>🟣 Quantum Kernel SVM</h3>
          <div className="bench-metric">
            <span className="bench-val">74.0%</span>
            <span className="bench-label">Accuracy</span>
          </div>
          <div className="bench-metric">
            <span className="bench-val">0.8487</span>
            <span className="bench-label">ROC-AUC</span>
          </div>
          <div className="bench-detail">
            <p>⚛️ Trained on 200 samples</p>
            <p>⚛️ 8 PCA features → 8 qubits</p>
            <p>⚛️ ZZFeatureMap encoding</p>
          </div>
        </div>

        <div className="benchmark-card green">
          <h3>🟢 Hybrid Combined</h3>
          <div className="bench-metric">
            <span className="bench-val">83.0%</span>
            <span className="bench-label">Accuracy</span>
          </div>
          <div className="bench-metric">
            <span className="bench-val">0.9301</span>
            <span className="bench-label">ROC-AUC</span>
          </div>
          <div className="bench-detail">
            <p>🏆 Best accuracy overall</p>
            <p>🏆 Best ROC-AUC overall</p>
            <p>🏆 60% Classical + 40% Quantum</p>
          </div>
        </div>
      </div>

      {/* Accuracy Chart */}
      <div className="chart-card">
        <h3>📈 Accuracy Comparison (%)</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
            <XAxis dataKey="name" tick={{ fill: '#fff', fontSize: 12 }} />
            <YAxis domain={[60, 90]} tick={{ fill: '#fff' }} />
            <Tooltip
              contentStyle={{ backgroundColor: '#1a1a2e', border: '1px solid #9467bd', borderRadius: '8px' }}
              labelStyle={{ color: '#fff' }}
            />
            <Bar dataKey="accuracy" name="Accuracy (%)" radius={[6, 6, 0, 0]}
              fill="url(#colorGrad)"
              label={{ position: 'top', fill: '#fff', fontWeight: 'bold' }}
            />
            <defs>
              <linearGradient id="colorGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%"   stopColor="#9467bd" />
                <stop offset="100%" stopColor="#1f77b4" />
              </linearGradient>
            </defs>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* ROC-AUC Chart */}
      <div className="chart-card">
        <h3>📈 ROC-AUC Comparison (×100)</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
            <XAxis dataKey="name" tick={{ fill: '#fff', fontSize: 12 }} />
            <YAxis domain={[75, 100]} tick={{ fill: '#fff' }} />
            <Tooltip
              contentStyle={{ backgroundColor: '#1a1a2e', border: '1px solid #2ca02c', borderRadius: '8px' }}
              labelStyle={{ color: '#fff' }}
            />
            <Bar dataKey="roc_auc" name="ROC-AUC (×100)" radius={[6, 6, 0, 0]}
              fill="url(#colorGrad2)"
              label={{ position: 'top', fill: '#fff', fontWeight: 'bold' }}
            />
            <defs>
              <linearGradient id="colorGrad2" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%"   stopColor="#2ca02c" />
                <stop offset="100%" stopColor="#1f77b4" />
              </linearGradient>
            </defs>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Pipeline */}
      <div className="pipeline-section">
        <h3>🔄 Complete Pipeline</h3>
        <div className="pipeline-flow">
          {[
            { icon: '🧪', title: 'SMILES Input',        desc: 'Drug molecule text' },
            { icon: '🔬', title: 'Morgan Fingerprint',   desc: '1024-bit vector' },
            { icon: '📉', title: 'PCA Reduction',        desc: '1024 → 8 features' },
            { icon: '⚛️', title: 'ZZFeatureMap',         desc: '8 qubits encoding' },
            { icon: '🤖', title: 'Hybrid Prediction',    desc: '83.0% accuracy' },
            { icon: '🎯', title: 'ACTIVE/INACTIVE',      desc: 'Final verdict' },
          ].map((step, i) => (
            <React.Fragment key={i}>
              <div className="pipeline-step">
                <div className="step-icon">{step.icon}</div>
                <div className="step-title">{step.title}</div>
                <div className="step-desc">{step.desc}</div>
              </div>
              {i < 5 && <div className="step-arrow">→</div>}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* Dataset Info */}
      <div className="dataset-card">
        <h3>📚 Dataset Information</h3>
        <div className="dataset-grid">
          {[
            { label: 'Dataset',      value: 'MoleculeNet BACE' },
            { label: 'Molecules',    value: '1,522' },
            { label: 'Training',     value: '1,210 samples' },
            { label: 'Testing',      value: '152 samples' },
            { label: 'Features',     value: '1,024 bits' },
            { label: 'Target',       value: 'BACE-1 inhibition' },
            { label: 'Disease',      value: "Alzheimer's" },
            { label: 'Qubits Used',  value: '8' },
          ].map((item, i) => (
            <div key={i} className="dataset-item">
              <span className="dataset-label">{item.label}</span>
              <span className="dataset-value">{item.value}</span>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
}

export default BenchmarkSection;
