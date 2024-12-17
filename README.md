# English to Mandarin Translator

A web application that translates English text to Mandarin Chinese using Claude 3 Sonnet. The application includes proofreading of the English text, translation to Mandarin, and quality assessment of the translation.

## Features

- English text proofreading
- Translation to Mandarin Chinese (Singapore localization)
- Quality assessment of translations
- Automatic retry for failed translations
- Web interface for easy interaction
- RESTful API endpoints

## Architecture

The application is split into two main components:

- **Backend**: FastAPI + Langgraph
- **Frontend**: Simple web interface using FastHTML

## Prerequisites
- Docker and Docker Compose
- Anthropic API key (for Claude 3)
- Python 3.12

## Running the application

1. Clone the repository: 
2. Run `docker compose up` to start the application.
3. Open `http://localhost:8080` in your browser to use the application.

## Deploying to Google Cloud Run
Setup continuous deployment for two GCR functions. Have each point to one of the two folders (backend and frontend). Be sure to set the environment variables in the GCR functions.

## Security
Ideally, you would set API keys as an environment variable, rather than pass it into the form.