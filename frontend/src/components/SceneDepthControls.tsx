/** Author: Codex | Created: 2026-11-23 23:21:31 +08:00 | Scene depth and timed focus controls. */
import type {FocusCue,SceneDepth} from "../../../remotion/src/components/elementMotionMath.mjs";

type Props={depth:SceneDepth;cues:FocusCue[];selected:string;labels:{id:string;label:string}[];disabled:boolean;playheadMs:number;startMs:number;endMs:number;onChange:(depth:SceneDepth,cues:FocusCue[])=>void;onSeek:(ms:number)=>void};

/** Assign depth to the selected element and edit focus cues at the current preview time. */
export function SceneDepthControls({depth,cues,selected,labels,disabled,playheadMs,startMs,endMs,onChange,onSeek}:Props){
  const eligible=!!selected&&selected!=="presenter";
  const canCue=playheadMs>=startMs&&playheadMs+400<=endMs&&(cues.length<100||cues.some(c=>c.atMs===playheadMs));
  /** Update a layer and clear cues that referred to it when it is removed. */
  const setDepth=(value:SceneDepth[string]|"")=>{
    const next={...depth};
    if(value)next[selected]=value;
    else delete next[selected];
    onChange(next,value?cues:cues.filter(c=>c.target!==selected));
  };
  /** Store a cue at the playhead, replacing any cue at the same time. */
  const setCue=(target:string|null)=>onChange(depth,[...cues.filter(c=>c.atMs!==playheadMs),{atMs:playheadMs,target}].sort((a,b)=>a.atMs-b.atMs));
  return <fieldset disabled={disabled}>
    <legend>景深与焦点</legend>
    <label className="editor-field"><span>当前元素景深</span><select disabled={!eligible} value={depth[selected]??""} onChange={e=>setDepth(e.target.value as SceneDepth[string]|"")}>
      <option value="">不参与分层</option><option value="near">近景</option><option value="middle">中景</option><option value="far">远景</option>
    </select></label>
    <p>把进度条移到口播提到该元素的位置，再设置焦点。切换需留出 0.4 秒，人物小窗不参与。</p>
    <button type="button" disabled={!canCue||!eligible||!depth[selected]} onClick={()=>setCue(selected)}>在当前帧聚焦</button>
    <button type="button" disabled={!canCue||!cues.some(c=>c.target&&c.atMs<playheadMs)} onClick={()=>setCue(null)}>在当前帧恢复全览</button>
    {cues.length>0&&<ul aria-label="焦点时间点">{cues.map(c=><li key={c.atMs}>
      <button type="button" onClick={()=>onSeek(c.atMs)}>{(c.atMs/1000).toFixed(2)} 秒 · {c.target?(labels.find(el=>el.id===c.target)?.label??c.target):"恢复全览"}</button>
      <button type="button" aria-label={`移除 ${(c.atMs/1000).toFixed(2)} 秒焦点`} onClick={()=>onChange(depth,cues.filter(item=>item!==c))}>移除</button>
    </li>)}</ul>}
  </fieldset>;
}
