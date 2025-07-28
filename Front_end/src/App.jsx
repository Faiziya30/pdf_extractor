import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import Upload from './pages/Upload';
import Results from './pages/Results';
import Header from './components/Header';
import { Toaster } from 'react-hot-toast';

const App = () => {
  return (
    <Router>
      <Toaster />
      <div className="min-h-screen bg-gray-100 dark:bg-gray-900 text-gray-900 dark:text-gray-100">
        <Header />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/upload" element={<Upload />} />
          <Route path="/results" element={<Results />} />
        </Routes>
      </div>
    </Router>
  );
};

export default App;