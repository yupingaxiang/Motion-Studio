/** Author: Codex | Created: 2026-11-24 20:03:00 +08:00 | Showcase a replaceable image or muted clip in a moving white frame. | Modified: 2026-11-24 20:06:59 +08:00 */
import {AbsoluteFill,Easing,Img,interpolate,OffthreadVideo,Sequence,staticFile,useCurrentFrame,useVideoConfig} from "remotion";

type Props={mediaSrc?:string;mediaType?:string;title?:string;caption?:string;focusX?:number;focusY?:number;focusWidth?:number;focusHeight?:number};
export const assetShowcaseDefaults={mediaSrc:"fred-examples/FLOW-001.jpg",mediaType:"image",title:"画面里的素材",caption:"示例 · Motion Studio 项目素材"};
const glide=Easing.bezier(.38,0,.22,1);

/** Map an interval in seconds to eased progress, clamped for frame seeking. */
function progress(time:number,start:number,end:number){
  return interpolate(time,[start,end],[0,1],{extrapolateLeft:"clamp",extrapolateRight:"clamp",easing:glide});
}

/** Display an asset with an optional spotlight in display-window percentages. Video stays muted. */
export function AssetShowcase({mediaSrc=assetShowcaseDefaults.mediaSrc,mediaType=assetShowcaseDefaults.mediaType,title=assetShowcaseDefaults.title,caption=assetShowcaseDefaults.caption,focusX=0,focusY=0,focusWidth=0,focusHeight=0}:Props){
  const frame=useCurrentFrame();
  const {fps,durationInFrames}=useVideoConfig();
  const time=frame/fps;
  const exitAt=Math.min(4.55,Math.max(.95,durationInFrames/fps-.65));
  const enter=progress(time,0,.83);
  const camera=progress(time,.85,exitAt);
  const exit=progress(time,exitAt,exitAt+.58);
  const hasFocus=[focusX,focusY,focusWidth,focusHeight].every(Number.isFinite)&&focusX>=0&&focusY>=0&&focusWidth>0&&focusHeight>0&&focusX+focusWidth<=100&&focusY+focusHeight<=100;
  const focus=hasFocus&&exitAt>3.2?progress(time,1.35,2.15)-progress(time,exitAt-.7,exitAt):0;
  const zoom=hasFocus?1+Math.min(.48,Math.max(0,70/Math.max(focusWidth,focusHeight)-1))*focus:1;
  const centerX=hasFocus?focusX+focusWidth/2:50;
  const centerY=hasFocus?focusY+focusHeight/2:50;
  const panX=Math.max(-(zoom-1)*50,Math.min((zoom-1)*50,(50-centerX)*zoom*focus));
  const panY=Math.max(-(zoom-1)*50,Math.min((zoom-1)*50,(50-centerY)*zoom*focus));
  const videoStart=Math.round(.83*fps);
  const media=mediaSrc || assetShowcaseDefaults.mediaSrc;
  const src=/^(?:https?:\/\/|\/)/.test(media)?media:staticFile(media);
  const video=Boolean(mediaSrc)&&mediaType==="video";
  const fit={width:"100%",height:"100%",objectFit:"contain" as const};
  return <AbsoluteFill style={{background:"#0c0c0b",color:"#f7f6f3",fontFamily:'"Microsoft YaHei",sans-serif',overflow:"hidden"}}>
    <Img src={staticFile("scene-assets/black-grid-4x3.png")} alt="" style={{position:"absolute",width:"100%",height:"100%"}}/>
    <AbsoluteFill aria-hidden style={{opacity:.055,whiteSpace:"nowrap",fontSize:115,fontWeight:800,lineHeight:"176px",transform:`translate(-120px,${-40-time*21}px)`}}>
      {Array.from({length:9},(_,i)=><div key={i} style={{marginLeft:i%2*225}}>{"阿祥 AI　　".repeat(5)}</div>)}
    </AbsoluteFill>
    <div style={{position:"absolute",left:146,top:104,opacity:enter*(1-exit),transform:`translateY(${18*(1-enter)}px)`}}>
      <div style={{fontSize:21,letterSpacing:4,color:"#c6c4bf"}}>素材展示</div>
      <div style={{fontSize:56,fontWeight:750,marginTop:13}}>{title}</div>
    </div>
    <div style={{position:"absolute",left:146,top:258,width:1148,height:700,boxSizing:"border-box",padding:18,borderRadius:24,background:"#faf9f6",color:"#20201f",boxShadow:"0 26px 70px #0009",opacity:enter*(1-exit),transform:`translate(${88*(1-enter)-58*exit-12*camera}px,${24*(1-enter)-8*camera}px) scale(${.97+.03*enter+.028*camera-.02*exit})`}}>
      <div style={{position:"relative",height:608,background:"#151514",borderRadius:12,overflow:"hidden"}}>
        <div style={{position:"absolute",inset:0,transform:`translate(${panX}%,${panY}%) scale(${zoom})`}}>
          {video?<Sequence from={videoStart} premountFor={videoStart}><OffthreadVideo src={src} muted style={fit}/></Sequence>:<Img src={src} alt={title} style={fit}/>}
          {focus>0&&<div aria-hidden style={{position:"absolute",left:`${focusX}%`,top:`${focusY}%`,width:`${focusWidth}%`,height:`${focusHeight}%`,boxShadow:"0 0 0 1600px #0007",outline:"1px solid #ffffff80",borderRadius:5,opacity:focus,pointerEvents:"none"}}/>}
        </div>
      </div>
      <div style={{margin:"16px 7px 0",fontSize:23,overflow:"hidden",whiteSpace:"nowrap",textOverflow:"ellipsis"}}>{caption}</div>
    </div>
  </AbsoluteFill>;
}
