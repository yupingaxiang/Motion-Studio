# FredTalk source adapters

Upstream: https://github.com/njrhts2kvv-star/FredTalk/tree/main/components/projects/f14691016c16/src/components
License: MIT, retained in LICENSE. Original source hashes, imported tree identity and adapted-file hashes are in provenance.json.

Imported actual motion implementations: talk-highlighter-sweep.tsx (catalog V087), talk-stack-fan-out.tsx, talk-error-retype.tsx, talk-rack-focus-pair.tsx. The last three are public project source files registered in the upstream project, not asserted to be individually approved catalog entries. Motion Studio IDs use descriptive names accordingly.

Adaptations: a Chinese system font fallback replaces unavailable private FredMiSans; highlight copy is parameterized. Wrappers in ../FredTemplates.tsx preserve 960x540 source geometry scaled uniformly into a 1440x1080 white canvas. Vertical margins remain; no aspect stretching. Real demo images are Motion Studio's own template covers copied into remotion/public/fred-examples. No private recordings, music or author photos are imported.

Upstream MIT permission covers distributed source as stated by that repository. Source collection identity is not an assertion that all underlying reference designs or third-party media were independently authored by FredTalk. New media inputs require their own provenance.

Known constraints: retyping cues are authored for four-character examples; long strings need timing adaptation. Highlighter copy must fit the available line. Five-image fan and two-image focus retain their source cardinality. These are executable source adapters, not generic adapters for every record in the 432-entry upstream catalog.
