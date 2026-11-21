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


## 2026-11-21 Scene editor verification
- Added scene content, whole-card placement/scale, local timing and explicit versioned saves; AI review-brief and rendering consume scene-edits.json. Confirmed scenes remain locked.
- Shared Remotion Player/export component; six templates support transparent foreground preview. No transparent video export or arbitrary internal-element timeline implemented.
- 14 Python regression tests passed (scene editor 4, handoff 3, scene props 1, Fred 2, project assets 4); counter timing 10 assertions passed. Frontend and Remotion TypeScript checks and production build passed.
- Real SCENE-EDIT render: .tmp/editor-render.mp4, 105 frames/3.5 seconds; transparent PNG .tmp/editor-alpha.png has alpha range 0..255.
- Browser verified immediate text/layout changes, checkerboard transparency, save/reload retention and discard restoring saved values. Demo S01 contains an explicit saved editor draft; original approvals/recommendations retained.
- Bound background images are also passed into the shared live preview; presenter video is preview-only and starts at the selected file beginning.


## 2026-11-21 Independent element editing correction
- Replaced implicit whole-composition dragging with template-declared element hit-testing, independent offsets and preview-only selection outline. Blank canvas deselects without moving the composition. All 12 adapters mark semantic elements; Fred coordinates compensate its 1.5 stage scale.
- Homepage project cards now expose separate editor/review links.
- Browser: at frame90, dragging COMP left card produced x104/y-74; right card and title bounding rects stayed identical. Saved and reloaded, selected left card and verified x104/y-74 persisted; restored test offsets to zero and saved. Homepage editor link opened editor route successfully. Demo S04 now contains a neutral saved editor draft.
- Real rendered still .tmp/element-edit.png shows left card independently shifted +100/-90 while right card stays in place.
- 11 Python tests passed including new element validation/persistence and CLI handoff; frontend and Remotion typechecks/build passed.
