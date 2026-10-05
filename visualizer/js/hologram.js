// visualizer/js/hologram.js
// Procedural holographic scale comparison landmark system (Jet, Eiffel Tower, Burj Khalifa)

let hologramGroup = null;
let hologramMaterial = null;
let hologramEnabled = true;

function initHologram(scene) {
  hologramGroup = new THREE.Group();
  hologramGroup.name = "hologramGroup";
  hologramGroup.visible = false;
  scene.add(hologramGroup);

  hologramMaterial = new THREE.LineBasicMaterial({
    color: 0x00f3ff,
    transparent: true,
    opacity: 0.85,
    blending: THREE.AdditiveBlending,
    depthWrite: false
  });
  window.hologramMaterial = hologramMaterial;
}

function clearHologramGroup() {
  if (!hologramGroup) return;
  while (hologramGroup.children.length > 0) {
    const child = hologramGroup.children[0];
    hologramGroup.remove(child);
    if (child.isGroup) {
      while (child.children.length > 0) {
        const subChild = child.children[0];
        child.remove(subChild);
        if (subChild.geometry) subChild.geometry.dispose();
        if (subChild.material) {
          if (subChild.material.map) subChild.material.map.dispose();
          if (subChild.material !== hologramMaterial) subChild.material.dispose();
        }
      }
    } else {
      if (child.geometry) child.geometry.dispose();
      if (child.material) {
        if (child.material.map) child.material.map.dispose();
        if (child.material !== hologramMaterial) child.material.dispose();
      }
    }
  }
}

