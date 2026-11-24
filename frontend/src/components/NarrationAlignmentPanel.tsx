/** Author: Codex | Created: 2026-11-24 20:22:22 +08:00 | Run and review local audio alignment against the storyboard. */
import {useEffect,useState} from "react";
import {api} from "../api";
import type {AssetRecord,NarrationAlignment,NarrationTiming} from "../types";

/** Show a source-video time range or the reason it needs review. */
function timingLabel(timing:NarrationTiming){
  if(timing.startMs==null || timing.endMs==null)return "未匹配";
  return `${(timing.startMs/1000).toFixed(2)}–${(timing.endMs/1000).toFixed(2)} 秒${timing.status==="review"?" · 待复核":""}`;
}

/** Select a registered recording, run local recognition, and show timestamps for the active scene. */
export function NarrationAlignmentPanel({projectId,sceneId,revision}:{projectId:string;sceneId:string;revision:number}){
  const [sources,setSources]=useState<{asset:AssetRecord;scope:string}[]>([]);
  const [choice,setChoice]=useState("");
  const [result,setResult]=useState<NarrationAlignment|null>(null);
  const [busy,setBusy]=useState(false);
  const [error,setError]=useState("");
  useEffect(()=>{
    let active=true;
    const scopes=[projectId,"library"];
    Promise.all(scopes.map(scope=>api.listAssets(scope))).then(lists=>{
      if(active)setSources(lists.flatMap(({assets},i)=>assets.filter(a=>["audio","video","recording"].includes(a.mediaType)).map(asset=>({asset,scope:scopes[i]}))));
    }).catch(e=>{if(active)setError(e.message)});
    api.getNarrationAlignment(projectId).then(saved=>{
      if(active){setResult(saved);if(saved)setChoice(`${saved.scope}/${saved.assetId}`)}
    }).catch(e=>{if(active)setError(e.message)});
    return ()=>{active=false};
  },[projectId]);
  const source=sources.find(s=>`${s.scope}/${s.asset.assetId}`===choice);
  const stale=result?.stale || (result && result.storyboardRevision!==revision);
  const row=result?.scenes.find(s=>s.sceneId===sceneId);
  /** Ask the local workbench to align the current script revision; keep the previous result on failure. */
  async function run(){
    if(!source || busy)return;
    setBusy(true);setError("");
    try{setResult(await api.alignNarration(projectId,source.asset.assetId,source.scope,revision))}
    catch(e){setError(e instanceof Error?e.message:String(e))}
    finally{setBusy(false)}
  }
  return <details className="mb-4 rounded-xl border border-ms-border bg-ms-panel p-3">
    <summary className="cursor-pointer font-semibold">口播时间戳</summary>
    <p className="mt-2 text-xs text-ms-muted">本地识别整段口播，再按分镜顺序匹配稿子。时间以源视频为准。</p>
    <div className="mt-2 flex flex-wrap gap-2">
      <select aria-label="口播素材" value={choice} onChange={e=>setChoice(e.target.value)} disabled={busy} className="min-w-0 rounded bg-ms-border p-2">
        <option value="">选择口播素材</option>
        {sources.map(({scope,asset})=><option value={`${scope}/${asset.assetId}`} key={`${scope}/${asset.assetId}`}>{scope==="library"?"公共素材":"项目素材"} · {asset.name}</option>)}
      </select>
      <button disabled={!source || busy} onClick={run} className="rounded bg-ms-border px-3 disabled:opacity-40">{busy?"本地识别中…":"开始对齐"}</button>
    </div>
    {!sources.length && <p className="mt-2 text-xs text-ms-muted">请先在素材库导入口播视频或音频。</p>}
    {error && <p role="alert" className="mt-2 text-sm text-red-400">{error}</p>}
    {result && <p className="mt-2 text-xs text-ms-muted">来源：{result.assetName}{stale?" · 分镜已更新，请重新对齐":""}</p>}
    {row && !stale && <div className="mt-2 text-sm"><strong>{timingLabel(row)}</strong><ul className="mt-2 space-y-1">{row.sentences.map((s,i)=><li key={i}><span className="text-ms-accent">{timingLabel(s)}</span>　{s.text}</li>)}</ul></div>}
  </details>;
}
