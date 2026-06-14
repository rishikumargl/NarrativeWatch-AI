import React from 'react';
import { Link } from 'react-router-dom';

export default function Header() {
  return (
    <header className="bg-gradient-to-r from-blue-600 to-blue-700 shadow-lg">
      <div className="container mx-auto px-4 py-6">
        <div className="flex justify-between items-center">
          <Link to="/" className="flex items-center gap-3">
            <div className="text-4xl font-bold text-white">📰</div>
            <div>
              <h1 className="text-3xl font-bold text-white">NarrativeWatch</h1>
              <p className="text-blue-100 text-sm">Real News Intelligence Platform</p>
            </div>
          </Link>
          
          <nav className="flex gap-6">
            <Link to="/" className="text-white hover:text-blue-100 transition font-medium">
              Home
            </Link>
            <Link to="/history" className="text-white hover:text-blue-100 transition font-medium">
              History
            </Link>
          </nav>
        </div>
      </div>
    </header>
  );
}
