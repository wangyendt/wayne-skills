import {Node,NodeProps} from '@motion-canvas/2d';
import {BBox} from '@motion-canvas/core';
import * as THREE from 'three';
let shared:THREE.WebGLRenderer;
/** Pinhole projection on a virtual plane in front of the camera; all display axes share one scale. */
export class Projection3D extends Node {
 private world=new THREE.Scene();
 private camera=new THREE.PerspectiveCamera(38,1160/730,.1,100);
 private point=new THREE.Mesh(new THREE.SphereGeometry(.10,24,16),new THREE.MeshBasicMaterial({color:0x70e5c0}));
 private projected=new THREE.Mesh(new THREE.SphereGeometry(.08,24,16),new THREE.MeshBasicMaterial({color:0xffb267}));
 private ray=new THREE.Line(new THREE.BufferGeometry(),new THREE.LineBasicMaterial({color:0x58b9ff}));
 private progress:()=>number;
 constructor(props:NodeProps & {progress:()=>number}) {
  const {progress,...rest}=props;super(rest);this.progress=progress;
  this.world.add(new THREE.GridHelper(10,10,0x39516f,0x23354d));
  this.world.add(new THREE.AxesHelper(3));
  this.world.add(this.point,this.projected,this.ray);
  const plane=new THREE.Mesh(new THREE.PlaneGeometry(3,2.4),new THREE.MeshBasicMaterial({color:0x58b9ff,transparent:true,opacity:.16,side:THREE.DoubleSide,depthWrite:false}));
  plane.position.z=1;this.world.add(plane);
  const outline=new THREE.LineSegments(new THREE.EdgesGeometry(plane.geometry),new THREE.LineBasicMaterial({color:0x58b9ff}));
  outline.position.copy(plane.position);this.world.add(outline);
  this.world.add(new THREE.Mesh(new THREE.BoxGeometry(.3,.3,.3),new THREE.MeshBasicMaterial({color:0xb9a0ff})));
 }
 protected getCacheBBox(){return new BBox(-580,-365,1160,730);}
 protected draw(ctx:CanvasRenderingContext2D){
  const p=this.progress(),z=5-2*p;
  this.point.position.set(1,.8,z);
  this.projected.position.set(1/z,.8/z,1);
  const positions=new Float32Array([0,0,0,1,.8,z]);
  this.ray.geometry.setAttribute('position',new THREE.BufferAttribute(positions,3));
  this.camera.position.set(7,5,-6);this.camera.lookAt(0,.4,2);
  if(!shared){shared=new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});shared.setClearColor(0x090f1c);shared.setSize(1160,730);}
  shared.render(this.world,this.camera);ctx.drawImage(shared.domElement,-580,-365,1160,730);this.drawChildren(ctx);
 }
}
