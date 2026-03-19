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
  };

  const loadSampleDocument = (sampleType: string) => {
    fetch(`/samples/${sampleType}.json`)
      .then(res => res.json())
      .then(data => {
        setFileName(`${sampleType}.json`);
        onFileUpload(data);
      })
      .catch(err => {
        console.error('Error loading sample:', err);
        alert('Could not load sample document');
      });
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div
        className={`relative border-2 border-dashed rounded-lg p-8 transition-all duration-200 ${
          isDragging
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 hover:border-gray-400'
        } ${isProcessing ? 'opacity-50 pointer-events-none' : ''}`}
        onDragEnter={handleDragIn}
        onDragLeave={handleDragOut}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          type="file"
          id="file-upload"
          className="hidden"
          accept=".json"
          onChange={handleFileInput}
          disabled={isProcessing}
        />
        
        <div className="text-center">
          <svg
            className="mx-auto h-12 w-12 text-gray-400"
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
              className="cursor-pointer text-blue-600 hover:text-blue-500 font-medium"
            >
              Upload a KYC document
            </label>
            <p className="text-gray-500 text-sm mt-1">or drag and drop</p>
          </div>
          
          <p className="text-xs text-gray-500 mt-2">JSON files only</p>
          
          {fileName && (
            <div className="mt-4 p-3 bg-green-50 rounded-md">
              <p className="text-sm text-green-800">
                <span className="font-medium">Loaded:</span> {fileName}
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Sample Documents */}
      <div className="mt-6">
        <p className="text-sm text-gray-600 mb-3 text-center">
          Or try a sample document:
        </p>
        <div className="flex gap-3 justify-center flex-wrap">
          <button
            onClick={() => loadSampleDocument('pan_card')}
            disabled={isProcessing}
            className="px-4 py-2 bg-white border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            🪪 PAN Card
          </button>
          <button
            onClick={() => loadSampleDocument('passport')}
            disabled={isProcessing}
            className="px-4 py-2 bg-white border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            🛂 Passport
          </button>
          <button
            onClick={() => loadSampleDocument('drivers_license')}
            disabled={isProcessing}
            className="px-4 py-2 bg-white border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            🚗 Driver's License
          </button>
        </div>
      </div>
    </div>
  );
};