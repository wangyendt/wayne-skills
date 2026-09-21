import {makeScene2D,Node,Txt,Line,Circle,Rect,Latex} from '@motion-canvas/2d';
import {createSignal,linear} from '@motion-canvas/core';
import {Projection3D} from '../space3d';
import timing from '../timing.json';
import captions from '../subtitles.json';
import config from '../../video.config.json';
const color={text:'#eff5fe',muted:'#92a6c1',mint:'#70e5c0',blue:'#58b9ff'};
function text(n:Node,value:any,x:number,y:number,size=28,fill=color.text){n.add(new Txt({text:value,x,y,fontSize:size,fontFamily:config.font,fill}));}
function formula(n:Node,tex:string,x:number,y:number,size=48){n.add(new Latex({tex,x,y,fontSize:size,fill:color.mint}));}
function geometry(n:Node,p:()=>number){
 n.add(new Projection3D({progress:p,position:[-320,-30]}));
 formula(n,String.raw`u=f\frac{X}{Z}`,580,-130,64);
 formula(n,String.raw`v=f\frac{Y}{Z}`,580,130,64);
 text(n,'虚拟成像平面（置于相机前方）',-330,354,23,color.muted);
}
function inverse(n:Node,p:()=>number){
 // This example uses normalized f=X=1: u=1/Z. Replace with the requested model.
 const xo=(v:number)=>-730+950*v,yo=(v:number)=>240-500*v;
 n.add(new Line({points:[[-730,-320],[-730,240],[280,240]],stroke:color.muted,lineWidth:2}));
 n.add(new Line({points:[[xo(0),yo(0)],[xo(1),yo(1)]],stroke:color.mint,lineWidth:5,end:p}));
 n.add(new Circle({x:()=>xo(p()),y:()=>yo(p()),size:20,fill:color.mint}));
 formula(n,String.raw`u`, -772,-333,32);formula(n,String.raw`Z^{-1}`,310,286,32);
 text(n,'0',-747,270,23,color.muted);text(n,'1',xo(1),278,23,color.muted);
 formula(n,String.raw`u=(fX)\,Z^{-1}`,602,-87,49);
 formula(n,String.raw`f=X=1`,602,93,36);
}
const builders=[geometry,inverse];
export default makeScene2D(function* (view){
 view.fill(config.background);
 if(timing.scenes.length!==builders.length)throw Error('Add one scene builder per entry in scenes.json');
 for(const scene of timing.scenes){
  const p=createSignal(0),root=new Node({});view.add(root);builders[scene.id-1](root,p);
  text(root,scene.title,-770,-466,29,color.muted);text(root,'教学示意',820,-466,20,color.muted);
  const cues=captions.filter(c=>c.scene===scene.id),sub=new Node({});view.add(sub);
  const now=()=>scene.start+p()*scene.duration;
  sub.add(new Rect({x:0,y:config.subtitleCenterY-config.height/2,width:config.width,height:115,fill:config.background}));
  text(sub,()=>cues.find(c=>now()>=c.start&&now()<c.end)?.text??'',0,config.subtitleCenterY-config.height/2,config.subtitleFontSize,'#ffffff');
  yield* p(1,scene.duration,linear);root.remove();sub.remove();
 }
});
