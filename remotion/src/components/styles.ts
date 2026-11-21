/**
 * 风格主题：从 styleId 解析色彩与字体。
 * 三个原创风格：minimal-tech / blueprint / engraving。
 * 这些值与 library/styles/<id>/style.json 保持一致。
 */

export interface StyleTheme {
  styleId: string;
  background: string;
  foreground: string;
  primary: string;
  accent: string;
  muted: string;
  titleFont: string;
  bodyFont: string;
}

const FALLBACK: StyleTheme = {
  styleId: "minimal-tech",
  background: "#0A0E1A",
  foreground: "#FFFFFF",
  primary: "#00D4FF",
  accent: "#FF3D71",
  muted: "#5A6478",
  titleFont: "Arial, sans-serif",
  bodyFont: "Arial, sans-serif",
};

const THEMES: Record<string, StyleTheme> = {
  "minimal-tech": {
    styleId: "minimal-tech",
    background: "#0A0E1A",
    foreground: "#FFFFFF",
    primary: "#00D4FF",
    accent: "#FF3D71",
    muted: "#5A6478",
    titleFont: "Arial, Helvetica, sans-serif",
    bodyFont: "Arial, Helvetica, sans-serif",
  },
  blueprint: {
    styleId: "blueprint",
    background: "#0B2A4A",
    foreground: "#E8F1FF",
    primary: "#7BB8FF",
    accent: "#FFB347",
    muted: "#4A6FA5",
    titleFont: "'Courier New', monospace",
    bodyFont: "'Courier New', monospace",
  },
  engraving: {
    styleId: "engraving",
    background: "#F4ECD8",
    foreground: "#1A1A1A",
    primary: "#3D2817",
    accent: "#8B4513",
    muted: "#8A7E5F",
    titleFont: "Georgia, 'Times New Roman', serif",
    bodyFont: "Georgia, 'Times New Roman', serif",
  },
};

export function getTheme(styleId?: string): StyleTheme {
  if (!styleId) return FALLBACK;
  return THEMES[styleId] ?? FALLBACK;
}
