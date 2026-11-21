# Repair project assets and scene backgrounds
- Treat folder scope as a browser filter over project/shared asset registries, explain physical storage and distinguish choosing from binding.
- Reuse SceneMedia controls inside editor: explicit folder filter, import image, selected-image preview, bind/clear with revision/lock checks, refresh on returning from asset library.
- Bind actual full-opacity background beneath template foreground in shared renderer. Clear only marked canvas backgrounds, preserve card surfaces. Use SCENE-EDIT for any bound background, including non-editor scenes/all template families.
- Preserve generic template MP4s as library demonstrations and label them accordingly; show link to live adapted preview.
- Test CLI no-edit background path; retain asset upload/bind/clear tests; typecheck/build and actual render/browser checks.
