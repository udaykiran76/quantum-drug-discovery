import React from 'react';

function Header() {
  return (
    <header className="header">
      <div className="header-content">
        <div className="header-left">
          <span className="header-icon">🧬</span>
          <div>
            <h1 className="header-title">Quantum Drug Discovery</h1>
            <p className="header-subtitle">Alzheimer's BACE-1 Inhibitor Prediction</p>
          </div>
        </div>
        <div className="header-right">
          <div className="header-badge">
            <span>⚛️ Qiskit Powered</span>
          </div>
          <div className="header-badge green">
            <span>🎯 83.0% Accuracy</span>
          </div>
          <div className="header-badge purple">
            <span>💊 Alzheimer's Research</span>
          </div>
        </div>
      </div>
    </header>
  );
}

export default Header;
