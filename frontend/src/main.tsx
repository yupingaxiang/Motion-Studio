/** Author: Codex | Modified: 2026-11-21 17:00:00 +08:00 | Output review route. */
import React from "react";
import ReactDOM from "react-dom/client";
import { HashRouter, Routes, Route, Navigate } from "react-router-dom";
import "./index.css";
import { OutputReview } from "./pages/OutputReview";
import { Layout } from "./components/Layout";
import { StoryboardReview } from "./pages/StoryboardReview";
import { MotionLibrary } from "./pages/MotionLibrary";
import { AssetLibrary } from "./pages/AssetLibrary";
import { StyleLibrary } from "./pages/StyleLibrary";
import { ProjectList } from "./pages/ProjectList";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <HashRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Navigate to="/projects" replace />} />
          <Route path="/projects" element={<ProjectList />} />
          <Route path="/outputs/:projectId" element={<OutputReview />} />
          <Route path="/review/:projectId" element={<StoryboardReview />} />
          <Route path="/motions" element={<MotionLibrary />} />
          <Route path="/assets" element={<AssetLibrary />} />
          <Route path="/styles" element={<StyleLibrary />} />
        </Route>
      </Routes>
    </HashRouter>
  </React.StrictMode>
);
