import React, { useRef, useEffect } from 'react';

function BlochSphere({ angle, label, index }) {
  const mountRef   = useRef(null);
  const sceneRef   = useRef(null);
  const frameRef   = useRef(null);
  const hoveredRef = useRef(false);

  useEffect(() => {
    if (!mountRef.current) return;

    const loadThree = async () => {
      if (!window.THREE) {
        const script = document.createElement('script');
        script.src   = 'https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js';
        script.async = true;
        document.head.appendChild(script);
        await new Promise(resolve => script.onload = resolve);
      }

      const THREE     = window.THREE;
      const container = mountRef.current;
      const width     = 160;
      const height    = 160;

      // Scene setup
      const scene    = new THREE.Scene();
      scene.background = new THREE.Color('#f5f3ff');

      const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 100);
      camera.position.set(2.8, 2, 2.8);
      camera.lookAt(0, 0, 0);

      const renderer = new THREE.WebGLRenderer({ antialias: true });
      renderer.setSize(width, height);
      renderer.setPixelRatio(window.devicePixelRatio);
      container.innerHTML = '';
      container.appendChild(renderer.domElement);

      sceneRef.current = { scene, camera, renderer };

      // Sphere wireframe
      const sphereGeo = new THREE.SphereGeometry(1, 24, 24);
      const sphereMat = new THREE.MeshBasicMaterial({
        color: 0x7c3aed, wireframe: true, transparent: true, opacity: 0.12
      });
      const sphere = new THREE.Mesh(sphereGeo, sphereMat);
      scene.add(sphere);

      // Equator ring
      const ringGeo = new THREE.TorusGeometry(1, 0.005, 8, 64);
      const ringMat = new THREE.MeshBasicMaterial({ color: 0x7c3aed, transparent: true, opacity: 0.3 });
      scene.add(new THREE.Mesh(ringGeo, ringMat));

      // Axis lines
      const makeAxis = (start, end, color) => {
        const geo = new THREE.BufferGeometry().setFromPoints([
          new THREE.Vector3(...start),
          new THREE.Vector3(...end)
        ]);
        return new THREE.Line(geo, new THREE.LineBasicMaterial({ color, transparent: true, opacity: 0.4 }));
      };

      scene.add(makeAxis([-1.4,0,0],[1.4,0,0], 0x1d4ed8));
      scene.add(makeAxis([0,-1.4,0],[0,1.4,0], 0x059669));
      scene.add(makeAxis([0,0,-1.4],[0,0,1.4], 0xdc2626));

      // Poles
      const poleGeo = new THREE.SphereGeometry(0.06, 8, 8);
      const pole0   = new THREE.Mesh(poleGeo, new THREE.MeshBasicMaterial({ color: 0x059669 }));
      const pole1   = new THREE.Mesh(poleGeo, new THREE.MeshBasicMaterial({ color: 0xdc2626 }));
      pole0.position.set(0,  1.0, 0);
      pole1.position.set(0, -1.0, 0);
      scene.add(pole0);
      scene.add(pole1);

      // State vector
      const theta = angle;
      const phi   = angle * 2.1 + index * 0.5;
      let vx = Math.sin(theta) * Math.cos(phi);
      let vy = Math.cos(theta);
      let vz = Math.sin(theta) * Math.sin(phi);

      const vectorPoints = [new THREE.Vector3(0,0,0), new THREE.Vector3(vx, vy, vz)];
      const vectorGeo    = new THREE.BufferGeometry().setFromPoints(vectorPoints);
      const vectorMat    = new THREE.LineBasicMaterial({ color: 0x7c3aed, linewidth: 3 });
      const vectorLine   = new THREE.Line(vectorGeo, vectorMat);
      scene.add(vectorLine);

      // Vector tip
      const tipGeo = new THREE.SphereGeometry(0.08, 12, 12);
      const tipMat = new THREE.MeshBasicMaterial({ color: 0x7c3aed });
      const tip    = new THREE.Mesh(tipGeo, tipMat);
      tip.position.set(vx, vy, vz);
      scene.add(tip);

      // Probability orbit path
      const orbitPoints = [];
      for (let i = 0; i <= 64; i++) {
        const t = (i / 64) * Math.PI * 2;
        orbitPoints.push(new THREE.Vector3(
          Math.sin(theta) * Math.cos(t),
          Math.cos(theta),
          Math.sin(theta) * Math.sin(t)
        ));
      }
      const orbitGeo = new THREE.BufferGeometry().setFromPoints(orbitPoints);
      const orbitMat = new THREE.LineBasicMaterial({ color: 0x1d4ed8, transparent: true, opacity: 0.25 });
      scene.add(new THREE.Line(orbitGeo, orbitMat));

      // Processing particles
      const particles  = [];
      const particleGeo = new THREE.SphereGeometry(0.03, 6, 6);
      const colors      = [0x7c3aed, 0x1d4ed8, 0x059669];

      for (let i = 0; i < 5; i++) {
        const mat = new THREE.MeshBasicMaterial({
          color: colors[i % 3], transparent: true, opacity: 0.8
        });
        const particle = new THREE.Mesh(particleGeo, mat);
        particles.push({ mesh: particle, offset: (i / 5) * Math.PI * 2, speed: 1.5 + i * 0.3 });
        scene.add(particle);
      }

      // Glow sphere
      const glowGeo = new THREE.SphereGeometry(1.05, 16, 16);
      const glowMat = new THREE.MeshBasicMaterial({
        color: 0x7c3aed, transparent: true, opacity: 0.04, side: THREE.BackSide
      });
      scene.add(new THREE.Mesh(glowGeo, glowMat));

      let time       = 0;
      let isSpinning = true;

      // Mouse interaction
      const el = renderer.domElement;
      el.addEventListener('mouseenter', () => {
        hoveredRef.current = true;
        sphereMat.opacity  = 0.25;
        vectorMat.color.set(0x1d4ed8);
        tipMat.color.set(0x1d4ed8);
      });
      el.addEventListener('mouseleave', () => {
        hoveredRef.current = false;
        sphereMat.opacity  = 0.12;
        vectorMat.color.set(0x7c3aed);
        tipMat.color.set(0x7c3aed);
      });

      // Animate
      const animate = () => {
        frameRef.current = requestAnimationFrame(animate);
        time += 0.02;

        const speed = hoveredRef.current ? 0.025 : 0.008;
        scene.rotation.y += speed;

        // Animate state vector precession
        const newPhi = phi + time * 0.5;
        const newVx  = Math.sin(theta) * Math.cos(newPhi);
        const newVy  = Math.cos(theta);
        const newVz  = Math.sin(theta) * Math.sin(newPhi);

        vectorGeo.setFromPoints([
          new THREE.Vector3(0, 0, 0),
          new THREE.Vector3(newVx, newVy, newVz)
        ]);
        tip.position.set(newVx, newVy, newVz);

        // Animate particles
        particles.forEach(({ mesh, offset, speed: s }) => {
          const t   = time * s + offset;
          mesh.position.set(
            Math.sin(theta) * Math.cos(t) * 0.95,
            Math.cos(theta) * 0.95,
            Math.sin(theta) * Math.sin(t) * 0.95
          );
          mesh.material.opacity = hoveredRef.current
            ? 0.5 + 0.4 * Math.sin(time * 3 + offset)
            : 0.3 + 0.3 * Math.sin(time * 2 + offset);
        });

        // Pulse glow on hover
        glowMat.opacity = hoveredRef.current
          ? 0.08 + 0.05 * Math.sin(time * 4)
          : 0.04;

        renderer.render(scene, camera);
      };

      animate();
    };

    loadThree();

    return () => {
      if (frameRef.current) cancelAnimationFrame(frameRef.current);
      if (sceneRef.current) sceneRef.current.renderer.dispose();
    };
  }, [angle, index]);

  return (
    <div className="bloch-sphere-container">
      <div className="bloch-label">{label}</div>
      <div ref={mountRef} className="bloch-canvas-3d" title="Hover to interact!" />
      <div className="bloch-angle">θ = {angle.toFixed(3)} rad</div>
    </div>
  );
}


