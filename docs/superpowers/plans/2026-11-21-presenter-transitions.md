# Paired presenter transition templates
Approved direction: 4:3, continuous original presenter video/audio, rounded bottom-right PiP without border; independent entrance and return templates.
- PRESENTER-IN: full-frame hold, 0.87s smooth shrink to right-bottom, knowledge cards reveal with stagger.
- PRESENTER-OUT: knowledge cards retract first, bottom-right presenter expands smoothly to full-frame and continues.
- Shared deterministic geometry, no video remount/crossfade between duplicate audio tracks; source frame offset preserves adjacent-cut continuity.
- Template demo uses original procedural stand-in marked DEMO DATA; real project rendering requires presenterSrc and stages an allowed local video. No reference video copied.
- Expose title/three knowledge cards/transition time/source frame/PiP geometry/crop in editor; per-element drag applies to cards and presenter.
- Register metadata, compositions, editor map and template gallery category. Render actual preview MP4s/posters and verify decoding; test endpoint geometry and source/offset validation.
