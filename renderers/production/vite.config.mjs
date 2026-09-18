import { defineConfig } from '../rhine/node_modules/vite/dist/node/index.js';
import path from 'node:path';
const threeRoot=path.resolve('../rhine/node_modules/three');
export default defineConfig({resolve:{alias:[{find:'three/addons',replacement:path.join(threeRoot,'examples/jsm')},{find:'three',replacement:threeRoot}]},server:{host:'127.0.0.1'}});
