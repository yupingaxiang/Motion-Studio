import { useEffect, useState } from "react";
import { api } from "../api";
import type { StyleSpec } from "../types";

export function StyleLibrary() {
  const [styles, setStyles] = useState<StyleSpec[]>([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<StyleSpec | null>(null);

  useEffect(() => {
    api.getStyles().then((r) => {
      setStyles(r.styles);
      setLoading(false);
    });
  }, []);

  if (loading) return <div className="p-8 text-ms-muted">加载中...</div>;

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-2">视觉风格库</h1>
      <p className="text-ms-muted text-sm mb-6">
        三个原创风格：Minimal Tech、Blueprint、Engraving。每个风格含色彩规范、构图规则、字体建议、动画节奏、图像生成提示词与推荐/禁用场景。
        Codex 可直接检索。
      </p>

      <div className="grid grid-cols-3 gap-4 mb-6">
        {styles.map((s) => (
          <div
            key={s.styleId}
            onClick={() => setSelected(s)}
            className="rounded-xl overflow-hidden cursor-pointer border border-ms-border hover:border-ms-accent transition-colors"
          >
            {/* 色彩预览 */}
            <div className="h-32 flex" style={{ background: s.background }}>
              {s.colors.slice(0, 5).map((c) => (
                <div key={c.hex} className="flex-1 flex items-end justify-center pb-2">
                  <div
                    className="w-8 h-8 rounded-full border-2 border-white/20"
                    style={{ background: c.hex }}
                  />
                </div>
              ))}
            </div>
            <div className="p-4 bg-ms-panel">
              <div className="text-xs font-mono text-ms-accent">{s.styleId}</div>
              <h3 className="font-semibold mt-1">{s.name}</h3>
              <p className="text-xs text-ms-muted line-clamp-2 mt-1">{s.description}</p>
              <div className="flex flex-wrap gap-1 mt-2">
                {s.tags.slice(0, 4).map((t) => (
                  <span key={t} className="text-xs px-1.5 py-0.5 rounded bg-ms-border text-ms-muted">{t}</span>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>

      {styles.length === 0 && (
        <div className="text-center py-12 text-ms-muted">
          暂无风格。运行 <code className="text-ms-accent">python scripts/motion_studio.py init</code> 生成。
        </div>
      )}

      {/* 详情弹窗 */}
      {selected && (
        <div
          className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-8"
          onClick={() => setSelected(null)}
        >
          <div
            className="bg-ms-panel border border-ms-border rounded-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto p-6"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-start justify-between mb-4">
              <div>
                <div className="text-xs font-mono text-ms-accent">{selected.styleId}</div>
                <h2 className="text-xl font-bold">{selected.name}</h2>
              </div>
              <button onClick={() => setSelected(null)} className="text-ms-muted hover:text-white">✕</button>
            </div>

            {/* 风格预览面板 */}
            <div className="rounded-lg p-6 mb-4" style={{ background: selected.background, color: selected.foreground }}>
              <div style={{ fontFamily: selected.titleFont, fontSize: 36, fontWeight: 700 }}>
                标题示例 Title Sample
              </div>
              <div style={{ fontFamily: selected.bodyFont, fontSize: 16, opacity: 0.7, marginTop: 8 }}>
                正文示例 body text sample —— {selected.styleId}
              </div>
              <div className="flex gap-2 mt-4">
                {selected.colors.map((c) => (
                  <div key={c.hex} className="flex flex-col items-center">
                    <div className="w-12 h-12 rounded" style={{ background: c.hex, border: `1px solid ${selected.foreground}33` }} />
                    <div className="text-xs mt-1" style={{ opacity: 0.6 }}>{c.name}</div>
                  </div>
                ))}
              </div>
            </div>

            <p className="text-sm text-gray-300 mb-4">{selected.description}</p>

            <div className="grid grid-cols-2 gap-6 text-sm">
              <Section title="色彩规范">
                {selected.colors.map((c) => (
                  <div key={c.hex} className="flex items-center gap-2 mb-1">
                    <div className="w-4 h-4 rounded" style={{ background: c.hex }} />
                    <span className="text-gray-300">{c.name}</span>
                    <span className="text-ms-muted text-xs">{c.hex}</span>
                    <span className="text-ms-muted text-xs">— {c.usage}</span>
                  </div>
                ))}
              </Section>

              <Section title="构图规则">
                <ul className="space-y-1">
                  {selected.compositionRules.map((r, i) => (
                    <li key={i} className="text-xs text-gray-300">• {r}</li>
                  ))}
                </ul>
              </Section>

              <Section title="字体建议">
                <ul className="space-y-1">
                  {selected.fontSuggestions.map((r, i) => (
                    <li key={i} className="text-xs text-gray-300">• {r}</li>
                  ))}
                </ul>
                <div className="mt-2 text-xs">
                  <span className="text-ms-muted">标题字体: </span>
                  <span className="text-ms-accent">{selected.titleFont}</span>
                </div>
              </Section>

              <Section title="动画节奏建议">
                <ul className="space-y-1">
                  {selected.animationRhythm.map((r, i) => (
                    <li key={i} className="text-xs text-gray-300">• {r}</li>
                  ))}
                </ul>
              </Section>

              <Section title="图像生成提示词">
                <div className="bg-ms-bg rounded p-2 text-xs text-gray-300 font-mono break-all">
                  {selected.imagePromptTemplate}
                </div>
                <div className="mt-2">
                  <div className="text-xs text-ms-accent2 mb-1">Negative Prompt</div>
                  <div className="bg-ms-bg rounded p-2 text-xs text-gray-400 font-mono break-all">
                    {selected.negativePrompt}
                  </div>
                </div>
              </Section>

              <Section title="场景适用性">
                <div className="mb-2">
                  <div className="text-xs text-green-400 mb-1">✓ 推荐场景</div>
                  <div className="flex flex-wrap gap-1">
                    {selected.recommendedScenes.map((s) => (
                      <span key={s} className="text-xs px-2 py-0.5 rounded bg-green-500/20 text-green-400">{s}</span>
                    ))}
                  </div>
                </div>
                <div>
                  <div className="text-xs text-red-400 mb-1">✗ 禁用场景</div>
                  <div className="flex flex-wrap gap-1">
                    {selected.forbiddenScenes.map((s) => (
                      <span key={s} className="text-xs px-2 py-0.5 rounded bg-red-500/20 text-red-400">{s}</span>
                    ))}
                  </div>
                </div>
              </Section>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div>
      <div className="text-xs text-ms-muted uppercase mb-2">{title}</div>
      {children}
    </div>
  );
}