function QuantumCircuit({ n_qubits = 8 }) {
  return (
    <div className="circuit-container">
      <h3 className="section-title">⚛️ ZZFeatureMap Quantum Circuit</h3>
      <p className="section-desc">Gate-level view of the quantum circuit used for molecular encoding</p>

      <div className="circuit-diagram">
        {Array.from({ length: n_qubits }, (_, i) => (
          <div key={i} className="circuit-row">

            <span className="qubit-label">q{i}</span>

            <div className="circuit-line" />

            {/* H gate */}
            <div className="gate h-gate">H</div>
            <div className="circuit-line" />

            {/* Rz gate */}
            <div className="gate rz-gate">Rz(x{i})</div>
            <div className="circuit-line" />

            {/* ZZ gate */}
            {i < n_qubits - 1 && (
              <div className="gate zz-gate">ZZ</div>
            )}
            {i === n_qubits - 1 && (
              <div className="gate-placeholder" />
            )}
            <div className="circuit-line" />

            {/* Second Rz */}
            <div className="gate rz-gate">Rz</div>
            <div className="circuit-line" />

            {/* Measure */}
            <div className="gate measure-gate">M</div>

          </div>
        ))}
      </div>

      <div className="circuit-legend">
        <div className="legend-gate h-gate-small">H</div>
        <span>Hadamard — creates superposition</span>
        <div className="legend-gate rz-gate-small">Rz</div>
        <span>Rotation — encodes feature value</span>
        <div className="legend-gate zz-gate-small">ZZ</div>
        <span>Entanglement — captures feature interactions</span>
        <div className="legend-gate measure-gate-small">M</div>
        <span>Measurement — collapses quantum state</span>
      </div>
    </div>
  );
}


