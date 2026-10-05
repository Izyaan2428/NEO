// visualizer/js/asteroids.js
// Procedural asteroid geometry, trajectory curves, materials, and kinematic data structures

const TIME_SCALE = 0.15;
let asteroidGroups = [];
let asteroidGroup = null;
let interactiveObjects = [];

function initAsteroids(scene, textureLoader, asteroidData) {
  asteroidGroup = new THREE.Group();
  scene.add(asteroidGroup);

  if (typeof beaconMesh !== 'undefined' && beaconMesh) {
    asteroidGroup.add(beaconMesh);
    interactiveObjects.push(beaconMesh);
  }

  const asteroidBumpMap = textureLoader.load('https://unpkg.com/three-globe/example/img/earth-topology.png');
  asteroidBumpMap.wrapS = THREE.RepeatWrapping;
  asteroidBumpMap.wrapT = THREE.RepeatWrapping;
  asteroidBumpMap.repeat.set(4, 4);

  const asteroidNormalTex = textureLoader.load('https://unpkg.com/three-globe/example/img/earth-topology.png');
  asteroidNormalTex.wrapS = THREE.RepeatWrapping;
  asteroidNormalTex.wrapT = THREE.RepeatWrapping;
  asteroidNormalTex.repeat.set(4, 4);

  if (!asteroidData || asteroidData.length === 0) {
    console.warn("No asteroids found in dataset.");
    return;
  }

  const minMiss = Math.min(...asteroidData.map(a => Number(a["Miss Distance (km)"]) || 1e6));
  const maxMiss = Math.max(...asteroidData.map(a => Number(a["Miss Distance (km)"]) || 7e7));
  const maxDiam = Math.max(...asteroidData.map(a => Number(a["Diameter (m)"]) || 100));
  const minDiam = Math.min(...asteroidData.map(a => Number(a["Diameter (m)"]) || 10));

  asteroidData.forEach((ast, idx) => {
    const isHazard = Boolean(ast["Hazardous"]);
    const missKm = Number(ast["Miss Distance (km)"]) || 5e6;
    const diamM = Number(ast["Diameter (m)"]) || 50;
    const velKmh = Number(ast["Velocity (km/h)"]) || 30000;
    const missLd = Number(ast["Lunar Distance (LD)"]) || (missKm / 384400.0);
    const scaleAnalogy = ast["Scale Analogy"] || "Scale unknown";

    const normDist = (maxMiss > minMiss) ? (missKm - minMiss) / (maxMiss - minMiss) : 0.5;
    const periRadius = 18 + normDist * 64;

    const inclination = (((idx * 43) % 75) - 37.5) * (Math.PI / 180);
    const theta = (idx / Math.max(1, asteroidData.length)) * Math.PI * 2;

    // Periapsis coordinates
    const pMiddle = new THREE.Vector3(
      periRadius * Math.cos(theta),
      periRadius * Math.sin(theta) * Math.sin(inclination),
      periRadius * Math.sin(theta) * Math.cos(inclination)
    );

    const normal = pMiddle.clone().normalize();
    const tangent = new THREE.Vector3(
      -Math.sin(theta),
      Math.cos(theta) * Math.sin(inclination),
      Math.cos(theta) * Math.cos(inclination)
    ).normalize();

    // Hyperbolic trajectory asymptotes
    const dDeep = 450 + normDist * 180;
    const pStart = pMiddle.clone()
      .sub(tangent.clone().multiplyScalar(dDeep))
      .add(normal.clone().multiplyScalar(dDeep * 0.08));
    const pEnd = pMiddle.clone()
      .add(tangent.clone().multiplyScalar(dDeep))
      .add(normal.clone().multiplyScalar(dDeep * 0.08));

    // Trajectory spline
    const curve = new THREE.CatmullRomCurve3([pStart, pMiddle, pEnd], false, 'catmullrom', 0.1);

    // Trajectory line geometry and vertex colors
    const curvePts = curve.getPoints(120);
    const colors = [];
    const peakCol = isHazard ? new THREE.Color(0xff003c) : new THREE.Color(0x00f0ff);
    const voidCol = new THREE.Color(0x000000);

    for (let s = 0; s < curvePts.length; s++) {
      const normS = s / (curvePts.length - 1);
      const intensity = Math.pow(Math.sin(normS * Math.PI), 1.6);
      const col = voidCol.clone().lerp(peakCol, intensity);
      colors.push(col.r, col.g, col.b);
    }

    const pathGeo = new THREE.BufferGeometry().setFromPoints(curvePts);
    pathGeo.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));

    const pathMat = new THREE.LineBasicMaterial({
      vertexColors: true,
      transparent: true,
      opacity: 0.85,
      blending: THREE.AdditiveBlending,
      depthWrite: false
    });
    const flybyLine = new THREE.Line(pathGeo, pathMat);
    scene.add(flybyLine);

    // High-density geometry and procedural displacement
    const normDiam = (maxDiam > minDiam) ? (diamM - minDiam) / (maxDiam - minDiam) : 0.5;
    const geoSize = 0.55 + normDiam * 1.5;
    const astGeo = new THREE.IcosahedronGeometry(geoSize, 6);

    const posAttr = astGeo.attributes.position;
    const v = new THREE.Vector3();
    const craterCenter = new THREE.Vector3(
      Math.sin(idx * 2.13),
      Math.cos(idx * 3.41),
      Math.sin(idx * 1.77)
    ).normalize();
    
    for (let p = 0; p < posAttr.count; p++) {
      v.fromBufferAttribute(posAttr, p);
      const dir = v.clone().normalize();
      
      const ridge1 = (1.0 - Math.abs(Math.sin(dir.x * 2.4 + idx * 0.7))) * 0.16;
      const ridge2 = Math.pow(Math.abs(Math.cos(dir.z * 3.6 + dir.y * 2.2)), 2.0) * 0.10;
      const gouge1 = -Math.pow(Math.abs(Math.sin(dir.y * 4.5 + dir.x * 3.2)), 2.5) * 0.12;
      const gouge2 = -Math.pow(Math.abs(Math.cos(dir.z * 6.0 + dir.x * 1.5)), 3.0) * 0.08;
      const microGrain = Math.sin(dir.x * 18.0) * Math.cos(dir.y * 18.0) * Math.sin(dir.z * 18.0) * 0.02;
      
      const angleToCrater = dir.angleTo(craterCenter);
      let craterDisp = 0.0;
      if (angleToCrater < 0.50) {
        const u = angleToCrater / 0.50;
        const bowl = -Math.pow(Math.cos(Math.min(1.0, u * 1.25) * Math.PI * 0.5), 2.0) * 0.22;
        const rim = Math.pow(Math.sin(Math.max(0.0, (u - 0.55) / 0.45) * Math.PI), 2.0) * 0.09;
        craterDisp = bowl + rim;
      }
      
      const totalDisp = 1.0 + ridge1 + ridge2 + gouge1 + gouge2 + microGrain + craterDisp;
      v.multiplyScalar(totalDisp);
      posAttr.setXYZ(p, v.x, v.y, v.z);
    }

    astGeo.computeVertexNormals();

    const rotAxis = new THREE.Vector3(
      (Math.random() - 0.5) * 2,
      (Math.random() - 0.5) * 2,
      (Math.random() - 0.5) * 2
    ).normalize();
    const rotSpeed = 0.005 + Math.random() * 0.015;

    const astMat = new THREE.MeshStandardMaterial({
      color: 0x222426,
      roughness: 0.95,
      metalness: 0.05,
      flatShading: false,
      bumpMap: asteroidBumpMap,
      bumpScale: 0.02,
      normalMap: asteroidNormalTex,
      normalScale: new THREE.Vector2(2.5, 2.5),
      emissive: isHazard ? new THREE.Color(0xff003c) : new THREE.Color(0x000000),
      emissiveIntensity: isHazard ? 0.35 : 0.0
    });
    const rockMesh = new THREE.Mesh(astGeo, astMat);

    if (isHazard) {
      const markerGeo = new THREE.RingGeometry(geoSize * 1.4, geoSize * 1.55, 32);
      const markerMat = new THREE.MeshBasicMaterial({
        color: 0xff003c,
        side: THREE.DoubleSide,
        transparent: true,
        opacity: 0.95
      });
      const marker = new THREE.Mesh(markerGeo, markerMat);
      marker.rotation.x = Math.PI / 2;
      rockMesh.add(marker);
    }

    const hitboxRadius = geoSize * 8.0;
    const hitboxGeo = new THREE.SphereGeometry(hitboxRadius, 16, 16);
    const hitboxMat = new THREE.MeshBasicMaterial({ visible: false });
    const hitboxMesh = new THREE.Mesh(hitboxGeo, hitboxMat);

    const astGroup = new THREE.Group();
    astGroup.add(rockMesh);
    astGroup.add(hitboxMesh);

    const startT = (idx * 0.28 + 0.15) % 1.0;
    const flybySpeed = (velKmh / 60000.0) * 0.0006 + 0.0003;

    const telemetryData = {
      name: ast["Name"],
      isHazard: isHazard,
      diameter: diamM,
      velocity: velKmh,
      missKm: missKm,
      missLd: missLd,
      scaleAnalogy: scaleAnalogy,
      curve: curve,
      t: startT,
      speed: flybySpeed,
      rotAxis: rotAxis,
      rotSpeed: rotSpeed,
      periapsis: pMiddle,
      inclination: inclination,
      group: astGroup,
      rock: rockMesh,
      hitbox: hitboxMesh,
      geoSize: geoSize
    };

    astGroup.userData = telemetryData;
    rockMesh.userData = telemetryData;
    hitboxMesh.userData = telemetryData;

    const initialPos = curve.getPoint(startT);
    astGroup.position.copy(initialPos);

    asteroidGroup.add(astGroup);
    asteroidGroups.push(telemetryData);
    interactiveObjects.push(hitboxMesh);
  });
}
