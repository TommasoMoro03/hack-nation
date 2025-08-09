# FinDocGPT 💰

An AI-powered financial document analysis and investment strategy platform built for hackathon challenges. FinDocGPT combines document processing, market forecasting, and conversational AI to provide comprehensive financial insights.

## 🚀 Features

- **Document Analysis**: Upload and process PDF financial documents with intelligent text extraction
- **AI-Powered Chat**: Conversational interface with multiple AI models (OpenAI GPT-4, Claude, Gemini)
- **Financial Insights**: Analyze company filings, earnings reports, and SEC documents
- **Vector Search**: Semantic search through processed documents using ChromaDB
- **Company & Year Filtering**: Organized document retrieval by company and year
- **Modern UI**: Responsive design with dark/light mode support

## 🏗️ Architecture

This is a full-stack application with:

- **Frontend**: Next.js 15 with React 19, TypeScript, and Tailwind CSS
- **Backend**: FastAPI with Python for document processing and API endpoints
- **Database**: ChromaDB for vector embeddings and semantic search
- **AI Integration**: Multiple AI models via API integrations

## 📁 Project Structure

```
hack-nation/
├── client/                     # Next.js frontend application
│   ├── app/                   # Next.js App Router
│   ├── components/            # React components
│   │   ├── ui/               # shadcn/ui component library
│   │   ├── ai-prompt.tsx     # Main AI chat interface
│   │   ├── file-upload-dialog.tsx
│   │   └── selected-files-display.tsx
│   ├── hooks/                # Custom React hooks
│   ├── lib/                  # Utilities and stores
│   └── package.json
├── server/                    # FastAPI backend application
│   ├── api/                  # API routes
│   │   └── v1/endpoints/     # API endpoints
│   ├── core/                 # Core configuration
│   ├── services/             # Business logic
│   ├── storage/              # Database layer
│   ├── main.py               # FastAPI application entry
│   └── requirements.txt
└── README.md
```

## 🛠️ Tech Stack

### Frontend

- **Next.js 15** - React framework with App Router
- **React 19** - UI library with latest features
- **TypeScript** - Type-safe development
- **Tailwind CSS v4** - Utility-first styling
- **shadcn/ui** - Modern component library
- **Zustand** - State management
- **Motion** (Framer Motion) - Animations
- **Lucide React** - Icon library

### Backend

- **FastAPI** - Modern Python web framework
- **ChromaDB** - Vector database for embeddings
- **LangChain** - Text processing and chunking
- **PyPDF** - PDF text extraction
- **OpenAI API** - AI model integration
- **Uvicorn** - ASGI server

## ⚡ Quick Start

### Prerequisites

- Node.js 18+ and npm/bun
- Python 3.8+
- Git

### Frontend Setup

```bash
cd client
npm install
npm run dev
```

The frontend will be available at `http://localhost:3000`

### Backend Setup

```bash
cd server
pip install -r requirements.txt
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## 📡 API Endpoints

### Document Management

- `POST /api/v1/documents/upload` - Upload PDF documents for processing
- `GET /api/v1/documents/files` - Get all processed files
- `GET /api/v1/documents/files/company/{company}` - Get files by company
- `GET /api/v1/documents/files/year/{year}` - Get files by year

## 💡 Usage

1. **Upload Documents**: Use the file upload dialog to add PDF financial documents
2. **Ask Questions**: Type financial questions in the AI prompt interface
3. **Get Insights**: Receive AI-powered analysis based on uploaded documents
4. **Explore Data**: Filter and search through processed documents

## 🔧 Development

### Frontend Commands

```bash
npm run dev        # Start development server
npm run build      # Build for production
npm run start      # Start production server
npm run lint       # Run ESLint
```

### Backend Commands

```bash
uvicorn main:app --reload    # Start development server
```

## 🏆 Hackathon Features

This project was built for hackathon challenges and includes:

- **Rapid Prototyping**: Quick setup and deployment
- **Scalable Architecture**: Modular design for easy feature additions
- **AI Integration**: Multiple AI models for diverse use cases
- **Document Processing**: Automated PDF analysis and indexing
- **Modern UI/UX**: Professional interface with smooth animations

## 📄 File Processing

The system automatically:

1. Extracts text from uploaded PDF documents
2. Parses filenames for company and year metadata (format: `COMPANY_YEAR.pdf`)
3. Chunks text using LangChain's RecursiveCharacterTextSplitter
4. Creates vector embeddings using ChromaDB
5. Enables semantic search across document content

## 🎨 UI Components

Built with shadcn/ui components including:

- Responsive chat interface
- File upload with drag & drop
- AI model selection dropdown
- Dark/light mode toggle
- Animated transitions

## 🔒 Security

- Input validation on all API endpoints
- File type restrictions for uploads
- Error handling and logging
- Secure file processing pipeline

## 🤝 Contributing

This is a hackathon project, but contributions are welcome:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📜 License

This project is built for educational and hackathon purposes.

---

**Built with ❤️ for financial innovation**
