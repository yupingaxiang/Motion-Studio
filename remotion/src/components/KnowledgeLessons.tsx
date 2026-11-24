/** Author: Codex | Created: 2026-11-22 22:50:00 +08:00 | Semantic lesson animations: parallel skills, prompt execution, and grounded retrieval. | Modified: 2026-11-24 18:12:08 +08:00 */
import React from "react";
import {AbsoluteFill,Easing,interpolate,useCurrentFrame} from "remotion";

const ink="#202027",accent="#8554e8",muted="#777580";
const font='"Microsoft YaHei",sans-serif';
/** Ease a frame-timed entrance into place without wall-clock animation. */
const progress=(frame:number,start:number,length=18)=>interpolate(frame,[start,start+length],[0,1],{extrapolateLeft:"clamp",extrapolateRight:"clamp",easing:Easing.out(Easing.cubic)});
/** A reusable surface whose stable ID permits individual editing and animation. */
const Surface:React.FC<{id:string;x:number;y:number;width:number;height:number;p?:number;children:React.ReactNode}>=({id,x,y,width,height,p=1,children})=><div data-motion-element={id} data-motion-label={id} style={{position:"absolute",left:x,top:y,width,height,padding:28,boxSizing:"border-box",background:"white",borderRadius:26,boxShadow:"0 16px 50px #2920390c",border:"1px solid #ebe8f0",opacity:Math.min(1,p*1.35),transform:`translateY(${(1-p)*16}px)`}}>{children}</div>;
/** Shared neutral lesson canvas, with a clear original-schematic identity. */
const Canvas:React.FC<{title:string;children:React.ReactNode}>=({title,children})=><AbsoluteFill data-motion-canvas="true" style={{background:"#f8f7fb",color:ink,fontFamily:font}}><div style={{position:"absolute",left:84,top:77,color:accent,fontSize:20,letterSpacing:4}}>AI / FIELD NOTES</div><h1 data-motion-element="title" style={{position:"absolute",left:84,top:113,fontSize:54,lineHeight:1.4,margin:0,maxWidth:1200}}>{title}</h1>{children}<div style={{position:"absolute",left:84,bottom:56,fontSize:17,color:muted,letterSpacing:2}}>MOTION STUDIO · 原理示意</div></AbsoluteFill>;

export interface SkillMatrixProps {title?:string;labels?:string[];details?:string[];cueFrames?:number[]}
/** Present four peer capabilities as a matrix, with no arrows or implied dependency. */
export const SkillMatrix:React.FC<SkillMatrixProps>=({title="四项能力，逐项练起来",labels=["提示词工程","知识库搭建","Agent 工作流","真实项目"],details=["把任务说清楚","让回答有依据","把工具串起来","把方案跑起来"],cueFrames=[15,40,65,90]})=>{const f=useCurrentFrame();return <Canvas title={title}>{labels.slice(0,4).map((label,i)=><Surface key={i} id={`card-${i}`} x={84+i%2*495} y={292+Math.floor(i/2)*290} width={461} height={250} p={progress(f,cueFrames[i]??i*25)}><div style={{fontSize:19,color:accent,letterSpacing:3}}>CAPABILITY {String(i+1).padStart(2,"0")}</div><div style={{fontSize:38,fontWeight:750,marginTop:25}}>{label}</div><div style={{fontSize:25,color:muted,marginTop:18}}>{details[i]}</div></Surface>)}</Canvas>};

