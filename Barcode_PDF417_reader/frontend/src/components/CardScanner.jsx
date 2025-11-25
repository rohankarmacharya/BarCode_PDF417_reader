"use client";

import { useState } from "react";
import axios from "axios";

function CardScanner({ onSuccess, onError }) {
  const [loading, setLoading] = useState(false);
  const [frontResult, setFrontResult] = useState(null);
  const [backResult, setBackResult] = useState(null);
  const [frontFileName, setFrontFileName] = useState(null);
  const [backFileName, setBackFileName] = useState(null);

  const handleFileUpload = async (event, side) => {
    const file = event.target.files[0];
    if (!file) return;

    try {
      setLoading(true);

      const formData = new FormData();
      if (side === "front") {
        formData.append("front", file);
        setFrontFileName(file.name);
      } else {
        formData.append("back", file);
        setBackFileName(file.name);
      }

      const response = await axios.post(
        "http://localhost:8000/upload/card",
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
        }
      );

      if (side === "front") {
        setFrontResult(response.data.data.front);
      } else {
        setBackResult(response.data.data.back);
      }
      onSuccess();
    } catch (error) {
      const errorMsg = error.response?.data?.error || "Failed to upload card";
      onError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 border border-slate-200">
      <h2 className="text-xl font-semibold text-slate-900 mb-4">
        Card Scanner
      </h2>

      <div className="space-y-4">
        {/* Front */}
        <div>
          <p className="text-sm font-medium text-slate-700 mb-2">Front</p>
          <div className="border-2 border-dashed border-slate-300 rounded-lg p-6 text-center hover:border-blue-400 transition-colors cursor-pointer">
            <input
              type="file"
              accept="image/*"
              onChange={(e) => handleFileUpload(e, "front")}
              disabled={loading}
              className="hidden"
              id="card-front-input"
            />
            <label htmlFor="card-front-input" className="cursor-pointer block">
              <svg
                className="mx-auto h-10 w-10 text-slate-400 mb-2"
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
              <p className="text-slate-600 text-sm font-medium">
                {loading ? "Processing..." : "Upload front"}
              </p>
            </label>
          </div>
          {frontFileName && (
            <p className="text-xs text-slate-600 mt-2">File: {frontFileName}</p>
          )}
          {frontResult && (
            <div className="mt-2 p-2 bg-green-50 border border-green-200 rounded text-xs">
              <p className="text-green-800">Uploaded successfully</p>
            </div>
          )}
        </div>

        {/* Back */}
        <div>
          <p className="text-sm font-medium text-slate-700 mb-2">Back</p>
          <div className="border-2 border-dashed border-slate-300 rounded-lg p-6 text-center hover:border-blue-400 transition-colors cursor-pointer">
            <input
              type="file"
              accept="image/*"
              onChange={(e) => handleFileUpload(e, "back")}
              disabled={loading}
              className="hidden"
              id="card-back-input"
            />
            <label htmlFor="card-back-input" className="cursor-pointer block">
              <svg
                className="mx-auto h-10 w-10 text-slate-400 mb-2"
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
              <p className="text-slate-600 text-sm font-medium">
                {loading ? "Processing..." : "Upload back"}
              </p>
            </label>
          </div>
          {backFileName && (
            <p className="text-xs text-slate-600 mt-2">File: {backFileName}</p>
          )}
          {backResult && (
            <div className="mt-2 p-2 bg-green-50 border border-green-200 rounded text-xs">
              <p className="text-green-800">Uploaded successfully</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default CardScanner;
