// visualizer/js/interaction.js
// Camera transitions, raycasting, touch controls, telemetry drawer, and auto-pilot mode

let raycaster = null;
let mouse = null;
let hoveredMesh = null;
let selectedMesh = null;
let isTracking = false;
let defaultCamPos = null;

let autoPilotInterval = null;
let autoPilotIndex = 0;

let _interactionScene = null;
let _interactionCamera = null;
let _interactionRenderer = null;
let _interactionControls = null;
let _interactionTooltip = null;
let _interactionDrawer = null;

function initInteraction(scene, camera, renderer, controls, tooltip, drawer) {
  _interactionScene = scene;
  _interactionCamera = camera;
  _interactionRenderer = renderer;
  _interactionControls = controls;
  _interactionTooltip = tooltip;
  _interactionDrawer = drawer;

  raycaster = new THREE.Raycaster();
  mouse = new THREE.Vector2(-999, -999);
  defaultCamPos = camera.position.clone();

  window.addEventListener('mousemove', (e) => {
    const rect = renderer.domElement.getBoundingClientRect();
    mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
    mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

    if (hoveredMesh && tooltip) {
      tooltip.style.left = e.clientX + 'px';
      tooltip.style.top = e.clientY + 'px';
    }
  });

  renderer.domElement.addEventListener('touchend', function(e) {
    if (!e.changedTouches || e.changedTouches.length === 0) return;
    const touch = e.changedTouches[0];
    const rect = renderer.domElement.getBoundingClientRect();

    // Calculate precise normalized device coordinates for mobile touch
    mouse.x = ((touch.clientX - rect.left) / rect.width) * 2 - 1;
    mouse.y = -((touch.clientY - rect.top) / rect.height) * 2 + 1;

    raycaster.setFromCamera(mouse, camera);
    if (typeof asteroidGroup !== 'undefined' && asteroidGroup) {
      const intersects = raycaster.intersectObjects(asteroidGroup.children, true);
      if (intersects.length > 0) {
        e.preventDefault();
        triggerTargetLock(intersects[0].object);
      }
    }
  }, { passive: false });

  renderer.domElement.addEventListener('click', (e) => {
    const rect = renderer.domElement.getBoundingClientRect();
    mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
    mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

    raycaster.setFromCamera(mouse, camera);
    if (typeof asteroidGroup !== 'undefined' && asteroidGroup) {
      const intersects = raycaster.intersectObjects(asteroidGroup.children, true);
      if (intersects.length > 0) {
        triggerTargetLock(intersects[0].object);
      }
    }
  });

  window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      stopAutoPilot();
      resetToEarthView();
    }
  });

  const drawerCloseBtn = document.getElementById('drawer-close-btn') || document.querySelector('.close-btn') || document.querySelector('.drawer-close');
  if (drawerCloseBtn) {
    const onDrawerClose = (ev) => {
      if (ev) {
        ev.preventDefault();
        ev.stopPropagation();
      }
      resetToEarthView();
    };
    drawerCloseBtn.addEventListener('click', onDrawerClose);
    drawerCloseBtn.addEventListener('touchend', onDrawerClose);
  }
}

function triggerTargetLock(target) {
  stopAutoPilot();
  if (target.userData && target.userData.isStation) {
    flyToStation(target);
  } else {
    flyToAsteroid(target);
  }
}

