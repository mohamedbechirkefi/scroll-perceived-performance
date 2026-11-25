// SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0
// Sandbox worker: runs the ported schedule and reference model (engine.ts) for one bounded
// configuration (K = 10 trials). It computes lower bounds; it measures nothing.
import { simulate, type SandboxInput, type SandboxOutput } from "./engine";

export type WorkerRequest = { type: "run"; input: SandboxInput } | { type: "cancel" };
export type WorkerReply =
  | { type: "done"; input: SandboxInput; output: SandboxOutput }
  | { type: "cancelled" }
  | { type: "error"; message: string };

onmessage = (ev: MessageEvent<WorkerRequest>) => {
  const m = ev.data;
  if (m.type === "cancel") {
    postMessage({ type: "cancelled" } satisfies WorkerReply);
    return;
  }
  try {
    postMessage({ type: "done", input: m.input, output: simulate(m.input) } satisfies WorkerReply);
  } catch (e) {
    postMessage({ type: "error", message: e instanceof Error ? e.message : String(e) } satisfies WorkerReply);
  }
};
