/** Author: Codex | Created: 2026-11-24 18:28:42 +08:00 | Grid backdrop, presenter and transparent template. | Modified: 2026-11-24 19:31:23 +08:00 */
import React from "react";
import {AbsoluteFill,Img,interpolate,OffthreadVideo,staticFile,useCurrentFrame,useVideoConfig} from "remotion";

type Props={presenterSrc:string;cueFrames:number[]};
const cards=[["提示词工程","把任务说清楚"],["知识库搭建","让回答有依据"],["Agent 工作流","把流程串起来"],["真实项目","验证结果能落地"]];
const text="#F0F3F7",muted="#536172",accent="#8AC8FF";

/** Sample an asymmetric lift, hold and return from the current scene frame. */
function liftAt(frame:number,cue:number){
  return interpolate(frame-cue,[0,11,23,39],[0,1,1,0],{
    extrapolateLeft:"clamp",extrapolateRight:"clamp",
    easing:[t=>1-(1-t)**3,t=>t,t=>t*t*(3-2*t)],
  });
}

/** Move through an overview, upper cards, lower cards and back, using a slow–fast–slow rail. */
function cameraAt(frame:number,duration:number){
  const stops=[0,.15,.34,.48,.67,.80,1];
  const t=frame/Math.max(1,duration-1);
  const track=(values:number[])=>interpolate(t,stops,values,{
    extrapolateLeft:"clamp",extrapolateRight:"clamp",
    easing:u=>u*u*u*(10+u*(-15+6*u)),
  });
  return `translate(${track([16,22,-10,-12,-24,-26,0])}px,${track([20,24,16,13,-28,-34,0])}px) rotate(${track([-1.65,-1.9,.85,.7,-.95,-.65,0])}deg) scale(${track([.96,.95,1.08,1.09,1.1,1.105,1])})`;
}

/** Ease a short slide into the resting layout, leaving later cues available for card lifts. */
function entranceAt(frame:number,start:number,length:number){
  return interpolate(frame,[start,start+length],[0,1],{
    extrapolateLeft:"clamp",extrapolateRight:"clamp",easing:t=>1-(1-t)**3,
  });
}

/** Compose the grid, scrolling word wall, presenter and transparent template. */
export function LayeredPresenterDemo({presenterSrc,cueFrames}:Props){
  const frame=useCurrentFrame();
  const {durationInFrames}=useVideoConfig();
  const heading=entranceAt(frame,1,14);
  const rowHeight=176;
  const scroll=(frame*1.65)%(rowHeight*2);
  return <AbsoluteFill style={{overflow:"hidden",fontFamily:'"Microsoft YaHei",sans-serif',color:text}}>
    <Img src={staticFile("scene-assets/black-grid-4x3.png")} alt="" style={{position:"absolute",inset:0,width:"100%",height:"100%"}}/>
    <AbsoluteFill aria-hidden style={{overflow:"hidden",color:"#B9C9DB",opacity:.085,pointerEvents:"none"}}>
      <div style={{position:"absolute",top:-44,left:-140,transform:`translateY(${-scroll}px)`,fontSize:116,fontWeight:800,lineHeight:`${rowHeight}px`,whiteSpace:"nowrap",letterSpacing:9}}>
        {Array.from({length:10},(_,i)=><div key={i} style={{marginLeft:i%2*240}}>{"阿祥 AI　　".repeat(5)}</div>)}
      </div>
    </AbsoluteFill>
    {presenterSrc&&<div style={{position:"absolute",right:96,bottom:177,width:210,height:280,borderRadius:22,overflow:"hidden"}}>
      <OffthreadVideo src={staticFile(presenterSrc)} style={{width:"100%",height:"100%",objectFit:"cover",objectPosition:"48% 43%"}}/>
    </div>}
    <AbsoluteFill style={{pointerEvents:"none",transformOrigin:"430px 550px",transform:cameraAt(frame,durationInFrames)}}>
      <AbsoluteFill style={{opacity:heading,transform:`translateY(${(1-heading)*22}px)`}}>
      <div style={{position:"absolute",left:96,top:112,fontSize:24,fontWeight:650,color:accent}}>能力笔记</div>
      <h1 style={{position:"absolute",left:92,top:153,fontSize:77,margin:0,lineHeight:1.12,letterSpacing:-2,fontWeight:800}}>四项能力怎么练？</h1>
      <div aria-hidden style={{position:"absolute",left:96,top:270,width:914,height:1,background:"#F0F3F744"}}/>
      </AbsoluteFill>
      {cards.map(([title,desc],i)=>{
        const enter=entranceAt(frame,4+i*3,15);
        const lift=cueFrames[i]===undefined?0:liftAt(frame,cueFrames[i]);
        return <div key={title} style={{position:"absolute",left:96,top:318+i*153,width:914,height:126,opacity:enter,transform:`translate(${(enter-1)*64}px,${(1-enter)*10-20*lift}px)`}}>
          <div style={{position:"absolute",inset:0,background:"#FFFFFF",border:"1px solid #E2E7EC",borderRadius:14,boxShadow:"0 5px 14px #00000045"}}/>
          <div aria-hidden style={{position:"absolute",inset:0,opacity:lift,borderRadius:14,boxShadow:"0 16px 30px #00000066"}}/>
          <div style={{position:"absolute",inset:0,display:"grid",gridTemplateColumns:"64px 1fr",alignItems:"center",padding:"0 28px"}}>
            <div style={{fontSize:23,fontWeight:700,color:"#34678C",fontVariantNumeric:"tabular-nums"}}>{`0${i+1}`}</div>
            <div>
              <div style={{fontSize:40,fontWeight:750,lineHeight:1.14,color:"#202630"}}>{title}</div>
              <div style={{fontSize:25,marginTop:8,lineHeight:1.2,color:muted}}>{desc}</div>
            </div>
          </div>
        </div>;
      })}
    </AbsoluteFill>
  </AbsoluteFill>;
}