function createLandmarkHologram(asteroidDiameterMeters, geoSize) {
  clearHologramGroup();
  if (!hologramEnabled || !asteroidDiameterMeters) return null;

  const diam = Number(asteroidDiameterMeters) || 100;
  let landmarkName = "";
  let landmarkHeight = 0;
  let landmarkWidth = 0;
  let landmarkDim = "";
  const pts = [];

  function addSeg(x1, y1, z1, x2, y2, z2) {
    pts.push(new THREE.Vector3(x1, y1, z1), new THREE.Vector3(x2, y2, z2));
  }

  if (diam < 100) {
    // Passenger jet silhouette (length ~70m, wingspan ~65m)
    landmarkName = "Passenger Jet (747)";
    landmarkHeight = 70;
    landmarkWidth = 65;
    landmarkDim = "70m Length";

    // Nose cone & Cockpit
    addSeg(0, 70, 0, -3.2, 62, 0);
    addSeg(0, 70, 0, 3.2, 62, 0);
    addSeg(-3.2, 62, 0, 3.2, 62, 0);
    addSeg(0, 70, 0, 0, 62, 3);
    addSeg(-3.2, 62, 0, 0, 62, 3);
    addSeg(3.2, 62, 0, 0, 62, 3);
    addSeg(-2.8, 64, 1.5, 2.8, 64, 1.5);

    // Fuselage tube
    addSeg(-3.2, 62, 0, -3.2, 10, 0);
    addSeg(3.2, 62, 0, 3.2, 10, 0);
    addSeg(0, 62, 3, 0, 10, 3);
    addSeg(-3.2, 45, 0, 3.2, 45, 0);
    addSeg(-3.2, 28, 0, 3.2, 28, 0);

    // Left Wing
    addSeg(-3.2, 42, 0, -32.5, 22, 0);
    addSeg(-32.5, 22, 0, -32.5, 27, 0);
    addSeg(-32.5, 27, 0, -3.2, 50, 0);
    addSeg(-32.5, 27, 0, -32.5, 32, 2.5); // Winglet
    addSeg(-12, 30, -2, -12, 38, -2);     // Engine
    addSeg(-10, 34, -2, -14, 34, -2);

    // Right Wing
    addSeg(3.2, 42, 0, 32.5, 22, 0);
    addSeg(32.5, 22, 0, 32.5, 27, 0);
    addSeg(32.5, 27, 0, 3.2, 50, 0);
    addSeg(32.5, 27, 0, 32.5, 32, 2.5);  // Winglet
    addSeg(12, 30, -2, 12, 38, -2);      // Engine
    addSeg(10, 34, -2, 14, 34, -2);

    // Horizontal Tail Stabilizers
    addSeg(-3.2, 6, 0, -12.5, 2, 0);
    addSeg(-12.5, 2, 0, -12.5, 5, 0);
    addSeg(-12.5, 5, 0, -3.2, 10, 0);
    addSeg(3.2, 6, 0, 12.5, 2, 0);
    addSeg(12.5, 2, 0, 12.5, 5, 0);
    addSeg(12.5, 5, 0, 3.2, 10, 0);

    // Vertical Tail Fin & Closure
    addSeg(0, 12, 0, 0, 2, 16);
    addSeg(0, 2, 16, 0, 0, 14);
    addSeg(0, 0, 14, 0, 0, 0);
    addSeg(-3.2, 10, 0, 0, 0, 0);
    addSeg(3.2, 10, 0, 0, 0, 0);

  } else if (diam <= 450) {
    // Eiffel Tower silhouette (height 330m, stepped tapered wireframe lines)
    landmarkName = "Eiffel Tower";
    landmarkHeight = 330;
    landmarkWidth = 125;
    landmarkDim = "330m Height";

    // Base Pillars & Ground Ties
    addSeg(-62.5, 0, 0, -38, 57, 0);
    addSeg(62.5, 0, 0, 38, 57, 0);
    addSeg(-38, 0, 0, -25, 57, 0);
    addSeg(38, 0, 0, 25, 57, 0);
    addSeg(-62.5, 0, 0, -38, 0, 0);
    addSeg(38, 0, 0, 62.5, 0, 0);

    // Base Arch
    addSeg(-25, 0, 0, -18, 30, 0);
    addSeg(-18, 30, 0, 0, 40, 0);
    addSeg(0, 40, 0, 18, 30, 0);
    addSeg(18, 30, 0, 25, 0, 0);

    // Base Trusses
    addSeg(-62.5, 0, 0, -25, 57, 0);
    addSeg(-38, 0, 0, -38, 57, 0);
    addSeg(62.5, 0, 0, 25, 57, 0);
    addSeg(38, 0, 0, 38, 57, 0);

    // Level 1 Platform (Y = 57 to 62)
    addSeg(-42, 57, 0, 42, 57, 0);
    addSeg(-40, 62, 0, 40, 62, 0);
    addSeg(-42, 57, 0, -40, 62, 0);
    addSeg(42, 57, 0, 40, 62, 0);

    // Tier 2 (Y = 62 to 115)
    addSeg(-35, 62, 0, -20, 115, 0);
    addSeg(35, 62, 0, 20, 115, 0);
    addSeg(-20, 62, 0, -12, 115, 0);
    addSeg(20, 62, 0, 12, 115, 0);
    addSeg(-35, 62, 0, -12, 115, 0);
    addSeg(-20, 62, 0, -20, 115, 0);
    addSeg(35, 62, 0, 12, 115, 0);
    addSeg(20, 62, 0, 20, 115, 0);

    // Level 2 Platform (Y = 115 to 120)
    addSeg(-24, 115, 0, 24, 115, 0);
    addSeg(-22, 120, 0, 22, 120, 0);
    addSeg(-24, 115, 0, -22, 120, 0);
    addSeg(24, 115, 0, 22, 120, 0);

    // Tapered Shaft (Y = 120 to 276)
    addSeg(-18, 120, 0, -4, 276, 0);
    addSeg(18, 120, 0, 4, 276, 0);
    addSeg(0, 120, 0, 0, 276, 0);

    let prevY = 120, prevW = 18;
    [160, 200, 240, 276].forEach(y => {
      const w = 18 - (18 - 4) * ((y - 120) / (276 - 120));
      addSeg(-w, y, 0, w, y, 0);
      addSeg(-prevW, prevY, 0, w, y, 0);
      addSeg(prevW, prevY, 0, -w, y, 0);
      prevY = y;
      prevW = w;
    });

    // Level 3 Platform & Dome (Y = 276 to 295)
    addSeg(-7, 276, 0, 7, 276, 0);
    addSeg(-4, 276, 0, -3, 295, 0);
    addSeg(4, 276, 0, 3, 295, 0);
    addSeg(-3, 295, 0, 3, 295, 0);

    // Lantern & Spire (Y = 295 to 330)
    addSeg(-2, 295, 0, -1.5, 305, 0);
    addSeg(2, 295, 0, 1.5, 305, 0);
    addSeg(-1.5, 305, 0, 1.5, 305, 0);
    addSeg(0, 305, 0, 0, 330, 0);
    addSeg(-3, 318, 0, 3, 318, 0);

  } else {
    // Skyscraper (Burj Khalifa silhouette, height 828m, stepped vertical setbacks)
    landmarkName = "Burj Khalifa";
    landmarkHeight = 828;
    landmarkWidth = 140;
    landmarkDim = "828m Height";

    // Base Podium
    addSeg(-70, 0, 0, 70, 0, 0);
    addSeg(-70, 0, 0, -70, 80, 0);
    addSeg(70, 0, 0, 70, 80, 0);
    addSeg(-70, 40, 0, 70, 40, 0);

    // Central Spine Line
    addSeg(0, 0, 0, 0, 750, 0);

    // Stepped Setbacks
    const setbacks = [
      { y0: 80, y1: 160, xL: -58, xR: 70, shelfL: -70, shelfR: 70 },
      { y0: 160, y1: 240, xL: -58, xR: 50, shelfL: -58, shelfR: 70 },
      { y0: 240, y1: 320, xL: -46, xR: 50, shelfL: -58, shelfR: 50 },
      { y0: 320, y1: 400, xL: -46, xR: 38, shelfL: -46, shelfR: 50 },
      { y0: 400, y1: 480, xL: -34, xR: 38, shelfL: -46, shelfR: 38 },
      { y0: 480, y1: 560, xL: -34, xR: 26, shelfL: -34, shelfR: 38 },
      { y0: 560, y1: 630, xL: -22, xR: 26, shelfL: -34, shelfR: 26 },
      { y0: 630, y1: 700, xL: -12, xR: 12, shelfL: -22, shelfR: 26 },
      { y0: 700, y1: 750, xL: -6, xR: 6, shelfL: -12, shelfR: 12 }
    ];

    setbacks.forEach(tier => {
      if (tier.shelfL !== tier.xL) addSeg(tier.shelfL, tier.y0, 0, tier.xL, tier.y0, 0);
      if (tier.shelfR !== tier.xR) addSeg(tier.xR, tier.y0, 0, tier.shelfR, tier.y0, 0);
      addSeg(tier.xL, tier.y0, 0, tier.xL, tier.y1, 0);
      addSeg(tier.xR, tier.y0, 0, tier.xR, tier.y1, 0);
      const midY = (tier.y0 + tier.y1) * 0.5;
      addSeg(tier.xL, midY, 0, tier.xR, midY, 0);
      addSeg(tier.xL, tier.y1, 0, tier.xR, tier.y1, 0);
    });

    // Pinnacle Needle Spire (Y = 750 to 828)
    addSeg(-6, 750, 0, 0, 828, 0);
    addSeg(6, 750, 0, 0, 828, 0);
    addSeg(0, 750, 0, 0, 828, 0);
    addSeg(-4, 790, 0, 4, 790, 0);
    addSeg(-2, 815, 0, 2, 815, 0);
  }

  // Measurement bracket line alongside the landmark
  const xBrk = -(landmarkWidth * 0.5 + 18);
  addSeg(xBrk, 0, 0, xBrk, landmarkHeight, 0);
  addSeg(xBrk, landmarkHeight, 0, xBrk + 12, landmarkHeight, 0);
  addSeg(xBrk, 0, 0, xBrk + 12, 0, 0);
  addSeg(xBrk - 6, landmarkHeight * 0.5, 0, xBrk + 6, landmarkHeight * 0.5, 0);
  // Ground baseline
  addSeg(-(landmarkWidth * 0.5 + 24), 0, 0, (landmarkWidth * 0.5 + 16), 0, 0);

  // Build THREE.LineSegments
  const landmarkGeo = new THREE.BufferGeometry().setFromPoints(pts);
  const landmarkLines = new THREE.LineSegments(landmarkGeo, hologramMaterial);
  landmarkLines.position.y = -landmarkHeight * 0.5;

  const wireframeSubGroup = new THREE.Group();
  wireframeSubGroup.add(landmarkLines);

  // Scale relative to asteroid visual radius:
  const gSize = geoSize || 1.2;
  const scaleFactor = (gSize * 2.0) / Math.max(1, diam);
  wireframeSubGroup.scale.set(scaleFactor, scaleFactor, scaleFactor);
  hologramGroup.add(wireframeSubGroup);

  // Landmark visual metrics in hologramGroup coordinates (unscaled)
  const landmarkVisualHeight = landmarkHeight * scaleFactor;
  const landmarkVisualWidth = (landmarkWidth + 36) * scaleFactor;
  const visualTop = landmarkVisualHeight * 0.5;

  // Interactive high-resolution scale comparison label billboard
  const canvas = document.createElement('canvas');
  canvas.width = 1024;
  canvas.height = 384;
  const ctx = canvas.getContext('2d');

  // Glowing cyber container background
  const bgGrad = ctx.createLinearGradient(0, 0, 1024, 384);
  bgGrad.addColorStop(0, 'rgba(4, 12, 28, 0.95)');
  bgGrad.addColorStop(1, 'rgba(8, 22, 44, 0.92)');
  ctx.fillStyle = bgGrad;
  ctx.strokeStyle = '#00f3ff';
  ctx.lineWidth = 5;

  if (ctx.roundRect) {
    ctx.beginPath();
    ctx.roundRect(6, 6, 1012, 372, 18);
    ctx.fill();
    ctx.stroke();
  } else {
    ctx.fillRect(6, 6, 1012, 372);
    ctx.strokeRect(6, 6, 1012, 372);
  }

  // Cyber corner accents (bold cyan)
  ctx.fillStyle = '#00f3ff';
  ctx.fillRect(6, 6, 36, 8);
  ctx.fillRect(6, 6, 8, 36);
  ctx.fillRect(982, 6, 36, 8);
  ctx.fillRect(1010, 6, 8, 36);
  ctx.fillRect(6, 370, 36, 8);
  ctx.fillRect(6, 342, 8, 36);
  ctx.fillRect(982, 370, 36, 8);
  ctx.fillRect(1010, 342, 8, 36);

  // Subdued divider line
  ctx.strokeStyle = 'rgba(0, 243, 255, 0.25)';
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(32, 74);
  ctx.lineTo(992, 74);
  ctx.stroke();

  // Header tag (bold cyan, >= 24px)
  ctx.font = 'bold 26px monospace';
  ctx.fillStyle = '#00f3ff';
  ctx.fillText("⌖ HOLOGRAPHIC SCALE COMPARISON", 36, 50);

  // Landmark name & dimension (crisp 48px bold white)
  ctx.font = 'bold 48px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
  ctx.fillStyle = '#ffffff';
  ctx.fillText(`${landmarkName} (${landmarkDim})`, 36, 136);

  // Asteroid comparison (bold 36px yellow-orange)
  ctx.font = 'bold 36px monospace';
  ctx.fillStyle = '#ffaa00';
  ctx.fillText(`vs Asteroid (${Math.round(diam)}m)`, 36, 206);

  // Ratio readout (bold 32px cyan)
  const ratio = (diam / landmarkHeight).toFixed(2);
  ctx.font = 'bold 32px monospace';
  ctx.fillStyle = '#00f3ff';
  ctx.fillText(`Asteroid is ${ratio}x Landmark size`, 36, 276);

  // Subtitle note (crisp 24px white)
  ctx.font = '24px monospace';
  ctx.fillStyle = 'rgba(255, 255, 255, 0.65)';
  ctx.fillText(`1:1 Physical Scale Proportionality`, 36, 340);

  const tex = new THREE.CanvasTexture(canvas);
  tex.minFilter = THREE.LinearFilter;
  const spriteMat = new THREE.SpriteMaterial({
    map: tex,
    transparent: true,
    opacity: 0.95,
    blending: THREE.AdditiveBlending,
    depthWrite: false
  });
  const labelSprite = new THREE.Sprite(spriteMat);

  // Card dimensions in unscaled world units, scaled comfortably to inspection zoom
  const cardHeightWorld = Math.max(1.15, Math.min(2.0, gSize * 0.9));
  const cardWidthWorld = cardHeightWorld * (1024 / 384);
  labelSprite.scale.set(cardWidthWorld, cardHeightWorld, 1.0);

  // Position clearly ABOVE the landmark wireframe so it never overlaps the 3D asteroid geometry
  const cardY = visualTop + (cardHeightWorld * 0.55) + 0.35;
  labelSprite.position.set(0, cardY, 0);
  hologramGroup.add(labelSprite);

  // Store bounding dimensions on hologramGroup for safe clearance docking
  const totalHalfWidth = Math.max(landmarkVisualWidth * 0.5 + 0.3, cardWidthWorld * 0.5);
  hologramGroup.userData = {
    visualHalfWidth: totalHalfWidth,
    visualHeight: (visualTop + cardHeightWorld + 0.5) * 2.0,
    gSize: gSize
  };

  return hologramGroup;
}

window.createLandmarkHologram = createLandmarkHologram;

window.toggleHologram = function() {
  hologramEnabled = !hologramEnabled;
  const btn = document.getElementById('hologram-toggle');
  const label = btn ? btn.querySelector('.toggle-label') : null;
  if (hologramEnabled) {
    if (btn) btn.classList.remove('disabled');
    if (label) label.innerText = "3D HOLO COMPARISON: ON";
    if (selectedMesh && isTracking && selectedMesh.userData && selectedMesh.userData.diameter) {
      createLandmarkHologram(selectedMesh.userData.diameter, selectedMesh.userData.geoSize);
      if (hologramGroup) hologramGroup.visible = true;
    }
  } else {
    if (btn) btn.classList.add('disabled');
    if (label) label.innerText = "3D HOLO COMPARISON: OFF";
    if (hologramGroup) hologramGroup.visible = false;
  }
};
