// visualizer/js/main.js
// Scene, camera, renderer initialization, render loop, and responsive window events

let scene = null;
let camera = null;
let renderer = null;
let controls = null;
let textureLoader = null;
let defaultCamPos = null;

const clock = new THREE.Clock();

try {
  console.log("NEO Sentinel Engine Initialized. Loaded asteroids:", (typeof asteroidData !== 'undefined' && asteroidData) ? asteroidData.length : 0);

  const trackedCountEl = document.getElementById('tracked-count');
  if (trackedCountEl) {
    trackedCountEl.innerText = (typeof asteroidData !== 'undefined' && asteroidData) ? asteroidData.length : 0;
  }

  const container = document.getElementById('canvas-container');
  if (!container) throw new Error("Mounting container #canvas-container does not exist.");

  const tooltip = document.getElementById('hover-tooltip');
  const drawer = document.getElementById('telemetry-drawer');

  // Scene setup
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x000000);

  const width = window.innerWidth || 1200;
  const height = window.innerHeight || 800;

  camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 15000);
  defaultCamPos = new THREE.Vector3(38, 20, 46);
  camera.position.copy(defaultCamPos);

  renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: "high-performance" });
  renderer.setSize(width, height);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.0;
  container.appendChild(renderer.domElement);

  controls = new THREE.OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.05;
  controls.minDistance = 14;
  controls.maxDistance = 400;

  textureLoader = new THREE.TextureLoader();
  textureLoader.crossOrigin = 'anonymous';

  // Initialize domain modules
  if (typeof initHologram === 'function') {
    initHologram(scene);
  }

  if (typeof initCelestial === 'function') {
    initCelestial(scene, textureLoader);
  }

  if (typeof initAsteroids === 'function') {
    initAsteroids(scene, textureLoader, typeof asteroidData !== 'undefined' ? asteroidData : []);
  }

  if (typeof initInteraction === 'function') {
    initInteraction(scene, camera, renderer, controls, tooltip, drawer);
  }

  function animate() {
    requestAnimationFrame(animate);
    const elapsed = clock.getElapsedTime();

    if (typeof TWEEN !== 'undefined') {
      TWEEN.update();
    }

    // Solar billboarding & lighting synchronization
    if (sunGroup && typeof sunPosition !== 'undefined' && sunPosition) {
      sunGroup.position.copy(sunPosition);
    }
    if (sunCorona && camera) {
      sunCorona.quaternion.copy(camera.quaternion);
    }
    if (sunLight && sunGroup) {
      sunLight.position.copy(sunGroup.position);
      sunLight.target.position.set(0, 0, 0);
      sunLight.target.updateMatrixWorld();
    }

    if (sunGroup) {
      const currentSunDir = sunGroup.position.clone().normalize();
      if (typeof earthShaderUniforms !== 'undefined' && earthShaderUniforms && earthShaderUniforms.uSunDir) {
        earthShaderUniforms.uSunDir.value.copy(currentSunDir);
      }
    }

    if (typeof atmosphereMat !== 'undefined' && atmosphereMat && atmosphereMat.uniforms && atmosphereMat.uniforms.uSunPos && sunGroup) {
      atmosphereMat.uniforms.uSunPos.value.copy(sunGroup.position);
    }

    // Planetary rotation
    if (earthMesh) earthMesh.rotation.y += 0.0011;
    if (cloudMesh) cloudMesh.rotation.y += 0.0017;

    // Ground station radar pulse
    if (pingRing && ringMat && maleLight) {
      const pingPhase = (elapsed * 1.8) % 1.0;
      pingRing.scale.set(1.0 + pingPhase * 3.2, 1.0 + pingPhase * 3.2, 1.0);
      ringMat.opacity = Math.max(0.0, 0.9 * (1.0 - pingPhase));
      maleLight.intensity = 1.2 + 0.8 * Math.sin(elapsed * 6.0);
    }

    // Asteroid kinematics and tumbling
    if (typeof asteroidGroups !== 'undefined' && asteroidGroups) {
      asteroidGroups.forEach((item) => {
        item.t = (item.t + item.speed * TIME_SCALE) % 1.0;
        const currentPos = item.curve.getPoint(item.t);
        item.group.position.copy(currentPos);

        if (item.rotAxis && item.rotSpeed) {
          item.rock.rotateOnAxis(item.rotAxis, item.rotSpeed);
        }
      });
    }

    // Target tracking and screen-space reticle projection
    if (typeof isTracking !== 'undefined' && isTracking && selectedMesh) {
      controls.target.copy(selectedMesh.position);

      // Holographic Scale Landmark Tracking & Flicker Animation
      if (typeof hologramGroup !== 'undefined' && hologramGroup && hologramGroup.visible) {
        const rightVec = new THREE.Vector3(1, 0, 0).applyQuaternion(camera.quaternion).normalize();
        const gSize = (selectedMesh.userData && selectedMesh.userData.geoSize) ? selectedMesh.userData.geoSize : 1.5;
        const offsetDist = gSize * 2.8 + 1.2;
        hologramGroup.position.copy(selectedMesh.position).addScaledVector(rightVec, offsetDist);
        hologramGroup.quaternion.copy(camera.quaternion);

        if (window.hologramMaterial) {
          window.hologramMaterial.opacity = 0.75 + 0.15 * Math.sin(Date.now() * 0.012);
        }
      }

      const reticle = document.getElementById('targeting-reticle');
      if (reticle && reticle.classList.contains('active')) {
        const vector = selectedMesh.position.clone();
        vector.project(camera);
        if (vector.z < 1.0) {
          const x = (vector.x * 0.5 + 0.5) * window.innerWidth;
          const y = (vector.y * -0.5 + 0.5) * window.innerHeight;
          reticle.style.left = x + 'px';
          reticle.style.top = y + 'px';
          reticle.style.display = 'block';
        } else {
          reticle.style.display = 'none';
        }
      }
    }

    // Raycast hover detection
    if (typeof raycaster !== 'undefined' && raycaster && typeof mouse !== 'undefined' && mouse && typeof asteroidGroup !== 'undefined' && asteroidGroup) {
      raycaster.setFromCamera(mouse, camera);
      const hits = raycaster.intersectObjects(asteroidGroup.children, true);

      if (hits.length > 0) {
        const hitObj = hits[0].object;
        if (hoveredMesh !== hitObj) {
          hoveredMesh = hitObj;
          document.body.style.cursor = 'pointer';
          if (tooltip) {
            tooltip.style.display = 'block';
            if (hoveredMesh.userData && hoveredMesh.userData.isStation) {
              tooltip.innerHTML = `<span style="color:#00f0ff; font-weight:700;">📡 ${hoveredMesh.userData.name}</span><br><span style="color:rgba(255,255,255,0.7); font-size:10px;">[${hoveredMesh.userData.coords}]</span>`;
            } else if (hoveredMesh.userData) {
              const u = hoveredMesh.userData;
              tooltip.innerHTML = `<span style="color:#00f0ff; font-weight:700;">⌖ ${u.name}</span> • ${u.isHazard ? '<span style="color:#ff003c; font-weight:700;">⚠️ HAZARDOUS</span>' : '<span style="color:#00ff88; font-weight:700;">NOMINAL</span>'}<br><span style="color:rgba(255,255,255,0.6); font-size:10px;">CLICK TO LOCK TARGET</span>`;
            }
          }
        }
      } else {
        if (hoveredMesh) {
          hoveredMesh = null;
          document.body.style.cursor = 'default';
          if (tooltip) tooltip.style.display = 'none';
        }
      }
    }

    controls.update();
    renderer.render(scene, camera);
  }

  animate();

  if (typeof AUTO_PILOT_ENABLED !== 'undefined' && AUTO_PILOT_ENABLED) {
    if (typeof triggerAutoPilot === 'function') {
      triggerAutoPilot();
    }
  }

  function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight, true);
    if (!isTracking && drawer && !drawer.classList.contains('open') && drawer.style.right !== '0px') {
      drawer.style.right = '-100vw';
    }
  }

  window.addEventListener('resize', onWindowResize);
  window.addEventListener('orientationchange', () => {
    setTimeout(onWindowResize, 150);
  });

} catch (error) {
  document.body.innerHTML = "<h1 style='color:red; text-align:center; margin-top: 20%; font-family:monospace;'>CRASH: " + error.message + "</h1><pre style='color:#ff8888; text-align:center; font-family:monospace;'>" + (error.stack || '') + "</pre>";
  console.error("CRASH:", error);
}
