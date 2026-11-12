// BeatBound GEAR characters, drawn like the game's character review sheet (Design/character_proposals.html).
(() => {
  const BPM = 128, SPB = 60 / BPM;
  const HOP = 0.11;

  // ---------- 그리기 도구 (128 기준 좌표, 가운데 원점) ----------
  const hex = (h) => [parseInt(h.slice(1, 3), 16), parseInt(h.slice(3, 5), 16), parseInt(h.slice(5, 7), 16)];
  const rgba = (h, a, mix = 0) => { const [r, g, b] = hex(h); const m = (v) => Math.round(v + (255 - v) * mix); return `rgba(${m(r)},${m(g)},${m(b)},${a})`; };
  const VOID = "#0b0e1a";
  function rr(c, x, y, w, h, r) { c.beginPath(); c.roundRect(x, y, w, h, r); }
  function frame(c, col, thick = 13) {
    rr(c, -62, -62, 124, 124, 26); c.fillStyle = rgba(col, 0.14); c.fill();
    c.lineWidth = thick; c.strokeStyle = col;
    rr(c, -62 + thick / 2, -62 + thick / 2, 124 - thick, 124 - thick, 26 - thick / 2); c.stroke();
  }
  function solid(c, col, a = 1) { rr(c, -62, -62, 124, 124, 26); c.fillStyle = rgba(col, a); c.fill(); }
  function capsule(c, cx, bottom, w, h) { rr(c, cx - w / 2, bottom - h, w, h, w / 2); c.fill(); }
  function circle(c, x, y, r) { c.beginPath(); c.arc(x, y, r, 0, Math.PI * 2); }
  const ease = { outQuad: (t) => 1 - (1 - t) * (1 - t), outCubic: (t) => 1 - Math.pow(1 - t, 3), outBack: (t) => { const s = 1.70158; return 1 + (s + 1) * Math.pow(t - 1, 3) + s * Math.pow(t - 1, 2); } };
  const lerp = (a, b, t) => a + (b - a) * t;
  const clamp01 = (v) => Math.max(0, Math.min(1, v));

  // ---------- 캐릭터 정의 ----------
  // draw(c, col, m): m = { t, low, mid, high, kick[3], beat, bar, downbeat, beatT(박 후 경과초), local(캐릭터 상태) }
  const CHARS = [
    { id: "BEEP", unlock: ["free", "FREE"], roll: "구름",
      how: "네모 눈 두 개. 첫 박에 눈이 커지고 두 마디마다 깜빡인다.", ghost: "frame",
      draw(c, col, m) {
        frame(c, col);
        const blink = (m.beat % 8 === 7) && m.beatT < 0.12;
        const pop = m.downbeat ? Math.max(0, 1 - m.beatT * 5) : 0;
        c.fillStyle = rgba(col, 1, 0.75);
        const w = 20 + pop * 6, h = blink ? 5 : 26 + pop * 8;
        rr(c, -26 - w / 2, -10 - h / 2, w, h, 4); c.fill();
        rr(c, 26 - w / 2, -10 - h / 2, w, h, 4); c.fill();
        rr(c, -14, 22, 28, 7, 3.5); c.fill();
      } },
    { id: "PAD", unlock: ["free", "FREE"], roll: "대칭",
      how: "작은 패드 2×2. 박마다 한 칸씩 시계 방향으로 켜지고 첫 박엔 네 칸 다.", ghost: "frame",
      draw(c, col, m) {
        frame(c, col);
        const order = [[-1, -1], [1, -1], [1, 1], [-1, 1]];
        const lit = m.beat % 4;
        const fade = Math.max(0, 1 - m.beatT / SPB);
        order.forEach(([x, y], i) => {
          const on = m.downbeat ? fade : (i === lit ? 0.35 + 0.65 * fade : 0);
          c.fillStyle = rgba(col, 0.22 + 0.78 * on, 0.55 * on);
          rr(c, x * 19 - 16, y * 19 - 16, 32, 32, 7); c.fill();
        });
      } },
    { id: "STAR", unlock: ["normal", "Hoshi · NORMAL"], roll: "속돎",
      how: "가운데 별이 박마다 45° 돌며 반짝, 네 귀퉁이 점은 하이햇에 깜빡.", ghost: "frame",
      draw(c, col, m) {
        frame(c, col);
        const turn = (m.beat + ease.outBack(clamp01(m.beatT / 0.16))) * Math.PI / 4;
        const s = 1 + Math.max(0, 0.35 - m.beatT * 1.6) + m.low * 0.1;
        c.save(); c.rotate(turn); c.scale(s, s);
        c.fillStyle = rgba(col, 1, 0.8);
        c.beginPath();
        for (let i = 0; i < 8; i++) { const a = i * Math.PI / 4, r = i % 2 ? 9 : 30; c.lineTo(Math.cos(a) * r, Math.sin(a) * r); }
        c.closePath(); c.fill(); c.restore();
        [[-1, -1], [1, -1], [1, 1], [-1, 1]].forEach(([x, y], i) => {
          c.fillStyle = rgba(col, 0.25 + 0.75 * clamp01(m.high * (i % 2 ? 1.2 : 0.9)), 0.6);
          circle(c, x * 34, y * 34, 5); c.fill();
        });
      } },
    { id: "TAPE", unlock: ["normal", "Ame · NORMAL"], roll: "구름",
      how: "카세트. 릴 두 개가 중음에 맞춰 빨라졌다 느려졌다 한다.", ghost: "solid",
      draw(c, col, m) {
        solid(c, col, 0.92);
        c.fillStyle = VOID; rr(c, -44, -36, 88, 46, 10); c.fill();
        c.fillStyle = rgba(col, 0.35); rr(c, -24, -26, 48, 26, 4); c.fill();
        m.local.spin = (m.local.spin || 0) + m.dt * (3 + m.mid * 9);
        [-24, 24].forEach((x) => {
          c.fillStyle = rgba(col, 1, 0.75); circle(c, x, -13, 15); c.fill();
          c.save(); c.translate(x, -13); c.rotate(m.local.spin);
          c.fillStyle = VOID;
          for (let i = 0; i < 3; i++) { c.rotate(Math.PI * 2 / 3); rr(c, -3, -13, 6, 8, 2); c.fill(); }
          circle(c, 0, 0, 4.5); c.fill(); c.restore();
        });
        c.fillStyle = VOID; c.beginPath(); c.moveTo(-34, 50); c.lineTo(-24, 30); c.lineTo(24, 30); c.lineTo(34, 50); c.closePath(); c.fill();
        c.fillStyle = rgba(col, 0.9); circle(c, -14, 42, 4); c.fill(); circle(c, 14, 42, 4); c.fill();
      } },
    { id: "SCOPE", unlock: ["normal", "Wub :O · NORMAL"], roll: "구름",
      how: "오실로스코프 파형. 킥에 진폭이 커지고 워블처럼 주기가 출렁인다.", ghost: "frame",
      draw(c, col, m) {
        frame(c, col);
        c.strokeStyle = rgba(col, 0.25); c.lineWidth = 2;
        c.beginPath(); c.moveTo(-44, 0); c.lineTo(44, 0); c.moveTo(0, -40); c.lineTo(0, 40); c.stroke();
        const amp = 6 + m.low * 26 + m.kick[0] * 14;
        const k = 0.09 + 0.05 * Math.sin(m.t * Math.PI * 2 / (SPB * 2));
        c.strokeStyle = rgba(col, 1, 0.75); c.lineWidth = 8; c.lineCap = "round"; c.lineJoin = "round";
        c.beginPath();
        for (let x = -40; x <= 40; x += 2) c.lineTo(x, Math.sin(x * k * 1.6 + m.t * 9) * amp * (1 - Math.pow(x / 44, 4)));
        c.stroke();
      } },
    { id: "DICE", unlock: ["hard", "Fogo · HARD"], roll: "구름",
      how: "주사위. 몇 번째 박인지 눈 개수(1~4)로 보여 준다. 굴러가면 진짜 주사위처럼.", ghost: "solid",
      draw(c, col, m) {
        solid(c, col, 1);
        const n = (((m.beat % 4) + 4) % 4) + 1;
        const P = { 1: [[0, 0]], 2: [[-1, -1], [1, 1]], 3: [[-1, -1], [0, 0], [1, 1]], 4: [[-1, -1], [1, -1], [-1, 1], [1, 1]] }[n];
        const pop = 1 + Math.max(0, 0.45 - m.beatT * 3);
        c.fillStyle = VOID;
        P.forEach(([x, y]) => { circle(c, x * 30, y * 30, 11 * pop); c.fill(); });
      } },
    { id: "BYTE", unlock: ["hard", "Shadow · HARD"], roll: "구름",
      how: "8비트 블록 로봇. 박마다 만세↔팔 내리기를 번갈아 하고, 첫 박엔 눈이 켜진다.", ghost: "solid",
      draw(c, col, m) {
        const A = [
          "...##...",
          ".######.",
          ".#.##.#.",
          ".######.",
          "########",
          "#.####.#",
          "..#..#..",
          "..#..#.."];
        const B = [
          "#..##..#",
          "########",
          ".#.##.#.",
          ".######.",
          ".######.",
          ".######.",
          ".#....#.",
          "##....##"];
        const g = m.beat % 2 ? B : A;
        const px = 15, o = -60;
        c.fillStyle = col;
        g.forEach((row, y) => [...row].forEach((ch, x) => { if (ch === "#") { c.fillRect(o + x * px, o + y * px, px + 0.5, px + 0.5); } }));
        if (m.downbeat && m.beatT < 0.15) { c.fillStyle = rgba(col, 1, 0.85); c.fillRect(o + 2 * px, o + 2 * px, px, px); c.fillRect(o + 5 * px, o + 2 * px, px, px); }
      } },
    { id: "NEST", unlock: ["hard", "Yantra · HARD"], roll: "속돎",
      how: "겹친 사각형. 안쪽 네모는 박마다, 마름모는 마디마다 반대로 45° 돈다.", ghost: "frame",
      draw(c, col, m) {
        frame(c, col, 9);
        const inner = (m.beat + ease.outBack(clamp01(m.beatT / 0.18))) * Math.PI / 4;
        const mid = -(m.bar + ease.outCubic(clamp01((m.beat % 4 === 0 ? m.beatT : 1) / 0.3))) * Math.PI / 4 + Math.PI / 4;
        c.save(); c.rotate(mid); c.strokeStyle = rgba(col, 0.9, 0.3); c.lineWidth = 7; rr(c, -33, -33, 66, 66, 6); c.stroke(); c.restore();
        c.save(); c.rotate(inner); c.strokeStyle = rgba(col, 1, 0.7); c.lineWidth = 7; rr(c, -19, -19, 38, 38, 4); c.stroke(); c.restore();
        c.fillStyle = rgba(col, 1, 0.9); circle(c, 0, 0, 5 + m.low * 6); c.fill();
      } },
    { id: "KNOB", unlock: ["hard", "Overdrive · HARD"], roll: "속돎",
      how: "신스 노브. 음량만큼 바늘이 돌고 눈금이 켜진다. 끝까지 가면 마지막 눈금이 하얗게.", ghost: "frame",
      draw(c, col, m) {
        frame(c, col);
        const lv = clamp01(m.low * 0.6 + m.mid * 0.4 + m.kick[1] * 0.4);
        m.local.lv = lerp(m.local.lv ?? lv, lv, lv > (m.local.lv ?? 0) ? 0.5 : 0.08);
        const a0 = Math.PI * 0.75, span = Math.PI * 1.5;
        for (let i = 0; i < 7; i++) {
          const a = a0 + span * i / 6, on = m.local.lv >= i / 6 - 0.02;
          c.fillStyle = i === 6 && on ? "#ffffff" : rgba(col, on ? 1 : 0.25, on ? 0.4 : 0);
          circle(c, Math.cos(a) * 41, Math.sin(a) * 41, 4.5); c.fill();
        }
        c.fillStyle = rgba(col, 1, 0.75); circle(c, 0, 0, 27); c.fill();
        const a = a0 + span * m.local.lv;
        c.strokeStyle = VOID; c.lineWidth = 7; c.lineCap = "round";
        c.beginPath(); c.moveTo(Math.cos(a) * 6, Math.sin(a) * 6); c.lineTo(Math.cos(a) * 22, Math.sin(a) * 22); c.stroke();
      } },
    { id: "WOOFER", unlock: ["extreme", "Drop · EXTREME"], roll: "대칭",
      how: "우퍼. 킥이 들어올 때마다 콘이 쿵 하고 튀어나온다.", ghost: "solid",
      draw(c, col, m) {
        solid(c, col, 0.95);
        c.fillStyle = VOID;
        [[-1, -1], [1, -1], [1, 1], [-1, 1]].forEach(([x, y]) => { circle(c, x * 47, y * 47, 5); c.fill(); });
        circle(c, 0, 0, 47); c.fill();
        const push = 1 + m.low * 0.1 + m.kick[0] * 0.28;
        c.save(); c.scale(push, push);
        c.strokeStyle = rgba(col, 0.55); c.lineWidth = 5; circle(c, 0, 0, 38); c.stroke();
        c.fillStyle = rgba(col, 0.3); circle(c, 0, 0, 30); c.fill();
        c.fillStyle = rgba(col, 1, 0.7); circle(c, 0, 0, 13); c.fill();
        c.restore();
      } },
    { id: "VINYL", unlock: ["extreme", "Ether · EXTREME"], roll: "속돎",
      how: "레코드 슬리브. 판은 계속 돌고, 첫 박마다 스크래치하듯 살짝 되감는다.", ghost: "solid",
      draw(c, col, m) {
        solid(c, col, 0.92);
        const scratch = m.downbeat && m.beatT < 0.14 ? -Math.sin(m.beatT / 0.14 * Math.PI) * 9 : 0;
        m.local.spin = (m.local.spin || 0) + m.dt * (4 + scratch);
        c.fillStyle = VOID; circle(c, 0, 0, 52); c.fill();
        c.strokeStyle = rgba(col, 0.18); c.lineWidth = 2;
        [44, 37, 30].forEach((r) => { circle(c, 0, 0, r); c.stroke(); });
        c.save(); c.rotate(m.local.spin);
        c.fillStyle = rgba(col, 1, 0.6); circle(c, 0, 0, 19); c.fill();
        c.fillStyle = VOID; c.fillRect(-3, -18, 6, 10);
        circle(c, 0, 0, 4); c.fill();
        c.restore();
      } },
    { id: "VOX", unlock: ["extreme", "Voz · EXTREME"], roll: "구름",
      how: "노래하는 얼굴. 소리가 클수록 입이 크게 벌어지고 눈은 ^ ^ 로 감긴다.", ghost: "frame",
      draw(c, col, m) {
        frame(c, col);
        const v = clamp01(m.low * 0.45 + m.mid * 0.7);
        c.strokeStyle = rgba(col, 1, 0.75); c.lineWidth = 7; c.lineCap = "round"; c.lineJoin = "round";
        [-22, 22].forEach((x) => {
          c.beginPath();
          if (v > 0.55) { c.moveTo(x - 9, -14); c.lineTo(x, -24); c.lineTo(x + 9, -14); }
          else { c.moveTo(x, -26); c.lineTo(x, -12); }
          c.stroke();
        });
        c.fillStyle = rgba(col, 1, 0.75);
        const h = 6 + v * 28, w = 30 - v * 6;
        rr(c, -w / 2, 4, w, h, Math.min(w, h) / 2); c.fill();
      } },
  ];

  // ---------- 가상 음악 ----------
  function music(t) {
    const beatF = t / SPB, beat = Math.floor(beatF), beatT = (beatF - beat) * SPB;
    const eighthT = ((t / (SPB / 2)) % 1) * (SPB / 2);
    const kickEnv = Math.exp(-beatT * 9);
    const snare = (beat % 2 === 1) ? Math.exp(-beatT * 12) : 0;
    const hat = Math.exp(-eighthT * 22);
    const low = clamp01(0.15 + kickEnv * 0.85);
    const mid = clamp01(0.3 + 0.25 * Math.sin(t * 1.7) + snare * 0.5);
    const high = clamp01(0.1 + hat * 0.8 + 0.1 * Math.sin(t * 5.3));
    return { beat, bar: Math.floor(beat / 4), beatT, downbeat: beat % 4 === 0, low, mid, high };
  }


  const EQ = { id: "EQ", draw(c, col, m) {
    frame(c, col, 12); c.fillStyle = col;
    const lv = [m.low, m.mid, m.high];
    [-30, 0, 30].forEach((x, i) => capsule(c, x, 40, 18, 22 + 54 * lv[i]));
  } };
  const byId = Object.fromEntries([EQ, ...CHARS].map((ch) => [ch.id, ch]));
  window.BBChars = {
    ids: Object.keys(byId),
    draw(c, id, col, t, local) {
      const ch = byId[id]; if (!ch) return;
      const mu = music(t);
      ch.draw(c, col, { ...mu, t, dt: 1 / 60, kick: mu.low, local: local || {} });
    },
  };
})();