function flyToAsteroid(obj) {
  const group = obj.isGroup ? obj : (obj.userData.group || obj.parent || obj);
  const data = obj.userData;
  selectedMesh = group;
  isTracking = true;

  const tooltip = _interactionTooltip || document.getElementById('hover-tooltip');
  if (tooltip) tooltip.style.display = 'none';

  const camera = _interactionCamera;
  const controls = _interactionControls;

  const astPos = group.position.clone();
  const gSize = (data && data.geoSize) ? data.geoSize : 1.2;
  const camDist = Math.max(5.6, gSize * 3.4 + 1.8);
  const viewOffset = astPos.clone().normalize().multiplyScalar(camDist).add(new THREE.Vector3(0, camDist * 0.32, 0));
  const targetCamPos = astPos.clone().add(viewOffset);

  if (camera && controls) {
    new TWEEN.Tween(camera.position)
      .to({ x: targetCamPos.x, y: targetCamPos.y, z: targetCamPos.z }, 1600)
      .easing(TWEEN.Easing.Cubic.InOut)
      .start();

    new TWEEN.Tween(controls.target)
      .to({ x: astPos.x, y: astPos.y, z: astPos.z }, 1600)
      .easing(TWEEN.Easing.Cubic.InOut)
      .start();
  }

  const nameEl = document.getElementById('drawer-name');
  if (nameEl && data.name) nameEl.innerText = data.name;
  
  const threatEl = document.getElementById('drawer-threat');
  if (threatEl) {
    if (data.isHazard) {
      threatEl.className = 'threat-pill threat-hazard';
      threatEl.innerText = '⚠️ POTENTIALLY HAZARDOUS';
    } else {
      threatEl.className = 'threat-pill threat-safe';
      threatEl.innerText = '🛡️ NOMINAL TRAJECTORY';
    }
  }

  const scaleEl = document.getElementById('drawer-scale');
  if (scaleEl && data.scaleAnalogy) {
    scaleEl.innerText = `Scale: ${data.scaleAnalogy}`;
  }
  const diamEl = document.getElementById('drawer-diameter');
  if (diamEl && data.diameter) {
    diamEl.innerText = `${data.diameter.toLocaleString('en-US', {maximumFractionDigits: 1})} m`;
  }
  const velEl = document.getElementById('drawer-velocity');
  if (velEl && data.velocity) {
    velEl.innerText = `${data.velocity.toLocaleString('en-US', {maximumFractionDigits: 0})} km/h`;
  }
  const distEl = document.getElementById('drawer-distance');
  if (distEl && data.missKm) {
    distEl.innerText = `${data.missKm.toLocaleString('en-US', {maximumFractionDigits: 0})} km`;
  }
  const ldEl = document.getElementById('drawer-ld');
  if (ldEl && data.missLd) {
    ldEl.innerText = `${data.missLd.toFixed(2)} LD`;
  }
  const incEl = document.getElementById('drawer-inc');
  if (incEl && typeof data.inclination !== 'undefined') {
    incEl.innerText = `${(data.inclination * (180/Math.PI)).toFixed(1)}°`;
  }

  renderSilhouette(data.diameter, data.scaleAnalogy);
  if (typeof createLandmarkHologram === 'function' && data && data.diameter) {
    createLandmarkHologram(data.diameter, data.geoSize);
    if (typeof hologramGroup !== 'undefined' && hologramGroup) {
      hologramGroup.visible = (typeof hologramEnabled !== 'undefined') ? hologramEnabled : true;
    }
  }

  const drawer = _interactionDrawer || document.getElementById('telemetry-drawer');
  if (drawer) {
    drawer.classList.add('open');
    drawer.style.right = '0px';
  }

  const reticle = document.getElementById('targeting-reticle');
  const reticleTag = document.getElementById('reticle-status');
  if (reticle) {
    reticle.classList.add('active');
    if (data.isHazard) {
      reticle.classList.add('hazard');
      if (reticleTag) reticleTag.innerText = `⚠️ LOCK: ${data.name} [HAZARD]`;
    } else {
      reticle.classList.remove('hazard');
      if (reticleTag) reticleTag.innerText = `⌖ LOCK: ${data.name} [NOMINAL]`;
    }
    if (camera) {
      const vector = group.position.clone();
      vector.project(camera);
      const x = (vector.x * 0.5 + 0.5) * window.innerWidth;
      const y = (vector.y * -0.5 + 0.5) * window.innerHeight;
      reticle.style.left = x + 'px';
      reticle.style.top = y + 'px';
      reticle.style.display = 'block';
    }
  }
}

