import assert from 'node:assert/strict';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {execFileSync} from 'node:child_process';
import {runtime,root} from './runtime.mjs';
const json=async p=>JSON.parse(await readFile(root+p,'utf8'));
const config=await json('video.config.json'),timing=await json('src/timing.json'),cues=await json('src/subtitles.json'),audio=await json('audio/status.json');
const allowSilent=process.argv.includes('--allow-silent');
assert(audio.narrated||allowSilent,'Narration is still a silent smoke-test track. Run prepare_audio.py first.');
assert(timing.scenes.length>0&&cues.length>0);
let previous=0;
for(const s of timing.scenes){assert(Math.abs(s.start-previous)<.001);assert(s.duration>0);previous=s.start+s.duration;}
assert(Math.abs(previous-timing.total_duration)<.001);
for(let i=0;i<cues.length;i++){
 const c=cues[i];assert(c.start>=0&&c.end>c.start&&c.end<=timing.total_duration);assert(c.text.trim());
 assert(i===0||c.start>=cues[i-1].end,'Caption overlap');
 const scene=timing.scenes.find(s=>s.id===c.scene);assert(scene&&c.start>=scene.start&&c.end<=scene.start+scene.duration+.001);
}
const media=JSON.parse(execFileSync('ffprobe',['-v','error','-show_streams','-show_format','-of','json',root+'output/film.mp4'],{encoding:'utf8'}));
const video=media.streams.find(s=>s.codec_type==='video');
assert(video&&video.width===config.width&&video.height===config.height);
const [num,den]=video.avg_frame_rate.split('/').map(Number);assert(Math.abs(num/den-config.fps)<.01);
assert(Math.abs(Number(media.format.duration)-timing.total_duration)<.2);
assert(media.streams.some(s=>s.codec_type==='audio'));
assert(!media.streams.some(s=>s.codec_type==='subtitle'),'Avoid duplicate soft subtitles');
const rt=await runtime();
try{
 const page=await rt.browser.newPage({viewport:{width:1500,height:1100}});
 await page.goto(rt.url+'/output/index.html');
 await page.waitForFunction(()=>document.querySelector('video').readyState>=2);
 await mkdir(root+'output/verification',{recursive:true});
 const results=[];
 for(let i=0;i<cues.length;i++){
  const cue=cues[i];
  const result=await page.evaluate(async({cue,config})=>{
   const v=document.querySelector('video');
   await new Promise(resolve=>{v.addEventListener('seeked',resolve,{once:true});v.currentTime=(cue.start+cue.end)/2;});
   await new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)));
   const canvas=document.createElement('canvas');canvas.width=v.videoWidth;canvas.height=v.videoHeight;
   const ctx=canvas.getContext('2d');ctx.drawImage(v,0,0);
   const data=ctx.getImageData(80,config.subtitleCenterY-40,config.width-160,80).data;
   let white=0;for(let j=0;j<data.length;j+=4)if(data[j]>205&&data[j+1]>205&&data[j+2]>205)white++;
   ctx.font=config.subtitleFontSize+'px '+config.font;
   return{whitePixels:white,width:ctx.measureText(cue.text).width,textTracks:v.textTracks.length,png:canvas.toDataURL('image/png')};
  },{cue,config});
  results.push({scene:cue.scene,text:cue.text,whitePixels:result.whitePixels,textWidth:result.width,passed:result.whitePixels>100&&result.width<=config.subtitleSafeWidth&&result.textTracks===0});
  if(i===cues.length-1||cues[i+1].scene!==cue.scene)await writeFile(root+`output/verification/${cue.scene}.png`,Buffer.from(result.png.split(',')[1],'base64'));
 }
 const report={media,mode:audio.narrated?'narrated':'silent-smoke-test',captions:results,allPassed:results.every(x=>x.passed),limits:'White pixel sampling proves caption-region ink, not semantics or exact audio synchronization. Manual visual/listening review is still required.'};
 await writeFile(root+'output/validation.json',JSON.stringify(report,null,2));
 assert(report.allPassed,'Caption visibility or width check failed');
 console.log(JSON.stringify({passed:true,mode:report.mode,captions:results.length,duration:media.format.duration}));
}finally{await rt.close();}
