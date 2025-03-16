// App.js (Main Routing Component)
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import ContactPage from './pages/contactpage.js'; // Importing the ContactPage component
import Homepage from './pages/homepage.js';
import LoginPage from './pages/loginpage.js';
import CreateAccountPage from './pages/createaccountpage.js';
import DashboardPage from './pages/dashboard.js';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Homepage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/create-account" element={<CreateAccountPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/contact" element={<ContactPage />} />
      </Routes>
    </Router>
  );
}

export default App;
