# Mission Stack

Private, pre-launch website for Mission Stack: customer systems for established home-service businesses.

The site is intentionally static and dependency-free. Its public pages include explicit `noindex` metadata, and `robots.txt` blocks crawling until launch approval.

## Local checks

```sh
npm run lint
npm run build
npm test
npm run check:routes
```

Use `python3 -m http.server 4173` for a local preview at `http://127.0.0.1:4173/`.
