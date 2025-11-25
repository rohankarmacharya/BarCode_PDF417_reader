# Document Scanner Application

A full-stack web application for scanning and processing documents (barcodes, PDF417 codes, checkbooks, and cards) with PDF report generation.

## Features

- **Barcode Scanning**: Decode 1D and 2D barcodes using pyzbar
- **PDF417 Decoding**: Extract data from PDF417 codes
- **Document Upload**: Upload checkbook and card images (front/back)
- **PDF Report Generation**: Combine all scanned data into a downloadable PDF
- **Session Management**: Upload multiple documents and reset sessions
- **Responsive UI**: Clean, modern interface built with React and Tailwind CSS

## Tech Stack

### Backend
- **Framework**: FastAPI
- **Image Processing**: OpenCV, Pillow
- **Barcode Decoding**: pyzbar
- **PDF417 Decoding**: pdf417decoder
- **PDF Generation**: reportlab
- **Server**: Uvicorn

### Frontend
- **Framework**: React 18
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **HTTP Client**: Axios

## Installation

### Backend Setup

1. Navigate to the backend directory:
\`\`\`bash
cd backend
\`\`\`

2. Create a virtual environment:
\`\`\`bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
\`\`\`

3. Install dependencies:
\`\`\`bash
pip install -r requirements.txt
\`\`\`

4. Create `.env` file (optional):
\`\`\`bash
cp .env.example .env
\`\`\`

5. Run the server:
\`\`\`bash
python main.py
\`\`\`

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
\`\`\`bash
cd frontend
\`\`\`

2. Install dependencies:
\`\`\`bash
npm install
\`\`\`

3. Start the development server:
\`\`\`bash
npm run dev
\`\`\`

The application will be available at `http://localhost:5173`

## API Endpoints

### Health Check
- **GET** `/health` - Check if API is running

### Session Management
- **GET** `/session` - Get current session data
- **POST** `/reset` - Clear all uploads and reset session

### Upload Endpoints
- **POST** `/upload/barcode` - Upload and decode barcode image
- **POST** `/upload/pdf417` - Upload and decode PDF417 image
- **POST** `/upload/checkbook` - Upload checkbook scan
- **POST** `/upload/card` - Upload card front and/or back

### Report Generation
- **GET** `/generate-pdf` - Generate and download combined PDF report

## Usage

1. Start both backend and frontend servers
2. Open the application in your browser
3. Upload documents using the scanner cards:
   - Barcode Scanner: Upload barcode images
   - PDF417 Scanner: Upload PDF417 code images
   - Checkbook Scanner: Upload checkbook scans
   - Card Scanner: Upload card front and back
4. View uploaded items in the Report section
5. Click "Generate & Download PDF" to create a combined report
6. Click "Reset Session" to clear all uploads and start over

## File Structure

\`\`\`
project/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── decoders.py          # Image decoding logic
│   ├── pdf_generator.py     # PDF report generation
│   ├── config.py            # Configuration
│   ├── requirements.txt     # Python dependencies
│   └── .env.example         # Environment variables template
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Main app component
│   │   ├── components/      # React components
│   │   ├── App.css          # Styles
│   │   ├── main.jsx         # Entry point
│   │   └── index.css        # Global styles
│   ├── package.json         # Node dependencies
│   ├── vite.config.js       # Vite configuration
│   ├── tailwind.config.js   # Tailwind configuration
│   └── postcss.config.js    # PostCSS configuration
└── README.md
\`\`\`

## Troubleshooting

### Backend Issues

**"Failed to fetch" error in frontend**
- Ensure backend is running on `http://localhost:8000`
- Check CORS configuration in `main.py`
- Verify all dependencies are installed

**Barcode/PDF417 not detected**
- Ensure image quality is good
- Try different image formats (PNG, JPG, BMP)
- Check image resolution (higher resolution images work better)

### Frontend Issues

**Vite dev server not starting**
- Clear node_modules and reinstall: `rm -rf node_modules && npm install`
- Check Node.js version (requires Node 14+)

**Tailwind styles not applying**
- Ensure Tailwind CSS is properly configured
- Run `npm run build` to rebuild

## Development

### Adding New Decoders

1. Create a new decoder class in `backend/decoders.py`
2. Add corresponding endpoint in `backend/main.py`
3. Create React component in `frontend/src/components/`
4. Add component to `frontend/src/App.jsx`

### Customizing PDF Report

Edit `backend/pdf_generator.py` to modify:
- Report layout and styling
- Included data fields
- Image sizing and positioning

## License

MIT

## Support

For issues or questions, please open an issue in the repository.
