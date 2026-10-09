/**
 * HealthGuard 3D Medicine Reminder Experience.
 * Built with Three.js. Provides dosage-form specific 3D animations (Tablet, Capsule, Syrup, Inhaler),
 * interactive 360° orbit inspection, glass-of-water swallowing sequence, simplified human silhouette anatomy transit,
 * playback controls (Play, Pause, Replay, Reset), and automatic 2D fallback.
 */

class Medicine3DExperience {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.options = Object.assign({
            dosageForm: "Tablet",
            medicineName: "Augmentin 625 Duo Tablet",
            primaryColor: 0x2563eb,
            secondaryColor: 0x1d4ed8,
            pillColor: 0xffffff,
            capColor: 0x9333ea,
            autoPlaySequence: true,
            onDoseTaken: null
        }, options);

        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.animationFrameId = null;
        this.medicineGroup = null;
        this.waterGlassGroup = null;
        this.silhouetteGroup = null;
        this.checkmarkGroup = null;
        this.particlesGroup = null;

        // Interaction state
        this.isDragging = false;
        this.previousMousePosition = { x: 0, y: 0 };
        this.userRotation = { x: 0, y: 0 };
        this.isPaused = false;

        // Animation sequence state
        this.sequencePhase = 0; // 0: Idle rotate, 1: Glass appears, 2: Move to water, 3: Swallowing silhouette, 4: Done/Checkmark
        this.phaseStartTime = 0;
        this.clock = null;