function flyToStation(mesh) {
  selectedMesh = null;
  isTracking = false;
  if (typeof hologramGroup !== 'undefined' && hologramGroup) {
    hologramGroup.visible = false;
  }
  const tooltip = _interactionTooltip || document.getElementById('hover-tooltip');
  if (tooltip) tooltip.style.display = 'none';

  const worldPos = new THREE.Vector3();
  mesh.getWorldPosition(worldPos);

  const camTarget = worldPos.clone().normalize().multiplyScalar(15.5);

  const camera = _interactionCamera;
  const controls = _interactionControls;

  if (camera && controls) {
    new TWEEN.Tween(camera.position)
      .to({ x: camTarget.x, y: camTarget.y, z: camTarget.z }, 1600)
      .easing(TWEEN.Easing.Cubic.InOut)
      .start();

    new TWEEN.Tween(controls.target)
      .to({ x: worldPos.x, y: worldPos.y, z: worldPos.z }, 1600)
      .easing(TWEEN.Easing.Cubic.InOut)
      .start();
  }

  const nameEl = document.getElementById('drawer-name');
  if (nameEl) nameEl.innerText = "MALÉ COMMAND";
  const threatEl = document.getElementById('drawer-threat');
  if (threatEl) {
    threatEl.className = 'threat-pill threat-safe';
    threatEl.innerText = '📡 ACTIVE SENSOR UPLINK';
  }

  const scaleEl = document.getElementById('drawer-scale');
  if (scaleEl) scaleEl.innerText = "Scale: Ground Sensor Station (4.18° N, 73.51° E)";
  const diamEl = document.getElementById('drawer-diameter');
  if (diamEl) diamEl.innerText = "Surface Sensor Array";
  const velEl = document.getElementById('drawer-velocity');
  if (velEl) velEl.innerText = "1,670 km/h (Earth Rotation)";
  const distEl = document.getElementById('drawer-distance');
  if (distEl) distEl.innerText = "0.0 km (Earth Surface)";
  const ldEl = document.getElementById('drawer-ld');
  if (ldEl) ldEl.innerText = "0.00 LD";
  const incEl = document.getElementById('drawer-inc');
  if (incEl) incEl.innerText = "4.2° N Equat.";

  const silContainer = document.getElementById('drawer-silhouette');
  if (silContainer) {
    silContainer.innerHTML = `
      <div style="font-size:12px; color:#00f0ff; font-family:monospace; padding-bottom:10px;">
        ● RADAR BEACON: ONLINE<br>
        ● OPTICAL SENSORS: CALIBRATED<br>
        ● LAT: 4.1755° N | LON: 73.5093° E
      </div>
    `;
  }

  const drawer = _interactionDrawer || document.getElementById('telemetry-drawer');
  if (drawer) {
    drawer.classList.add('open');
    drawer.style.right = '0px';
  }

  const reticle = document.getElementById('targeting-reticle');
  if (reticle) {
    reticle.classList.remove('active');
    reticle.classList.remove('hazard');
    reticle.style.display = 'none';
  }
}

function resetToEarthView() {
  stopAutoPilot();
  isTracking = false;
  selectedMesh = null;
  if (typeof hologramGroup !== 'undefined' && hologramGroup) {
    hologramGroup.visible = false;
  }
  const drawer = _interactionDrawer || document.getElementById('telemetry-drawer');
  if (drawer) {
    drawer.classList.remove('open');
    drawer.style.right = '-100vw';
  }

  const reticle = document.getElementById('targeting-reticle');
  if (reticle) {
    reticle.classList.remove('active');
    reticle.classList.remove('hazard');
    reticle.style.display = 'none';
  }

  const camera = _interactionCamera;
  const controls = _interactionControls;
  const camPos = defaultCamPos || new THREE.Vector3(38, 20, 46);

  if (camera && controls) {
    new TWEEN.Tween(camera.position)
      .to({ x: camPos.x, y: camPos.y, z: camPos.z }, 1500)
      .easing(TWEEN.Easing.Cubic.InOut)
      .start();

    new TWEEN.Tween(controls.target)
      .to({ x: 0, y: 0, z: 0 }, 1500)
      .easing(TWEEN.Easing.Cubic.InOut)
      .start();
  }
}
window.resetToEarthView = resetToEarthView;

