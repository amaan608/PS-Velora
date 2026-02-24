'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import FileUpload from '@/components/FileUpload';

export default function Home() {
  const router = useRouter();
  const [uploadComplete, setUploadComplete] = useState(false);
  const [optimizing, setOptimizing] = useState(false);
  const [error, setError] = useState('');
  const [warning, setWarning] = useState('');

  const handleUploadSuccess = (data) => {
    setUploadComplete(true);
    setError('');
    setWarning('');
  };

  const handleOptimize = async () => {
    setOptimizing(true);
    setError('');
    setWarning('');

    try {
      const response = await fetch('/api/optimize', {
        method: 'POST',
      });

      const result = await response.json();

      if (result.success) {
        // Check if there are unassigned employees
        if (result.data?.unassigned_employees > 0) {
          setWarning(`${result.data.unassigned_employees} employees could not be assigned due to capacity or preference constraints`);
          // Wait a moment to show warning, then redirect
          setTimeout(() => {
            router.push('/dashboard');
          }, 2000);
        } else {
          // Redirect immediately if all assigned
          router.push('/dashboard');
        }
      } else {
        setError(result.message || 'Optimization failed');
      }
    } catch (err) {
      setError(`Error: ${err.message}`);
    } finally {
      setOptimizing(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <span className="text-white text-xl font-bold">V</span>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Velora</h1>
                <p className="text-sm text-gray-600">Employee Transportation Optimizer</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            Optimize Your Corporate Transportation
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Upload employee and vehicle data to generate optimal routes, reduce costs,
            and improve efficiency with AI-powered optimization algorithms.
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-3 gap-6 mb-12">
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="text-3xl mb-3">🚗</div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Smart Routing</h3>
            <p className="text-gray-600 text-sm">
              Nearest Neighbor Heuristic with 2-opt improvement for optimal routes
            </p>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="text-3xl mb-3">💰</div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Cost Savings</h3>
            <p className="text-gray-600 text-sm">
              Save up to 60% compared to individual cab rides through vehicle sharing
            </p>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="text-3xl mb-3">⏱️</div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Time Optimization</h3>
            <p className="text-gray-600 text-sm">
              Respect time windows and priority constraints for all employees
            </p>
          </div>
        </div>

        {/* Upload Section */}
        <div className="mb-8">
          <FileUpload onUploadSuccess={handleUploadSuccess} />
        </div>

        {/* Optimize Button */}
        {uploadComplete && (
          <div className="max-w-2xl mx-auto">
            <button
              onClick={handleOptimize}
              disabled={optimizing}
              className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-4 px-6 rounded-lg font-semibold text-lg hover:from-blue-700 hover:to-purple-700 disabled:from-gray-400 disabled:to-gray-400 disabled:cursor-not-allowed transition-all shadow-lg"
            >
              {optimizing ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Optimizing Routes...
                </span>
              ) : (
                'Run Optimization'
              )}
            </button>

            {error && (
              <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
                {error}
              </div>
            )}

            {warning && (
              <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg text-yellow-800">
                ⚠️ {warning}
              </div>
            )}
          </div>
        )}

        {/* How It Works */}
        <div className="mt-16 bg-white rounded-lg shadow-md p-8">
          <h3 className="text-2xl font-bold text-gray-900 mb-6 text-center">How It Works</h3>
          <div className="grid md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center mx-auto mb-3 font-bold text-lg">1</div>
              <h4 className="font-semibold text-gray-900 mb-2">Upload Data</h4>
              <p className="text-sm text-gray-600">Upload employee and vehicle Excel files</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center mx-auto mb-3 font-bold text-lg">2</div>
              <h4 className="font-semibold text-gray-900 mb-2">Assign Vehicles</h4>
              <p className="text-sm text-gray-600">Priority-based greedy assignment algorithm</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center mx-auto mb-3 font-bold text-lg">3</div>
              <h4 className="font-semibold text-gray-900 mb-2">Optimize Routes</h4>
              <p className="text-sm text-gray-600">2-opt algorithm improves route efficiency</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center mx-auto mb-3 font-bold text-lg">4</div>
              <h4 className="font-semibold text-gray-900 mb-2">View Results</h4>
              <p className="text-sm text-gray-600">Interactive map and detailed metrics</p>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-8 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p className="text-gray-400">
            Built for hackathon • Pure Python optimization • No third-party APIs
          </p>
        </div>
      </footer>
    </div>
  );
}
