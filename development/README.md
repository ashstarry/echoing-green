# Echoing Green — development source

The repository root remains the published GitHub Pages site. This directory contains the editable project and earlier source checkpoints.

| Directory | Contents |
| --- | --- |
| `app/runtime-cp47/` | Current frontend, local decision server, tests, contract and build script. Start here. |
| `api/` | Source mirror of the deployed Sites Jev proxy, including its gateway, tests and deployment configuration. |
| `app/runtime-cp17/` … `app/runtime-cp46/` | Earlier runtime source checkpoints, for project history and compatibility testing. |
| `work/` | Project-authored Blender modeling, lighting, rig/export, simulation, evaluation and release scripts. |
| `source-provenance.json` | Original paths and hashes; the API mirror identifies its source commit. |

## Run the current town locally

Use Node.js 22.13 or newer (Node.js 24 is recommended for the API project).

```sh
cd development/app/runtime-cp47
npm ci
npm run dev
```

The install step copies the already-versioned web assets from the repository's root `assets/` into the ignored local `public/assets/` directory. The server binds to `127.0.0.1:4240`; set `PORT` to use another port.

The world and activity controls do not need a provider key. To enable the local free-text decision service, set `OPENROUTER_API_KEY` in the process environment or set `OPENROUTER_API_KEY_FILE` to a private file **outside this repository**. On macOS/Linux the file must be readable only by its owner. No real key is included. Local request logs go to the ignored `.local/semantic-runs/` directory.

```sh
npm test
npm run build
```

`dist/` is a local static preview. Do not replace the root published site by copying server files into it. The public browser's decision endpoint is configured separately; provider credentials belong only in the backend Secret store.

## API source

The `api/` directory is a source mirror of the existing Sites deployment, not a request to create a new service. Its `.openai/hosting.json` identifies that existing project; this identifier is not a credential. The deployment still uses the existing Sites workflow and encrypted runtime Secret. Publishing this mirror to GitHub does not redeploy or change the service.

```sh
cd development/api
node --test tests/*.test.mjs
```

The mirror retains its package lock and build scripts for a full installation/build when needed. It contains no runtime environment values or source-repository access tokens.

## History and authoring tools

Historical source and 600 authoring/evaluation/release scripts are retained with their original relative layout. Run those scripts from a complete authoring workspace: many expect earlier `.blend` files, reference images or render/checkpoint data. Those large historical assets and raw experiment outputs are **not** bundled here. The current web model, textures, audio and runtime data are already present in root `assets/`.

The CP29/CP31 JSON data used by current migration tests is included; other historical builds are source records rather than independently packaged releases. The existing repository root still serves the current site unchanged.

## Security and portability

- `.env` files, real keys, private configuration, raw request logs, dependency installations and caches are excluded.
- The current local server accepts credentials from the environment or an external file rather than an author-specific filesystem path.
- The local server's checkpoint marker is aligned with CP44.
- These portability edits are recorded in `source-provenance.json`; the published frontend behavior is unchanged.
- Historical tools may contain patterns for detecting local paths and secrets. These are detection rules, not credentials.
