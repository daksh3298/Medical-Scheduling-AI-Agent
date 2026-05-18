def get_html():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Medical Appoint AI Assistant</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f0f4f8;
            display: flex;
            height: 100vh;
            overflow: hidden;
        }

        /* ==================== SIDEBAR ==================== */
        .sidebar {
            width: 68px;
            background: #1e40af;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 16px 0;
            gap: 6px;
            z-index: 10;
        }

        .sidebar-logo {
            width: 42px; height: 42px;
            background: white;
            border-radius: 12px;
            display: flex; align-items: center; justify-content: center;
            font-size: 20px;
            margin-bottom: 12px;
        }

        .sidebar-btn {
            width: 42px; height: 42px;
            border-radius: 10px;
            display: flex; align-items: center; justify-content: center;
            cursor: pointer; font-size: 18px;
            transition: all 0.2s;
            color: rgba(255,255,255,0.6);
            position: relative; border: none; background: none;
        }

        .sidebar-btn:hover { background: rgba(255,255,255,0.15); color: white; }
        .sidebar-btn.active { background: rgba(255,255,255,0.2); color: white; }

        .sidebar-btn .tip {
            position: absolute; left: 54px;
            background: #1f2937; color: white;
            padding: 4px 8px; border-radius: 6px;
            font-size: 11px; white-space: nowrap;
            opacity: 0; pointer-events: none;
            transition: opacity 0.15s; z-index: 100;
        }

        .sidebar-btn:hover .tip { opacity: 1; }
        .sidebar-divider { width: 36px; height: 1px; background: rgba(255,255,255,0.15); margin: 6px 0; }
        .sidebar-bottom { margin-top: auto; }

        /* ==================== LEFT PANEL ==================== */
        .left-panel {
            width: 272px;
            background: white;
            border-right: 1px solid #e5e7eb;
            display: flex; flex-direction: column;
            overflow: hidden;
        }

        .panel-header { padding: 18px 16px 12px; border-bottom: 1px solid #f3f4f6; }
        .panel-header h2 { font-size: 15px; font-weight: 700; color: #111827; }
        .panel-header p { font-size: 12px; color: #9ca3af; margin-top: 2px; }

        .panel-body { flex: 1; overflow-y: auto; padding: 10px; }

        .sec-label {
            font-size: 10px; font-weight: 700; color: #9ca3af;
            text-transform: uppercase; letter-spacing: 0.6px;
            padding: 8px 6px 5px;
        }

        .action-card {
            padding: 10px 12px; border-radius: 8px;
            cursor: pointer; transition: all 0.15s;
            margin-bottom: 3px; border: 1px solid transparent;
        }

        .action-card:hover { background: #f9fafb; border-color: #e5e7eb; }

        .ac-title { font-size: 13px; font-weight: 500; color: #111827; }
        .ac-desc { font-size: 11px; color: #9ca3af; margin-top: 2px; }

        .badge {
            display: inline-block; padding: 2px 7px;
            border-radius: 20px; font-size: 10px; font-weight: 600; margin-top: 5px;
        }

        .b-blue { background: #dbeafe; color: #1d4ed8; }
        .b-green { background: #dcfce7; color: #15803d; }

        .download-item {
            display: flex; align-items: center; gap: 10px;
            padding: 10px 12px; border-radius: 8px;
            cursor: pointer; transition: all 0.15s;
            text-decoration: none; color: inherit;
            margin-bottom: 4px; border: 1px solid #e5e7eb;
            background: #fafafa;
        }

        .download-item:hover { background: #f3f4f6; }
        .dl-icon { font-size: 22px; }
        .dl-info { flex: 1; }
        .dl-name { font-size: 13px; font-weight: 500; color: #111827; }
        .dl-size { font-size: 11px; color: #9ca3af; }
        .dl-btn { font-size: 16px; }

        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #d1d5db; border-radius: 2px; }

        /* ==================== CALL SCREEN ==================== */
        .call-screen {
            flex: 1;
            background: linear-gradient(160deg, #0a1628 0%, #0f2547 50%, #1a1f3a 100%);
            display: flex;
            flex-direction: column;
            overflow: hidden;
            position: relative;
        }

        /* Header bar */
        .call-top-bar {
            display: flex; align-items: center; justify-content: space-between;
            padding: 18px 24px 0;
        }

        .call-hospital-name {
            display: flex; align-items: center; gap: 8px;
            color: rgba(255,255,255,0.85);
            font-size: 13px; font-weight: 500;
        }

        .call-conn-badge {
            display: flex; align-items: center; gap: 5px;
            background: rgba(16,185,129,0.15);
            border: 1px solid rgba(16,185,129,0.3);
            border-radius: 20px; padding: 4px 10px;
            font-size: 11px; color: #34d399;
        }

        .conn-dot {
            width: 6px; height: 6px;
            background: #10b981; border-radius: 50%;
            animation: connblink 2s infinite;
        }

        @keyframes connblink {
            0%,100% { opacity: 1; } 50% { opacity: 0.3; }
        }

        .call-clear-btn {
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.12);
            color: rgba(255,255,255,0.5);
            border-radius: 8px; padding: 5px 12px;
            font-size: 11px; cursor: pointer;
            transition: all 0.2s;
        }

        .call-clear-btn:hover { background: rgba(255,255,255,0.14); color: rgba(255,255,255,0.8); }

        /* Center avatar section */
        .call-center-area {
            flex: 1;
            display: flex; flex-direction: column;
            align-items: center; justify-content: center;
            padding: 20px;
            gap: 14px;
        }

        .avatar-wrapper {
            position: relative;
            width: 130px; height: 130px;
            display: flex; align-items: center; justify-content: center;
        }

        .pulse-ring {
            position: absolute;
            border-radius: 50%;
            display: none;
        }

        .pulse-ring-1 {
            width: 130px; height: 130px;
            border: 2px solid currentColor;
            animation: ringpulse 2s ease-out infinite;
        }

        .pulse-ring-2 {
            width: 130px; height: 130px;
            border: 2px solid currentColor;
            animation: ringpulse 2s ease-out infinite 0.7s;
        }

        @keyframes ringpulse {
            0%   { transform: scale(1); opacity: 0.7; }
            100% { transform: scale(1.8); opacity: 0; }
        }

        .avatar-circle {
            width: 110px; height: 110px;
            border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            font-size: 48px;
            position: relative; z-index: 1;
            transition: all 0.4s ease;
            background: linear-gradient(135deg, #1e40af, #1d4ed8);
            box-shadow: 0 8px 32px rgba(37,99,235,0.4);
        }

        /* State-based colors */
        .state-idle .pulse-ring { display: none; }
        .state-idle .avatar-circle { background: linear-gradient(135deg, #374151, #4b5563); box-shadow: 0 8px 24px rgba(0,0,0,0.4); }

        .state-listening .pulse-ring { display: block; color: #22c55e; }
        .state-listening .avatar-circle { background: linear-gradient(135deg, #065f46, #059669); box-shadow: 0 8px 32px rgba(16,185,129,0.5); }

        .state-processing .pulse-ring { display: none; }
        .state-processing .avatar-circle {
            background: linear-gradient(135deg, #92400e, #d97706);
            box-shadow: 0 8px 32px rgba(217,119,6,0.5);
            animation: spin-slow 2s linear infinite;
        }

        @keyframes spin-slow {
            0%,100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }

        .state-speaking .pulse-ring { display: block; color: #60a5fa; }
        .state-speaking .avatar-circle { background: linear-gradient(135deg, #1e3a8a, #2563eb); box-shadow: 0 8px 32px rgba(96,165,250,0.6); }

        .call-agent-name {
            color: white; font-size: 20px; font-weight: 600;
            letter-spacing: -0.3px;
        }

        .call-agent-sub {
            color: rgba(255,255,255,0.45); font-size: 12px;
        }

        .call-timer {
            color: rgba(255,255,255,0.6);
            font-size: 14px; font-weight: 500;
            font-variant-numeric: tabular-nums;
            letter-spacing: 1px;
            display: none;
        }

        .call-status-pill {
            padding: 8px 20px;
            border-radius: 30px;
            font-size: 13px; font-weight: 500;
            transition: all 0.3s;
            min-width: 160px; text-align: center;
        }

        .status-idle    { background: rgba(255,255,255,0.07); color: rgba(255,255,255,0.4); }
        .status-listening { background: rgba(34,197,94,0.15); color: #4ade80; border: 1px solid rgba(34,197,94,0.3); }
        .status-processing { background: rgba(251,191,36,0.15); color: #fbbf24; border: 1px solid rgba(251,191,36,0.3); }
        .status-speaking  { background: rgba(96,165,250,0.15); color: #93c5fd; border: 1px solid rgba(96,165,250,0.3); }

        /* Transcript */
        .call-transcript {
            margin: 0 20px;
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 16px;
            padding: 12px 16px;
            max-height: 180px;
            overflow-y: auto;
            display: flex; flex-direction: column; gap: 8px;
        }

        .transcript-empty {
            color: rgba(255,255,255,0.2);
            font-size: 12px; text-align: center;
            padding: 10px 0;
        }

        .transcript-msg {
            font-size: 12.5px; line-height: 1.5;
            padding: 6px 10px; border-radius: 8px;
        }

        .transcript-user {
            background: rgba(37,99,235,0.2);
            color: rgba(255,255,255,0.85);
            align-self: flex-end; text-align: right;
        }

        .transcript-ai {
            background: rgba(255,255,255,0.06);
            color: rgba(255,255,255,0.7);
            align-self: flex-start;
        }

        .transcript-label {
            font-size: 10px; font-weight: 700;
            text-transform: uppercase; letter-spacing: 0.5px;
            opacity: 0.6; display: block; margin-bottom: 2px;
        }

        /* Controls */
        .call-controls {
            display: flex; align-items: center; justify-content: center;
            gap: 24px;
            padding: 20px 24px 28px;
        }

        .ctrl-circle-btn {
            width: 56px; height: 56px;
            border-radius: 50%;
            border: none; cursor: pointer;
            display: flex; align-items: center; justify-content: center;
            font-size: 20px;
            transition: all 0.2s;
        }

        .mute-btn {
            background: rgba(255,255,255,0.1);
            color: white;
        }

        .mute-btn:hover { background: rgba(255,255,255,0.18); transform: scale(1.05); }
        .mute-btn.muted { background: rgba(239,68,68,0.2); color: #f87171; }

        .call-start-btn {
            width: 72px; height: 72px; font-size: 26px;
            background: linear-gradient(135deg, #16a34a, #15803d);
            box-shadow: 0 6px 24px rgba(22,163,74,0.5);
            color: white;
        }

        .call-start-btn:hover { transform: scale(1.07); box-shadow: 0 8px 32px rgba(22,163,74,0.7); }

        .call-end-btn {
            width: 72px; height: 72px; font-size: 26px;
            background: linear-gradient(135deg, #dc2626, #b91c1c);
            box-shadow: 0 6px 24px rgba(220,38,38,0.5);
            color: white;
        }

        .call-end-btn:hover { transform: scale(1.07); box-shadow: 0 8px 32px rgba(220,38,38,0.7); }

        .ctrl-label {
            font-size: 10px; color: rgba(255,255,255,0.35);
            text-align: center; margin-top: 6px;
        }

        .ctrl-wrap { display: flex; flex-direction: column; align-items: center; }
    </style>
</head>
<body>


    <!-- CALL SCREEN -->
    <div class="call-screen">

        <!-- Top bar -->
        <div class="call-top-bar">
            <div class="call-hospital-name">
                Online City Hospital
            </div>
            <div style="display:flex; gap:10px; align-items:center;">
                <div class="call-conn-badge">
                    <div class="conn-dot"></div>
                    AI Ready
                </div>
                <button class="call-clear-btn" onclick="clearHistory()">Clear</button>
            </div>
        </div>

        <!-- Center avatar -->
        <div class="call-center-area">

            <div class="avatar-wrapper" id="avatarWrapper">
                <div class="pulse-ring pulse-ring-1"></div>
                <div class="pulse-ring pulse-ring-2"></div>
                <div class="avatar-circle" id="avatarCircle" style="font-size:22px;font-weight:700;letter-spacing:-1px;">AI</div>
            </div>

            <div class="call-agent-name">Medical Appoint AI Assistant</div>
            <div class="call-agent-sub">Online City Hospital</div>
            <div class="call-timer" id="callTimer">00:00</div>

            <div class="call-status-pill status-idle" id="callStatusPill">
                Press Start Call to begin
            </div>

        </div>

        <!-- Transcript -->
        <div class="call-transcript" id="callTranscript">
            <div class="transcript-empty" id="transcriptEmpty">Your conversation will appear here...</div>
        </div>

        <!-- Controls -->
        <div class="call-controls">
            <div class="ctrl-wrap">
                <button class="ctrl-circle-btn mute-btn" id="muteBtn" onclick="toggleMute()" style="font-size:13px;font-weight:700;">Mic</button>
                <div class="ctrl-label" id="muteLabel">Mute</div>
            </div>

            <div class="ctrl-wrap">
                <button class="ctrl-circle-btn call-start-btn" id="callBtn" onclick="toggleCall()" style="font-size:14px;font-weight:700;">Call</button>
                <div class="ctrl-label" id="callLabel">Start Call</div>
            </div>

            <div class="ctrl-wrap">
                <button class="ctrl-circle-btn mute-btn" onclick="clearHistory()" title="Clear history" style="font-size:18px;font-weight:400;">×</button>
                <div class="ctrl-label">Clear</div>
            </div>
        </div>

    </div>

    <script>
        // ==================== SESSION ====================
        let sessionId = 'sess_' + Math.random().toString(36).substr(2, 9);

        // ==================== CALL STATE ====================
        let callActive    = false;
        let callMuted     = false;
        let callAudio     = null;   // { source, stop }
        let timerInterval = null;
        let timerSeconds  = 0;
        let sharedAudioCtx = null;  // persistent AudioContext unlocked on button click
        let lastAIResponse = '';    // saved so barge-in noise can resume speaking

        let bargeInCtx    = null;
        let bargeInStream = null;
        let bargeInFrame  = null;

        // Listening state (Deepgram WebSocket streaming)
        let dgSocket       = null;
        let dgStream       = null;
        let dgRecorder     = null;
        let isListening    = false;
        let dgTranscript   = '';
        let dgSilenceTimer = null;
        let noSpeechTimer  = null;

        const BARGE_THRESHOLD = 55;
        const NOISE_PATTERN   = /^[\s.,!?;:\-_*'"()\[\]]+$|^(um+|uh+|hmm+|ah+|oh+|er+|mm+|hm+|yeah|yep|nope|okay|ok|sure|right|like)[\s.,!?]*$/i;

        // ==================== CALL TOGGLE ====================
        function toggleCall() {
            callActive ? endCall() : startCall();
        }

        function startCall() {
            // Create AudioContext HERE (inside user gesture) — this unlocks audio for the session
            if (!sharedAudioCtx || sharedAudioCtx.state === 'closed') {
                sharedAudioCtx = new AudioContext();
            }
            callActive = true;
            timerSeconds = 0;
            document.getElementById('callTimer').style.display = 'block';
            timerInterval = setInterval(() => {
                timerSeconds++;
                const m = String(Math.floor(timerSeconds / 60)).padStart(2,'0');
                const s = String(timerSeconds % 60).padStart(2,'0');
                document.getElementById('callTimer').textContent = m + ':' + s;
            }, 1000);

            setCallBtn(true);
            setCallState('listening');
            startListening();
        }

        function endCall() {
            callActive = false;
            clearInterval(timerInterval);
            document.getElementById('callTimer').style.display = 'none';
            stopCallAudio();
            stopBargeIn();
            stopListening();
            window.speechSynthesis.cancel();
            setCallBtn(false);
            setCallState('idle');
        }

        function setCallBtn(active) {
            const btn   = document.getElementById('callBtn');
            const label = document.getElementById('callLabel');
            if (active) {
                btn.className   = 'ctrl-circle-btn call-end-btn';
                btn.textContent = 'End';
                label.textContent = 'End Call';
            } else {
                btn.className   = 'ctrl-circle-btn call-start-btn';
                btn.textContent = 'Call';
                label.textContent = 'Start Call';
            }
        }

        // ==================== CALL STATE UI ====================
        function setCallState(state) {
            const wrapper = document.getElementById('avatarWrapper');
            const pill    = document.getElementById('callStatusPill');

            wrapper.className = 'avatar-wrapper state-' + state;

            const cfg = {
                idle:       { text: 'Press Start Call to begin', pillClass: 'status-idle' },
                listening:  { text: 'Listening...',   pillClass: 'status-listening' },
                processing: { text: 'Processing...', pillClass: 'status-processing' },
                speaking:   { text: 'Speaking...',   pillClass: 'status-speaking' }
            };

            const c = cfg[state] || cfg.idle;
            pill.textContent = c.text;
            pill.className   = 'call-status-pill ' + c.pillClass;
        }

        // ==================== MUTE ====================
        function toggleMute() {
            callMuted = !callMuted;
            const btn   = document.getElementById('muteBtn');
            const label = document.getElementById('muteLabel');
            btn.textContent   = callMuted ? 'Muted' : 'Mic';
            btn.className     = 'ctrl-circle-btn mute-btn' + (callMuted ? ' muted' : '');
            label.textContent = callMuted ? 'Unmute' : 'Mute';
        }

        // ==================== AUDIO (AudioContext-based, no autoplay block) ====================
        function stopCallAudio() {
            if (callAudio) {
                try { callAudio.source.stop(); } catch(e) {}
                callAudio = null;
            }
        }

        async function playTTS(blob) {
            return new Promise(async (resolve, reject) => {
                try {
                    if (!sharedAudioCtx || sharedAudioCtx.state === 'closed') {
                        sharedAudioCtx = new AudioContext();
                    }
                    if (sharedAudioCtx.state === 'suspended') {
                        await sharedAudioCtx.resume();
                    }
                    const arrayBuffer = await blob.arrayBuffer();
                    const audioBuffer = await sharedAudioCtx.decodeAudioData(arrayBuffer);
                    const source = sharedAudioCtx.createBufferSource();
                    source.buffer = audioBuffer;
                    source.connect(sharedAudioCtx.destination);
                    source.onended = resolve;
                    callAudio = { source };
                    source.start(0);
                } catch(e) {
                    console.error('TTS playback error:', e);
                    reject(e);
                }
            });
        }

        // ==================== SPEAK (Groq TTS → browser fallback) ====================
        async function speakResponse(text) {
            // Try Groq TTS first
            try {
                const ttsRes = await fetch('/api/tts', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text, voice: 'aura-asteria-en' })
                });
                if (ttsRes.ok) {
                    const blob = await ttsRes.blob();
                    await startBargeIn();
                    try { await playTTS(blob); } catch(e) { console.warn('AudioContext play failed, trying browser TTS:', e); await browserSpeak(text); }
                    stopBargeIn();
                    callAudio = null;
                    return;
                }
                console.warn('Groq TTS returned', ttsRes.status, '— using browser TTS');
            } catch(e) {
                console.warn('Groq TTS fetch failed:', e, '— using browser TTS');
            }
            // Fallback: browser SpeechSynthesis
            await browserSpeak(text);
        }

        function browserSpeak(text) {
            return new Promise((resolve) => {
                window.speechSynthesis.cancel();
                const u = new SpeechSynthesisUtterance(text);
                u.rate = 0.80; u.pitch = 1.0; u.volume = 1.0;
                u.onend   = resolve;
                u.onerror = resolve;
                // Safety: resolve after estimated read time + 2s buffer so it never hangs
                setTimeout(resolve, Math.max(3000, text.length * 65));
                window.speechSynthesis.speak(u);
                // Barge-in: cancel browser speech if user speaks
                startBargeInBrowser(u);
            });
        }

        function startBargeInBrowser(utterance) {
            navigator.mediaDevices.getUserMedia({ audio: true }).then(stream => {
                const ctx = new AudioContext();
                const analyser = ctx.createAnalyser();
                analyser.fftSize = 256;
                ctx.createMediaStreamSource(stream).connect(analyser);
                const data = new Uint8Array(analyser.frequencyBinCount);
                function check() {
                    if (!window.speechSynthesis.speaking) { ctx.close(); stream.getTracks().forEach(t=>t.stop()); return; }
                    analyser.getByteFrequencyData(data);
                    const vol = data.reduce((a,b)=>a+b,0)/data.length;
                    if (vol > BARGE_THRESHOLD) {
                        window.speechSynthesis.cancel();
                        ctx.close(); stream.getTracks().forEach(t=>t.stop());
                        return;
                    }
                    requestAnimationFrame(check);
                }
                requestAnimationFrame(check);
            }).catch(()=>{});
        }

        // Resume speaking last response without barge-in (used after barge-in interruption only)
        async function resumeLastResponse() {
            if (!lastAIResponse || !callActive) { if (callActive) startListening(); return; }
            const textToSpeak = lastAIResponse;
            lastAIResponse = ''; // clear so it can only replay once — prevents infinite loop
            setCallState('speaking');
            try {
                const ttsRes = await fetch('/api/tts', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text: textToSpeak, voice: 'aura-asteria-en' })
                });
                if (ttsRes.ok) {
                    const blob = await ttsRes.blob();
                    await playTTS(blob);
                }
            } catch(e) { console.warn('Resume TTS error:', e); }
            finally {
                callAudio = null;
                if (callActive) startListening();
            }
        }

        // ==================== BARGE-IN ====================
        async function startBargeIn() {
            if (callMuted) return;
            try {
                bargeInStream = await navigator.mediaDevices.getUserMedia({
                    audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true }
                });
                bargeInCtx    = new AudioContext();
                const analyser = bargeInCtx.createAnalyser();
                analyser.fftSize = 256;
                bargeInCtx.createMediaStreamSource(bargeInStream).connect(analyser);
                const data      = new Uint8Array(analyser.frequencyBinCount);
                let triggered       = false;
                let sustainedFrames = 0;
                const SUSTAIN_NEEDED = 10; // ~167ms at 60fps — requires deliberate speech
                const startedAt = Date.now();

                function check() {
                    if (!callActive || triggered) return;
                    // Grace period: ignore first 1500ms so residual mic noise after user speech doesn't re-trigger
                    if (Date.now() - startedAt < 1500) { bargeInFrame = requestAnimationFrame(check); return; }
                    analyser.getByteFrequencyData(data);
                    const vol = data.reduce((a,b) => a+b, 0) / data.length;
                    if (vol > BARGE_THRESHOLD) {
                        sustainedFrames++;
                        if (sustainedFrames >= SUSTAIN_NEEDED) {
                            triggered = true;
                            stopCallAudio();
                            window.speechSynthesis.cancel();
                            stopBargeIn();
                            setCallState('listening');
                            startListening();
                            return;
                        }
                    } else {
                        sustainedFrames = 0;
                    }
                    bargeInFrame = requestAnimationFrame(check);
                }
                bargeInFrame = requestAnimationFrame(check);
            } catch(e) { console.log('Barge-in error:', e); }
        }

        function stopBargeIn() {
            cancelAnimationFrame(bargeInFrame);
            if (bargeInCtx)    { bargeInCtx.close(); bargeInCtx = null; }
            if (bargeInStream) { bargeInStream.getTracks().forEach(t => t.stop()); bargeInStream = null; }
        }

        // ==================== LISTEN (Deepgram WebSocket streaming) ====================
        function stopListening() {
            isListening = false;
            clearTimeout(dgSilenceTimer); dgSilenceTimer = null;
            clearTimeout(noSpeechTimer);  noSpeechTimer  = null;
            if (dgRecorder && dgRecorder.state !== 'inactive') { try { dgRecorder.stop(); } catch(e){} }
            if (dgSocket)  { try { dgSocket.close(); } catch(e){} dgSocket = null; }
            if (dgStream)  { dgStream.getTracks().forEach(t => t.stop()); dgStream = null; }
            dgRecorder = null; dgTranscript = '';
        }

        async function startListening() {
            if (!callActive || callMuted || isListening) return;
            isListening  = true;
            dgTranscript = '';
            setCallState('listening');

            try {
                dgStream = await navigator.mediaDevices.getUserMedia({
                    audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true }
                });
            } catch { endCall(); return; }

            let dgKey;
            try {
                const kr = await fetch('/api/deepgram-key');
                dgKey = (await kr.json()).key;
            } catch(e) { console.error('No Deepgram key:', e); endCall(); return; }

            const params = new URLSearchParams({
                model: 'nova-2',
                language: 'en-US',
                punctuate: 'true',
                smart_format: 'true',
                vad_events: 'true',
                endpointing: '1000',
                utterance_end_ms: '2000',
                interim_results: 'true',
                filler_words: 'false'
            });
            // Keyword boosting for commonly misheard words
            ['dgupta0444', 'sdsu', 'edu', 'gmail', 'outlook', 'yahoo'].forEach(kw => {
                params.append('keywords', kw + ':2');
            });
            dgSocket = new WebSocket('wss://api.deepgram.com/v1/listen?' + params, ['token', dgKey]);
            dgSocket.binaryType = 'arraybuffer';

            dgSocket.onopen = () => {
                dgRecorder = new MediaRecorder(dgStream);
                dgRecorder.ondataavailable = e => {
                    if (dgSocket && dgSocket.readyState === WebSocket.OPEN && e.data.size > 0) {
                        dgSocket.send(e.data);
                    }
                };
                dgRecorder.start(100);

                // No-speech timeout: start AFTER Deepgram is connected so the user's
                // first words aren't missed during WebSocket setup (which can take 1-2s)
                noSpeechTimer = setTimeout(() => {
                    if (!isListening) return;
                    stopListening();
                    if (callActive) {
                        processTranscript('I did not catch that, are you still there');
                    }
                }, 8000);
            };

            dgSocket.onmessage = e => {
                let msg;
                try { msg = JSON.parse(e.data); } catch { return; }

                if (msg.type === 'SpeechStarted') {
                    clearTimeout(noSpeechTimer); noSpeechTimer = null;
                    clearTimeout(dgSilenceTimer); dgSilenceTimer = null;
                }

                if (msg.type === 'Results') {
                    const alt = msg.channel?.alternatives?.[0];
                    if (!alt) return;
                    const text = (alt.transcript || '').trim();
                    if (!text) return;
                    // Reject low-confidence transcripts (ambient noise / echo)
                    if ((alt.confidence || 0) < 0.6) return;

                    if (msg.is_final) {
                        dgTranscript += (dgTranscript ? ' ' : '') + text;
                        // Arm fallback: submit if no speech_final/UtteranceEnd arrives within 4s
                        clearTimeout(dgSilenceTimer);
                        dgSilenceTimer = setTimeout(() => {
                            if (dgTranscript && isListening) _submitTranscript();
                        }, 4000);
                    }

                    if (msg.speech_final && dgTranscript) {
                        _submitTranscript();
                    }
                }

                if (msg.type === 'UtteranceEnd' && dgTranscript) {
                    _submitTranscript();
                }
            };

            dgSocket.onerror = e => console.error('Deepgram WS error:', e);
            dgSocket.onclose = () => {};
        }

        function _submitTranscript() {
            if (!isListening) return;
            const text = dgTranscript.trim();
            stopListening();
            if (!text || text.length < 2 || NOISE_PATTERN.test(text)) {
                if (callActive) {
                    if (lastAIResponse) {
                        clearTimeout(noSpeechTimer); noSpeechTimer = null;
                        resumeLastResponse();
                    } else {
                        startListening();
                    }
                }
                return;
            }
            lastAIResponse = '';
            processTranscript(text);
        }

        function normalizeTranscript(text) {
            // Convert spoken email format: "john dot smith at gmail dot com" → "john.smith@gmail.com"
            // Pattern: word(s) + "at" + word + "dot" + word  →  reconstruct email
            return text.replace(
                /\b([\w][\w\s]*?)\s+at\s+([\w][\w]*?)\s+dot\s+([\w]{2,6})\b/gi,
                (_, user, domain, tld) => `${user.trim().replace(/\s+dot\s+/gi, '.').replace(/\s+/g, '')}@${domain.trim()}.${tld.trim()}`
            );
        }

        async function processTranscript(transcript) {
            if (!callActive) return;
            transcript = normalizeTranscript(transcript);
            addTranscript(transcript, true);
            setCallState('processing');

            try {
                const chatRes  = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: transcript, session_id: sessionId, patient_id: 'patient_1' })
                });
                const chatData = await chatRes.json();
                const response = chatData.response || '';

                addTranscript(response, false);
                if (!callActive) return;

                lastAIResponse = response;
                setCallState('speaking');
                try {
                    // Timeout: scales with text length so long sentences aren't cut off
                    const ttsTimeout = Math.max(15000, response.length * 110);
                    await Promise.race([
                        speakResponse(response),
                        new Promise(resolve => setTimeout(resolve, ttsTimeout))
                    ]);
                } catch(e) {
                    console.error('TTS error:', e);
                } finally {
                    stopCallAudio();
                    stopBargeIn();
                    if (callActive) startListening();
                }

            } catch(e) {
                console.error('Call loop error:', e);
                if (callActive) startListening();
            }
        }

        // ==================== TRANSCRIPT ====================
        function addTranscript(text, isUser) {
            const container = document.getElementById('callTranscript');
            const empty     = document.getElementById('transcriptEmpty');
            if (empty) empty.remove();

            const msg = document.createElement('div');
            msg.className = 'transcript-msg ' + (isUser ? 'transcript-user' : 'transcript-ai');
            msg.innerHTML = '<span class="transcript-label">' + (isUser ? 'You' : 'AI') + '</span>' + escapeHtml(text);
            container.appendChild(msg);
            container.scrollTop = container.scrollHeight;

            // Keep last 12 messages
            const msgs = container.querySelectorAll('.transcript-msg');
            if (msgs.length > 12) msgs[0].remove();
        }

        function escapeHtml(s) {
            return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
        }

        // ==================== CLEAR ====================
        async function clearHistory() {
            try { await fetch('/api/chat/clear?session_id=' + sessionId, { method: 'POST' }); } catch(e) {}
            sessionId = 'sess_' + Math.random().toString(36).substr(2, 9);
            const container = document.getElementById('callTranscript');
            container.innerHTML = '<div class="transcript-empty" id="transcriptEmpty">Your conversation will appear here...</div>';
            if (callActive) endCall();
        }

        // ==================== PANELS ====================
        function showPanel(name, btn) {
            ['call','appointments'].forEach(p => {
                const el = document.getElementById('panel-' + p);
                if (el) el.style.display = 'none';
            });
            const panel = document.getElementById('panel-' + name);
            if (panel) panel.style.display = 'block';
            document.querySelectorAll('.sidebar-btn').forEach(b => b.classList.remove('active'));
            if (btn) btn.classList.add('active');

            if (name === 'appointments') loadDoctors();
        }

        // ==================== DATA LOADERS ====================
        async function loadDoctors() {
            try {
                const res  = await fetch('/api/doctors');
                const data = await res.json();
                document.getElementById('doctors-list').innerHTML = data.doctors.map(d => `
                    <div class="action-card">
                        <div class="ac-title">${d.name}</div>
                        <div class="ac-desc">${d.specialty}</div>
                        <span class="badge b-green">Available</span>
                    </div>
                `).join('');
            } catch(e) {
                document.getElementById('doctors-list').innerHTML =
                    '<div style="color:#ef4444;font-size:13px;padding:10px">Error loading doctors</div>';
            }
        }


    </script>
</body>
</html>
"""
