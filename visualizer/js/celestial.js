// visualizer/js/celestial.js
// Sun hierarchy, lighting, starfield, Earth shaders, and Malé ground station

const sunPosition = new THREE.Vector3(1200, 400, -1200);
let sunGroup = null;
let sunCore = null;
let sunCorona = null;
let sunLight = null;
let ambientLight = null;
let skyDome = null;
let earthMesh = null;
let cloudMesh = null;
let atmosphereMesh = null;
let atmosphereMat = null;
let earthShaderUniforms = null;
let maleStationGroup = null;
let beaconMesh = null;
let maleLight = null;
let pingRing = null;
let ringMat = null;

function createSunCanvasTexture() {
  const c = document.createElement('canvas');
  c.width = 2048;
  c.height = 2048;
  const ctx = c.getContext('2d');

  const cx = 1024;
  const cy = 1024;
  const maxR = 1024;

  const grad = ctx.createRadialGradient(cx, cy, 0, cx, cy, maxR);

  // Core (0% to 15% radius): Pure blinding white (#ffffff at opacity 1.0)
  grad.addColorStop(0.0, 'rgba(255, 255, 255, 1.0)');
  grad.addColorStop(0.10, 'rgba(255, 255, 255, 1.0)');
  grad.addColorStop(0.15, 'rgba(255, 255, 255, 1.0)');

  // Photosphere (15% to 50% radius): Bright yellow-orange (#ffaa22 transitioning with exponential curve Math.pow(1 - r, 2) to simulate limb darkening)
  const photoSteps = 16;
  for (let i = 1; i <= photoSteps; i++) {
    const t = i / photoSteps;
    const r = 0.15 + t * 0.35;
    const f = Math.pow(1.0 - t, 2.0);
    const g = Math.round(170 + (255 - 170) * f);
    const b = Math.round(34 + (255 - 34) * Math.pow(f, 1.5));
    const a = 1.0 - 0.25 * (1.0 - f);
    grad.addColorStop(Number(r.toFixed(4)), `rgba(255, ${g}, ${b}, ${a.toFixed(3)})`);
  }

  // Corona (50% to 100% radius): Deep solar red-orange fading smoothly to absolute zero opacity rgba(255, 60, 0, 0)
  const coronaSteps = 20;
  for (let j = 1; j <= coronaSteps; j++) {
    const u = j / coronaSteps;
    const r = 0.50 + u * 0.50;
    const falloff = Math.pow(1.0 - u, 2.5);
    const g = Math.round(60 + (170 - 60) * (1.0 - u));
    const a = 0.75 * falloff;
    grad.addColorStop(Number(r.toFixed(4)), `rgba(255, ${g}, 0, ${a.toFixed(4)})`);
  }

  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, 2048, 2048);

  const tex = new THREE.CanvasTexture(c);
  tex.needsUpdate = true;
  return tex;
}

function latLonToCartesian(lat, lon, radius) {
  const phi = (90 - lat) * (Math.PI / 180);
  const theta = (lon + 180) * (Math.PI / 180);
  const x = -radius * Math.sin(phi) * Math.cos(theta);
  const y = radius * Math.cos(phi);
  const z = radius * Math.sin(phi) * Math.sin(theta);
  return new THREE.Vector3(x, y, z);
}

