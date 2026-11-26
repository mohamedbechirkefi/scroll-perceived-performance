// SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { App } from "./App";
import "./fonts.css";
import "./style.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
