<!-- SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0 -->
# Dependency licences (M6, 2026-11-25)

Scope: every Python distribution installed in `.venv` by `uv sync --frozen --all-groups --all-extras` from the committed `uv.lock`, read from the installed package metadata (`License-Expression`, else the licence classifiers), and every npm package installed in `demo/node_modules` by `npm ci` from the committed `demo/package-lock.json`, read from each package's own `package.json`. Platform binaries that npm skipped on this machine (other operating systems) are not listed. Nothing here is legal advice; the owner decides on any licence question.

## Summary

- Python: 26 distributions. npm: 53 installed packages, of which 3 (react, react-dom, scheduler) are bundled into the static demo; the others are build and test tools only.
- Every licence is one of MIT, MIT-CMU, BSD (0BSD, 2-clause, 3-clause), ISC, Apache-2.0, PSF-2.0 or the Python Software Foundation licence, CC0-1.0, Zlib, or MPL-2.0. **No licence outside the permissive list of the M6 brief was found.**
- Flags for the owner's attention (not problems):
  1. **MPL-2.0** (file-level weak copyleft): `hypothesis` (test tool, not distributed) and `lightningcss` with its macOS binary (CSS build tool, not part of the built page). MPL-2.0 is on the brief's list; it would matter only if their source files were modified and distributed.
  2. **matplotlib** uses the Python Software Foundation based matplotlib licence (permissive); `pillow` uses MIT-CMU (permissive, historical PIL licence).
  3. **Tools outside the lock files**, used but not distributed: Google Chrome 158.0.8127.38 (proprietary freeware; drives the measurements, not redistributed), pandoc 3.6.3 (GPL-2.0-or-later; a build tool whose output is not a derivative of pandoc), the `typst` Python package (Apache-2.0), Node 22.23.3 (MIT and bundled third-party licences).
  4. The demo's own `package.json` declares `"license": "SEE LICENSE IN ../LICENSE"`, the repository's custom licence (DEC-001).

## Python (`.venv`)

| Package | Version | Licence (metadata) | Role |
|---|---|---|---|
| attrs | 26.1.0 | MIT | transitive |
| contourpy | 1.4.0 | BSD-3-Clause | transitive |
| cycler | 0.12.1 | BSD License | transitive |
| fonttools | 4.68.0 | MIT | transitive |
| greenlet | 3.5.6 | MIT AND PSF-2.0 | transitive |
| hypothesis | 6.170.15 | MPL-2.0 | development (direct) |
| iniconfig | 2.3.1 | MIT | transitive |
| jsonschema | 4.26.0 | MIT | runtime (direct) |
| jsonschema-specifications | 2025.9.1 | MIT | transitive |
| kiwisolver | 1.5.1 | BSD License | transitive |
| matplotlib | 3.11.2 | Python Software Foundation License | runtime (direct) |
| numpy | 2.5.4 | BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0 | runtime (direct) |
| packaging | 26.3 | Apache-2.0 OR BSD-2-Clause | transitive |
| pillow | 13.0.0 | MIT-CMU | transitive |
| playwright | 1.65.0 | Apache-2.0 | runtime (direct) |
| pluggy | 1.7.0 | MIT License | transitive |
| pygments | 2.21.0 | BSD-2-Clause | transitive |
| pyparsing | 3.3.3 | MIT | transitive |
| pytest | 9.2.0 | MIT | development (direct) |
| python-dateutil | 4.0.0 | BSD-3-Clause | transitive |
| referencing | 0.37.0 | MIT | transitive |
| rpds-py | 2026.9.1 | MIT | transitive |
| scipy | 1.18.1 | BSD License | runtime (direct) |
| sortedcontainers | 2.4.0 | Apache Software License | transitive |
| typing_extensions | 4.16.0 | PSF-2.0 | transitive |
| tzdata | 2026.6 | Apache-2.0 | transitive |

## npm (`demo/node_modules`)

| Package | Version | Licence (`package.json`) | Role |
|---|---|---|---|
| @jridgewell/sourcemap-codec | 1.6.0 | MIT | build/test |
| @oxc-project/types | 0.156.0 | MIT | build/test |
| @rolldown/binding-darwin-arm64 | 1.2.19 | MIT | build/test, optional platform binary |
| @rolldown/pluginutils | 1.1.1 | MIT | build/test |
| @standard-schema/spec | 1.1.0 | MIT | build/test |
| @types/chai | 5.2.3 | MIT | build/test |
| @types/deep-eql | 4.0.2 | MIT | build/test |
| @types/estree | 1.0.11 | MIT | build/test |
| @types/react | 19.3.0 | MIT | build/test |
| @types/react-dom | 19.3.0 | MIT | build/test |
| @vitejs/plugin-react | 6.1.2 | MIT | build/test |
| @vitest/expect | 4.1.12 | MIT | build/test |
| @vitest/mocker | 4.1.12 | MIT | build/test |
| @vitest/pretty-format | 4.1.12 | MIT | build/test |
| @vitest/runner | 4.1.12 | MIT | build/test |
| @vitest/snapshot | 4.1.12 | MIT | build/test |
| @vitest/spy | 4.1.12 | MIT | build/test |
| @vitest/utils | 4.1.12 | MIT | build/test |
| assertion-error | 2.0.1 | MIT | build/test |
| chai | 6.3.0 | MIT | build/test |
| convert-source-map | 2.0.0 | MIT | build/test |
| csstype | 3.2.4 | MIT | build/test |
| detect-libc | 2.1.2 | Apache-2.0 | build/test |
| es-module-lexer | 2.3.2 | MIT | build/test |
| estree-walker | 3.0.3 | MIT | build/test |
| expect-type | 1.4.0 | Apache-2.0 | build/test |
| fdir | 6.5.0 | MIT | build/test |
| fsevents | 2.3.3 | MIT | build/test, optional platform binary |
| lightningcss | 1.33.0 | MPL-2.0 | build/test |
| lightningcss-darwin-arm64 | 1.33.0 | MPL-2.0 | build/test, optional platform binary |
| magic-string | 0.30.21 | MIT | build/test |
| nanoid | 3.3.20 | MIT | build/test |
| obug | 2.2.1 | MIT | build/test |
| pathe | 2.0.3 | MIT | build/test |
| picocolors | 1.1.1 | ISC | build/test |
| picomatch | 4.0.7 | MIT | build/test |
| postcss | 8.5.33 | MIT | build/test |
| react | 19.3.1 | MIT | runtime (bundled into dist) |
| react-dom | 19.3.1 | MIT | runtime (bundled into dist) |
| rolldown | 1.2.19 | MIT | build/test |
| scheduler | 0.28.0 | MIT | runtime (bundled into dist) |
| siginfo | 2.0.0 | ISC | build/test |
| source-map-js | 1.2.4 | BSD-3-Clause | build/test |
| stackback | 0.0.2 | MIT | build/test |
| std-env | 4.3.0 | MIT | build/test |
| tinybench | 2.9.0 | MIT | build/test |
| tinyexec | 1.4.0 | MIT | build/test |
| tinyglobby | 0.2.17 | MIT | build/test |
| tinyrainbow | 3.2.0 | MIT | build/test |
| typescript | 5.9.3 | Apache-2.0 | build/test |
| vite | 8.3.5 | MIT | build/test |
| vitest | 4.1.12 | MIT | build/test |
| why-is-node-running | 2.3.0 | MIT | build/test |
