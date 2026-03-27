import React, { useState, useCallback } from 'react';
import { api } from '../services/api';
import type { ProcessingResponse } from '../types';

interface EDDUploadZoneProps {
  onProcessingComplete: (result: ProcessingResponse) => void;
}

export default function EDDUploadZone({ onProcessingComplete }: EDDUploadZoneProps) {
  const [idFile, setIdFile] = useState<File | null>(null);
  const [csvFile, setCsvFile] = useState<File | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [idDragActive, setIdDragActive] = useState(false);
  const [csvDragActive, setCsvDragActive] = useState(false);

  // Handle ID file drag events
  const handleIdDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setIdDragActive(true);
    } else if (e.type === 'dragleave') {
      setIdDragActive(false);
    }
  }, []);

  // Handle CSV file drag events
  const handleCsvDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setCsvDragActive(true);
    } else if (e.type === 'dragleave') {
      setCsvDragActive(false);
    }
  }, []);

  // Handle ID file drop
  const handleIdDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIdDragActive(false);
    setError(null);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      const validTypes = ['application/pdf', 'image/png', 'image/jpeg', 'image/jpg'];
      
      if (!validTypes.includes(file.type)) {
        setError('ID Document must be a PDF or image file');
        return;
      }
      
      setIdFile(file);
    }
  }, []);

  // Handle CSV file drop
  const handleCsvDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setCsvDragActive(false);
    setError(null);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      
      if (file.type !== 'text/csv' && !file.name.endsWith('.csv')) {
        setError('Transaction History must be a CSV file');
        return;
      }
      
      setCsvFile(file);
    }
  }, []);

  // Handle ID file input change
  const handleIdFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setError(null);
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      const validTypes = ['application/pdf', 'image/png', 'image/jpeg', 'image/jpg'];
      
      if (!validTypes.includes(file.type)) {
        setError('ID Document must be a PDF or image file');
        return;
      }
      
      setIdFile(file);
    }
  };

  // Handle CSV file input change
  const handleCsvFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setError(null);
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      
      if (file.type !== 'text/csv' && !file.name.endsWith('.csv')) {
        setError('Transaction History must be a CSV file');
        return;
      }
      
      setCsvFile(file);
    }
  };

  // Read file as text
  const readFileAsText = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => {
        resolve(reader.result as string);
      };
      reader.onerror = reject;
      reader.readAsText(file);
    });
  };

  // Handle EDD Analysis
  const handleRunEDDAnalysis = async () => {
    if (!idFile || !csvFile) return;

    setIsProcessing(true);
    setError(null);

    try {
      // Read CSV file as text
      const csvText = await readFileAsText(csvFile);

      // Call the API with the ID file and CSV text
      // The backend will handle reading the ID file
      const result = await api.uploadFile(
        idFile,
        csvText,
        'AML'
      );

      onProcessingComplete(result);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to process EDD analysis';
      setError(errorMessage);
      console.error('EDD Analysis error:', err);
    } finally {
      setIsProcessing(false);
    }
  };

  const bothFilesSelected = idFile !== null && csvFile !== null;

  return (
    <div className="w-full max-w-4xl mx-auto space-y-6">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Enhanced Due Diligence (EDD)</h2>
        <p className="text-gray-600">Upload both ID document and transaction history for comprehensive AML analysis</p>
      </div>

      {/* ID Document Upload Zone */}
      <div className="space-y-2">
        <label className="block text-sm font-semibold text-gray-700">
          1. Upload ID Document (PDF/Image)
        </label>
        <div
          className={`modern-card relative border-2 border-dashed rounded-xl p-8 transition-all duration-300 ease-out ${
            idDragActive
              ? 'border-blue-500 bg-blue-50 bg-gradient-to-br from-blue-50 to-sky-50 scale-[1.02] shadow-xl'
              : idFile
              ? 'border-green-500 bg-green-50'
              : 'border-gray-300 bg-white/80 hover:border-blue-300 hover:bg-white hover:shadow-lg'
          }`}
          onDragEnter={handleIdDrag}
          onDragOver={handleIdDrag}
          onDragLeave={handleIdDrag}
          onDrop={handleIdDrop}
          style={{ backdropFilter: 'blur(8px)' }}
        >
          <input
            type="file"
            id="id-file-input"
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            onChange={handleIdFileChange}
            accept=".pdf,.png,.jpg,.jpeg"
            disabled={isProcessing}
          />
          <div className="space-y-2 text-center">
            {idFile ? (
              <>
                <svg className="mx-auto h-12 w-12 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                <p className="text-sm font-medium text-gray-900">{idFile.name}</p>
                <p className="text-xs text-gray-500">{(idFile.size / 1024).toFixed(2)} KB</p>
              </>
            ) : (
              <>
                <svg className="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                  <path
                    d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                    strokeWidth={2}
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
                <p className="text-sm text-gray-600">
                  <span className="font-semibold text-blue-600 hover:text-blue-700">Click to upload</span> or drag and drop
                </p>
                <p className="text-xs text-gray-500">PDF, PNG, JPG up to 10MB</p>
              </>
            )}
          </div>
        </div>
      </div>

      {/* CSV Transaction History Upload Zone */}
      <div className="space-y-2">
        <label className="block text-sm font-semibold text-gray-700">
          2. Upload Transaction History (CSV)
        </label>
        <div
          className={`modern-card relative border-2 border-dashed rounded-xl p-8 transition-all duration-300 ease-out ${
            csvDragActive
              ? 'border-blue-500 bg-blue-50 bg-gradient-to-br from-blue-50 to-sky-50 scale-[1.02] shadow-xl'
              : csvFile
              ? 'border-green-500 bg-green-50'
              : 'border-gray-300 bg-white/80 hover:border-blue-300 hover:bg-white hover:shadow-lg'
          }`}
          onDragEnter={handleCsvDrag}
          onDragOver={handleCsvDrag}
          onDragLeave={handleCsvDrag}
          onDrop={handleCsvDrop}
          style={{ backdropFilter: 'blur(8px)' }}
        >
          <input
            type="file"
            id="csv-file-input"
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            onChange={handleCsvFileChange}
            accept=".csv"
            disabled={isProcessing}
          />
          <div className="space-y-2 text-center">
            {csvFile ? (
              <>
                <svg className="mx-auto h-12 w-12 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                <p className="text-sm font-medium text-gray-900">{csvFile.name}</p>
                <p className="text-xs text-gray-500">{(csvFile.size / 1024).toFixed(2)} KB</p>
              </>
            ) : (
              <>
                <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  />
                </svg>
                <p className="text-sm text-gray-600">
                  <span className="font-semibold text-blue-600 hover:text-blue-700">Click to upload</span> or drag and drop
                </p>
                <p className="text-xs text-gray-500">CSV file with transaction history</p>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="rounded-md bg-red-50 p-4">
          <div className="flex">
            <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                clipRule="evenodd"
              />
            </svg>
            <div className="ml-3">
              <p className="text-sm font-medium text-red-800">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Run EDD Analysis Button */}
      <div className="flex justify-center pt-4">
        <button
          onClick={handleRunEDDAnalysis}
          disabled={!bothFilesSelected || isProcessing}
          className={`px-8 py-3 rounded-lg font-semibold text-white transition-all duration-200 ${
            bothFilesSelected && !isProcessing
              ? 'bg-blue-600 hover:bg-blue-700 shadow-lg hover:shadow-xl transform hover:scale-105'
              : 'bg-gray-400 cursor-not-allowed'
          }`}
        >
          {isProcessing ? (
            <span className="flex items-center gap-2">
              <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Processing...
            </span>
          ) : (
            'Run EDD Analysis'
          )}
        </button>
      </div>
    </div>
  );
}
