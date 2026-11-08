// Motor JS Dual para Simuladores de Péndulo Simple y Péndulo Doble
// Crea instancias independientes con persistencia en segundo plano para Dash SPA

(function() {
    function createPendulumEngine(fixedMode, prefix, defaultT1, defaultT2) {
        let initialized = false;
        const mode = fixedMode; // 'Simple' o 'Doble'
        let isRunning = false;
        let fixTrails = false;
        let time = 0.0;
        const dt = 0.001;
        let simSpeed = 1.0;

        let g = 9.8, b = 0.0, L1 = 2.0, L2 = 1.0, m1 = 1.0, m2 = 1.0;
        let t1_0 = defaultT1, t2_0 = defaultT2, nPendulums = 5, log_dt = -3.0;

        let states = [];
        let trails = [];
        let timeHistory = [];
        let divHistory = [];
        let phaseHistory = [];
        let energyT = [];
        let energyV = [];
        let energyTot = [];

        const palette = [
            '#ff0000', '#0400fa', '#002400', '#000000', '#880088', '#ff8080',
            '#80ffff', '#df80ff', '#ffff80', '#ffaa80', '#80ffbf', '#c080ff'
        ];

        let ctxSim = null, ctxDiv = null, ctxPhase = null;
        let canSim = null, canDiv = null, canPhase = null;
        let animationId = null;
        let boundBtnIniciar = null;

        function el(suffix) {
            return document.getElementById(prefix + suffix);
        }

        function setText(suffix, text) {
            const node = el(suffix);
            if (node && node.innerText !== text) node.innerText = text;
        }

        function massToRadius(m) {
            const val = Math.max(0.1, Number(m) || 1.0);
            return 3.0 + 4.0 * Math.pow(val, 0.6);
        }

        // --- AUTO-RECONEXIÓN DE LIENZOS (CANVAS) EN DASH ---
        function ensureCanvas() {
            const hostSim = el('canvas-physics-host');
            const hostDiv = el('canvas-div-host');
            const hostPhase = el('canvas-phase-host');

            if (!hostSim || !hostDiv || !hostPhase) return false;

            let createdOrResized = false;

            let cSim = hostSim.querySelector('canvas');
            if (!cSim) {
                cSim = document.createElement('canvas');
                hostSim.appendChild(cSim);
                createdOrResized = true;
            }
            if (canSim !== cSim) {
                canSim = cSim;
                ctxSim = canSim.getContext('2d');
                createdOrResized = true;
            }

            let cDiv = hostDiv.querySelector('canvas');
            if (!cDiv) {
                cDiv = document.createElement('canvas');
                hostDiv.appendChild(cDiv);
                createdOrResized = true;
            }
            if (canDiv !== cDiv) {
                canDiv = cDiv;
                ctxDiv = canDiv.getContext('2d');
                createdOrResized = true;
            }

            let cPhase = hostPhase.querySelector('canvas');
            if (!cPhase) {
                cPhase = document.createElement('canvas');
                hostPhase.appendChild(cPhase);
                createdOrResized = true;
            }
            if (canPhase !== cPhase) {
                canPhase = cPhase;
                ctxPhase = canPhase.getContext('2d');
                createdOrResized = true;
            }

            if (hostSim.clientWidth === 0 || hostSim.clientHeight === 0) {
                return false;
            }

            [canSim, canDiv, canPhase].forEach(c => {
                if (c.parentElement) {
                    const w = c.parentElement.clientWidth;
                    const h = c.parentElement.clientHeight;
                    if (w > 0 && h > 0 && (c.width !== w || c.height !== h)) {
                        c.width = w;
                        c.height = h;
                        createdOrResized = true;
                    }
                }
            });

            if (createdOrResized) {
                updateUIFromState();
                updateIndicators();
                drawAllInternal();
            }
            return true;
        }

        window.addEventListener('resize', function() {
            ensureCanvas();
        });

        // --- MOTOR MATEMÁTICO RK4 ---
        function derivatives(state) {
            let [t1, w1, t2, w2] = state;

            if (mode === 'Simple') {
                let dw1 = -(g / L1) * Math.sin(t1) - b * w1;
                return [w1, dw1, 0, 0];
            }

            let delta = t1 - t2;
            let den = 2.0 * m1 + m2 - m2 * Math.cos(2.0 * delta);
            let num1 = -g * (2.0 * m1 + m2) * Math.sin(t1)
                       - m2 * g * Math.sin(t1 - 2.0 * t2)
                       - 2.0 * Math.sin(delta) * m2 * (w2 * w2 * L2 + w1 * w1 * L1 * Math.cos(delta));
            let dw1 = (num1 / (L1 * den)) - b * w1;

            let num2 = 2.0 * Math.sin(delta) * (
                w1 * w1 * L1 * (m1 + m2)
                + g * (m1 + m2) * Math.cos(t1)
                + w2 * w2 * L2 * m2 * Math.cos(delta)
            );
            let dw2 = (num2 / (L2 * den)) - b * w2;

            return [w1, dw1, w2, dw2];
        }

        function rk4Step() {
            for (let i = 0; i < nPendulums; i++) {
                let y = states[i];
                if (!y) continue;
                let k1 = derivatives(y);
                let k2 = derivatives([y[0]+0.5*dt*k1[0], y[1]+0.5*dt*k1[1], y[2]+0.5*dt*k1[2], y[3]+0.5*dt*k1[3]]);
                let k3 = derivatives([y[0]+0.5*dt*k2[0], y[1]+0.5*dt*k2[1], y[2]+0.5*dt*k2[2], y[3]+0.5*dt*k2[3]]);
                let k4 = derivatives([y[0]+dt*k3[0], y[1]+dt*k3[1], y[2]+dt*k3[2], y[3]+dt*k3[3]]);

                states[i] = [
                    y[0] + (dt/6)*(k1[0] + 2*k2[0] + 2*k3[0] + k4[0]),
                    y[1] + (dt/6)*(k1[1] + 2*k2[1] + 2*k3[1] + k4[1]),
                    y[2] + (dt/6)*(k1[2] + 2*k2[2] + 2*k3[2] + k4[2]),
                    y[3] + (dt/6)*(k1[3] + 2*k2[3] + 2*k3[3] + k4[3])
                ];
            }
            time += dt;
        }

        function wrapAngle(a) {
            return ((a + Math.PI) % (2 * Math.PI) + 2 * Math.PI) % (2 * Math.PI) - Math.PI;
        }

        function calculateEnergy(state) {
            if (!state) return [0, 0, 0];
            let [t1, w1, t2, w2] = state;
            let T, V;
            if (mode === 'Simple') {
                T = 0.5 * m1 * (L1 * w1) ** 2;
                V = m1 * g * L1 * (1.0 - Math.cos(t1));
            } else {
                T = 0.5 * m1 * (L1 * w1) ** 2
                    + 0.5 * m2 * ((L1 * w1) ** 2 + (L2 * w2) ** 2 + 2.0 * L1 * L2 * w1 * w2 * Math.cos(t1 - t2));
                V = (m1 + m2) * g * L1 * (1.0 - Math.cos(t1)) + m2 * g * L2 * (1.0 - Math.cos(t2));
            }
            return [T, V, T + V];
        }

        function recordSample() {
            if (states.length === 0) return;

            for (let i = 0; i < nPendulums; i++) {
                let s = states[i];
                let x = mode === 'Simple' ? L1 * Math.sin(s[0]) : L1 * Math.sin(s[0]) + L2 * Math.sin(s[2]);
                let y = mode === 'Simple' ? L1 * Math.cos(s[0]) : L1 * Math.cos(s[0]) + L2 * Math.cos(s[2]);
                trails[i].push({x, y});

                if (!fixTrails) {
                    if (trails[i].length > 100) trails[i].shift();
                } else {
                    if (trails[i].length > 3500) trails[i].shift();
                }
            }

            timeHistory.push(time);
            if (nPendulums > 1) {
                let maxDiff = mode === 'Simple'
                    ? Math.abs(states[nPendulums - 1][0] - states[0][0])
                    : Math.abs(states[nPendulums - 1][0] - states[0][0]) + Math.abs(states[nPendulums - 1][2] - states[0][2]);
                let div = maxDiff > 1e-12 ? Math.log10(maxDiff) : -12;
                divHistory.push(div);
            } else {
                divHistory.push(-8);
            }

            let t1wrap = wrapAngle(states[0][0]);
            if (mode === 'Simple') {
                phaseHistory.push({x: t1wrap, y: states[0][1]});
            } else {
                let t2wrap = wrapAngle(states[0][2]);
                phaseHistory.push({x: t1wrap, y: t2wrap});
            }

            let energies = calculateEnergy(states[0]);
            energyT.push(energies[0]);
            energyV.push(energies[1]);
            energyTot.push(energies[2]);

            if (timeHistory.length > 300) {
                timeHistory.shift();
                divHistory.shift();
                phaseHistory.shift();
                energyT.shift();
                energyV.shift();
                energyTot.shift();
            }
        }

        function initStates() {
            time = 0.0;
            states = [];
            trails = [];
            let dtheta = Math.pow(10, log_dt) * Math.PI / 180;
            let baset1 = t1_0 * Math.PI / 180;
            let baset2 = t2_0 * Math.PI / 180;

            for (let i = 0; i < nPendulums; i++) {
                states.push([baset1 + i * dtheta, 0, baset2 + i * dtheta, 0]);
                trails.push([]);
            }
            timeHistory = [];
            divHistory = [];
            phaseHistory = [];
            energyT = [];
            energyV = [];
            energyTot = [];

            recordSample();
            updateUIFromState();
            updateIndicators();
            if (ensureCanvas()) drawAllInternal();
        }

        function clearTrails() {
            trails.forEach(t => t.length = 0);
            timeHistory = [];
            divHistory = [];
            phaseHistory = [];
            energyT = [];
            energyV = [];
            energyTot = [];
            recordSample();
            if (ensureCanvas()) drawAllInternal();
        }

        function updateUIFromState() {
            setText('val-t1', `${t1_0}°`);
            setText('val-t2', `${t2_0}°`);
            setText('val-n', `${nPendulums}`);
            setText('val-dt', `${Number(log_dt).toFixed(1)}`);
            setText('val-l1', `${Number(L1).toFixed(1)} m`);
            setText('val-l2', `${Number(L2).toFixed(1)} m`);
            setText('val-g', `${Number(g).toFixed(1)} m/s²`);
            setText('val-b', `${Number(b).toFixed(2)}`);
            setText('val-m1', `${Number(m1).toFixed(1)} kg`);
            setText('val-m2', `${Number(m2).toFixed(1)} kg`);
            setText('val-speed', `${Number(simSpeed).toFixed(1)}x`);

            const btnIni = el('btn-iniciar');
            if (btnIni) {
                btnIni.innerText = isRunning ? 'Pausar' : 'Iniciar';
                btnIni.className = isRunning ? 'action-btn accent-active' : 'action-btn primary';
            }

            const btnFix = el('btn-fijar');
            if (btnFix) {
                btnFix.innerText = fixTrails ? 'Soltar Estelas' : 'Fijar Estelas';
                btnFix.className = fixTrails ? 'action-btn accent-active' : 'action-btn';
            }
        }

        function updateIndicators() {
            setText('ind-time', time.toFixed(3) + ' s');
            if (divHistory.length > 0 && nPendulums > 1) {
                let maxDiff = Math.pow(10, divHistory[divHistory.length - 1]);
                setText('ind-div', maxDiff.toExponential(2) + ' rad');
            } else {
                setText('ind-div', '0.00e+0 rad');
            }
            if (states.length > 0) {
                let energies = calculateEnergy(states[0]);
                setText('ind-energy', energies[2].toFixed(4) + ' J');
            }
        }

        // --- RENDERIZADO EN CANVAS 2D ---
        function drawPhysics() {
            if (!ctxSim || !canSim || states.length === 0) return;
            ctxSim.clearRect(0, 0, canSim.width, canSim.height);
            let cx = canSim.width / 2;
            let cy = canSim.height / 2;
            let maxR = mode === 'Simple' ? L1 * 1.2 : (L1 + L2) * 1.15;
            let scale = Math.min(cx, cy) / maxR;

            const r1 = massToRadius(m1);
            const r2 = massToRadius(m2);

            ctxSim.strokeStyle = '#2a2a32';
            ctxSim.lineWidth = 1;
            ctxSim.beginPath();
            ctxSim.arc(cx, cy, L1 * scale, 0, Math.PI * 2);
            ctxSim.stroke();
            if (mode === 'Doble') {
                ctxSim.beginPath();
                ctxSim.arc(cx, cy, (L1 + L2) * scale, 0, Math.PI * 2);
                ctxSim.stroke();
            }

            ctxSim.fillStyle = '#fff';
            ctxSim.beginPath();
            ctxSim.arc(cx, cy, 4, 0, Math.PI * 2);
            ctxSim.fill();

            for (let i = nPendulums - 1; i >= 0; i--) {
                if (trails[i] && trails[i].length > 1) {
                    ctxSim.beginPath();
                    ctxSim.moveTo(cx + trails[i][0].x * scale, cy + trails[i][0].y * scale);
                    for (let j = 1; j < trails[i].length; j++) {
                        ctxSim.lineTo(cx + trails[i][j].x * scale, cy + trails[i][j].y * scale);
                    }
                    ctxSim.strokeStyle = palette[i % palette.length];
                    ctxSim.lineWidth = 1.5;
                    ctxSim.stroke();
                }
            }

            for (let i = nPendulums - 1; i >= 0; i--) {
                let s = states[i];
                if (!s) continue;
                let x1 = L1 * Math.sin(s[0]);
                let y1 = L1 * Math.cos(s[0]);
                let px1 = cx + x1 * scale, py1 = cy + y1 * scale;

                ctxSim.strokeStyle = palette[i % palette.length];
                ctxSim.lineWidth = 2;
                ctxSim.beginPath();
                ctxSim.moveTo(cx, cy);
                ctxSim.lineTo(px1, py1);
                ctxSim.stroke();

                if (mode === 'Simple') {
                    ctxSim.fillStyle = palette[i % palette.length];
                    ctxSim.beginPath();
                    ctxSim.arc(px1, py1, r1, 0, Math.PI * 2);
                    ctxSim.fill();
                } else {
                    let x2 = x1 + L2 * Math.sin(s[2]);
                    let y2 = y1 + L2 * Math.cos(s[2]);
                    let px2 = cx + x2 * scale, py2 = cy + y2 * scale;
                    ctxSim.beginPath();
                    ctxSim.moveTo(px1, py1);
                    ctxSim.lineTo(px2, py2);
                    ctxSim.stroke();

                    // Esfera Masa 1 (articulación intermedia) con radio variable r1
                    ctxSim.fillStyle = palette[i % palette.length];
                    ctxSim.beginPath();
                    ctxSim.arc(px1, py1, r1, 0, Math.PI * 2);
                    ctxSim.fill();

                    // Esfera Masa 2 (extremo libre) con radio variable r2
                    ctxSim.fillStyle = palette[i % palette.length];
                    ctxSim.beginPath();
                    ctxSim.arc(px2, py2, r2, 0, Math.PI * 2);
                    ctxSim.fill();
                }
            }
        }

        function drawChart(ctx, can, histX, histY, color, minY, maxY) {
            if (!ctx || !can) return;
            ctx.clearRect(0, 0, can.width, can.height);

            let padL = 36, padR = 14, padT = 14, padB = 22;
            let w = can.width - padL - padR;
            let h = can.height - padT - padB;
            if (w <= 0 || h <= 0) return;

            ctx.strokeStyle = '#2a2a32';
            ctx.fillStyle = '#050505';
            ctx.font = '10px monospace';
            ctx.lineWidth = 1;

            for (let k = 0; k <= 4; k++) {
                let py = padT + (k / 4) * h;
                let valY = maxY - (k / 4) * (maxY - minY);
                ctx.beginPath();
                ctx.moveTo(padL, py);
                ctx.lineTo(padL + w, py);
                ctx.stroke();
                ctx.fillText(valY.toFixed(1), 4, py + 3);
            }

            if (histX.length < 2) return;

            let minX = Math.min(...histX);
            let maxX = Math.max(...histX);
            if (maxX - minX < 0.1) maxX = minX + 0.1;

            ctx.strokeStyle = color;
            ctx.lineWidth = 1.8;
            ctx.beginPath();
            for (let i = 0; i < histX.length; i++) {
                let px = padL + ((histX[i] - minX) / (maxX - minX)) * w;
                let clampedY = Math.max(minY, Math.min(maxY, histY[i]));
                let py = padT + h - ((clampedY - minY) / (maxY - minY)) * h;
                if (i === 0) ctx.moveTo(px, py);
                else ctx.lineTo(px, py);
            }
            ctx.stroke();

            ctx.fillText(`t = ${time.toFixed(2)} s`, padL + w - 75, can.height - 5);
        }

        function drawAllInternal() {
            drawPhysics();
            drawChart(ctxDiv, canDiv, timeHistory, divHistory, '#189100', -8.0, 0.8);
            let phX = phaseHistory.map(p => p.x);
            let phY = phaseHistory.map(p => p.y);
            drawChart(ctxPhase, canPhase, phX, phY, '#0000aa', mode === 'Simple' ? -10 : -Math.PI, mode === 'Simple' ? 10 : Math.PI);
        }

        let lastFrameTime = performance.now();
        let frameCount = 0;

        function loop(currentFrameTime) {
            if (isRunning && states.length > 0) {
                let currentSubSteps = Math.max(1, Math.round(20 * simSpeed));
                for (let i = 0; i < currentSubSteps; i++) rk4Step();
                recordSample();
            }

            if (ensureCanvas()) {
                if (isRunning) {
                    updateIndicators();
                    drawAllInternal();
                }
            }

            frameCount++;
            if (currentFrameTime - lastFrameTime >= 1000) {
                setText('ind-fps', isRunning ? `${frameCount}` : '—');
                frameCount = 0;
                lastFrameTime = currentFrameTime;
            }

            animationId = requestAnimationFrame(loop);
        }

        return {
            syncCount: 0,
            mount: ensureCanvas,

            refreshView: function() {
                ensureCanvas();
                updateUIFromState();
                updateIndicators();
                drawAllInternal();
            },

            sync: function(config) {
                this.syncCount++;
                const currentBtnIniciar = el('btn-iniciar');
                const isRemount = (currentBtnIniciar && currentBtnIniciar !== boundBtnIniciar);

                const newM1 = config.m1 !== undefined ? Number(config.m1) : 1.0;
                const newM2 = config.m2 !== undefined ? Number(config.m2) : 1.0;

                if (isRemount) {
                    boundBtnIniciar = currentBtnIniciar;
                    this._lastStart = config.cStart || 0;
                    this._lastReset = config.cReset || 0;
                    this._lastClear = config.cClear || 0;
                    this._lastFix = config.cFix || 0;

                    if (!initialized) {
                        t1_0 = config.t1;
                        t2_0 = config.t2 !== undefined ? config.t2 : defaultT2;
                        nPendulums = config.n;
                        log_dt = config.logdt;
                        L1 = config.l1;
                        L2 = config.l2 !== undefined ? config.l2 : 1.0;
                        g = config.g;
                        b = config.b;
                        m1 = newM1;
                        m2 = newM2;
                        simSpeed = config.speed;
                        initStates();
                        initialized = true;
                    } else {
                        m1 = newM1;
                        m2 = newM2;
                        ensureCanvas();
                        updateUIFromState();
                        updateIndicators();
                        drawAllInternal();
                    }

                    if (!animationId) {
                        animationId = requestAnimationFrame(loop);
                    }
                    return;
                }

                let needReset = false;

                if ((config.cStart || 0) > (this._lastStart || 0)) {
                    isRunning = !isRunning;
                    this._lastStart = config.cStart;
                }
                if ((config.cReset || 0) > (this._lastReset || 0)) {
                    isRunning = false;
                    needReset = true;
                    this._lastReset = config.cReset;
                }
                if ((config.cClear || 0) > (this._lastClear || 0)) {
                    clearTrails();
                    this._lastClear = config.cClear;
                }
                if ((config.cFix || 0) > (this._lastFix || 0)) {
                    fixTrails = !fixTrails;
                    this._lastFix = config.cFix;
                    if (!fixTrails) {
                        for (let i = 0; i < trails.length; i++) {
                            while (trails[i].length > 100) trails[i].shift();
                        }
                    }
                }

                const newT2 = config.t2 !== undefined ? config.t2 : defaultT2;
                const newL2 = config.l2 !== undefined ? config.l2 : 1.0;

                if (t1_0 !== config.t1 || t2_0 !== newT2 || nPendulums !== config.n || log_dt !== config.logdt) {
                    t1_0 = config.t1;
                    t2_0 = newT2;
                    nPendulums = config.n;
                    log_dt = config.logdt;
                    isRunning = false;
                    needReset = true;
                }

                if (L1 !== config.l1 || L2 !== newL2 || g !== config.g || b !== config.b || m1 !== newM1 || m2 !== newM2) {
                    L1 = config.l1;
                    L2 = newL2;
                    g = config.g;
                    b = config.b;
                    m1 = newM1;
                    m2 = newM2;
                    if (!isRunning && time === 0.0) needReset = true;
                }

                simSpeed = config.speed;

                if (needReset || !initialized) {
                    initStates();
                    initialized = true;
                } else {
                    updateUIFromState();
                    updateIndicators();
                    if (ensureCanvas()) drawAllInternal();
                }

                if (!animationId) {
                    animationId = requestAnimationFrame(loop);
                }
            },

            snapshot: function() {
                if (!initialized || states.length === 0) initStates();
                return {
                    captured_at: Date.now(),
                    time: timeHistory.slice(),
                    div: divHistory.slice(),
                    phase_x: phaseHistory.map(p => p.x),
                    phase_y: phaseHistory.map(p => p.y),
                    energy_t: energyT.slice(),
                    energy_v: energyV.slice(),
                    energy_total: energyTot.slice()
                };
            }
        };
    }

    // Instancias independientes para cada página del menú lateral
    window.PendulumSimpleApp = createPendulumEngine('Simple', 'ps-', 120, 0);
    window.PendulumDoubleApp = createPendulumEngine('Doble', 'pd-', 180, -10);
})();