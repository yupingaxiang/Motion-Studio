/** Author: Codex | Created: 2026-11-24 19:34:47 +08:00 | Reusable screenshot focus with an anchored spotlight. | Modified: 2026-11-24 19:43:59 +08:00 */
import React from "react";
import {AbsoluteFill,Easing,Img,interpolate,OffthreadVideo,staticFile,useCurrentFrame,useVideoConfig} from "remotion";

type Props={presenterSrc?:string;imageSrc?:string;title?:string;targetX?:number;targetY?:number;targetWidth?:number;targetHeight?:number};
const sampleBox={x:574,y:188,w:240,h:110};
export const screenshotFocusDefaults={imageSrc:"",title:"这条数据怎么看？",targetX:58,targetY:33,targetWidth:24,targetHeight:19,presenterSrc:""};
const pushCurve=Easing.bezier(.42,0,.24,1);
const pullCurve=Easing.bezier(.29,0,.48,1);

/** Sample an eased frame interval with fixed endpoints for seeking and export. */
function beat(frame:number,start:number,end:number,easing=(t:number)=>t*t*(3-2*t)){
  return interpolate(frame,[start,end],[0,1],{extrapolateLeft:"clamp",extrapolateRight:"clamp",easing});
}

/** Demonstrate a side entrance, anchored camera move, spotlight hold and return. */
export function ScreenshotFocus({presenterSrc="",imageSrc="",title=screenshotFocusDefaults.title,targetX:tx=58,targetY:ty=33,targetWidth=24,targetHeight=19}:Props){
  const w=Math.min(75,Math.max(5,targetWidth))*9.92;
  const h=Math.min(75,Math.max(5,targetHeight))*5.7;
  const box=imageSrc?{x:Math.min(992-w,Math.max(0,tx*9.92)),y:Math.min(570-h,Math.max(0,ty*5.7)),w,h}:sampleBox;
  const {fps}=useVideoConfig();
  const frame=useCurrentFrame()*30/fps;
  const enter=beat(frame,3,32);
  const push=beat(frame,47,91,pushCurve)-beat(frame,146,180,pullCurve);
  const drift=beat(frame,77,160);
  const spot=beat(frame,61,92)-beat(frame,141,172);
  const targetX=box.x+box.w/2,targetY=box.y+box.h/2;
  const gain=Math.min(.745,Math.max(.08,Math.min(912/box.w,490/box.h)-1));
  const scale=1+gain*(.94+.06*drift)*push;
  const x=(496-targetX)*push-110*(1-enter);
  const y=(252-targetY)*push;
  return <AbsoluteFill style={{overflow:"hidden",background:"#0c0c0b",color:"#F0F3F7",fontFamily:'"Microsoft YaHei",sans-serif'}}>
    <Img src={staticFile("scene-assets/black-grid-4x3.png")} alt="" style={{position:"absolute",inset:0,width:"100%",height:"100%"}}/>
    <AbsoluteFill aria-hidden style={{overflow:"hidden",opacity:.065,pointerEvents:"none"}}>
      <div style={{position:"absolute",top:-45,left:-140,fontSize:116,fontWeight:800,lineHeight:"176px",whiteSpace:"nowrap",transform:`translateY(${-(frame*1.65%352)}px)`}}>
        {Array.from({length:10},(_,i)=><div key={i} style={{marginLeft:i%2*240}}>{"阿祥 AI　　".repeat(5)}</div>)}
      </div>
    </AbsoluteFill>
    {presenterSrc&&<div style={{position:"absolute",right:82,bottom:130,width:210,height:280,borderRadius:22,overflow:"hidden"}}><OffthreadVideo muted src={staticFile(presenterSrc)} style={{width:"100%",height:"100%",objectFit:"cover",objectPosition:"48% 43%"}}/></div>}
    <AbsoluteFill style={{pointerEvents:"none"}}>
      <div style={{position:"absolute",top:121,left:96,color:"#8AC8FF",fontSize:23}}>界面示意</div>
      <h1 style={{position:"absolute",top:156,left:92,margin:0,fontSize:72,letterSpacing:-2}}>{title}</h1>
      <div style={{position:"absolute",top:300,left:96,width:992,height:570,overflow:"hidden",borderRadius:18,opacity:enter}}>
        <div style={{position:"absolute",inset:0,transformOrigin:`${targetX}px ${targetY}px`,transform:`translate(${x}px,${y}px) rotate(${-.9*push}deg) scale(${scale})`,background:"#F7F9FC",color:"#172C43"}}>
          {imageSrc?<Img src={staticFile(imageSrc)} alt="" style={{position:"absolute",inset:0,width:"100%",height:"100%",objectFit:"contain"}}/>:<>
          <div style={{height:68,display:"flex",alignItems:"center",padding:"0 40px",borderBottom:"1px solid #DAE3ED",fontSize:25,fontWeight:750}}>内容表现概览 <span style={{marginLeft:"auto",fontSize:17,color:"#63788E"}}>示例数据</span></div>
          <div style={{position:"absolute",top:110,left:53,fontSize:26,fontWeight:700}}>最近七天</div>
          <svg viewBox="0 0 450 290" style={{position:"absolute",top:176,left:50,width:450,height:290}} aria-hidden>
            {[32,96,160,224].map(n=><path key={n} d={`M0 ${n}H450`} stroke="#DCE5EE"/>)}
            <path d="M0 227 72 190 144 208 216 150 288 167 360 106 448 71" fill="none" stroke="#477CB4" strokeWidth="6" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          <div style={{position:"absolute",left:box.x,top:box.y,width:box.w,height:box.h,boxSizing:"border-box",borderRadius:11,background:"#E3EFFB",padding:"13px 20px"}}><div style={{fontSize:19,color:"#3E607F"}}>完播率</div><div style={{fontSize:46,fontWeight:850,lineHeight:1.2}}>42.8%</div></div>
          <div style={{position:"absolute",left:574,top:348,color:"#61788E",fontSize:20}}>近七天发布 · 4 条</div>
          </>}
          <svg viewBox="0 0 992 570" style={{position:"absolute",inset:0,opacity:spot,pointerEvents:"none"}} aria-hidden>
            <defs><mask id="screenshot-spot"><rect width="992" height="570" fill="white"/><rect x={box.x-8} y={box.y-8} width={box.w+16} height={box.h+16} rx="18" fill="black"/></mask></defs>
            <rect width="992" height="570" fill="#122438" fillOpacity=".57" mask="url(#screenshot-spot)"/>
            <rect x={box.x-8} y={box.y-8} width={box.w+16} height={box.h+16} rx="18" fill="none" stroke="#4388CF" strokeWidth="3"/>
          </svg>
        </div>
      </div>
    </AbsoluteFill>
  </AbsoluteFill>;
}
