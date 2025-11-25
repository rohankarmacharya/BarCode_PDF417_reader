"use client"

import { useState, useEffect } from "react"
import BarcodeScanner from "./components/BarcodeScanner"
import PDF417Scanner from "./components/PDF417Scanner"
import CheckbookScanner from "./components/CheckbookScanner"
import CardScanner from "./components/CardScanner"
import ReportSection from "./components/ReportSection"
import "./App.css"

function App() {
  const [sessionData, setSessionData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchSessionData()
  }, [])

  const fetchSessionData = async () => {
    try {
      const response = await fetch("http://localhost:8000/session")
      if (response.ok) {
        const data = await response.json()
        setSessionData(data)
      }
    } catch (err) {
      console.error("Failed to fetch session:", err)
    }
  }

  const handleUploadSuccess = () => {
    fetchSessionData()
    setError(null)
  }

  const handleUploadError = (message) => {
    setError(message)
  }

  const handleReset = async () => {
    try {
      setLoading(true)
      const response = await fetch("http://localhost:8000/reset", {
        method: "POST",
      })
      if (response.ok) {
        setSessionData(null)
        setError(null)
        fetchSessionData()
      }
    } catch (err) {
      setError("Failed to reset session")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <header className="bg-white shadow-sm border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <h1 className="text-3xl font-bold text-slate-900">Document Scanner</h1>
          <p className="text-slate-600 mt-1">Upload and scan documents to generate reports</p>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <BarcodeScanner onSuccess={handleUploadSuccess} onError={handleUploadError} />
          <PDF417Scanner onSuccess={handleUploadSuccess} onError={handleUploadError} />
          <CheckbookScanner onSuccess={handleUploadSuccess} onError={handleUploadError} />
          <CardScanner onSuccess={handleUploadSuccess} onError={handleUploadError} />
        </div>

        <ReportSection sessionData={sessionData} onReset={handleReset} loading={loading} />
      </main>
    </div>
  )
}

export default App
