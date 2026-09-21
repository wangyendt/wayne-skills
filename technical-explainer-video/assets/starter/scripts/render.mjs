import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {runtime,root} from './runtime.mjs';
const timing=JSON.parse(await readFile(root+'src/timing.json','utf8'));
const cues=JSON.parse(await readFile(root+'src/subtitles.json','utf8'));
const rt=await runtime();
try{
 await mkdir(root+'output/keyframes',{recursive:true});
 const page=await rt.browser.newPage();
 const pageErrors=[];page.on('pageerror',error=>pageErrors.push(String(error)));
 await page.goto(rt.url+'/render.html');
 await page.waitForFunction(()=>window.ready,{}, {timeout:120000});
 if(process.argv.includes('--stills')){
  for(const s of timing.scenes){
   const cue=cues.filter(c=>c.scene===s.id).at(-1);
   const t=cue?(cue.start+cue.end)/2:s.start+s.duration*.8;
   const png=await page.evaluate(t=>window.previewAt(t),t);
   await writeFile(root+`output/keyframes/${String(s.id).padStart(2,'0')}.png`,Buffer.from(png.split(',')[1],'base64'));
  }
 }else{
  await page.evaluate(()=>{window.renderFilm();});
  const deadline=Date.now()+Math.max(900000,timing.total_duration*20000);
  while(true){
   await page.waitForTimeout(2000);
   const state=await page.evaluate(()=>({done:window.finished,result:window.result,frame:window.progress,errors:window.errors}));
   console.log('render frame',state.frame);
   if(pageErrors.length||state.errors.length)throw Error(JSON.stringify([...pageErrors,...state.errors]));
   if(state.done){if(state.result!==0)throw Error(`Render failed: ${state.result}`);break;}
   if(Date.now()>deadline)throw Error('Render timed out');
  }
 }
 const errors=[...pageErrors,...await page.evaluate(()=>window.errors)];
 await writeFile(root+'output/render_log.json',JSON.stringify({errors},null,2));
 if(errors.length)throw Error(errors.join('\n'));
 const chapters=JSON.stringify(timing.scenes.map(s=>[s.start,s.title])).replaceAll('<','\\u003c');
 const html=`<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="icon" href="data:,"><title>教学视频</title><style>body{margin:24px;background:#090f1c;color:#eff5fe;font:16px system-ui}main{max-width:1400px;margin:auto}video{width:100%;max-height:80vh}nav{display:flex;gap:10px;flex-wrap:wrap;margin:18px 0}button{background:#14243a;color:#c8e8ff;border:1px solid #354d68;border-radius:7px;padding:10px;cursor:pointer}a{color:#70e5c0;margin-right:24px}</style><main><video controls playsinline preload="metadata" src="film.mp4"></video><nav></nav><a href="film.mp4" download>视频</a><a href="captions.srt" download>字幕</a></main><script>const v=document.querySelector('video');const chapters=${chapters};for(const [t,title] of chapters){const b=document.createElement('button');b.textContent=title;b.onclick=()=>{v.currentTime=t+.5;v.play().catch(()=>{});};document.querySelector('nav').append(b);}</script></html>`;
 await writeFile(root+'output/index.html',html);
}finally{await rt.close();}
