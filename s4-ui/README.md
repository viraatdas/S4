# S4 UI - Modern Semantic Search UI

<div align="center">
  <img src="public/logo512.png" alt="S4 Logo" width="120" />
  <h3 align="center">S4 UI - Modern Semantic Search Interface</h3>
  <p align="center">A sleek, responsive React frontend for the S4 Semantic Search Service</p>
</div>

<p align="center">
  <a href="#key-features">Key Features</a> •
  <a href="#getting-started">Getting Started</a> •
  <a href="#development">Development</a> •
  <a href="#deployment">Deployment</a> •
  <a href="#screenshots">Screenshots</a> •
  <a href="#tech-stack">Tech Stack</a>
</p>

## Key Features

- **Modern, Responsive Design**: Beautiful UI that works on desktop and mobile
- **Intuitive Search Interface**: Simple yet powerful search functionality
- **Multi-format Content Management**: Upload, view, and delete documents, videos, and audio files
- **Semantic Video & Audio Search**: Extract and search meaning from video and audio content
- **Usage Statistics**: Track document count, tokens, and search queries
- **Secure Authentication**: API key-based authentication with secure storage
- **Tenant Management**: For admin users to manage multiple tenants (coming soon)

## Getting Started

### Prerequisites

- Node.js 14+ and npm
- S4 backend service running (see main [S4 README](../README.md))

### Installation

1. Clone the repository (if you haven't already):
   ```bash
   git clone https://github.com/yourusername/S4.git
   cd S4/s4-ui
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create a `.env` file in the root directory:
   ```
   REACT_APP_API_URL=http://localhost:8000/api
   ```

4. Start the development server:
   ```bash
   npm start
   ```

5. Open [http://localhost:3000](http://localhost:3000) to view the application.

## Development

### Project Structure

```
s4-ui/
├── public/
│   ├── index.html
│   └── favicon.ico
├── src/
│   ├── components/        # Reusable UI components
│   ├── pages/             # Page components
│   ├── services/          # API services
│   ├── styles/            # CSS styles
│   ├── App.js             # Main application component
│   └── index.js           # Entry point
├── .env                   # Environment variables
└── package.json           # Dependencies and scripts
```

### Available Scripts

- `npm start` - Starts the development server
- `npm test` - Runs tests
- `npm run build` - Builds the app for production
- `npm run eject` - Ejects from Create React App

## Media Processing Capabilities

S4 UI provides a user-friendly interface for S4's powerful media processing capabilities:

### Video Search

Upload video files (MP4, MOV, AVI, etc.) and S4 will:
- Extract audio and transcribe speech to text
- Process visual content for scene understanding (if enabled)
- Create searchable embeddings from the content
- Allow you to search for moments or concepts within videos

### Audio Search

Similar to video, S4 processes audio files (MP3, WAV) to:
- Transcribe spoken content
- Analyze audio patterns
- Create semantic embeddings
- Enable natural language search across your audio library

### Document Search

Traditional document formats (PDF, DOCX, TXT) are processed to:
- Extract text content
- Preserve formatting where relevant
- Create searchable semantic embeddings
- Allow searching across your entire document repository

## Deployment

### Building for Production

1. Build the application:
   ```bash
   npm run build
   ```

2. The build files will be in the `build/` directory.

### Deployment Options

#### Docker

A Dockerfile is provided to containerize the UI:

```bash
docker build -t s4-ui .
docker run -p 3000:80 s4-ui
```

#### AWS S3 + CloudFront

1. Build the application
2. Upload the contents of the `build/` directory to an S3 bucket
3. Configure CloudFront to serve the S3 bucket

#### Netlify/Vercel

Connect your repository to Netlify or Vercel for automatic deployments.

## Screenshots

### Login Page
![Login Page](docs/images/login-screenshot.png)

### Dashboard
![Dashboard](docs/images/dashboard-screenshot.png)

### Document Upload
![Document Upload](docs/images/upload-screenshot.png)

### Search Results
![Search Results](docs/images/search-screenshot.png)

## Tech Stack

- **React**: UI library
- **React Router**: Navigation
- **React Bootstrap**: UI components
- **Axios**: API requests
- **Formik & Yup**: Form handling and validation
- **React Icons**: Icon library

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

## Acknowledgements

- Create React App
- React Bootstrap
- React Icons
- All contributors to the S4 project

---

<div align="center">
  <sub>Built with ❤️ by the S4 team</sub>
</div> 