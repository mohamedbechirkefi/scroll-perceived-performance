// SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0
// Small motion helpers. Transform and opacity only; every helper respects reduced motion.
import { useEffect, useLayoutEffect, useRef, useState, type RefObject } from "react";

export const reducedMotion = () =>
  typeof window !== "undefined" && typeof window.matchMedia === "function" && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

/**
 * Sliding indicator under the pressed button of a segmented control. The indicator is a
 * 1 px bar placed with translate() and sized with scaleX(), so only transform changes.
 */
export function useSlidingIndicator(active: string) {
  const group = useRef<HTMLDivElement | null>(null);
  const bar = useRef<HTMLSpanElement | null>(null);
  const first = useRef(true);
  useLayoutEffect(() => {
    const place = () => {
      const g = group.current, b = bar.current;
      if (!g || !b) return;
      const btn = g.querySelector<HTMLElement>('button[aria-pressed="true"]');
      if (!btn) { b.style.opacity = "0"; return; }
      b.style.opacity = "1";
      b.style.transform = `translate(${btn.offsetLeft}px, ${btn.offsetTop + btn.offsetHeight - 3}px) scaleX(${btn.offsetWidth})`;
    };
    const b = bar.current;
    if (b && first.current) { b.style.transition = "none"; place(); void b.offsetWidth; b.style.transition = ""; first.current = false; }
    else place();
    if (typeof ResizeObserver === "undefined" || !group.current) return;
    const ro = new ResizeObserver(() => {
      if (!bar.current) return;
      bar.current.style.transition = "none"; place(); void bar.current.offsetWidth; bar.current.style.transition = "";
    });
    ro.observe(group.current);
    return () => ro.disconnect();
  }, [active]);
  return { group, bar };
}

/** True once the element has entered the viewport (never resets). */
export function useSeenOnce<T extends Element>(): [RefObject<T | null>, "idle" | "waiting" | "seen"] {
  const ref = useRef<T | null>(null);
  const [state, setState] = useState<"idle" | "waiting" | "seen">("idle");
  useEffect(() => {
    const el = ref.current;
    if (!el || reducedMotion() || typeof IntersectionObserver === "undefined") return;
    const r = el.getBoundingClientRect();
    if (r.top < window.innerHeight * 0.9) return; // already on screen at load: no reveal
    setState("waiting");
    const io = new IntersectionObserver((es) => {
      if (es.some((e) => e.isIntersecting)) { setState("seen"); io.disconnect(); }
    }, { threshold: 0.25 });
    io.observe(el);
    return () => io.disconnect();
  }, []);
  return [ref, state];
}
