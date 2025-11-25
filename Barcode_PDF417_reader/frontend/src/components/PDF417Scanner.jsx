"use client";

import { useState } from "react";
import axios from "axios";

function PDF417Scanner({ onSuccess, onError }) {
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
        "http://localhost:8000/upload/pdf417",
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
        }
      );

      setResult(response.data.data);
      onSuccess();
    } catch (error) {
      const errorMsg = error.response?.data?.error || "Failed to decode PDF417";
      onError(errorMsg);
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 border border-slate-200">
      <h2 className="text-xl font-semibold text-slate-900 mb-4">
        PDF417 Scanner
      </h2>

      <div className="border-2 border-dashed border-slate-300 rounded-lg p-8 text-center hover:border-blue-400 transition-colors cursor-pointer">
        <input
          type="file"
          accept="image/*"
          onChange={handleFileUpload}
          disabled={loading}
          className="hidden"
          id="pdf417-input"
        />
        <label htmlFor="pdf417-input" className="cursor-pointer block">
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
            {loading ? "Processing..." : "Click to upload PDF417 image"}
          </p>
          <p className="text-slate-500 text-sm mt-1">PNG, JPG, BMP</p>
        </label>
      </div>

      {fileName && (
        <p className="text-sm text-slate-600 mt-3">File: {fileName}</p>
      )}

      {result && (
        <div className="mt-4 space-y-3">
          {result.pdf417_data &&
            result.pdf417_data.map((data, idx) => (
              <div
                key={idx}
                className="p-4 bg-green-50 border border-green-200 rounded"
              >
                <p className="text-green-800 font-semibold mb-3">
                  PDF417 Detected - {data.format}
                </p>

                {data.parsed && data.parsed.user && (
                  <div className="space-y-4">
                    {/* Personal Information */}
                    <div className="bg-white p-4 rounded border border-green-100">
                      <h4 className="font-semibold text-slate-900 mb-3">
                        Personal Information
                      </h4>
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="font-medium text-slate-600">
                            Last Name:
                          </span>
                          <p className="text-slate-800">
                            {data.parsed.user.last || "-"}
                          </p>
                        </div>
                        <div>
                          <span className="font-medium text-slate-600">
                            First Name:
                          </span>
                          <p className="text-slate-800">
                            {data.parsed.user.first || "-"}
                          </p>
                        </div>
                        <div>
                          <span className="font-medium text-slate-600">
                            Date of Birth:
                          </span>
                          <p className="text-slate-800">
                            {data.parsed.user.dob || "-"}
                          </p>
                        </div>
                        <div>
                          <span className="font-medium text-slate-600">
                            Sex:
                          </span>
                          <p className="text-slate-800">
                            {data.parsed.user.sex || "-"}
                          </p>
                        </div>
                      </div>
                    </div>

                    {/* Physical Description */}
                    <div className="bg-white p-4 rounded border border-green-100">
                      <h4 className="font-semibold text-slate-900 mb-3">
                        Physical Description
                      </h4>
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="font-medium text-slate-600">
                            Eye Color:
                          </span>
                          <p className="text-slate-800">
                            {data.parsed.user.eyes || "-"}
                          </p>
                        </div>
                        <div>
                          <span className="font-medium text-slate-600">
                            Height:
                          </span>
                          <p className="text-slate-800">
                            {data.parsed.user.height || "-"}
                          </p>
                        </div>
                        <div>
                          <span className="font-medium text-slate-600">
                            Weight:
                          </span>
                          <p className="text-slate-800">
                            {data.parsed.user.weight || "-"}
                          </p>
                        </div>
                      </div>
                    </div>

                    {/* Address */}
                    <div className="bg-white p-4 rounded border border-green-100">
                      <h4 className="font-semibold text-slate-900 mb-3">
                        Address
                      </h4>
                      <div className="space-y-2 text-sm">
                        <div>
                          <span className="font-medium text-slate-600">
                            Street Address:
                          </span>
                          <p className="text-slate-800">
                            {data.parsed.user.street || "-"}
                          </p>
                        </div>
                        <div>
                          <span className="font-medium text-slate-600">
                            City:
                          </span>
                          <p className="text-slate-800">
                            {data.parsed.user.city || "-"}
                          </p>
                        </div>
                        <div className="grid grid-cols-3 gap-4">
                          <div>
                            <span className="font-medium text-slate-600">
                              State:
                            </span>
                            <p className="text-slate-800">
                              {data.parsed.user.state || "-"}
                            </p>
                          </div>
                          <div>
                            <span className="font-medium text-slate-600">
                              Postal Code:
                            </span>
                            <p className="text-slate-800">
                              {data.parsed.user.postal || "-"}
                            </p>
                          </div>
                          <div>
                            <span className="font-medium text-slate-600">
                              Country:
                            </span>
                            <p className="text-slate-800">
                              {data.parsed.user.country || "-"}
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Document Information */}
                    <div className="bg-white p-4 rounded border border-green-100">
                      <h4 className="font-semibold text-slate-900 mb-3">
                        Document Information
                      </h4>
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="font-medium text-slate-600">
                            ID Number:
                          </span>
                          <p className="text-slate-800">
                            {data.parsed.user.id || "-"}
                          </p>
                        </div>
                        <div>
                          <span className="font-medium text-slate-600">
                            Expiration Date:
                          </span>
                          <p className="text-slate-800">
                            {data.parsed.user.expires || "-"}
                          </p>
                        </div>
                        <div>
                          <span className="font-medium text-slate-600">
                            Issue Date:
                          </span>
                          <p className="text-slate-800">
                            {data.parsed.user.issued || "-"}
                          </p>
                        </div>
                        <div>
                          <span className="font-medium text-slate-600">
                            Card Revision Date:
                          </span>
                          <p className="text-slate-800">
                            {data.parsed.user.card_revision || "-"}
                          </p>
                        </div>
                        <div>
                          <span className="font-medium text-slate-600">
                            Country:
                          </span>
                          <p className="text-slate-800">
                            {data.parsed.user.country || "-"}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Raw data fallback */}
                {!data.parsed && (
                  <p className="text-sm text-green-700">
                    <strong>Data:</strong> {data.data}
                  </p>
                )}
              </div>
            ))}
        </div>
      )}
    </div>
  );
}

export default PDF417Scanner;
