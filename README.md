# EmailEssence

An intelligent email companion designed to enhance productivity through AI-powered email management and summarization.

## Overview

EmailEssence is a sophisticated email management solution that leverages artificial intelligence to transform how users interact with their inboxes. By providing intelligent email summarization, clutter-free reading experiences, and smart prioritization, EmailEssence helps users focus on what matters most in their communications.

## Key Features

### MVP Features
- 🔐 Secure OAuth 2.0 authentication with email providers
- 🤖 AI-powered email summarization
- 📧 Clean, clutter-free reader view
- 📱 Responsive web interface
- ⚡ Real-time email processing

### Feature Complete (FC) Features
- 🎨 Customizable dashboard with modular components
- 🔍 Advanced keyword analysis and topic identification
- 💻 Cross-platform desktop support via Electron
- 🔄 Incremental email fetching for large inboxes
- 🎯 Smart email prioritization
- 🛠️ Enhanced user preferences and settings

## Technical Stack

### Frontend
- React - Modern UI framework
- Remix - Full-stack web framework
- Electron - Desktop application framework
- JavaScript - Type-safe development

### Backend
- Python - Core backend services
- FastAPI - High-performance API framework
- MongoDB - Flexible document database
- Redis - High-performance caching
- OpenRouter - AI-powered email processing

### Infrastructure
- Express.js - Web server and middleware
- OAuth 2.0 - Secure authentication
- IMAP - Email protocol support

## Getting Started

### Prerequisites
- Node.js (v18 or higher)
- Python (v3.12 or higher)
- MongoDB
- Redis
- UV Package Manager (for Python dependency management)

### Installation

#### Environment Variables
Create a `.env` file in the backend directory using `.env.example` as a template:

#### Backend Setup
We use UV (https://astral.sh/uv) for Python package management. Choose your platform:

##### Windows
```powershell
# Run the PowerShell setup script
.\backend\setup.ps1
```

##### Linux/macOS
```bash
# Run the bash setup script
chmod +x backend/setup.sh
./backend/setup.sh
```

The setup scripts will:
1. Install UV if not present
2. Create a virtual environment
3. Install all development dependencies
4. Set up environment variables

#### Frontend Setup
```bash
cd frontend
npm install
```

## Development

### Starting the Backend
```bash
cd backend
uvicorn main:app --reload
```

### Starting the Frontend
```bash
cd frontend
npm run dev
```

## Documentation

- [Frontend Documentation](https://react.dev/reference/rules)
- [Backend Documentation](https://fastapi.tiangolo.com/)
- [Database Documentation](https://www.mongodb.com/docs/)
- [Authentication Documentation](https://oauth.net/2/)

## Contributing

TODO

## License

TODO

## Authors

- Emma Melkumian
- Joseph Madigan
- Shayan Shahla
- Ritesh Samal
