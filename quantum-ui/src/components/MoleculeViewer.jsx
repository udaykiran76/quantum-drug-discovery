import React, { useState, useEffect } from 'react';

function MoleculeViewer({ smiles }) {
  const [sdfData, setSdfData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState(false);

  useEffect(() => {
    if (!smiles) return;
    setLoading(true);
    setError(false);
    setSdfData(null);

    fetch(
      `https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/smiles/${encodeURIComponent(smiles)}/SDF?record_type=3d`
    )
      .then(res => res.text())
      .then(data => {
        if (data && !data.includes('PUGREST.NotFound') && !data.includes('Status: 404')) {
          setSdfData(data);
        } else {
          setError(true);
        }
        setLoading(false);
      })
      .catch(() => {
        setError(true);
        setLoading(false);
      });
  }, [smiles]);

  const getViewerHTML = (sdf) => `
    <!DOCTYPE html>
    <html>
    <head>
      <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { background: #0a0a0a; overflow: hidden; width: 100%; height: 100vh; }
        #viewer { width: 100%; height: 100vh; position: relative; }
        .controls {
          position: absolute;
          bottom: 10px;
          left: 50%;
          transform: translateX(-50%);
          display: flex;
          gap: 8px;
          z-index: 100;
        }
        .ctrl-btn {
          background: rgba(148,103,189,0.8);
          border: 1px solid #9467bd;
          color: white;
          padding: 4px 10px;
          border-radius: 4px;
          cursor: pointer;
          font-size: 11px;
        }
        .ctrl-btn:hover { background: rgba(148,103,189,1); }
      </style>
      <script src="https://3dmol.org/build/3Dmol-min.js"></script>
    </head>
    <body>
      <div id="viewer"></div>
      <div class="controls">
        <button class="ctrl-btn" onclick="toggleSpin()">⟳ Spin</button>
        <button class="ctrl-btn" onclick="setStyle('stick')">Stick</button>
        <button class="ctrl-btn" onclick="setStyle('sphere')">Sphere</button>
        <button class="ctrl-btn" onclick="setStyle('both')">Both</button>
        <button class="ctrl-btn" onclick="viewer.zoomTo()">Reset</button>
      </div>
      <script>
        let spinning = true;
        let currentStyle = 'both';

        let viewer = $3Dmol.createViewer('viewer', {
          backgroundColor: '#0a0a0a'
        });

        let molData = \`${sdf.replace(/`/g, '\\`')}\`;

        viewer.addModel(molData, 'sdf');

        viewer.setStyle({}, {
          stick  : { colorscheme: 'RasmolAA', radius: 0.15 },
          sphere : { colorscheme: 'RasmolAA', scale: 0.3  }
        });

        viewer.zoomTo();
        viewer.spin(true);
        viewer.render();

        function toggleSpin() {
          spinning = !spinning;
          viewer.spin(spinning);
        }

        function setStyle(style) {
          currentStyle = style;
          if (style === 'stick') {
            viewer.setStyle({}, { stick: { colorscheme: 'RasmolAA', radius: 0.15 } });
          } else if (style === 'sphere') {
            viewer.setStyle({}, { sphere: { colorscheme: 'RasmolAA', scale: 0.4 } });
          } else {
            viewer.setStyle({}, {
              stick  : { colorscheme: 'RasmolAA', radius: 0.15 },
              sphere : { colorscheme: 'RasmolAA', scale: 0.3  }
            });
          }
          viewer.render();
        }
      </script>
    </body>
    </html>
  `;

  return (
    <div className="molecule-section">
      <h3 className="section-title">🔷 3D Interactive Molecule Viewer</h3>
      <p className="section-desc">
        Rotate: Left drag | Zoom: Scroll | Pan: Right drag | Use buttons to change view
      </p>

      <div className="viewer-container">
        {loading && (
          <div className="viewer-loading">
            <div className="loading-spinner" />
            <p>Loading 3D structure...</p>
          </div>
        )}

        {error && !loading && (
          <div className="viewer-loading">
            <p>⚠️ 3D structure not available for this molecule</p>
            <p style={{ fontSize: '0.8rem', color: '#666', marginTop: '0.5rem' }}>
              Try a well-known molecule like Aspirin or Caffeine
            </p>
          </div>
        )}

        {sdfData && !loading && (
          <iframe
            title="molecule-viewer"
            srcDoc={getViewerHTML(sdfData)}
            className="viewer-iframe"
            sandbox="allow-scripts"
          />
        )}
      </div>

      <div className="smiles-display">
        <span className="smiles-label">SMILES:</span>
        <code className="smiles-code">{smiles}</code>
      </div>

      <div className="viewer-legend">
        {[
          { color: '#ff4444', label: 'Oxygen' },
          { color: '#4444ff', label: 'Nitrogen' },
          { color: '#ffff44', label: 'Sulfur' },
          { color: '#aaaaaa', label: 'Carbon' },
          { color: '#ffffff', label: 'Hydrogen' },
          { color: '#44ffff', label: 'Fluorine' },
        ].map((item, i) => (
          <div key={i} className="legend-item">
            <div className="legend-dot" style={{ background: item.color }} />
            <span>{item.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default MoleculeViewer;