# Docu-Mentor

Docu-Mentor is an AI-powered documentation assistant that automatically suggests docstrings for Python functions in your pull requests. It integrates with GitHub as a GitHub App and uses OpenAI's GPT models to generate high-quality documentation.

## Features

- 🤖 Automatic docstring generation for new Python functions
- 🔍 Pull request analysis and diff parsing
- 💬 Intelligent comment suggestions
- 🔒 Secure GitHub App integration
- 📝 Google Style Python docstrings

## Architecture

The project consists of two main components:

### Backend (FastAPI)
- Handles GitHub webhooks
- Processes pull request diffs
- Generates docstrings using OpenAI
- Posts suggestions as PR comments

### Infrastructure (AWS)
- Runs on AWS ECS Fargate
- Load balanced with ALB
- Containerized with Docker
- Infrastructure as Code using Terraform

## Prerequisites

- Python 3.11+
- Node.js 18+
- Docker
- AWS CLI
- Terraform
- GitHub App credentials

## Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/docu-mentor.git
   cd docu-mentor
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**
   Create a `.env` file in the backend directory:
   ```
   GITHUB_APP_ID=your_app_id
   GITHUB_WEBHOOK_SECRET=your_webhook_secret
   GITHUB_PRIVATE_KEY_PEM_PATH=./private-key.pem
   OPENAI_API_KEY=your_openai_api_key
   ```

4. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

## Development

### Running the Backend
```bash
cd backend
uvicorn main:app --reload
```
The API will be available at `http://localhost:8000`

### Running the Frontend
```bash
cd frontend
npm run dev
```
The frontend will be available at `http://localhost:5173`

## Deployment

### Infrastructure Setup
```bash
cd terraform
terraform init
terraform apply
```

### CI/CD

The project includes GitHub Actions workflows for:
- Backend CI (`ci.yml`): Runs tests and linting
- Backend CD (`cd.yml`): Builds and deploys to AWS

## API Endpoints

- `GET /health`: Health check endpoint
- `POST /api/v1/webhook/github`: GitHub webhook endpoint

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- OpenAI for their powerful language models
- FastAPI for the excellent web framework
- GitHub for their comprehensive API