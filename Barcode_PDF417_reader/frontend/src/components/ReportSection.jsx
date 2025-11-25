"use client";

import React, { useState } from "react";
import axios from "axios";

function ReportSection({ sessionData, onReset, loading }) {
  const [generating, setGenerating] = useState(false);
  const [hasUploads, setHasUploads] = useState(false);
  const [selectedItems, setSelectedItems] = useState({
    barcode: true,
    pdf417: true,
    checkbook: true,
    card_front: true,
    card_back: true,
  });
  const [showSelectionModal, setShowSelectionModal] = useState(false);

  React.useEffect(() => {
    if (sessionData) {
      const hasData =
        sessionData.barcode ||
        sessionData.pdf417 ||
        sessionData.checkbook ||
        sessionData.card_front ||
        sessionData.card_back;
      setHasUploads(!!hasData);
    }
  }, [sessionData]);

  const handleItemToggle = (item) => {
    setSelectedItems((prev) => ({
      ...prev,
      [item]: !prev[item],
    }));
  };

  const handleGenerateSelectivePDF = async () => {
    try {
      setGenerating(true);
      const response = await axios.post(
        "http://localhost:8000/generate-pdf-selective",
        selectedItems,
        {
          responseType: "blob",
        }
      );

      const disposition = response.headers["content-disposition"] || "";
      let filename = "scan_report.pdf";
      const match = disposition.match(/filename="?([^";]+)"?/i);
      if (match && match[1]) {
        filename = match[1];
      }

      const url = window.URL.createObjectURL(
        new Blob([response.data], { type: "application/pdf" })
      );
      // Open in a new tab so the user can choose where/how to save.
      window.open(url, "_blank");
      setShowSelectionModal(false);
    } catch (error) {
      console.error("Failed to generate PDF:", error);
    } finally {
      setGenerating(false);
    }
  };

  const handleGeneratePDF = async () => {
    try {
      setGenerating(true);
      const response = await axios.get("http://localhost:8000/generate-pdf", {
        responseType: "blob",
      });

      const disposition = response.headers["content-disposition"] || "";
      let filename = "scan_report.pdf";
      const match = disposition.match(/filename="?([^";]+)"?/i);
      if (match && match[1]) {
        filename = match[1];
      }

      const url = window.URL.createObjectURL(
        new Blob([response.data], { type: "application/pdf" })
      );
      // Open in a new tab so the user can review and then choose Save As.
      window.open(url, "_blank");
    } catch (error) {
      console.error("Failed to generate PDF:", error);
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 border border-slate-200">
      <h2 className="text-xl font-semibold text-slate-900 mb-4">Report</h2>

      {sessionData && (
        <div className="mb-6 p-4 bg-slate-50 rounded-lg border border-slate-200">
          <h3 className="font-medium text-slate-900 mb-3">Uploaded Items:</h3>
          <ul className="space-y-2 text-sm text-slate-700">
            {sessionData.barcode && (
              <li className="flex items-center">
                <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                Barcode
              </li>
            )}
            {sessionData.pdf417 && (
              <li className="flex items-center">
                <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                PDF417
              </li>
            )}
            {sessionData.checkbook && (
              <li className="flex items-center">
                <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                Checkbook
              </li>
            )}
            {sessionData.card_front && (
              <li className="flex items-center">
                <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                Card Front
              </li>
            )}
            {sessionData.card_back && (
              <li className="flex items-center">
                <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                Card Back
              </li>
            )}
            {!hasUploads && (
              <li className="text-slate-500">No items uploaded yet</li>
            )}
          </ul>
        </div>
      )}

      <div className="flex gap-3">
        <button
          onClick={handleGeneratePDF}
          disabled={!hasUploads || generating}
          className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-300 text-white font-medium py-2 px-4 rounded-lg transition-colors"
        >
          {generating ? "Generating..." : "Generate All PDF"}
        </button>
        <button
          onClick={() => setShowSelectionModal(true)}
          disabled={!hasUploads || generating}
          className="flex-1 bg-purple-600 hover:bg-purple-700 disabled:bg-slate-300 text-white font-medium py-2 px-4 rounded-lg transition-colors"
        >
          {generating ? "Generating..." : "Select & Generate PDF"}
        </button>
        <button
          onClick={onReset}
          disabled={loading || !hasUploads}
          className="flex-1 bg-slate-600 hover:bg-slate-700 disabled:bg-slate-300 text-white font-medium py-2 px-4 rounded-lg transition-colors"
        >
          {loading ? "Resetting..." : "Reset Session"}
        </button>
      </div>

      {showSelectionModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold text-slate-900 mb-4">
              Select Items for PDF
            </h3>

            <div className="space-y-3 mb-6">
              {sessionData?.barcode && (
                <label className="flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={selectedItems.barcode}
                    onChange={() => handleItemToggle("barcode")}
                    className="w-4 h-4 text-blue-600 rounded"
                  />
                  <span className="ml-3 text-slate-700">Barcode</span>
                </label>
              )}
              {sessionData?.pdf417 && (
                <label className="flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={selectedItems.pdf417}
                    onChange={() => handleItemToggle("pdf417")}
                    className="w-4 h-4 text-blue-600 rounded"
                  />
                  <span className="ml-3 text-slate-700">PDF417</span>
                </label>
              )}
              {sessionData?.checkbook && (
                <label className="flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={selectedItems.checkbook}
                    onChange={() => handleItemToggle("checkbook")}
                    className="w-4 h-4 text-blue-600 rounded"
                  />
                  <span className="ml-3 text-slate-700">Checkbook</span>
                </label>
              )}
              {sessionData?.card_front && (
                <label className="flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={selectedItems.card_front}
                    onChange={() => handleItemToggle("card_front")}
                    className="w-4 h-4 text-blue-600 rounded"
                  />
                  <span className="ml-3 text-slate-700">Card Front</span>
                </label>
              )}
              {sessionData?.card_back && (
                <label className="flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={selectedItems.card_back}
                    onChange={() => handleItemToggle("card_back")}
                    className="w-4 h-4 text-blue-600 rounded"
                  />
                  <span className="ml-3 text-slate-700">Card Back</span>
                </label>
              )}
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => setShowSelectionModal(false)}
                className="flex-1 bg-slate-300 hover:bg-slate-400 text-slate-900 font-medium py-2 px-4 rounded-lg transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleGenerateSelectivePDF}
                disabled={generating}
                className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-300 text-white font-medium py-2 px-4 rounded-lg transition-colors"
              >
                {generating ? "Generating..." : "Generate PDF"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default ReportSection;
