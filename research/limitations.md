<!-- SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0 -->
# Limitations (living document)

Status at M0 (2026-11-24): no experiment has run. These are anticipated limitations of the draft protocol; they will be revised against actual results. Items 9 to 14 were added after the M3 confirmatory runs (2026-11-25).

1. **No perception claims.** All metrics are objective timings in a browser. Nothing here measures how fast an interface feels to a person. Any perceived-speed statement needs a human study, which is out of scope and would need an owner-approved protocol.
2. **One mock interface.** Results hold for one synthetic page with fixed layout and content. Real applications differ in DOM size, framework, caching and network behaviour.
3. **Synthetic latency.** Delays come from a seeded mock transport, not from a network. Bandwidth, connection setup, server variance and tail latency are not modelled beyond a uniform jitter of plus or minus 10%.
4. **One machine and one engine.** Chromium on an Apple M1 Pro laptop. Other engines (WebKit, Gecko), other devices and mobile hardware are not covered.
5. **Instrumentation limits.** Frame times are estimated in-page; Event Timing hides durations under 16 ms and rounds to 8 ms; headless rendering may not match a physical display.
6. **Scripted input.** Interactions and prefetch intent signals are scripted with fixed timing; real pointer behaviour is not modelled.
7. **Prefetch results are partly mechanical.** The benefit is bounded by the scripted lead time; the experiment measures whether the implementation and instrumentation recover it, and its costs, not how often real users hover before clicking.
8. **Simulation status.** All results are simulations within the stated assumptions; they are not claims about any real or proprietary product.
9. **Frame-scale effects depend on the paint-time method.** EXP-002 found SKELETON minus BLANK of -16.7 ms at L = 50 ms (equivalence not shown); under the alternative paint methods the estimate was -15.3 ms (raf1) and -9.1 ms (Element Timing), both equivalent within 17 ms (EXP-004 S1). Differences of about one frame are therefore method-dependent and are not interpreted as strategy effects.
10. **Sign rule on null contrasts.** The EXP-004 robustness rule compares signs of point estimates. For the write-path failure strata the main estimates are within about 3 ms of zero and not significant, so their sign changes across levels carry no information about direction.
11. **Test reading.** The protocol names a bootstrap interval, a Wilcoxon test and a Holm correction without stating which one decides H0. DEC-011 fixed the reading before data (Holm over Wilcoxon p-values); one contrast (EXP-002 SKELETON, L = 300 ms) differs between the two readings.
12. **TTFF sensitivity not computed.** The alternative paint method is recorded only for the usable-content frame, so the TTFF part of sensitivity S1 is missing (DEC-012).
13. **Reduced sensitivity coverage.** S2 to S4 use 10 seeds, L in {300, 1000} ms and p in {0, 0.3}; cells outside that set have only the S1 check.
14. **Run conditions.** One browser version (Chrome 158.0.8127.38), runs under `nice -n 10`, load average 1.4 to 2.4 at run starts with an editor and system services running. The exclusive window reduced, but did not remove, background activity.
