# AI/workbench handoff implementation
User explicitly authorized implementation of the confirmed boundary: Excel in AI conversation, production by AI/Skill, workbench only assets and review.
1. Add versioned storyboard publication and read-only continuation packet using existing Pydantic/files.
2. Correct scene-based approval counting, include notes and exact selected version conflicts.
3. Add real-output listing/playback and per-file feedback, readable by AI; no generation backend.
4. Rewrite canonical Skill with frontmatter, actual commands, Excel-to-scene mapping guidance and platform boundaries. Keep 4:3, four current templates.
Validation: isolated handoff tests, existing asset/props regressions, TypeScript/build, browser review/empty output view. Full production timing/audio remains explicitly outside this boundary change.
