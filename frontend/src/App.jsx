import { useEffect } from 'react';
import { Routes, Route, Navigate, useLocation } from 'react-router-dom';

import PortfolioLayout from './layouts/PortfolioLayout';
import AppShell from './layouts/AppShell';
import HomePage from './pages/HomePage';
import AIChat from './components/AI/AIChat';
import ZebioPage from './pages/ZebioPage';
import TradingProjectPage from './pages/TradingProjectPage';
import TubeProjectPage from './pages/TubeProjectPage';
import { getLenisInstance } from './components/portfolio/SmoothScroll';

function ScrollToTop() {
  const { pathname, hash } = useLocation();

  useEffect(() => {
    if (hash) {
      const id = hash.replace('#', '');
      
      const timeoutId = setTimeout(() => {
        const element = document.getElementById(id);
        if (element) {
          const lenis = getLenisInstance();
          if (lenis) {
            lenis.scrollTo(element, { offset: -100 });
          } else {
            const y = element.getBoundingClientRect().top + window.scrollY - 100;
            window.scrollTo({ top: y, behavior: 'smooth' });
          }
        }
      }, 100);
      
      return () => clearTimeout(timeoutId);
    }

    const lenis = getLenisInstance();
    if (lenis) {
      lenis.scrollTo(0, { immediate: true });
    } else {
      window.scrollTo({ top: 0, left: 0, behavior: 'instant' });
    }
  }, [pathname, hash]);

  return null;
}

function App() {
  return (
    <>
      <ScrollToTop />
      <Routes>
        <Route element={<PortfolioLayout />}>
          <Route path="/" element={<HomePage />} />
          <Route element={<AppShell />}>
            <Route path="/projects/zebio" element={<AIChat />} />
            <Route path="/projects/trading" element={<TradingProjectPage />} />
            <Route path="/projects/tube" element={<TubeProjectPage />} />
            <Route path="/projects/zebio/engineer" element={<ZebioPage />} />
          </Route>
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </>
  );
}

export default App;