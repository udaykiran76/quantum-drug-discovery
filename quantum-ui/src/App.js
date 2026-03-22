import React, { useState } from 'react';
import axios from 'axios';
import Header from './components/Header';
import InputSection from './components/InputSection';
import ResultSection from './components/ResultSection';
import BenchmarkSection from './components/BenchmarkSection';
import './index.css';

const API = 'http://localhost:8000';

function App() {
  const [smiles, setSmiles]     = useState('');
  const [result, setResult]     = useState(null);
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState('');
  const [activeTab, setActiveTab] = useState('predict');

  const handlePredict = async () => {
    if (!smiles.trim()) {
      setError('Please enter a SMILES string');
      return;
    }
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await axios.post(`${API}/predict`, { smiles });
      setResult({ ...response.data, smiles });
      setActiveTab('result');
    } catch (err) {
      setError('Prediction failed. Make sure backend is running.');
    } finally {
      setLoading(false);
    }
  };

  const handleExample = (exampleSmiles) => {
    setSmiles(exampleSmiles);
    setResult(null);
    setError('');
  };

  return (
    <div className="app">
      <Header />
      <main className="main">
        <div className="tab-bar">
          {['predict', 'result', 'benchmark'].map(tab => (
            <button
              key={tab}
              className={`tab-btn ${activeTab === tab ? 'active' : ''}`}
              onClick={() => setActiveTab(tab)}
            >
              {tab === 'predict'   && '🔬 Predict'}
              {tab === 'result'    && '🎯 Results'}
              {tab === 'benchmark' && '📊 Benchmark'}
            </button>
          ))}
        </div>

        {activeTab === 'predict' && (
          <InputSection
            smiles={smiles}
            setSmiles={setSmiles}
            loading={loading}
            error={error}
            onPredict={handlePredict}
            onExample={handleExample}
          />
        )}

        {activeTab === 'result' && (
          <ResultSection result={result} />
        )}

        {activeTab === 'benchmark' && (
          <BenchmarkSection />
        )}
      </main>
    </div>
  );
}

export default App;
