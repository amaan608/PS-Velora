'use client';

import { useState } from 'react';

export default function FileUpload({ onUploadSuccess }) {
  const [employeesFile, setEmployeesFile] = useState(null);
  const [vehiclesFile, setVehiclesFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState('');
  const [uploadData, setUploadData] = useState(null);

  const handleEmployeesFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setEmployeesFile(file);
      setMessage('');
    }
  };

  const handleVehiclesFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setVehiclesFile(file);
      setMessage('');
    }
  };

  const handleUpload = async () => {
    if (!employeesFile || !vehiclesFile) {
      setMessage('Please select both files');
      return;
    }

    setUploading(true);
    setMessage('');

    try {
      const formData = new FormData();
      formData.append('employees_file', employeesFile);
      formData.append('vehicles_file', vehiclesFile);

      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();

      if (result.success) {
        setMessage('Files uploaded successfully!');
        setUploadData(result.data);
        if (onUploadSuccess) {
          onUploadSuccess(result.data);
        }
      } else {
        setMessage(`Error: ${result.message}`);
      }
    } catch (error) {
      setMessage(`Upload failed: ${error.message}`);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 max-w-2xl mx-auto">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Upload Files</h2>
      
      <div className="space-y-4">
        {/* Employees File */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Employees Excel File
          </label>
          <input
            type="file"
            accept=".xlsx,.xls"
            onChange={handleEmployeesFileChange}
            className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100"
            disabled={uploading}
          />
          {employeesFile && (
            <p className="mt-1 text-sm text-gray-600">
              Selected: {employeesFile.name}
            </p>
          )}
        </div>

        {/* Vehicles File */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Vehicles Excel File
          </label>
          <input
            type="file"
            accept=".xlsx,.xls"
            onChange={handleVehiclesFileChange}
            className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100"
            disabled={uploading}
          />
          {vehiclesFile && (
            <p className="mt-1 text-sm text-gray-600">
              Selected: {vehiclesFile.name}
            </p>
          )}
        </div>

        {/* Upload Button */}
        <button
          onClick={handleUpload}
          disabled={uploading || !employeesFile || !vehiclesFile}
          className="w-full bg-primary-600 text-white py-2 px-4 rounded-md hover:bg-primary-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
        >
          {uploading ? 'Uploading...' : 'Upload Files'}
        </button>

        {/* Message */}
        {message && (
          <div className={`p-3 rounded-md ${
            message.includes('Error') || message.includes('failed')
              ? 'bg-red-50 text-red-700'
              : 'bg-green-50 text-green-700'
          }`}>
            {message}
          </div>
        )}

        {/* Upload Data Summary */}
        {uploadData && (
          <div className="mt-4 p-4 bg-blue-50 rounded-md">
            <h3 className="font-semibold text-blue-900 mb-2">Upload Summary</h3>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>Employees: {uploadData.num_employees}</li>
              <li>Vehicles: {uploadData.num_vehicles}</li>
              <li>Total Capacity: {uploadData.total_capacity}</li>
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
