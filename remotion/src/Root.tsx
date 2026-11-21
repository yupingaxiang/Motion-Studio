/** Author: Codex | Modified: 2026-11-21 15:30:00 +08:00 | Four native 4:3 templates; obsolete compositions removed. */
/**
 * Motion Studio Remotion 入口。
 * 注册四个 4:3 动效组件。
 *
 * 每个 composition 的 props 含 styleId，组件据此适配风格。
 * 默认画幅 4:3，1440x1080，30fps。
 */

import { Composition } from "remotion";
import { TextReveal } from "./components/TextReveal";
import { FlowExpand } from "./components/FlowExpand";
import { ConceptCompare } from "./components/ConceptCompare";
import { DataTrend } from "./components/DataTrend";

import { withSceneBackground } from "./components/SceneBackground";
const TextScene = withSceneBackground(TextReveal);
const FlowScene = withSceneBackground(FlowExpand);
const CompareScene = withSceneBackground(ConceptCompare);
const DataScene = withSceneBackground(DataTrend);
import { FredHighlight, FredStack, FredRetype, FredFocus } from "./components/FredTemplates";
import {NumberCounter,MediaFlash,CounterFlashIntro} from "./components/CounterFlash";
import {StickerExplainer} from "./components/StickerExplainer";
import {EditableScene} from "./components/EditableScene";
const FPS = 30;

/** Register real previews at their native output dimensions. */
export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition id="SCENE-EDIT" component={EditableScene} durationInFrames={150} fps={30} width={1440} height={1080} defaultProps={{templateId:"TEXT-001",content:{keyword:"实时编辑"},layout:{x:0,y:0,scale:1,transparent:false},startMs:0,endMs:5000}} calculateMetadata={({props})=>({durationInFrames:Math.max(1,Math.ceil(props.endMs*.03))})}/>
      <Composition id="STICKER-001" component={StickerExplainer} durationInFrames={270} fps={30} width={1440} height={1080}/>
      <Composition id="NUMBER-001" component={NumberCounter} durationInFrames={150} fps={30} width={1440} height={1080}/>
      <Composition id="MEDIA-001" component={MediaFlash} durationInFrames={150} fps={30} width={1440} height={1080}/>
      <Composition id="INTRO-001" component={CounterFlashIntro} durationInFrames={150} fps={30} width={1440} height={1080}/>
      <Composition id="FRED-V087" component={FredHighlight} durationInFrames={90} fps={30} width={1440} height={1080}/>
      <Composition id="FRED-STACK" component={FredStack} durationInFrames={204} fps={30} width={1440} height={1080}/>
      <Composition id="FRED-RETYPE" component={FredRetype} durationInFrames={177} fps={30} width={1440} height={1080}/>
      <Composition id="FRED-FOCUS" component={FredFocus} durationInFrames={216} fps={30} width={1440} height={1080}/>
      <Composition
        id="TEXT-001"
        component={TextScene}
        durationInFrames={90}
        fps={FPS}
        width={1440}
        height={1080}
        defaultProps={{
          keyword: "复利",
          subtitle: "大家好，今天介绍一个概念：复利。",
          styleId: "minimal-tech",
        }}
      />
      <Composition
        id="FLOW-001"
        component={FlowScene}
        durationInFrames={120}
        fps={FPS}
        width={1440}
        height={1080}
        defaultProps={{
          nodes: ["本金", "收益", "新本金", "新收益"],
          title: "利滚利的循环",
          styleId: "minimal-tech",
        }}
      />
      <Composition
        id="COMP-001"
        component={CompareScene}
        durationInFrames={120}
        fps={FPS}
        width={1440}
        height={1080}
        defaultProps={{
          leftLabel: "单利",
          rightLabel: "复利",
          leftValue: "线性增长",
          rightValue: "指数增长",
          styleId: "blueprint",
        }}
      />
      <Composition
        id="DATA-001"
        component={DataScene}
        durationInFrames={150}
        fps={FPS}
        width={1440}
        height={1080}
        defaultProps={{
          startValue: "1.00",
          endValue: "37.78",
          caption: "每天进步 1%，一年后 37 倍",
          styleId: "blueprint",
        }}
      />
    </>
  );
};
