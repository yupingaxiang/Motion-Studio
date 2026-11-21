# Element positioning and project entry
User correction: drag a specific card/element inside a template, never implicitly move the entire composition.
1. Add validated per-element x/y overrides to scene-edits; preserve legacy whole composition layout.
2. Mark semantic card/title/text elements in all twelve templates with stable IDs; apply independent CSS translate in shared Player/render composition, compensating Fred native scale.
3. Delegate pointer selection to marked elements, show selection outline and element selector; existing x/y inputs now target selected element; blank canvas does not move anything. Scale remains explicitly whole composition.
4. Add visible editor and review actions to homepage project cards without nested links.
5. Test persistence, invalid offsets and CLI handoff; build/typecheck, browser drag separate cards, inspect untouched siblings, save/reload, and render actual still.
No Git commands. No upstream Overlay Studio source copied.
