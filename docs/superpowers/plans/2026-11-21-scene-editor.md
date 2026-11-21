# Scene editor v1
Authorized: add storyboard editing inspired by Overlay Studio concepts, using our own React/Remotion implementation (no upstream source copied).
Scope: one editable motion card per scene. Live Remotion Player, metadata-driven content parameters, x/y/scale, in/out times, scrub/play, optional project video reference and lower-right presenter placement, transparent preview where supported. Save versioned scene-edits.json; AI handoff and rendering consume edits. Locked scenes reject writes; do not silently change selected templates.
Transparent preview supports text/flow/compare/data/number/sticker; full media backgrounds remain opaque. No alpha video export claim.
Tasks: failing edit persistence/conflict tests; backend contract and routes; shared editable composition and frontend player; editor UI and entry; CLI handoff/render integration; tests/typecheck/build/browser preview+save.
