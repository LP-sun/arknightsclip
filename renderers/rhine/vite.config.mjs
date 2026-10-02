import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { defineConfig } from 'vite';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const productionAssets = path.join(root, 'renderers/production/public/assets');
const rawData = path.join(root, 'data');

function sourceAssetMiddleware(directory) {
  return (req, res, next) => {
    const requestPath = decodeURIComponent(req.url?.split('?')[0] || '').replace(/^\//, '');
    const candidate = path.resolve(directory, requestPath);
    if (!candidate.startsWith(`${directory}${path.sep}`) || !fs.existsSync(candidate) || !fs.statSync(candidate).isFile()) {
      next();
      return;
    }
    res.statusCode = 200;
    res.setHeader('Content-Type', candidate.endsWith('.png') ? 'image/png' : 'application/octet-stream');
    fs.createReadStream(candidate).pipe(res);
  };
}

export default defineConfig({
  server: {
    host: '127.0.0.1',
    fs: { allow: [root] },
  },
  plugins: [{
    name: 'rhine-source-assets',
    configureServer(server) {
      server.middlewares.use('/assets', sourceAssetMiddleware(productionAssets));
      server.middlewares.use('/data', sourceAssetMiddleware(rawData));
    },
  }],
});