function initCelestial(scene, textureLoader) {
  // 1. ARCHITECTURAL HIERARCHY (The Sun Group)
  sunGroup = new THREE.Group();
  sunGroup.position.copy(sunPosition);
  scene.add(sunGroup);

  // 2. PART A: THE SOLID OCCLUDER CORE (Blinding white core)
  const coreGeo = new THREE.SphereGeometry(120, 32, 32);
  const coreMat = new THREE.MeshBasicMaterial({
    color: 0xffffff,
    toneMapped: false,
    depthWrite: true,
    depthTest: true
  });
  sunCore = new THREE.Mesh(coreGeo, coreMat);
  sunCore.renderOrder = 0;
  sunGroup.add(sunCore);

  // 3. PART B: THE PROCEDURAL GLOW CORONA (Additive Atmosphere)
  const canvasTexture = createSunCanvasTexture();
  const coronaGeo = new THREE.PlaneGeometry(1600, 1600);
  const coronaMat = new THREE.MeshBasicMaterial({
    map: canvasTexture,
    transparent: true,
    blending: THREE.AdditiveBlending,
    depthWrite: false,
    depthTest: true,
    side: THREE.DoubleSide
  });
  sunCorona = new THREE.Mesh(coronaGeo, coronaMat);
  sunCorona.renderOrder = 1;
  sunGroup.add(sunCorona);

  // Primary solar directional light anchored at the exact Sun world position
  sunLight = new THREE.DirectionalLight(0xffffff, 4.2);
  sunLight.position.copy(sunGroup.position);
  sunLight.target.position.set(0, 0, 0);
  scene.add(sunLight);
  scene.add(sunLight.target);

  ambientLight = new THREE.AmbientLight(0xffffff, 0.015);
  scene.add(ambientLight);

  // Skysphere and starfield
  const skyGeo = new THREE.SphereGeometry(8000, 64, 64);
  const skyTex = textureLoader.load('https://unpkg.com/three-globe/example/img/night-sky.png');
  skyTex.wrapS = THREE.RepeatWrapping;
  skyTex.wrapT = THREE.RepeatWrapping;
  const skyMat = new THREE.MeshBasicMaterial({
    map: skyTex,
    side: THREE.BackSide,
    depthWrite: false
  });
  skyDome = new THREE.Mesh(skyGeo, skyMat);
  scene.add(skyDome);

  const starCount = 2000;
  const starGeo = new THREE.BufferGeometry();
  const starPos = new Float32Array(starCount * 3);
  const starColors = new Float32Array(starCount * 3);

  for (let i = 0; i < starCount; i++) {
    const r = 2500 + Math.random() * 3500;
    const theta = Math.random() * Math.PI * 2;
    const phi = Math.acos(2 * Math.random() - 1);

    starPos[i * 3] = r * Math.sin(phi) * Math.cos(theta);
    starPos[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
    starPos[i * 3 + 2] = r * Math.cos(phi);

    const lum = 0.65 + Math.random() * 0.35;
    starColors[i * 3] = 0.75 * lum;
    starColors[i * 3 + 1] = 0.9 * lum;
    starColors[i * 3 + 2] = 1.0 * lum;
  }
  starGeo.setAttribute('position', new THREE.BufferAttribute(starPos, 3));
  starGeo.setAttribute('color', new THREE.BufferAttribute(starColors, 3));

  const starMat = new THREE.PointsMaterial({
    size: 2.0,
    vertexColors: true,
    transparent: true,
    opacity: 0.82
  });
  scene.add(new THREE.Points(starGeo, starMat));

  // Earth, clouds, and atmosphere shaders
  const earthDayTex = textureLoader.load('https://raw.githubusercontent.com/mrdoob/three.js/master/examples/textures/planets/earth_atmos_2048.jpg');
  const earthNormalTex = textureLoader.load('https://raw.githubusercontent.com/mrdoob/three.js/master/examples/textures/planets/earth_normal_2048.jpg');
  const earthSpecularTex = textureLoader.load('https://raw.githubusercontent.com/mrdoob/three.js/master/examples/textures/planets/earth_specular_2048.jpg');
  const earthCloudsTex = textureLoader.load('https://raw.githubusercontent.com/mrdoob/three.js/master/examples/textures/planets/earth_clouds_1024.png');
  const earthLightsTex = textureLoader.load('https://raw.githubusercontent.com/mrdoob/three.js/master/examples/textures/planets/earth_lights_2048.png');

  const earthGeo = new THREE.SphereGeometry(10, 64, 64);
  const earthMat = new THREE.MeshStandardMaterial({
    color: 0x1d365d,
    map: earthDayTex,
    normalMap: earthNormalTex,
    normalScale: new THREE.Vector2(0.85, 0.85),
    roughnessMap: earthSpecularTex,
    roughness: 0.85,
    metalness: 0.05,
    emissiveMap: earthLightsTex,
    emissive: new THREE.Color(0xffffff),
    emissiveIntensity: 1.0
  });

  // City lights night terminator shader
  try {
    earthMat.onBeforeCompile = (shader) => {
      earthShaderUniforms = shader.uniforms;
      shader.uniforms.uSunDir = { value: sunPosition.clone().normalize() };
      shader.vertexShader = `varying vec3 vWorldNormal;\n` + shader.vertexShader;
      shader.vertexShader = shader.vertexShader.replace(
        `#include <worldpos_vertex>`,
        `#include <worldpos_vertex>\nvWorldNormal = normalize((modelMatrix * vec4(normal, 0.0)).xyz);`
      );
      shader.fragmentShader = `uniform vec3 uSunDir;\nvarying vec3 vWorldNormal;\n` + shader.fragmentShader;
      shader.fragmentShader = shader.fragmentShader.replace(
        `#include <emissivemap_fragment>`,
        `#include <emissivemap_fragment>
         float sunDot = dot(normalize(vWorldNormal), normalize(uSunDir));
         float sunMask = smoothstep(-0.15, 0.1, sunDot);
         float nightMask = clamp(1.0 - sunMask, 0.0, 1.0);
         totalEmissiveRadiance *= (nightMask * 0.35);
        `
      );
    };
  } catch (err) {
    console.warn("Shader onBeforeCompile fallback:", err);
  }

  earthMesh = new THREE.Mesh(earthGeo, earthMat);
  scene.add(earthMesh);

  const cloudGeo = new THREE.SphereGeometry(10.18, 64, 64);
  const cloudMat = new THREE.MeshLambertMaterial({
    map: earthCloudsTex,
    transparent: true,
    opacity: 0.45,
    blending: THREE.NormalBlending
  });
  cloudMesh = new THREE.Mesh(cloudGeo, cloudMat);
  scene.add(cloudMesh);

  const atmosphereGeo = new THREE.SphereGeometry(10.42, 64, 64);
  atmosphereMat = new THREE.ShaderMaterial({
    vertexShader: `
      varying vec3 vNormal;
      varying vec3 vPosition;
      void main() {
        vNormal = normalize(normalMatrix * normal);
        vPosition = (modelViewMatrix * vec4(position, 1.0)).xyz;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `,
    fragmentShader: `
      varying vec3 vNormal;
      varying vec3 vPosition;
      uniform vec3 uSunPos;
      void main() {
        vec3 viewDir = normalize(-vPosition);
        float rim = 1.0 - max(dot(viewDir, vNormal), 0.0);
        float halo = pow(rim, 3.2);

        vec3 eyeSun = normalize((viewMatrix * vec4(uSunPos, 0.0)).xyz);
        float sunFacing = dot(vNormal, eyeSun);
        float daylight = smoothstep(-0.25, 0.5, sunFacing);

        vec3 rayleighColor = vec3(0.18, 0.58, 1.0);
        gl_FragColor = vec4(rayleighColor, halo * (0.2 + 0.8 * daylight) * 0.95);
      }
    `,
    uniforms: {
      uSunPos: { value: sunPosition }
    },
    blending: THREE.AdditiveBlending,
    side: THREE.BackSide,
    transparent: true,
    depthWrite: false
  });
  atmosphereMesh = new THREE.Mesh(atmosphereGeo, atmosphereMat);
  scene.add(atmosphereMesh);

  // Ground station telemetry marker (Malé station coordinates: 4.1755° N, 73.5093° E)
  const maleLat = 4.1755;
  const maleLon = 73.5093;
  const malePos = latLonToCartesian(maleLat, maleLon, 10.05);

  maleStationGroup = new THREE.Group();
  maleStationGroup.position.copy(malePos);

  const surfaceNormal = malePos.clone().normalize();
  maleStationGroup.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), surfaceNormal);

  const beaconGeo = new THREE.CylinderGeometry(0.08, 0.16, 0.45, 16);
  const beaconMat = new THREE.MeshStandardMaterial({
    color: 0x00f0ff,
    emissive: 0x00f0ff,
    emissiveIntensity: 2.2,
    roughness: 0.25,
    metalness: 0.85
  });
  beaconMesh = new THREE.Mesh(beaconGeo, beaconMat);
  beaconMesh.position.y = 0.22;
  maleStationGroup.add(beaconMesh);

  maleLight = new THREE.PointLight(0x00f0ff, 2.5, 6.0);
  maleLight.position.y = 0.5;
  maleStationGroup.add(maleLight);

  const ringGeo = new THREE.RingGeometry(0.12, 0.35, 32);
  ringMat = new THREE.MeshBasicMaterial({
    color: 0x00f0ff,
    transparent: true,
    opacity: 0.9,
    side: THREE.DoubleSide
  });
  pingRing = new THREE.Mesh(ringGeo, ringMat);
  pingRing.rotation.x = Math.PI / 2;
  pingRing.position.y = 0.02;
  maleStationGroup.add(pingRing);

  earthMesh.add(maleStationGroup);

  beaconMesh.userData = {
    name: "MALÉ GROUND COMMAND",
    isStation: true,
    coords: "4.1755° N, 73.5093° E",
    desc: "PRIMARY SENSOR & TELEMETRY UPLINK [MALDIVES]",
    group: maleStationGroup
  };
}
