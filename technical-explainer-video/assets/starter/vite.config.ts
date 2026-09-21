import {defineConfig} from 'vite';
import mc from '@motion-canvas/vite-plugin';
import ff from '@motion-canvas/ffmpeg';
const motionCanvas=typeof mc==='function'?mc:(mc as any).default;
const ffmpeg=typeof ff==='function'?ff:(ff as any).default;
export default defineConfig({plugins:[motionCanvas(),ffmpeg()],server:{host:'127.0.0.1'}});
