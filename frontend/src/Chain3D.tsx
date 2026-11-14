import { useEffect, useRef } from "react";
import * as THREE from "three";
import type { Block } from "./api";

const SLOTS = 9;
const GAP = 2.1;
const LAV = new THREE.Color("#CBB3E8");
const RED = new THREE.Color("#E34234");
const INK = new THREE.Color("#16101F");
const LIME = new THREE.Color("#D4FF4F");

/** The last few real blocks as a 3D chain. Width = transactions, height = fee (log scale). */
export default function Chain3D({ blocks, index }: { blocks: Block[]; index: number }) {
  const host = useRef<HTMLDivElement>(null);
  const state = useRef({ blocks, index, arrived: performance.now() });

  useEffect(() => {
    state.current.blocks = blocks;
  }, [blocks]);
  useEffect(() => {
    state.current.index = index;
    state.current.arrived = performance.now();
  }, [index]);

  useEffect(() => {
    const el = host.current!;
    const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
    let renderer: THREE.WebGLRenderer;
    try {
      renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    } catch {
      return; // no WebGL: the card still shows the numbers
    }
    renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
    renderer.setClearColor(0x000000, 0);
    el.appendChild(renderer.domElement);

    const scene = new THREE.Scene();
    scene.fog = new THREE.Fog(LIME, 14, 30); // older blocks fade into the lime card
    const camera = new THREE.PerspectiveCamera(30, 1, 0.1, 100);
    camera.position.set(0, 3.2, 16);
    camera.lookAt(0, 0.4, 0);

    scene.add(new THREE.HemisphereLight(0xffffff, LAV, 1.6));
    const sun = new THREE.DirectionalLight(0xffffff, 1.6);
    sun.position.set(5, 9, 7);
    scene.add(sun);

    const chain = new THREE.Group();
    scene.add(chain);
    const box = new THREE.BoxGeometry(1, 1, 1);
    const edges = new THREE.EdgesGeometry(box);
    const items = Array.from({ length: SLOTS }, () => {
      const mat = new THREE.MeshLambertMaterial({ color: LAV });
      const mesh = new THREE.Mesh(box, mat);
      const lineMat = new THREE.LineBasicMaterial({ color: INK });
      mesh.add(new THREE.LineSegments(edges, lineMat));
      chain.add(mesh);
      return { mesh, mat };
    });
    const linkGeo = new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(-GAP * SLOTS, -1, 0), new THREE.Vector3(GAP, -1, 0)]);
    chain.add(new THREE.Line(linkGeo, new THREE.LineBasicMaterial({ color: INK })));

    const resize = () => {
      const w = el.clientWidth || 1, h = el.clientHeight || 1;
      renderer.setSize(w, h, false);
      camera.aspect = w / h;
      camera.position.z = w / h < 1.4 ? 17 : 12.5;
      camera.updateProjectionMatrix();
    };
    const ro = new ResizeObserver(resize);
    ro.observe(el);
    resize();

    let visible = true;
    const io = new IntersectionObserver(([e]) => (visible = e.isIntersecting));
    io.observe(el);

    let raf = 0;
    const tick = (now: number) => {
      raf = requestAnimationFrame(tick);
      if (!visible || document.hidden) return;
      const { blocks: bl, index: idx, arrived } = state.current;
      if (!bl.length) return;
      const logs = bl.map((b) => Math.log(Math.max(b.fee, 1)));
      const lo = Math.min(...logs), hi = Math.max(...logs);
      const meanTx = bl.reduce((s, b) => s + b.tx, 0) / bl.length;
      const k = reduce ? 1 : Math.min((now - arrived) / 700, 1);
      const ease = 1 - Math.pow(1 - k, 3);

      items.forEach((it, slot) => {
        const age = SLOTS - 1 - slot; // 0 = newest
        const i = (((idx - age) % bl.length) + bl.length) % bl.length;
        const width = 0.55 + 0.7 * Math.sqrt(bl[i].tx / meanTx);
        const height = 0.45 + 2.1 * (hi > lo ? (logs[i] - lo) / (hi - lo) : 0.5);
        const grow = age === 0 ? ease : 1;
        it.mesh.scale.set(width, height * grow, width);
        it.mesh.position.set((slot - (SLOTS - 1)) * GAP + GAP * (1 - ease), -1 + (height * grow) / 2, 0);
        it.mat.color.copy(age === 0 ? RED : LAV);
      });
      chain.position.set(3.2, -0.1, 0);
      chain.rotation.y = -0.62;
      renderer.render(scene, camera);
    };
    raf = requestAnimationFrame(tick);

    return () => {
      cancelAnimationFrame(raf);
      ro.disconnect();
      io.disconnect();
      box.dispose(); edges.dispose(); linkGeo.dispose();
      items.forEach((i) => i.mat.dispose());
      renderer.dispose();
      renderer.domElement.remove();
    };
  }, []);

  return <div ref={host} className="hero-canvas" aria-hidden />;
}
