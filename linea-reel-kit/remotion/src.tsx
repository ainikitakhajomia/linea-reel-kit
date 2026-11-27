// Optional backend; install/use only under an existing eligible Remotion license.
// The default toolkit renderer does not depend on Remotion.
import React,{useLayoutEffect,useRef} from 'react';
import {registerRoot,Composition,AbsoluteFill,OffthreadVideo,Img,staticFile,useCurrentFrame,useVideoConfig} from 'remotion';
import {drawEffect,drawCaptions,defaultBrand} from '../src/effects.mjs';
type Job={width:number;height:number;fps:number;duration:number;brand?:Record<string,string>;video?:string;foregroundFrames?:string;walkthrough?:string;effects?:Array<{id:string;start:number;duration:number;[key:string]:unknown}>;captions?:unknown[]};
const Reel=({job}:{job:Job})=>{
 const canvas=useRef<HTMLCanvasElement>(null),frame=useCurrentFrame(),{fps,width,height}=useVideoConfig(),time=frame/fps;
 useLayoutEffect(()=>{const ctx=canvas.current!.getContext('2d')!;ctx.clearRect(0,0,width,height);ctx.save();ctx.scale(width/720,height/1280);for(const e of job.effects||[])if(time>=e.start&&time<e.start+e.duration)drawEffect(ctx,e.id,time-e.start,e,{...defaultBrand,...job.brand});drawCaptions(ctx,job.captions||[],time,job.brand);ctx.restore();},[frame,job,width,height,fps]);
 return <AbsoluteFill style={{background:job.brand?.background||defaultBrand.background}}>
 {job.video?<OffthreadVideo src={staticFile(job.video)} style={{width:'100%',height:'100%',objectFit:'cover'}}/>:null}
 {job.walkthrough?<OffthreadVideo muted src={staticFile(job.walkthrough)} style={{position:'absolute',left:'5%',top:'20%',width:'90%',height:'38%',objectFit:'contain'}}/>:null}
 <canvas ref={canvas} width={width} height={height} style={{position:'absolute',width:'100%',height:'100%'}}/>
 {job.foregroundFrames?<Img src={staticFile(job.foregroundFrames.replace('%06d',String(frame).padStart(6,'0')))} style={{position:'absolute',width:'100%',height:'100%'}}/>:null}
 </AbsoluteFill>;
};
const Root=()=> <Composition id="Reel" component={Reel} width={720} height={1280} fps={30} durationInFrames={90} defaultProps={{job:{width:720,height:1280,fps:30,duration:3,effects:[{id:'kinetic-hook',start:0,duration:3,text:'Meer tijd. Meer impact.'}]}}} calculateMetadata={({props})=>({width:props.job.width,height:props.job.height,fps:props.job.fps,durationInFrames:Math.ceil(props.job.duration*props.job.fps)})}/>;
registerRoot(Root);
