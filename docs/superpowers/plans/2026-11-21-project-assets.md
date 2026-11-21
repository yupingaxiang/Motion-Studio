# Project asset workflow
User approved continuing project folders, scene binding and scene preview playback.
Use existing shared/project registry and storyboard asset references; preserve locked scenes.
Implemented: dynamic folder matrix; metadata upload; scoped media preview; versioned background image binding with lock protection; content-addressed Remotion staging; existing preview manifest playback.
Ruling: first rendering integration supports background images only; video/audio import and playback remain available without claiming timeline integration.
Verification: isolated upload/bind/clear tests, stale and locked rejection tests, path scope rejection, TS checks, frontend build and real Remotion media render. No user storyboard/approvals changed during automated tests.