export interface PromptLessonProps {title?:string;prompt?:string;requirements?:string[];result?:string[];cueFrames?:number[]}
/** Animate task input, understood constraints, and a result that visibly satisfies those constraints. */
export const PromptLesson:React.FC<PromptLessonProps>=({title="提示词 → 理解要求 → 按要求输出",prompt="把今天的施工记录整理成日报",requirements=["按完成 / 问题 / 计划分组","每组一句，保留真实信息"],result=["完成：3号楼基础验收","问题：材料到场延迟","计划：明日复核施工进度"],cueFrames=[12,70,135,205]})=>{const f=useCurrentFrame();const [a,b,c,d]=cueFrames;const typed=prompt.slice(0,Math.floor(progress(f,a,40)*prompt.length));return <Canvas title={title}>
<Surface id="card-0" x={84} y={292} width={530} height={255} p={progress(f,a)}><div style={{color:accent,fontSize:21}}>01 / 输入提示词</div><div style={{fontSize:32,lineHeight:1.65,marginTop:24}}>{typed}<span style={{color:accent}}>▍</span></div></Surface>
<Surface id="card-1" x={672} y={292} width={370} height={255} p={progress(f,b)}><div style={{fontSize:21,color:accent}}>02 / AI 理解任务</div><div style={{fontSize:31,fontWeight:700,marginTop:25}}>施工记录 → 日报</div><div style={{fontSize:24,color:muted,marginTop:20}}>识别内容与输出格式</div></Surface>
<Surface id="card-2" x={84} y={585} width={530} height={300} p={progress(f,c)}><div style={{fontSize:21,color:accent}}>明确要求</div>{requirements.slice(0,3).map((s,i)=><div key={i} style={{fontSize:25,lineHeight:1.6,marginTop:20,color:f>=d?accent:ink}}>✓ {s}</div>)}</Surface>
<Surface id="card-3" x={672} y={585} width={370} height={300} p={progress(f,d)}><div style={{fontSize:21,color:accent}}>03 / 按要求输出</div>{result.slice(0,3).map((s,i)=><div key={i} style={{fontSize:23,lineHeight:1.65,marginTop:17,opacity:progress(f,d+i*14)}}>{s}</div>)}</Surface>
</Canvas>};

export interface KnowledgeLookupProps {title?:string;question?:string;document?:string;answer?:string;cueFrames?:number[]}
/** Show a database connection, question-triggered retrieval, and evidence flowing into an answer. */
export const KnowledgeLookup:React.FC<KnowledgeLookupProps>=({title="连接知识库，让回答有据可依",question="项目验收需要哪些资料？",document="验收清单：检查记录、材料证明、签字确认",answer="依据验收清单：准备检查记录、材料证明与签字确认。",cueFrames=[15,70,125,190]})=>{const f=useCurrentFrame();const [connect,ask,retrieve,reply]=cueFrames;const lookup=progress(f,retrieve,38);return <Canvas title={title}>
<svg width="1440" height="1080" style={{position:"absolute",inset:0}}><path d="M 510 427 L 742 427" stroke="#e0d8ed" strokeWidth="5" fill="none"/><path d="M 510 427 L 742 427" stroke={accent} strokeWidth="5" strokeDasharray="232" strokeDashoffset={232*(1-progress(f,connect,30))} fill="none"/><circle cx={742-232*lookup} cy="427" r="9" fill={accent} opacity={f>=retrieve&&f<retrieve+38?1:0}/><path d="M 920 554 L 920 638 L 570 638" stroke={accent} strokeWidth="3" fill="none" opacity={progress(f,reply)}/></svg>
<Surface id="card-0" x={84} y={302} width={426} height={250}><div style={{fontSize:21,color:accent}}>AI ASSISTANT</div><div style={{fontSize:49,fontWeight:800,marginTop:24}}>AI</div><div style={{fontSize:24,color:muted,marginTop:12}}>{f<retrieve?"已连接企业知识库":"正在检索相关资料"}</div></Surface>
<Surface id="card-1" x={742} y={302} width={300} height={250} p={progress(f,connect)}><div style={{fontSize:21,color:accent}}>企业知识库</div><div style={{fontSize:26,lineHeight:1.65,marginTop:24,background:f>=retrieve?"#f0e9fc":undefined,padding:10,borderRadius:12}}>{document}</div></Surface>
<Surface id="card-2" x={84} y={600} width={490} height={125} p={progress(f,ask)}><div style={{fontSize:18,color:muted}}>提问</div><div style={{fontSize:27,marginTop:10}}>{question}</div></Surface>
<Surface id="card-3" x={84} y={758} width={958} height={170} p={progress(f,reply)}><div style={{fontSize:20,color:accent}}>依据知识库回答</div><div style={{fontSize:27,lineHeight:1.55,marginTop:14}}>{answer}</div></Surface>
</Canvas>};
