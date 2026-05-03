import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import DashboardPage from './pages/DashboardPage';
import ArticleDetailPage from './pages/ArticleDetailPage';
import GraphPage from './pages/GraphPage';
import TimelineMapPage from './pages/TimelineMapPage';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<DashboardPage />} />
          <Route path="article/:id" element={<ArticleDetailPage />} />
          <Route path="graph" element={<GraphPage />} />
          <Route path="timeline" element={<TimelineMapPage />} />
          <Route path="*" element={<DashboardPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
