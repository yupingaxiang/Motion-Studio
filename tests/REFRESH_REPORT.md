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

## FredTalk first-batch import
- Actual public MIT source integrated for V087/highlighter, stack fan-out, error retype, rack-focus pair. Upstream source hashes, imported tree SHA and local adapted hashes recorded.
- Four full local MP4 renders PASS; all H.264 1440x1080 30fps, full FFmpeg decode PASS. Representative frames inspected. Original16:9 geometry uniformly fitted into 4:3, not reflowed.
- Fred provenance/registration tests PASS, Remotion TypeScript PASS, frontend build PASS.
- Browser FredTalk source filter returns four cards; details expose provenance/parameters; actual autoplay verified videoWidth=1440/videoHeight=1080.
- Records promoted from DRAFT to APPROVED only after successful render/decode. Existing user selections unchanged. Not the entire432-entry upstream catalog.

## Counter/media flash reference extraction
- Added independent NUMBER-001 and MEDIA-001 plus composed INTRO-001; original mechanisms reimplemented from inspected opening, no reference footage copied into demo assets.
- 10 pure frame-math assertions PASS (count endpoints, descending count, cut boundaries, hold, empty inputs). Remotion TypeScript PASS.
- All three real renders and full FFmpeg decode PASS; H.264 1440x1080 30fps, exactly5 seconds. Cards promoted after validation; backend API lists all three APPROVED with previewExists=true.
- Inspected numeric mid-count, settled title layout, eight successive media cut frames (including actual video inputs) and composed intro. Video start offset configurable; defaults30 frames to avoid blank source openings.

## Sticker explainer
- STICKER-001 original 4:3 composition built from inspected reference style: mint paper, outlined original SVG stickers, drawn connectors, taped notes.
- Configurable 2-5 node labels/images and cueFrames support per-node narration timing; no presenter footage fabricated. Lower-right reserved.
- TypeScript PASS; real render/full FFmpeg decode PASS, H.264 1440x1080 30fps,9s. Inspected2.8s and7.5s states; reduced summary font to remove orphan character and rerendered.
- Promoted to APPROVED after validation and rebuilt catalog.
