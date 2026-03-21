import React, { useCallback, useState } from 'react';

interface UploadZoneProps {
  onFileUpload: (data: any) => void;
  isProcessing: boolean;
}

export const UploadZone: React.FC<UploadZoneProps> = ({ onFileUpload, isProcessing }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [fileName, setFileName] = useState<string | null>(null);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDragIn = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.dataTransfer.items && e.dataTransfer.items.length > 0) {
      setIsDragging(true);
    }
  }, []);

  const handleDragOut = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      processFile(file);
    }
  }, []);

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      processFile(file);
    }
  }, []);

  const processFile = (file: File) => {
    setFileName(file.name);
    
    // Check if it's a JSON file
    if (file.name.endsWith('.json') || file.type === 'application/json') {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const json = JSON.parse(e.target?.result as string);
          onFileUpload(json);
        } catch (error) {
          alert('Invalid JSON file. Please upload a valid KYC document.');
          setFileName(null);
        }
      };
      reader.readAsText(file);
    } else if (
      file.type === 'application/pdf' || 
      file.type === 'image/jpeg' || 
      file.type === 'image/jpg' || 
      file.type === 'image/png'
    ) {
      // For PDF and images, pass the file directly
      // The backend will handle conversion and extraction
      onFileUpload(file);
    } else {
      alert('Unsupported file type. Please upload PDF, JPG, PNG, or JSON files.');
      setFileName(null);
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div
        className={`modern-card relative border-2 border-dashed rounded-xl p-8 transition-all duration-300 ease-out ${
          isDragging
            ? 'border-blue-400 bg-gradient-to-br from-blue-50 to-sky-50 scale-[1.02] shadow-xl'
            : 'border-gray-300 bg-white/80 hover:border-blue-300 hover:bg-white hover:shadow-lg'
        } ${isProcessing ? 'opacity-50 pointer-events-none' : ''}`}
        onDragEnter={handleDragIn}
        onDragLeave={handleDragOut}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        style={{ backdropFilter: 'blur(8px)' }}
      >
        <input
          type="file"
          id="file-upload"
          className="hidden"
          accept="application/pdf,image/jpeg,image/jpg,image/png,.json"
          onChange={handleFileInput}
          disabled={isProcessing}
        />
        
        <div className="text-center">
          <svg
            className={`mx-auto h-12 w-12 transition-all duration-300 ${
              isDragging ? 'text-blue-500 scale-110' : 'text-gray-400 hover:text-blue-400'
            }`}
            stroke="currentColor"
            fill="none"
            viewBox="0 0 48 48"
            aria-hidden="true"
          >
            <path
              d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
              strokeWidth={2}
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
          
          <div className="mt-4">
            <label
              htmlFor="file-upload"
              className="cursor-pointer text-blue-600 hover:text-blue-700 font-semibold text-lg transition-all duration-200 hover:scale-105 inline-block"
            >
              Upload a KYC document
            </label>
            <p className="text-gray-600 text-sm mt-2 font-medium">or drag and drop</p>
          </div>
          
          <p className="text-xs text-gray-500 mt-2">Supports PDF, JPG, PNG, and JSON formats</p>
          
          {fileName && (
            <div className="mt-4 p-3 bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg border border-green-200 animate-[slideIn_0.3s_ease-out] shadow-sm">
              <p className="text-sm text-green-800 font-medium flex items-center justify-center gap-2">
                <span className="text-green-600">✓</span>
                <span className="font-semibold">Loaded:</span> {fileName}
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Acceptable Document Types */}
      <div className="mt-6 p-5 bg-gradient-to-br from-blue-50 via-sky-50 to-blue-50 border border-blue-200 rounded-xl shadow-sm modern-card glass-effect">
        <h3 className="text-sm font-bold text-blue-900 mb-3 text-center tracking-wide uppercase">
          Acceptable KYC Documents
        </h3>
        <div className="flex gap-3 justify-center flex-wrap">
          <div className="flex items-center gap-2 px-4 py-2 bg-white/70 rounded-lg text-sm text-blue-800 font-medium shadow-sm hover:shadow-md hover:scale-105 transition-all duration-200 cursor-default border border-blue-100">
            <span className="text-xl">🪪</span>
            <span>PAN Card</span>
          </div>
          <div className="flex items-center gap-2 px-4 py-2 bg-white/70 rounded-lg text-sm text-blue-800 font-medium shadow-sm hover:shadow-md hover:scale-105 transition-all duration-200 cursor-default border border-blue-100">
            <span className="text-xl">🛂</span>
            <span>Passport</span>
          </div>
          <div className="flex items-center gap-2 px-4 py-2 bg-white/70 rounded-lg text-sm text-blue-800 font-medium shadow-sm hover:shadow-md hover:scale-105 transition-all duration-200 cursor-default border border-blue-100">
            <span className="text-xl">🚗</span>
            <span>Driving License</span>
          </div>
        </div>
        <p className="text-xs text-blue-700 mt-4 text-center font-medium">
          📋 Please ensure your document is clear and all details are visible
        </p>
      </div>
    </div>
  );
};