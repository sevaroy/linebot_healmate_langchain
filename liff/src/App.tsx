import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from 'react-router-dom';

// Import components
import Dashboard from '@components/Dashboard';
import TarotReader from '@components/TarotReader';
import ZodiacFortune from '@components/ZodiacFortune';
import MoodTracker from '@components/MoodTracker';
import History from '@components/History';
import LoadingScreen from '@components/common/LoadingScreen';
import ErrorScreen from '@components/common/ErrorScreen';

// Import LIFF Context
import { LiffProvider, useLiff } from './contexts/LiffContext';

// LIFF ID from environment variable or config
const LIFF_ID = import.meta.env.VITE_LIFF_ID || '';

// AppContent component is wrapped inside LiffProvider
const AppContent: React.FC = () => {
  const { isLoggedIn, userProfile, isLoading, error, liffObject, login } = useLiff();

  // Protected route component
  const ProtectedRoute: React.FC<{ element: React.ReactNode }> = ({ element }) => {
    // If loading, show loading screen
    if (isLoading) {
      return <LoadingScreen message="正在載入..." />;
    }
    
    // If there is an error, show error screen
    if (error) {
      return <ErrorScreen message={error} />;
    }
    
    // If not logged in, redirect to login page or show login prompt
    if (!isLoggedIn) {
      return (
        <div className="p-6 text-center">
          <h2 className="text-xl mb-4">請先登入</h2>
          <button 
            onClick={() => login()}
            className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 transition-colors"
          >
            LINE 登入
          </button>
        </div>
      );
    }
    
    // If logged in, render the element
    return <>{element}</>;
  };
  
  if (isLoading) {
    return <LoadingScreen message="正在初始化應用..." />;
  }

  if (error) {
    return <ErrorScreen message={error} />;
  }

  return (
    <div className="app-container max-w-4xl mx-auto p-4">
      <header className="bg-gradient-to-r from-purple-700 to-blue-600 text-white p-4 rounded-lg mb-4">
        <h1 className="text-xl font-bold text-center">LINE 占卜 & 心情陪伴 AI 師</h1>
        {isLoggedIn && userProfile && (
          <div className="flex items-center mt-2 justify-center">
            <img 
              src={userProfile.pictureUrl} 
              alt="Profile" 
              className="h-8 w-8 rounded-full mr-2 border-2 border-white"
            />
            <span>{userProfile.displayName}</span>
          </div>
        )}
      </header>
      
      {isLoggedIn && (
        <nav className="bg-white p-2 rounded-lg shadow mb-4 overflow-x-auto">
          <ul className="flex min-w-max">
            <li className="px-3 py-2">
              <Link to="/" className="text-purple-700 hover:text-purple-900">
                儀表板
              </Link>
            </li>
            <li className="px-3 py-2">
              <Link to="/tarot" className="text-purple-700 hover:text-purple-900">
                塔羅牌
              </Link>
            </li>
            <li className="px-3 py-2">
              <Link to="/zodiac" className="text-purple-700 hover:text-purple-900">
                星座運勢
              </Link>
            </li>
            <li className="px-3 py-2">
              <Link to="/mood" className="text-purple-700 hover:text-purple-900">
                心情日記
              </Link>
            </li>
            <li className="px-3 py-2">
              <Link to="/history" className="text-purple-700 hover:text-purple-900">
                歷史記錄
              </Link>
            </li>
          </ul>
        </nav>
      )}
      
      <main className="bg-white p-4 rounded-lg shadow">
        <Routes>
          <Route path="/" element={
            <ProtectedRoute element={<Dashboard liff={liffObject} userProfile={userProfile} />} />
          } />
          <Route path="/tarot" element={
            <ProtectedRoute element={<TarotReader liff={liffObject} userProfile={userProfile} />} />
          } />
          <Route path="/zodiac" element={
            <ProtectedRoute element={<ZodiacFortune liff={liffObject} userProfile={userProfile} />} />
          } />
          <Route path="/mood" element={
            <ProtectedRoute element={<MoodTracker liff={liffObject} userProfile={userProfile} />} />
          } />
          <Route path="/history" element={
            <ProtectedRoute element={<History liff={liffObject} userProfile={userProfile} />} />
          } />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
      
      <footer className="mt-4 text-center text-gray-600 text-sm">
        <p>© 2025 LINE 占卜 & 心情陪伴 AI 師</p>
      </footer>
    </div>
  );

// Main App component wraps AppContent with LiffProvider
const App: React.FC = () => {
  return (
    <Router>
      <LiffProvider liffId={LIFF_ID}>
        <AppContent />
      </LiffProvider>
    </Router>
  );
};

export default App;
