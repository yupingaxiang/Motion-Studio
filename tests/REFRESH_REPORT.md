# 2026-11-21 workspace refresh validation
- Frontend production build: PASS.
- Frontend and Remotion TypeScript checks: PASS.
- Selected candidate props regression: observed failure before fix, PASS after fix.
- Four real preview renders: PASS. TEXT 3s, FLOW 4s, COMP 4s, DATA 5s; all H.264 1440x1080.
- Full FFmpeg decode of all four MP4 files: PASS.
- Inspected four representative rendered frames; changed posters to 2.8s to show populated layouts.
- Browser: 1440px desktop matrix, category filter, 4:3 filter (four results), details dialog and autoplay checked. Narrow viewport navigation observed.
- Existing port 8000 used cached old schema; fresh validation server started at 8001 without stopping user's process.
- No Git commands. No original project approvals or recommendations overwritten.
- Full legacy acceptance suite not run because it edits demo approvals and produces a full video. Mixed-aspect final composition remains a separate limitation.

## Project assets follow-up
- Four isolated tests PASS: upload/bind/clear with actual file persistence, locked scene rejection, stale revision rejection, path scope rejection.
- Frontend and Remotion TypeScript checks PASS; production build PASS.
- Native 4:3 Remotion render with staged content-hashed background image PASS: .tmp/asset-preview.mp4 (90 frames).
- Browser verified dynamic shared/project folder cards, project folder navigation and review link.

## AI/workbench boundary implementation
- 3 handoff tests PASS: unknown scene approval cannot unlock production; reselection notes enter continuation packet; versioned storyboard publication and exact-file output notes roundtrip.
- Existing 4 asset tests and 1 candidate-props test PASS (8 total).
- Frontend TypeScript and production build PASS.
- New commands: publish-storyboard and review-brief. Skill now includes standard frontmatter, AI-side Excel intake and no workbench AI invocation.
- Output review lists existing MP4 only, persists notes atomically, feeds them back to AI. No real complete movie was generated as part of this task.
