# Barcode & PDF417 Document Scanner

A comprehensive full-stack web application for scanning, processing, and generating reports from various document types including barcodes, PDF417 codes, checkbooks, and cards.

![Document Scanner](https://via.placeholder.com/1200x600/4F46E5/FFFFFF?text=Barcode+PDF417+Scanner)

## ✨ Features

- **Multi-Format Scanning**

  - 1D and 2D barcode decoding
  - PDF417 code extraction and parsing
  - Checkbook image processing
  - Front/back card scanning

- **Advanced Processing**

  - Image enhancement for better recognition
  - Multi-angle barcode detection
  - AAMVA standard parsing for driver's licenses
  - Automatic data validation

- **User Experience**
  - Modern, responsive UI with dark/light mode
  - Real-time feedback and previews
  - Session management
  - Downloadable PDF reports
  - Cross-platform compatibility

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn
- OpenCV (for advanced image processing)

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/barcode-pdf417-reader.git
   cd barcode-pdf417-reader
   ```

2. **Set up the backend**

   ```bash
   # Navigate to backend directory
   cd backend

   # Create and activate virtual environment
   python -m venv venv
   # On Windows: venv\Scripts\activate
   source venv/bin/activate

   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Set up the frontend**

   ```bash
   # Navigate to frontend directory
   cd ../frontend

   # Install dependencies
   npm install
   ```

### Running the Application

1. **Start the backend server**

   ```bash
   cd backend
   python main.py
   ```

   The API will be available at `http://localhost:8000`

2. **Start the frontend development server**
   ```bash
   cd frontend
   npm run dev
   ```
   The application will be available at `http://localhost:5173`

## 🛠️ API Documentation

### Base URL

```
http://localhost:8000
```

### Endpoints

#### Health Check

- `GET /health` - Verify API status

#### Session Management

- `GET /session` - Retrieve current session data
- `POST /reset` - Clear all uploads and reset session

#### Document Processing

- `POST /upload/barcode` - Process barcode images
- `POST /upload/pdf417` - Decode PDF417 codes
- `POST /upload/checkbook` - Handle checkbook scans
- `POST /upload/card` - Process card images (front/back)

#### Report Generation

- `GET /generate-pdf` - Generate and download PDF report

## 📁 Project Structure

```
barcode-pdf417-reader/
├── backend/                  # FastAPI backend
│   ├── main.py              # Main application and routes
│   ├── decoders.py          # Barcode and PDF417 decoding logic
│   ├── pdf_generator.py     # PDF report generation
│   ├── config.py            # Application configuration
│   ├── requirements.txt     # Python dependencies
│   └── uploads/             # Temporary file storage
│
├── frontend/                # React frontend
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   │   ├── BarcodeScanner.jsx
│   │   │   ├── PDF417Scanner.jsx
│   │   │   ├── CheckbookScanner.jsx
│   │   │   ├── CardScanner.jsx
│   │   │   └── ReportSection.jsx
│   │   ├── App.jsx          # Main application component
│   │   └── main.jsx         # Application entry point
│   ├── public/              # Static assets
│   ├── package.json         # Frontend dependencies
│   └── vite.config.js       # Vite configuration
│
├── .gitignore
└── README.md
```

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest
```

### Frontend Tests

```bash
cd frontend
npm test
```

## 🐛 Troubleshooting

### Common Issues

**Barcode/PDF417 Not Detected**

- Ensure good lighting conditions
- Use high-resolution images
- Try different angles and distances
- Verify image format (PNG, JPG, BMP supported)

**Installation Problems**

- Ensure all system dependencies are installed
- Check Python and Node.js versions
- Clear npm/pip caches if needed

**API Connection Issues**

- Verify backend server is running
- Check CORS settings in `backend/main.py`
- Ensure no port conflicts (default: 8000 for backend, 5173 for frontend)

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📧 Contact

For support or questions, please open an issue in the repository or contact [your-email@example.com](mailto:your-email@example.com).

---

<div align="center">
  Made with ❤️ by Your Name | [![GitHub](https://img.shields.io/github/followers/yourusername?style=social)](https://github.com/yourusername)
</div>
