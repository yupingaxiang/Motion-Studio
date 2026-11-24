/** Author: Codex | Created: 2026-11-24 20:10:17 +08:00 | Scroll a filmstrip through a fixed selection window, then open the chosen image. | Modified: 2026-11-24 20:13:29 +08:00 */
import {AbsoluteFill,Easing,Img,interpolate,staticFile,useCurrentFrame,useVideoConfig} from "remotion";

type Props={srcs?:string[];selected?:number;title?:string};
export const filmReelDefaults={srcs:["fred-examples/TEXT-001.jpg","fred-examples/FLOW-001.jpg","fred-examples/COMP-001.jpg","fred-examples/DATA-001.jpg"],selected:3,title:"胶片轮播"};
const pitch=494;
const roll=Easing.bezier(.43,.02,.21,1);
const settle=Easing.bezier(.25,0,.25,1);

/** Return clamped progress for a seekable roll or settle. */
function beat(t:number,start:number,end:number,easing:(v:number)=>number){
  return interpolate(t,[start,end],[0,1],{easing,extrapolateLeft:"clamp",extrapolateRight:"clamp"});
}

/** Run a filmstrip and open the requested one-based image after a simulated click. */
export function FilmReel({srcs=filmReelDefaults.srcs,selected=filmReelDefaults.selected,title=filmReelDefaults.title}:Props){
  const {fps,durationInFrames}=useVideoConfig();
  const time=useCurrentFrame()/fps;
  const t=time/Math.max(1/fps,durationInFrames/fps)*6.6;
  const images=Array.isArray(srcs)?srcs.filter(src=>typeof src==="string"&&src.trim()):[];
  const items=images.length?images:filmReelDefaults.srcs;
  const index=Math.max(0,Math.min(items.length-1,Number.isFinite(selected)?Math.round(selected)-1:0));
  const landing=items.length===1?0:items.length+index;
  const travel=landing?((landing+.045)*beat(t,.4,3.46,roll)-.045*beat(t,3.46,3.8,settle)):0;
  const locked=beat(t,3.78,4.22,settle);
  const clickAt=4.72;
  const opening=beat(t,4.85,5.85,roll);
  const press=beat(t,clickAt,4.83,settle)-beat(t,4.83,5.02,settle);
  const ring=beat(t,clickAt,5.05,settle);
  const chrome=1-beat(t,4.87,5.42,settle);
  const lifted=t>=clickAt;
  const chosen=items[index];
  const chosenSrc=/^(?:https?:\/\/|\/)/.test(chosen)?chosen:staticFile(chosen);
  const first=Math.floor(travel)-2;
  return <AbsoluteFill style={{overflow:"hidden",color:"#faf9f6",background:"#0c0c0b",fontFamily:'"Microsoft YaHei",sans-serif'}}>
    <Img src={staticFile("scene-assets/black-grid-4x3.png")} alt="" style={{position:"absolute",width:"100%",height:"100%"}}/>
    <AbsoluteFill aria-hidden style={{opacity:.045,whiteSpace:"nowrap",fontSize:115,fontWeight:800,lineHeight:"176px",transform:`translate(-120px,${-40-time*21}px)`}}>
      {Array.from({length:9},(_,i)=><div key={i} style={{marginLeft:i%2*225}}>{"阿祥 AI　　".repeat(5)}</div>)}
    </AbsoluteFill>
    <div style={{position:"absolute",top:142,width:"100%",textAlign:"center",opacity:chrome}}>
      <div style={{fontSize:19,letterSpacing:7,color:"#bbb8af"}}>FILM REEL</div>
      <div style={{fontSize:55,fontWeight:750,marginTop:15}}>{title}</div>
    </div>
    <div style={{position:"absolute",top:335,left:0,right:0,height:388,opacity:chrome,background:"#191919",borderTop:"1px solid #3a3935",borderBottom:"1px solid #3a3935",overflow:"hidden"}}>
      {Array.from({length:6},(_,offset)=>{
        const slot=first+offset;
        const id=((slot%items.length)+items.length)%items.length;
        const media=items[id];
        const src=/^(?:https?:\/\/|\/)/.test(media)?media:staticFile(media);
        return <div key={slot} style={{position:"absolute",left:720-pitch/2,top:0,width:pitch,height:388,transform:`translateX(${(slot-travel)*pitch}px)`}}>
          {[18,355].map(y=><div key={y} style={{position:"absolute",top:y,left:22,right:22,display:"flex",justifyContent:"space-between"}}>{Array.from({length:9},(_,i)=><div key={i} style={{width:25,height:13,borderRadius:3,background:"#090909",boxShadow:"inset 0 0 0 1px #3d3b36"}}/>)}</div>)}
          <div style={{position:"absolute",inset:"49px 14px",background:"#101010",border:"1px solid #43423d",borderRadius:8,overflow:"hidden"}}>{(!lifted||slot!==landing)&&<Img src={src} alt="" style={{width:"100%",height:"100%",objectFit:"contain"}}/>}</div>
        </div>;
      })}
      <AbsoluteFill style={{background:"linear-gradient(90deg,#090909 0%,#090909a6 13%,#09090970 33%,transparent 33%,transparent 67%,#09090970 67%,#090909a6 87%,#090909 100%)"}}/>
    </div>
    <div style={{position:"absolute",left:478,top:371,opacity:chrome,width:484,height:316,borderRadius:11,boxSizing:"border-box",border:`${3+locked}px solid #f9f7ee`,boxShadow:`0 0 ${14+24*locked}px rgba(249,247,238,${.08+.12*locked})`,pointerEvents:"none"}}/>
    <div aria-hidden style={{position:"absolute",left:710,top:345,opacity:chrome,width:0,height:0,borderLeft:"10px solid transparent",borderRight:"10px solid transparent",borderTop:"12px solid #faf9f6"}}/>
    <div style={{position:"absolute",top:772,left:0,right:0,textAlign:"center",fontSize:22,letterSpacing:4,opacity:locked*chrome,transform:`translateY(${10*(1-locked)}px)`}}>已选中　{String(index+1).padStart(2,"0")} / {String(items.length).padStart(2,"0")}</div>
    {lifted&&<div style={{position:"absolute",left:487,top:384,width:466,height:290,boxSizing:"border-box",border:"1px solid #43423d",borderRadius:8,overflow:"hidden",background:"#101010",boxShadow:`0 ${16*opening}px ${38*opening}px #0009`,transform:`translateY(${11*opening}px) scale(${1+1.38*opening-.035*press})`}}>
      <Img src={chosenSrc} alt="选中的素材" style={{width:"100%",height:"100%",objectFit:"contain"}}/>
    </div>}
    {t>=4.48&&t<5.11&&<div aria-hidden style={{position:"absolute",left:868,top:582,pointerEvents:"none",opacity:beat(t,4.48,4.63,settle)*(1-beat(t,4.96,5.11,settle))}}>
      {t>=clickAt&&<div style={{position:"absolute",left:-20,top:-20,width:40,height:40,border:"2px solid #fff",borderRadius:"50%",opacity:1-ring,transform:`scale(${.45+1.25*ring})`}}/>}
      <svg width="38" height="43" viewBox="0 0 38 43" style={{transform:`translate(${18*(1-beat(t,4.48,clickAt,settle))}px,${12*(1-beat(t,4.48,clickAt,settle))}px) scale(${1-.12*press})`,transformOrigin:"top left"}}><path d="M2 2v32l9-8 6 14 6-3-6-14h13z" fill="#fff" stroke="#212121" strokeWidth="2" strokeLinejoin="round"/></svg>
    </div>}
  </AbsoluteFill>;
}
