import React from 'react';
import Upload from './Upload';
import './App.css'; // Keep this if you want to use the default Vite styling

function App() {
  return (
    <div className="min-h-screen bg-white flex flex-col items-center justify-center">
      <header className="mb-10 text-center">
        <h1 className="text-4xl font-extrabold text-gray-900">Reflowable.me</h1>
        <p className="text-gray-500 mt-2">Professional PDF to EPUB conversion</p>
      </header>
      
      <main className="w-full max-w-xl px-4">
        {/* This component handles the file selection and API call */}
        <Upload />
      </main>

      <footer className="mt-20 text-gray-400 text-sm">
        <p>© 2025 Reflowable.me - Fast PDF to EPUB Conversion</p>
      </footer>
    </div>
  );
}

export default App;