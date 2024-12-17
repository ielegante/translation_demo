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

- **Backend**: FastAPI application handling the translation logic
- **Frontend**: Simple web interface using FastAPI + Jinja2 templates

## Prerequisites

- Docker and Docker Compose
- Anthropic API key (for Claude 3)
- Python 3.9+

## Environment Setup

1. Clone the repository: 