function toggleMissionControls() {
  try {
    const pDoc = window.parent.document;
    if (!pDoc) return;

    const expandBtn = pDoc.querySelector('[data-testid="stExpandSidebarButton"] button, [data-testid="stExpandSidebarButton"], [data-testid="stSidebarTrigger"] button, [data-testid="stSidebarTrigger"], [data-testid="collapsedControl"] button, section[data-testid="collapsedControl"] button, button[aria-label="Expand sidebar"]');
    if (expandBtn) {
      expandBtn.click();
      return;
    }

    const collapseBtn = pDoc.querySelector('[data-testid="stSidebarCollapseButton"] button, [data-testid="stSidebarCollapseButton"], button[aria-label="Collapse sidebar"]');
    if (collapseBtn) {
      collapseBtn.click();
      return;
    }
  } catch (err) {
    console.warn("Could not toggle mission controls sidebar:", err);
  }
}
window.toggleMissionControls = toggleMissionControls;

function renderSilhouette(diameterM, scaleAnalogy) {
  const silContainer = document.getElementById('drawer-silhouette');
  if (!silContainer) return;

  let refLabel = "Boeing 737 (35m)";
  let refHeight = 35;
  if (diameterM < 15) {
    refLabel = "School Bus (12m)";
    refHeight = 12;
  } else if (diameterM < 50) {
    refLabel = "Airplane (38m)";
    refHeight = 38;
  } else if (diameterM < 150) {
    refLabel = "Football Stadium (110m)";
    refHeight = 110;
  } else if (diameterM < 400) {
    refLabel = "Skyscraper (300m)";
    refHeight = 300;
  } else {
    refLabel = "Burj Khalifa (828m)";
    refHeight = 828;
  }

  const astPx = Math.min(62, Math.max(16, (diameterM / (diameterM + refHeight)) * 72));
  const refPx = Math.min(62, Math.max(12, (refHeight / (diameterM + refHeight)) * 72));

  silContainer.innerHTML = `
    <div style="display:flex; flex-direction:column; align-items:center; gap:4px;">
      <div style="width:${astPx}px; height:${astPx}px; background:#00f0ff; border-radius:50%; box-shadow:0 0 10px rgba(0,240,255,0.6);"></div>
      <span style="font-size:9px; color:#00f0ff; font-weight:700;">NEO (${Math.round(diameterM)}m)</span>
    </div>
    <div style="display:flex; flex-direction:column; align-items:center; gap:4px;">
      <div style="width:${Math.max(6, refPx * 0.38)}px; height:${refPx}px; background:rgba(255,255,255,0.4); border-radius:2px;"></div>
      <span style="font-size:9px; color:rgba(255,255,255,0.6);">${refLabel}</span>
    </div>
  `;
}

function stopAutoPilot() {
  if (autoPilotInterval !== null) {
    clearInterval(autoPilotInterval);
    autoPilotInterval = null;
    console.warn("[AUTOPILOT] Manual override detected. Disengaging.");
    const apBadge = document.getElementById('autopilot-nav-badge');
    if (apBadge) apBadge.style.display = 'none';
  }
}

function triggerAutoPilot() {
  if (typeof AUTO_PILOT_ENABLED !== 'undefined' && !AUTO_PILOT_ENABLED) return;
  if (autoPilotInterval !== null) {
    clearInterval(autoPilotInterval);
    autoPilotInterval = null;
  }

  console.log("[AUTOPILOT] Auto-Pilot engaged. Initializing 8-second cycle.");
  const apBadge = document.getElementById('autopilot-nav-badge');
  if (apBadge) apBadge.style.display = 'inline-block';

  function cycleNextTarget() {
    if (typeof asteroidData === 'undefined' || !asteroidData || asteroidData.length === 0 || typeof asteroidGroups === 'undefined' || !asteroidGroups || asteroidGroups.length === 0) {
      return;
    }

    const target = asteroidGroups[autoPilotIndex];
    const targetName = (target && target.name) ? target.name : (asteroidData[autoPilotIndex] ? asteroidData[autoPilotIndex].Name : `TARGET-${autoPilotIndex + 1}`);

    console.log("[AUTOPILOT] Engaging target lock: " + targetName);
    autoPilotIndex = (autoPilotIndex + 1) % asteroidGroups.length;

    if (target && target.hitbox) {
      flyToAsteroid(target.hitbox);
    } else if (target && target.group) {
      flyToAsteroid(target.group);
    }
  }

  cycleNextTarget();
  autoPilotInterval = setInterval(cycleNextTarget, 8000);
}

window.triggerAutoPilot = triggerAutoPilot;
window.stopAutoPilot = stopAutoPilot;