        this.init();
    }

    isWebGLAvailable() {
        try {
            const canvas = document.createElement("canvas");
            return !!(window.WebGLRenderingContext && (canvas.getContext("webgl") || canvas.getContext("experimental-webgl")));
        } catch (e) {
            return false;
        }
    }

    init() {
        if (!this.container) return;

        // Check WebGL availability
        if (!this.isWebGLAvailable() || typeof THREE === "undefined") {
            console.warn("WebGL not available or Three.js not loaded. Falling back to 2D illustration mode.");
            this.render2DFallback();
            return;
        }

        this.container.innerHTML = "";
        const width = this.container.clientWidth || 480;
        const height = this.container.clientHeight || 360;

        // Setup Scene & Clock
        this.scene = new THREE.Scene();
        this.clock = new THREE.Clock();

        // Setup Camera
        this.camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 100);
        this.camera.position.set(0, 1.2, 5.2);
        this.camera.lookAt(0, 0.2, 0);

        // Setup Renderer
        this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: "high-performance" });
        this.renderer.setSize(width, height);
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        this.container.appendChild(this.renderer.domElement);

        // Setup Lighting
        this.setupLighting();

        // Build Medicine 3D Model
        this.buildMedicineModel(this.options.dosageForm);

        // Build Glass of Water
        this.buildGlassOfWater();

        // Build Silhouette & Swallowing Concept
        this.buildSwallowingSilhouette();

        // Build Success Checkmark
        this.buildCheckmark();

        // Add studio shadow plane
        this.buildShadowPlane();

        // Event listeners
        this.attachInteractionEvents();
        window.addEventListener("resize", () => this.onWindowResize());

        // Start render loop
        this.phaseStartTime = performance.now();
        this.animate();

        if (this.options.autoPlaySequence) {
            setTimeout(() => this.triggerSwallowingSequence(), 800);
        }
    }

    setupLighting() {
        const ambient = new THREE.AmbientLight(0xf8fafc, 1.2);
        this.scene.add(ambient);

        const keyLight = new THREE.DirectionalLight(0xffffff, 1.4);
        keyLight.position.set(4, 6, 4);
        keyLight.castShadow = true;
        keyLight.shadow.mapSize.width = 1024;
        keyLight.shadow.mapSize.height = 1024;
        this.scene.add(keyLight);

        const fillLight = new THREE.DirectionalLight(0xdbeafe, 0.8);
        fillLight.position.set(-4, 3, 2);
        this.scene.add(fillLight);

        const rimLight = new THREE.DirectionalLight(0x93c5fd, 1.0);
        rimLight.position.set(0, -2, -4);
        this.scene.add(rimLight);
    }

    buildShadowPlane() {
        const planeGeo = new THREE.PlaneGeometry(8, 8);
        const planeMat = new THREE.ShadowMaterial({ opacity: 0.15 });
        const plane = new THREE.Mesh(planeGeo, planeMat);
        plane.rotation.x = -Math.PI / 2;
        plane.position.y = -1.1;
        plane.receiveShadow = true;
        this.scene.add(plane);
    }

    buildMedicineModel(dosageForm) {
        if (this.medicineGroup) {
            this.scene.remove(this.medicineGroup);
        }
        this.medicineGroup = new THREE.Group();
        this.medicineGroup.position.set(0, 0.2, 0);

        const form = dosageForm.toLowerCase();

        if (form.includes("capsule")) {
            this.createCapsuleModel();
        } else if (form.includes("syrup") || form.includes("liquid") || form.includes("bottle")) {
            this.createSyrupModel();
        } else if (form.includes("inhaler") || form.includes("spray")) {
            this.createInhalerModel();
        } else {
            this.createTabletModel();
        }

        this.scene.add(this.medicineGroup);
    }

    createTabletModel() {
        const tabletMat = new THREE.MeshStandardMaterial({
            color: this.options.pillColor || 0xffffff,
            roughness: 0.32,
            metalness: 0.05
        });

        const cylinderGeo = new THREE.CylinderGeometry(1.0, 1.0, 0.32, 48, 1);
        const cylinder = new THREE.Mesh(cylinderGeo, tabletMat);
        cylinder.castShadow = true;
        cylinder.receiveShadow = true;
        this.medicineGroup.add(cylinder);

        const topDomeGeo = new THREE.SphereGeometry(1.0, 32, 16, 0, Math.PI * 2, 0, Math.PI / 4.2);
        topDomeGeo.scale(1.0, 0.35, 1.0);
        const topDome = new THREE.Mesh(topDomeGeo, tabletMat);
        topDome.position.y = 0.15;
        this.medicineGroup.add(topDome);

        const botDomeGeo = topDomeGeo.clone();
        botDomeGeo.rotateX(Math.PI);
        const botDome = new THREE.Mesh(botDomeGeo, tabletMat);
        botDome.position.y = -0.15;
        this.medicineGroup.add(botDome);

        const scoreGeo = new THREE.BoxGeometry(1.8, 0.04, 0.04);
        const scoreMat = new THREE.MeshStandardMaterial({ color: 0x94a3b8, roughness: 0.6 });
        const score = new THREE.Mesh(scoreGeo, scoreMat);
        score.position.y = 0.31;
        this.medicineGroup.add(score);

        this.medicineGroup.rotation.x = 0.35;
        this.medicineGroup.rotation.y = 0.4;
    }

    createCapsuleModel() {
        const capMat = new THREE.MeshStandardMaterial({
            color: this.options.capColor || 0x2563eb,
            roughness: 0.18,
            metalness: 0.12
        });

        const bodyMat = new THREE.MeshStandardMaterial({
            color: this.options.pillColor || 0xffffff,
            roughness: 0.2,
            metalness: 0.08
        });

        const capGroup = new THREE.Group();

        const capCylinder = new THREE.Mesh(new THREE.CylinderGeometry(0.52, 0.52, 0.9, 36), capMat);
        capCylinder.position.x = 0.45;
        capCylinder.rotation.z = Math.PI / 2;
        capCylinder.castShadow = true;
        capGroup.add(capCylinder);

        const capSphere = new THREE.Mesh(new THREE.SphereGeometry(0.52, 32, 16, 0, Math.PI * 2, 0, Math.PI / 2), capMat);
        capSphere.position.x = 0.9;
        capSphere.rotation.z = -Math.PI / 2;
        capSphere.castShadow = true;
        capGroup.add(capSphere);

        const bodyCylinder = new THREE.Mesh(new THREE.CylinderGeometry(0.5, 0.5, 0.9, 36), bodyMat);
        bodyCylinder.position.x = -0.45;
        bodyCylinder.rotation.z = Math.PI / 2;
        bodyCylinder.castShadow = true;
        capGroup.add(bodyCylinder);

        const bodySphere = new THREE.Mesh(new THREE.SphereGeometry(0.5, 32, 16, 0, Math.PI * 2, 0, Math.PI / 2), bodyMat);
        bodySphere.position.x = -0.9;
        bodySphere.rotation.z = Math.PI / 2;
        bodySphere.castShadow = true;
        capGroup.add(bodySphere);

        const ringGeo = new THREE.TorusGeometry(0.525, 0.02, 16, 40);
        const ringMat = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.7 });
        const ring = new THREE.Mesh(ringGeo, ringMat);
        ring.rotation.y = Math.PI / 2;
        capGroup.add(ring);

        this.medicineGroup.add(capGroup);
        this.medicineGroup.rotation.z = 0.25;
        this.medicineGroup.rotation.y = 0.5;
    }

    createSyrupModel() {
        const bottleGroup = new THREE.Group();

        const amberMat = new THREE.MeshStandardMaterial({
            color: 0x78350f,
            roughness: 0.15,
            metalness: 0.1,
            transparent: true,
            opacity: 0.88
        });

        const bodyGeo = new THREE.CylinderGeometry(0.65, 0.65, 1.4, 32);
        const body = new THREE.Mesh(bodyGeo, amberMat);
        body.castShadow = true;
        bottleGroup.add(body);

        const shoulderGeo = new THREE.ConeGeometry(0.65, 0.35, 32);
        const shoulder = new THREE.Mesh(shoulderGeo, amberMat);
        shoulder.position.y = 0.85;
        bottleGroup.add(shoulder);

        const neckGeo = new THREE.CylinderGeometry(0.28, 0.28, 0.4, 24);
        const neck = new THREE.Mesh(neckGeo, amberMat);
        neck.position.y = 1.1;
        bottleGroup.add(neck);

        const capGeo = new THREE.CylinderGeometry(0.32, 0.32, 0.35, 24);
        const capMat = new THREE.MeshStandardMaterial({ color: 0xf1f5f9, roughness: 0.4 });
        const cap = new THREE.Mesh(capGeo, capMat);
        cap.position.y = 1.35;
        bottleGroup.add(cap);

        const labelGeo = new THREE.CylinderGeometry(0.66, 0.66, 0.9, 32, 1, true, 0, Math.PI * 1.5);
        const labelMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.6 });
        const label = new THREE.Mesh(labelGeo, labelMat);
        bottleGroup.add(label);

        const cupGeo = new THREE.CylinderGeometry(0.42, 0.32, 0.6, 24, 1, true);
        const cupMat = new THREE.MeshStandardMaterial({ color: 0xbae6fd, transparent: true, opacity: 0.6, roughness: 0.2 });
        const cup = new THREE.Mesh(cupGeo, cupMat);
        cup.position.set(0.95, -0.4, 0.2);
        bottleGroup.add(cup);

        const liqGeo = new THREE.CylinderGeometry(0.38, 0.33, 0.3, 24);
        const liqMat = new THREE.MeshStandardMaterial({ color: 0xbe123c, roughness: 0.2 });
        const liq = new THREE.Mesh(liqGeo, liqMat);
        liq.position.set(0.95, -0.5, 0.2);
        bottleGroup.add(liq);

        bottleGroup.scale.set(0.85, 0.85, 0.85);
        this.medicineGroup.add(bottleGroup);
    }

    createInhalerModel() {
        const inhalerGroup = new THREE.Group();
        const blueMat = new THREE.MeshStandardMaterial({ color: 0x0284c7, roughness: 0.3 });

        const bodyGeo = new THREE.CylinderGeometry(0.48, 0.48, 1.4, 32);
        const body = new THREE.Mesh(bodyGeo, blueMat);
        inhalerGroup.add(body);

        const canGeo = new THREE.CylinderGeometry(0.42, 0.42, 0.8, 32);
        const canMat = new THREE.MeshStandardMaterial({ color: 0xcfd8dc, metalness: 0.8, roughness: 0.2 });
        const canister = new THREE.Mesh(canGeo, canMat);
        canister.position.y = 0.8;
        inhalerGroup.add(canister);

        const mouthGeo = new THREE.BoxGeometry(0.65, 0.45, 0.75);
        const mouthpiece = new THREE.Mesh(mouthGeo, blueMat);
        mouthpiece.position.set(0, -0.45, 0.48);
        inhalerGroup.add(mouthpiece);

        const capGeo = new THREE.BoxGeometry(0.68, 0.48, 0.3);
        const cap = new THREE.Mesh(capGeo, new THREE.MeshStandardMaterial({ color: 0x0369a1 }));
        cap.position.set(0, -0.45, 0.88);
        inhalerGroup.add(cap);

        const particleCount = 40;
        const partGeo = new THREE.BufferGeometry();
        const positions = new Float32Array(particleCount * 3);
        for (let i = 0; i < particleCount; i++) {
            positions[i * 3] = (Math.random() - 0.5) * 0.4;
            positions[i * 3 + 1] = -0.45 + (Math.random() - 0.5) * 0.3;
            positions[i * 3 + 2] = 1.0 + Math.random() * 1.2;
        }
        partGeo.setAttribute("position", new THREE.BufferAttribute(positions, 3));
        const partMat = new THREE.PointsMaterial({ color: 0xe0f2fe, size: 0.08, transparent: true, opacity: 0.7 });
        this.inhalerMist = new THREE.Points(partGeo, partMat);
        this.inhalerMist.visible = false;
        inhalerGroup.add(this.inhalerMist);

        inhalerGroup.scale.set(0.9, 0.9, 0.9);
        this.medicineGroup.add(inhalerGroup);
    }

    buildGlassOfWater() {
        this.waterGlassGroup = new THREE.Group();
        this.waterGlassGroup.position.set(1.6, -0.2, 0);

        const glassMat = new THREE.MeshStandardMaterial({
            color: 0xe0f2fe,
            roughness: 0.1,
            metalness: 0.05,
            transparent: true,
            opacity: 0.45
        });

        const glassGeo = new THREE.CylinderGeometry(0.55, 0.45, 1.4, 32, 1, true);
        const glassMesh = new THREE.Mesh(glassGeo, glassMat);
        this.waterGlassGroup.add(glassMesh);

        const baseGeo = new THREE.CylinderGeometry(0.46, 0.46, 0.12, 32);
        const baseMesh = new THREE.Mesh(baseGeo, glassMat);
        baseMesh.position.y = -0.65;
        this.waterGlassGroup.add(baseMesh);

        const waterMat = new THREE.MeshStandardMaterial({
            color: 0x38bdf8,
            roughness: 0.05,
            metalness: 0.1,
            transparent: true,
            opacity: 0.65
        });
        const waterGeo = new THREE.CylinderGeometry(0.5, 0.43, 1.0, 32);
        const waterMesh = new THREE.Mesh(waterGeo, waterMat);
        waterMesh.position.y = -0.15;
        this.waterGlassGroup.add(waterMesh);

        const surfGeo = new THREE.CircleGeometry(0.5, 32);
        const surfMat = new THREE.MeshBasicMaterial({ color: 0xbae6fd, transparent: true, opacity: 0.8 });
        const surf = new THREE.Mesh(surfGeo, surfMat);
        surf.rotation.x = -Math.PI / 2;
        surf.position.y = 0.35;
        this.waterGlassGroup.add(surf);

        this.waterGlassGroup.scale.set(0.001, 0.001, 0.001);
        this.waterGlassGroup.visible = false;
        this.scene.add(this.waterGlassGroup);
    }

    buildSwallowingSilhouette() {
        this.silhouetteGroup = new THREE.Group();
        this.silhouetteGroup.position.set(-1.4, 0.1, 0);

        const shape = new THREE.Shape();
        shape.moveTo(-0.2, 1.2);
        shape.quadraticCurveTo(0.3, 1.2, 0.5, 0.8);
        shape.lineTo(0.7, 0.5);
        shape.lineTo(0.55, 0.4);
        shape.lineTo(0.65, 0.3);
        shape.lineTo(0.62, 0.15);
        shape.quadraticCurveTo(0.65, 0.0, 0.55, -0.1);
        shape.quadraticCurveTo(0.3, -0.3, 0.25, -0.8);
        shape.lineTo(-0.4, -0.8);
        shape.quadraticCurveTo(-0.5, 0.5, -0.2, 1.2);

        const geom = new THREE.ShapeGeometry(shape);
        const mat = new THREE.MeshBasicMaterial({
            color: 0x3b82f6,
            transparent: true,
            opacity: 0.18,
            side: THREE.DoubleSide
        });
        const mesh = new THREE.Mesh(geom, mat);
        this.silhouetteGroup.add(mesh);

        const curve = new THREE.QuadraticBezierCurve3(
            new THREE.Vector3(0.5, 0.25, 0.05),
            new THREE.Vector3(0.2, -0.1, 0.05),
            new THREE.Vector3(0.15, -0.75, 0.05)
        );
        const tubeGeo = new THREE.TubeGeometry(curve, 24, 0.04, 8, false);
        const tubeMat = new THREE.MeshBasicMaterial({ color: 0x10b981, transparent: true, opacity: 0.7 });
        const tubeMesh = new THREE.Mesh(tubeGeo, tubeMat);
        this.silhouetteGroup.add(tubeMesh);

        this.silhouetteGroup.scale.set(0.001, 0.001, 0.001);
        this.silhouetteGroup.visible = false;
        this.scene.add(this.silhouetteGroup);
    }

    buildCheckmark() {
        this.checkmarkGroup = new THREE.Group();
        this.checkmarkGroup.position.set(0, 0.3, 1.0);

        const discGeo = new THREE.CircleGeometry(0.75, 40);
        const discMat = new THREE.MeshBasicMaterial({ color: 0x10b981, transparent: true, opacity: 0.9 });
        const disc = new THREE.Mesh(discGeo, discMat);
        this.checkmarkGroup.add(disc);

        const tickShape = new THREE.Shape();
        tickShape.moveTo(-0.35, 0.0);
        tickShape.lineTo(-0.1, -0.25);
        tickShape.lineTo(0.35, 0.25);
        tickShape.lineTo(0.28, 0.32);
        tickShape.lineTo(-0.1, -0.12);
        tickShape.lineTo(-0.28, 0.08);
        tickShape.closePath();

        const tickGeo = new THREE.ShapeGeometry(tickShape);
        const tickMat = new THREE.MeshBasicMaterial({ color: 0xffffff });
        const tick = new THREE.Mesh(tickGeo, tickMat);
        tick.position.z = 0.02;
        this.checkmarkGroup.add(tick);

        this.checkmarkGroup.scale.set(0.001, 0.001, 0.001);
        this.checkmarkGroup.visible = false;
        this.scene.add(this.checkmarkGroup);
    }

    attachInteractionEvents() {
        const dom = this.renderer.domElement;

        const onPointerDown = (e) => {
            this.isDragging = true;
            this.previousMousePosition = { x: e.clientX, y: e.clientY };
        };

        const onPointerMove = (e) => {
            if (!this.isDragging || !this.medicineGroup) return;
            const deltaX = e.clientX - this.previousMousePosition.x;
            const deltaY = e.clientY - this.previousMousePosition.y;

            this.medicineGroup.rotation.y += deltaX * 0.015;
            this.medicineGroup.rotation.x += deltaY * 0.015;

            this.previousMousePosition = { x: e.clientX, y: e.clientY };
        };

        const onPointerUp = () => {
            this.isDragging = false;
        };

        dom.addEventListener("pointerdown", onPointerDown);
        window.addEventListener("pointermove", onPointerMove);
        window.addEventListener("pointerup", onPointerUp);
    }

    onWindowResize() {
        if (!this.container || !this.renderer || !this.camera) return;
        const width = this.container.clientWidth;
        const height = this.container.clientHeight;
        if (width === 0 || height === 0) return;

        this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(width, height);
    }

    // Playback Controls
    pause() {
        this.isPaused = true;
        this.updateStepStatus("Paused (Click Play to resume)");
    }

    play() {
        this.isPaused = false;
        this.updateStepStatus("Playing 3D Animation...");
    }

    replay() {
        this.isPaused = false;
        this.reset();
        this.triggerSwallowingSequence();
    }

    reset() {
        this.sequencePhase = 0;
        this.phaseStartTime = performance.now();
        if (this.medicineGroup) {
            this.medicineGroup.position.set(0, 0.2, 0);
            this.medicineGroup.scale.set(1.0, 1.0, 1.0);
        }
        if (this.waterGlassGroup) {
            this.waterGlassGroup.scale.set(0.001, 0.001, 0.001);
            this.waterGlassGroup.visible = false;
        }
        if (this.silhouetteGroup) {
            this.silhouetteGroup.scale.set(0.001, 0.001, 0.001);
            this.silhouetteGroup.visible = false;
        }
        if (this.checkmarkGroup) {
            this.checkmarkGroup.scale.set(0.001, 0.001, 0.001);
            this.checkmarkGroup.visible = false;
        }
        if (this.inhalerMist) {
            this.inhalerMist.visible = false;
        }
        this.updateStepStatus("Interactive 3D Medicine View (Drag to Rotate)");
    }

    triggerSwallowingSequence() {
        this.phaseStartTime = performance.now();
        this.sequencePhase = 1;
        this.updateStepStatus("Step 1/3: Glass of water appears...");
    }

    confirmDoseTaken() {
        this.sequencePhase = 4;
        this.phaseStartTime = performance.now();
        this.updateStepStatus("✓ Dose Verified & Recorded!");
        if (typeof this.options.onDoseTaken === "function") {
            this.options.onDoseTaken();
        }
    }

    updateStepStatus(statusText) {
        const statusEl = document.getElementById("reminder-3d-step-desc");
        if (statusEl) {
            statusEl.textContent = statusText;
        }
    }

    animate() {
        this.animationFrameId = requestAnimationFrame(() => this.animate());

        if (this.isPaused) {
            this.renderer.render(this.scene, this.camera);
            return;
        }

        const now = performance.now();
        const elapsedSincePhase = (now - this.phaseStartTime) / 1000.0;
        const totalTime = this.clock ? this.clock.getElapsedTime() : 0;

        // Idle rotation of medicine if not actively dragged
        if (!this.isDragging && this.medicineGroup) {
            this.medicineGroup.rotation.y += 0.015;
            this.medicineGroup.position.y = 0.2 + Math.sin(totalTime * 2.2) * 0.05;
        }

        // Optimized Smooth 4.5s Sequence Timing
        if (this.sequencePhase === 1) {
            // Step 1: Glass appears (1.2s)
            this.waterGlassGroup.visible = true;
            const progress = Math.min(elapsedSincePhase / 1.0, 1.0);
            this.waterGlassGroup.scale.set(progress, progress, progress);

            if (elapsedSincePhase > 1.2) {
                this.sequencePhase = 2;
                this.phaseStartTime = now;
                this.updateStepStatus("Step 2/3: Ingestion with water...");
            }
        } else if (this.sequencePhase === 2) {
            // Step 2: Medicine moves toward glass (1.4s)
            const progress = Math.min(elapsedSincePhase / 1.3, 1.0);
            if (this.medicineGroup) {
                this.medicineGroup.position.x = progress * 1.2;
                this.medicineGroup.position.y = 0.2 + Math.sin(progress * Math.PI) * 0.35;
                this.medicineGroup.scale.set(1.0 - progress * 0.35, 1.0 - progress * 0.35, 1.0 - progress * 0.35);
            }

            if (elapsedSincePhase > 1.4) {
                this.sequencePhase = 3;
                this.phaseStartTime = now;
                this.updateStepStatus("Step 3/3: Esophageal transit & absorption...");
            }
        } else if (this.sequencePhase === 3) {
            // Step 3: Silhouette appears showing clean swallowing transit (1.5s)
            this.silhouetteGroup.visible = true;
            const progress = Math.min(elapsedSincePhase / 1.0, 1.0);
            this.silhouetteGroup.scale.set(progress * 1.1, progress * 1.1, progress * 1.1);

            if (this.inhalerMist) {
                this.inhalerMist.visible = true;
            }

            if (elapsedSincePhase > 1.5) {
                this.sequencePhase = 4;
                this.phaseStartTime = now;
                this.updateStepStatus("✓ Ready: Please confirm dose taken");
            }
        } else if (this.sequencePhase === 4) {
            // Step 4: Checkmark burst
            this.checkmarkGroup.visible = true;
            const progress = Math.min(elapsedSincePhase / 0.6, 1.0);
            const scale = Math.sin(progress * Math.PI * 0.5) * 1.15;
            this.checkmarkGroup.scale.set(scale, scale, scale);
        }

        this.renderer.render(this.scene, this.camera);
    }

    render2DFallback() {
        this.container.innerHTML = `
            <div class="p-6 text-center flex flex-col items-center justify-center h-full bg-slate-50 rounded-2xl">
                <div class="w-24 h-24 mb-3 relative flex items-center justify-center bg-teal-50 rounded-full border-4 border-teal-200 shadow-inner">
                    <span class="text-4xl animate-bounce">💊</span>
                </div>
                <h4 class="text-base font-bold text-slate-800">${this.options.medicineName}</h4>
                <p class="text-xs text-slate-500 mt-1">Dosage Form: <span class="font-semibold text-teal-700">${this.options.dosageForm}</span></p>
                <div class="mt-3 px-3 py-1.5 bg-teal-100 text-teal-800 text-xs font-semibold rounded-full flex items-center gap-1.5">
                    <span>💧</span> Take with full glass of water
                </div>
            </div>
        `;
    }

    destroy() {
        if (this.animationFrameId) {
            cancelAnimationFrame(this.animationFrameId);
        }
        if (this.renderer && this.renderer.domElement) {
            this.container.innerHTML = "";
        }
    }
}

window.Medicine3DExperience = Medicine3DExperience;