function QuantumVisual({ scaledFeatures, pcaFeatures }) {
  return (
    <div className="quantum-section">

      {/* Bloch Spheres */}
      <h3 className="section-title">🔵 Qubit States — Bloch Sphere Visualization</h3>
      <p className="section-desc">
        Each sphere shows the quantum state of one qubit after encoding molecular features.
        The cyan arrow shows the state vector — its angle encodes the molecular feature value.
      </p>

      <div className="bloch-grid">
       {scaledFeatures && scaledFeatures.map((angle, i) => (
  <BlochSphere
    key={i}
    angle={angle}
    label={`Qubit ${i + 1}`}
    index={i}
  />
))}
      </div>

      {/* Quantum Circuit */}
      <QuantumCircuit n_qubits={8} />

      {/* Quantum Kernel Explanation */}
      <div className="kernel-explanation">
        <h3 className="section-title">🔬 Quantum Kernel — How It Works</h3>
        <div className="kernel-grid">
          <div className="kernel-card">
            <div className="kernel-step">1</div>
            <h4>Feature Encoding</h4>
            <p>8 PCA features are scaled to [0, π] and encoded as rotation angles into 8 qubits using ZZFeatureMap</p>
          </div>
          <div className="kernel-card">
            <div className="kernel-step">2</div>
            <h4>Quantum State</h4>
            <p>Each molecule becomes a quantum state |φ(x)⟩ in a high-dimensional Hilbert space impossible to represent classically</p>
          </div>
          <div className="kernel-card">
            <div className="kernel-step">3</div>
            <h4>Kernel Computation</h4>
            <p>Similarity between molecules is computed as K(x,z) = |⟨φ(x)|φ(z)⟩|² — the quantum inner product</p>
          </div>
          <div className="kernel-card">
            <div className="kernel-step">4</div>
            <h4>SVM Classification</h4>
            <p>Classical SVM uses the quantum kernel matrix to find the optimal decision boundary between ACTIVE and INACTIVE molecules</p>
          </div>
        </div>
      </div>

      {/* Why Quantum */}
      <div className="why-quantum">
        <h3 className="section-title">💡 Why Quantum for BACE-1?</h3>
        <div className="why-grid">
          <div className="why-card">
            <span className="why-icon">🪤</span>
            <h4>The Flap Problem</h4>
            <p>BACE-1 has a flexible flap that opens and closes. Classical computers treat atoms as static balls — quantum computers model this movement accurately.</p>
          </div>
          <div className="why-card">
            <span className="why-icon">⚡</span>
            <h4>Proton Dynamics</h4>
            <p>BACE-1 binding depends on single proton movements. Classical force fields get this wrong. Quantum simulation captures proton behavior natively.</p>
          </div>
          <div className="why-card">
            <span className="why-icon">🔬</span>
            <h4>Electron Correlation</h4>
            <p>When a drug enters BACE-1, electrons rearrange dynamically. Quantum computers represent this naturally — it is the language electrons speak.</p>
          </div>
          <div className="why-card">
            <span className="why-icon">📐</span>
            <h4>Hilbert Space</h4>
            <p>Quantum kernel maps molecules to exponentially large Hilbert space — revealing patterns between molecules that classical kernels cannot detect.</p>
          </div>
        </div>
      </div>

    </div>
  );
}

export default QuantumVisual;
