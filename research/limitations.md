<!-- SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0 -->
# Limitations (living document)

Status at M0 (2026-11-24): no experiment has run. These are anticipated limitations of the draft protocol; they will be revised against actual results.

1. **No perception claims.** All metrics are objective timings in a browser. Nothing here measures how fast an interface feels to a person. Any perceived-speed statement needs a human study, which is out of scope and would need an owner-approved protocol.
2. **One mock interface.** Results hold for one synthetic page with fixed layout and content. Real applications differ in DOM size, framework, caching and network behaviour.
3. **Synthetic latency.** Delays come from a seeded mock transport, not from a network. Bandwidth, connection setup, server variance and tail latency are not modelled beyond a uniform jitter of plus or minus 10%.
4. **One machine and one engine.** Chromium on an Apple M1 Pro laptop. Other engines (WebKit, Gecko), other devices and mobile hardware are not covered.
5. **Instrumentation limits.** Frame times are estimated in-page; Event Timing hides durations under 16 ms and rounds to 8 ms; headless rendering may not match a physical display.
6. **Scripted input.** Interactions and prefetch intent signals are scripted with fixed timing; real pointer behaviour is not modelled.
7. **Prefetch results are partly mechanical.** The benefit is bounded by the scripted lead time; the experiment measures whether the implementation and instrumentation recover it, and its costs, not how often real users hover before clicking.
8. **Simulation status.** All results are simulations within the stated assumptions; they are not claims about any real or proprietary product.
