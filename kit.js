/* LFK: the drawing kit. Everything is SVG built from code; every frame is a pure function of time.
   No Math.random, no Date.now: use LFK.hash(i) for "random" so any frame renders identically. */
(function () {
  const NS = "http://www.w3.org/2000/svg";
  const P = { // palette (edit per series)
    bg: "#0B1220", navy: "#12263A", orange: "#FF9F43", red: "#FF3B30", lime: "#C6F432",
    skin: "#F4DCA6", outline: "#0B1220", shirt: "#FF8A70", pants: "#2A4A5A", hair: "#5A3A28",
  };
  const OUT = 6; // outline thickness

  function el(tag, attrs, parent) {
    const e = document.createElementNS(NS, tag);
    for (const k in attrs || {}) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  }
  const hash = (i) => { const s = Math.sin(i * 127.1 + 311.7) * 43758.5453; return s - Math.floor(s); };

  // ---- person(): jointed stickman, set via pose({...}) ----
  function person(parent, o = {}) {
    const c = o.colors || {};
    const shirt = c.shirt || P.shirt, pants = c.pants || P.pants, skin = c.skin || P.skin, hair = c.hair || P.hair;
    const g = el("g", {}, parent);
    const limb = (col, w) => el("path", { fill: "none", stroke: col, "stroke-width": w, "stroke-linecap": "round", "stroke-linejoin": "round" }, g);
    const legL = limb(pants, 26), legR = limb(pants, 26);
    const torso = limb(shirt, 44);
    const armL = limb(shirt, 20), armR = limb(shirt, 20);
    const head = el("circle", { r: 46, fill: skin, stroke: P.outline, "stroke-width": OUT }, g);
    const hairE = el("path", { fill: hair }, g);
    const eyeL = el("ellipse", { rx: 6, ry: 8, fill: P.outline }, g);
    const eyeR = el("ellipse", { rx: 6, ry: 8, fill: P.outline }, g);
    const brows = el("path", { fill: "none", stroke: P.outline, "stroke-width": 5, "stroke-linecap": "round" }, g);
    const mouth = el("ellipse", { rx: 10, fill: "#7a1f1f" }, g);

    function pose(p = {}) {
      const t = p.t || 0, walk = p.walk ? Math.sin(t * 8) : 0, run = p.run ? 1.6 : 1;
      const x = p.x || 0, y = p.y || 0, s = p.scale || 1, flip = p.flip ? -1 : 1;
      g.setAttribute("transform", `translate(${x} ${y}) scale(${s * flip} ${s})`);
      const hip = [0, 0], neck = [0, -110];
      const swing = walk * 28 * run;
      legL.setAttribute("d", `M0 0 L${-14 + swing} 60 L${-18 + swing * 1.4} 120`);
      legR.setAttribute("d", `M0 0 L${14 - swing} 60 L${18 - swing * 1.4} 120`);
      torso.setAttribute("d", `M${hip[0]} ${hip[1]} L${neck[0]} ${neck[1]}`);
      const [al, ar] = p.arms || [[-40, 50], [40, 50]]; // hand targets relative to shoulder
      armL.setAttribute("d", `M0 -95 L${al[0] * 0.6 - swing * 0.5} ${-95 + al[1] * 0.5} L${al[0]} ${-95 + al[1]}`);
      armR.setAttribute("d", `M0 -95 L${ar[0] * 0.6 + swing * 0.5} ${-95 + ar[1] * 0.5} L${ar[0]} ${-95 + ar[1]}`);
      head.setAttribute("cx", 0); head.setAttribute("cy", -160);
      hairE.setAttribute("d", `M-46 -165 A46 46 0 0 1 46 -165 L40 -185 L-40 -185 Z`);
      const blink = (Math.floor(t * 1000) % 3200) < 120 ? 0.1 : 1;
      eyeL.setAttribute("cx", -16); eyeR.setAttribute("cx", 16);
      eyeL.setAttribute("cy", -158); eyeR.setAttribute("cy", -158);
      eyeL.setAttribute("ry", 8 * blink); eyeR.setAttribute("ry", 8 * blink);
      const b = { calm: [0, 0], worried: [-6, 6], scared: [-10, 10], angry: [8, -8], happy: [-4, -2] }[p.brows || "calm"];
      brows.setAttribute("d", `M-26 ${-176 + b[0]} L-8 ${-176 + b[1]} M8 ${-176 + b[1]} L26 ${-176 + b[0]}`);
      const m = p.mouth || 0; // 0..1, drive from voice loudness
      mouth.setAttribute("cx", 0); mouth.setAttribute("cy", -136);
      mouth.setAttribute("ry", 2 + m * 12);
    }
    pose();
    return { g, pose };
  }

  // ---- zombie(): black silhouette with glowing eyes ----
  function zombie(parent, o = {}) {
    const g = el("g", {}, parent);
    const body = el("path", { fill: "#05080f", stroke: "#1b2b3f", "stroke-width": 4, "stroke-linejoin": "round",
      d: "M-30 0 L-26 -120 Q-70 -150 -64 -190 L-70 -230 Q-40 -280 0 -280 Q40 -280 70 -230 L64 -190 Q70 -150 26 -120 L30 0 Z" }, g);
    const eyes = el("g", { opacity: 0 }, g);
    el("circle", { cx: -18, cy: -230, r: 8, fill: "#fff" }, eyes);
    el("circle", { cx: 18, cy: -230, r: 8, fill: "#fff" }, eyes);
    return {
      g,
      place(x, y, s = 1) { g.setAttribute("transform", `translate(${x} ${y}) scale(${s})`); },
      glow(v) { eyes.setAttribute("opacity", v); },
      sway(t, amt = 6) { body.setAttribute("transform", `rotate(${Math.sin(t * 2) * amt} 0 0)`); },
    };
  }

  // ---- hand(): first-person grey hand, veins fade in ----
  function hand(parent, o = {}) {
    const g = el("g", {}, parent);
    el("path", { fill: "#9aa3ad", stroke: "#2b3440", "stroke-width": 5, "stroke-linejoin": "round",
      d: "M-40 0 Q-50 -70 -30 -100 L-20 -160 Q-10 -170 -4 -160 L0 -110 L8 -170 Q16 -178 22 -168 L22 -110 L34 -150 Q42 -156 46 -146 L40 -90 Q60 -60 50 0 Z" }, g);
    const veins = el("path", { fill: "none", stroke: "#111", "stroke-width": 4, opacity: 0,
      d: "M-10 -20 L-6 -90 M10 -20 L18 -100 M24 -30 L34 -110" }, g);
    return {
      g,
      place(x, y, s = 1, rot = 0) { g.setAttribute("transform", `translate(${x} ${y}) rotate(${rot}) scale(${s})`); },
      veins(v) { veins.setAttribute("opacity", v); },
    };
  }

  // ---- rain(): deterministic, hash-based ----
  function rain(parent, o = {}) {
    const n = o.count || 80, W = o.w || 1080, H = o.h || 1920;
    const g = el("g", { stroke: "#9fc4e8", "stroke-width": 2, opacity: 0.5 }, parent);
    const lines = [];
    for (let i = 0; i < n; i++) lines.push(el("line", {}, g));
    return {
      g,
      update(t) {
        lines.forEach((l, i) => {
          const x = hash(i) * W, speed = 900 + hash(i + 99) * 500, y = ((hash(i + 7) * H + t * speed) % (H + 80)) - 40;
          l.setAttribute("x1", x); l.setAttribute("y1", y); l.setAttribute("x2", x - 8); l.setAttribute("y2", y + 36);
        });
      },
    };
  }

  // ---- camera(): "put world point (x,y) at screen (540,860) at zoom S" ----
  function camera(world) {
    return { at(x, y, S = 1) { world.setAttribute("transform", `translate(${540 - x * S} ${860 - y * S}) scale(${S})`); } };
  }

  // ---- captions: 2-4 word chunks, [bracketed] word in accent ----
  function caption(parent, text, accent = P.lime) {
    const g = el("g", {}, parent);
    const parts = text.split(/(\[[^\]]+\])/).filter(Boolean);
    const t = el("text", { x: 540, y: 1250, "text-anchor": "middle", "font-family": "Impact, 'Arial Black', sans-serif",
      "font-size": 84, "font-weight": 900, "stroke": "#000", "stroke-width": 14, "paint-order": "stroke", "stroke-linejoin": "round" }, g);
    parts.forEach((p) => {
      const hl = p.startsWith("[");
      const s = el("tspan", { fill: hl ? accent : "#fff" }, t);
      s.textContent = hl ? p.slice(1, -1) : p;
    });
    return g;
  }

  // ---- scene context: bind a scene to the audio timeline ----
  function ctx(id) {
    const T = window.__timeline || { marks: {}, lines: [], duration: 10 };
    return {
      id, tl: gsap.timeline({ paused: true }),
      get DUR() { return T.duration; },
      mark: (name) => (T.marks[name] ?? 0),
      lines: T.lines,
      // every frame is a pure function of time
      drive(fn) { this.tl.eventCallback("onUpdate", () => fn(this.tl.time())); fn(0); },
      get tlObj() { return this.tl; },
    };
  }

  window.LFK = { P, OUT, el, hash, person, zombie, hand, rain, camera, caption, ctx, climber: zombie };
})();
