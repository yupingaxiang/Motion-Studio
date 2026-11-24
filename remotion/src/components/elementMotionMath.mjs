/** Author: Codex | Created: 2026-11-22 00:30:00 +08:00 | Deterministic per-element animation and focus shared by preview/export. | Modified: 2026-11-24 18:12:08 +08:00 */
export const MOTION_PRESETS=[{id:"none",label:"无附加动效"},{id:"fade-up",label:"淡入上移"},{id:"slide-left",label:"从左滑入"},{id:"slide-right",label:"从右滑入"},{id:"pop-in",label:"缩放弹入"},{id:"mask-reveal",label:"遮罩展开"},{id:"slow-zoom",label:"缓慢推近"},{id:"settle-zoom",label:"由大到小落定"},{id:"pulse",label:"重点脉冲"},{id:"keyframes",label:"自定义起点 → 终点"}];
/** Provide restrained preset-specific scale endpoints without overriding explicit user settings. */
export function presetScales(preset){return preset==="slow-zoom"?[1,1.12]:preset==="settle-zoom"?[1.2,1]:preset==="pulse"?[1,1.12]:preset==="pop-in"?[.72,1]:[1,1]}
/** Clamp and ease normalized time; backOut overshoots spatial values while opacity stays bounded. */
function eased(t,name){if(name==="linear")return t;if(name==="ease-out")return 1-Math.pow(1-t,3);if(name==="back-out"){const c=1.70158;return 1+(c+1)*Math.pow(t-1,3)+c*Math.pow(t-1,2)}return t*t*t*(t*(t*6-15)+10)}
/** Evaluate any frame in isolation: entrances hide before their start, zooms/pulses remain visible. */
export function motionAt(config={},timeMs=0){const {preset="none",startMs=0,durationMs=600,easing="smooth",distance=60,fromX=0,fromY=0,toX=0,toY=0}=config;const t=Math.max(0,Math.min(1,(timeMs-startMs)/Math.max(1,durationMs)));const p=eased(t,easing);const a=Math.max(0,Math.min(1,p));const scales=presetScales(preset);const s0=config.fromScale??scales[0],s1=config.toScale??scales[1];const out={x:0,y:0,scale:1,opacity:1,reveal:1};if(preset==="fade-up"){out.y=distance*(1-p);out.opacity=a}else if(preset==="slide-left"||preset==="slide-right"){out.x=(preset==="slide-left"?-1:1)*distance*(1-p);out.opacity=a}else if(preset==="pop-in"||preset==="settle-zoom"){out.scale=s0+(s1-s0)*p;out.opacity=a}else if(preset==="slow-zoom"){out.scale=s0+(s1-s0)*p}else if(preset==="pulse"){out.scale=s0+(s1-s0)*Math.sin(Math.PI*a)}else if(preset==="mask-reveal"){out.reveal=a}else if(preset==="keyframes"){out.x=fromX+(toX-fromX)*p;out.y=fromY+(toY-fromY)*p;out.scale=s0+(s1-s0)*p}out.scale=Math.max(.05,Math.min(4,out.scale));return out}
/** Blend successive focus changes without resetting the velocity of a transition already underway. */
function focusWeights(cues,timeMs){
  const weights=Object.create(null);
  let previous=null;
  for(const {atMs,target} of cues){
    if(atMs>timeMs)break;
    const t=Math.min(1,(timeMs-atMs)/400);
    const p=t*t*(3-2*t);
    if(previous)weights[previous]=(weights[previous]??0)-p;
    if(target)weights[target]=(weights[target]??0)+p;
    previous=target;
  }
  return weights;
}
/** Compose independent CSS properties with native transforms/opacity/blur, never replacing those animations. */
export function elementMotionCss(offsets={},animations={},timeMs=0,unit=1,protectedIds=[],depth={},focusCues=[]){const weights=focusWeights(focusCues,timeMs);const focused=Math.min(1,Object.values(weights).reduce((a,b)=>a+b,0));const background=focused?`[data-scene-background]{filter:blur(${4*focused/unit}px) brightness(${1-.25*focused});scale:${1+.025*focused};}`:"";return background+[...new Set([...Object.keys(offsets),...Object.keys(animations),...Object.keys(depth)])].filter(id=>/^[a-z][a-z0-9-]{0,63}$/.test(id)&&!protectedIds.includes(id)).map(id=>{const pos=offsets[id]??{x:0,y:0};if(!Number.isFinite(pos.x)||!Number.isFinite(pos.y))return "";const cfg=animations[id];const m=motionAt(cfg,timeMs);const layer=depth[id];const weight=weights[id]??0;const retreat=layer?Math.max(0,focused-weight):0;let css=`translate:${(pos.x+m.x)/unit}px ${(pos.y+m.y)/unit}px;`;if(cfg&&cfg.preset!=="none"){const alpha=Math.max(0,Math.min(1,m.opacity));if(alpha<1)css+=`mask-image:linear-gradient(rgba(0,0,0,${alpha}),rgba(0,0,0,${alpha}));-webkit-mask-image:linear-gradient(rgba(0,0,0,${alpha}),rgba(0,0,0,${alpha}));`;if(cfg.preset==="mask-reveal")css+=`clip-path:inset(0 ${(1-m.reveal)*100}% 0 0);`}if(layer||cfg&&cfg.preset!=="none")css+=`scale:${m.scale*(1+.075*weight-.035*retreat)};transform-origin:center center;`;if(layer){css+=`z-index:${layer==="near"?3:layer==="middle"?2:1};`;if(retreat>0)css+=`filter:blur(${(layer==="far"?2.5:layer==="middle"?1.8:1.3)*retreat/unit}px) opacity(${1-(layer==="far"?.32:layer==="middle"?.26:.20)*retreat});`;}return `[data-motion-element="${id}"]{${css}}`}).join("")}
