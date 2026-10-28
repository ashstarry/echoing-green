# Echoing Green · 言外

A living, cut-paper miniature town. Current scene: Borrowed Wind Town / 借风町.

English is the first-visit default. Music is enabled by default; browser autoplay rules may require your first click or keypress. Language and sound choices are saved locally.

The town simulates life in your browser and pauses when you leave. Use weather buttons, the Town journal and selectable actions to explore. Free-text wishes use a separately hosted secure Jev proxy; no provider credentials are included in this repository or in GitHub Pages.

## Run locally

Serve this directory with any static HTTP server. No build step is required for this public snapshot. GitHub Pages serves the main branch root.

## Sources and credits

- The Chinese name draws on Mei Yaochen’s words recorded in Ouyang Xiu’s *Liuyi Shihua*: https://zh.wikisource.org/wiki/六一詩話
- The English name draws on William Blake’s *The Echoing Green*: https://www.poetryfoundation.org/poems/56592/the-ecchoing-green
- Three.js and its decoder libraries retain their bundled license notices under `vendor/`.
- Town models, scene design, behavior logic and original soft chiptune arrangements are project assets. No license grant is implied for these assets.

## Security

Never add API keys, private configuration, raw API logs or research archives. `src/deployment-config.mjs` may contain only a public proxy URL. The provider key belongs in the proxy host’s secret storage, never in frontend environment variables or repository files.
