"use client";

import { useState } from "react";
import axios from "axios";

function CheckbookScanner({ onSuccess, onError }) {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [fileName, setFileName] = useState(null);

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    try {
      setLoading(true);
      setFileName(file.name);

      const formData = new FormData();
      formData.append("file", file);

      const response = await axios.post(
        "http://localhost:8000/upload/checkbook",
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
        }
      );

      setResult(response.data.data);
      onSuccess();
    } catch (error) {
      const errorMsg =
        error.response?.data?.error || "Failed to upload checkbook";
      onError(errorMsg);
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 border border-slate-200">
      <h2 className="text-xl font-semibold text-slate-900 mb-4">
        Checkbook Scanner
      </h2>

      <div className="border-2 border-dashed border-slate-300 rounded-lg p-8 text-center hover:border-blue-400 transition-colors cursor-pointer">
        <input
          type="file"
          accept="image/*"
          onChange={handleFileUpload}
          disabled={loading}
          className="hidden"
          id="checkbook-input"
        />
        <label htmlFor="checkbook-input" className="cursor-pointer block">
          <svg
            className="mx-auto h-12 w-12 text-slate-400 mb-2"
            stroke="currentColor"
            fill="none"
            viewBox="0 0 48 48"
          >
            <path
              d="M28 8H12a4 4 0 00-4 4v20m32-12v8a4 4 0 01-4 4H12m28-24l-3.172 3.172a4 4 0 01-5.656 0L28 8m0 0V4m0 4v28"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
          <p className="text-slate-600 font-medium">
            {loading ? "Processing..." : "Click to upload checkbook scan"}
          </p>
          <p className="text-slate-500 text-sm mt-1">PNG, JPG, BMP</p>
        </label>
      </div>

      {fileName && (
        <p className="text-sm text-slate-600 mt-3">File: {fileName}</p>
      )}

      {result && (
        <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded">
          <p className="text-green-800 font-medium">Checkbook uploaded!</p>
          <p className="text-sm text-green-700 mt-2">
            <strong>Format:</strong> {result.format} | <strong>Size:</strong>{" "}
            {result.size[0]}x{result.size[1]}
          </p>
        </div>
      )}
    </div>
  );
}

export default CheckbookScanner;
