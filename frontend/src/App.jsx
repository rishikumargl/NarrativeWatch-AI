import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ProjectProvider } from './context/ProjectContext';
import HomePage from './pages/HomePage';
import ProjectsPage from './pages/ProjectsPage';
import AnalyzePage from './pages/AnalyzePage';
import ResultsPage from './pages/ResultsPage';
import DocumentUploadPage from './pages/DocumentUploadPage';
import AnalyticsDashboard from './pages/AnalyticsDashboard';

function AppRoutes() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black">
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/projects" element={<ProjectsPage />} />
        <Route path="/analysis" element={<AnalyzePage />} />
        <Route path="/analysis/:id" element={<AnalyzePage />} />
        <Route path="/results/:id" element={<ResultsPage />} />
        <Route path="/documents" element={<DocumentUploadPage />} />
        <Route path="/analytics" element={<AnalyticsDashboard />} />

        {/* Catch-all redirect to home */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </div>
  );
}

function App() {
  return (
    <Router>
      <ProjectProvider>
        <AppRoutes />
      </ProjectProvider>
    </Router>
  );
}

export default App;
