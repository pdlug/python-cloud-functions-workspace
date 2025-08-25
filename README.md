# Python Cloud Functions Workspace

A Python monorepo using [uv](https://docs.astral.sh/uv/) workspaces that deploys APIs as Google Cloud Functions. This project demonstrates how to structure a monorepo with shared libraries and deployable services.

## Project Structure

```
python-cloud-functions-workspace/
├── libs/
│   ├── core/                # Core business logic and utilities
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── text.py      # Text processing functions
│   │   │   ├── models.py    # Business domain models (TextDocument, etc.)
│   │   └── pyproject.toml
│   └── api/                 # FastAPI library (depends on core)
│       ├── api/
│       │   ├── __init__.py
│       │   └── main.py      # FastAPI app with /hello routes
│       └── pyproject.toml
├── services/
│   └── api-function/        # Cloud Function deployment
│       ├── main.py          # Cloud Functions entry point
│       └── pyproject.toml
├── .github/workflows/
│   └── deploy-cloud-function.yml  # GitHub Actions deployment
└── pyproject.toml          # Workspace configuration
```

## Library Dependencies

This project demonstrates a multi-layer dependency structure:

- **`libs/core`**: Core business logic with simple models like `TextDocument`
- **`libs/api`**: FastAPI web layer that depends on `core` for business logic
- **`services/api-function`**: Cloud Function deployment that depends on `api`

Example dependency chain: `api-function` → `api` → `core`

## API Endpoints

The FastAPI app in `libs/api` provides:

- `GET /hello` - Returns `{"text": "Hello World!"}`
- `POST /hello` - Takes `{"name": "string"}` and returns `{"hello": "string"}`

The `core` library includes a simple `TextDocument` model and `get_word_count()` function that can be shared across services.

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- Google Cloud Platform account
- [gcloud](https://cloud.google.com/sdk/gcloud) CLI (for local deployment)

## Installation

```bash
git clone <your-repo-url>
cd python-cloud-functions-workspace
uv sync
```

## Local Development

Run the API locally:

```bash
cd services/api-function
uv run functions-framework --target=api_function --debug
```

Test the endpoints:

```bash
# GET endpoint
curl http://localhost:8080/hello

# POST endpoint
curl -X POST http://localhost:8080/hello \
  -H "Content-Type: application/json" \
  -d '{"name": "World"}'
```

## Development Tasks

This project uses [Poe the Poet](https://poethepoet.natn.io/) for task management. Available tasks:

```bash
# Type checking with mypy
uv run poe mypy

# Code linting with ruff
uv run poe lint

# Code formatting with ruff
uv run poe format

# Type checking (alias for mypy)
uv run poe typecheck
```

## Google Cloud Setup

```bash
# Create a new project (or use existing)
gcloud projects create your-project-id
gcloud config set project your-project-id

# Enable required APIs
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable artifactregistry.googleapis.com
```

## GitHub Actions Deployment

### 1. Automated Setup (Recommended)

Use the included setup script to automate service account creation and permissions:

```bash
# Run the setup script with your project ID
uv run python setup_gcp_deployment.py your-project-id

# Or with custom key file location
uv run python setup_gcp_deployment.py your-project-id --key-path ./gcp-key.json

# Skip project setup if APIs are already enabled
uv run python setup_gcp_deployment.py your-project-id --skip-project-setup
```

The script will:

- Create the `github-actions` service account
- Grant all necessary IAM permissions
- Generate and download the service account key
- Provide next steps for GitHub configuration

### 1. Manual Setup (Alternative)

If you prefer manual setup:

```bash
# Create a service account for GitHub Actions
gcloud iam service-accounts create github-actions \
  --display-name "GitHub Actions"

# Grant necessary permissions
gcloud projects add-iam-policy-binding your-project-id \
  --member="serviceAccount:github-actions@your-project-id.iam.gserviceaccount.com" \
  --role="roles/cloudfunctions.admin"

gcloud projects add-iam-policy-binding your-project-id \
  --member="serviceAccount:github-actions@your-project-id.iam.gserviceaccount.com" \
  --role="roles/cloudbuild.builds.editor"

gcloud projects add-iam-policy-binding your-project-id \
  --member="serviceAccount:github-actions@your-project-id.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"

# Create and download service account key
gcloud iam service-accounts keys create key.json \
  --iam-account github-actions@your-project-id.iam.gserviceaccount.com
```

### 2. Configure GitHub Secrets

Add the following secrets to your GitHub repository (Settings � Secrets and variables � Actions):

- `GCP_SA_KEY`: Contents of the `key.json` file (entire JSON)

### 3. Configure GitHub Variables (Optional)

You can override default deployment settings using GitHub repository variables (Settings → Secrets and variables → Actions → Variables tab):

- `FUNCTION_NAME`: Override default function name (`api-function`)
- `REGION`: Override default region (`us-central1`)

### 4. Update Workflow Configuration (Optional)

Edit `.github/workflows/deploy-cloud-function.yml` if needed:

- Adjust resource limits (`memory`, `timeout`) as needed
- Modify trigger conditions or deployment steps

### 5. Deploy

The workflow automatically deploys when:

- Code is pushed to the `main` branch
- Changes are made to `services/api-function/**` or `libs/api/**`
- Manually triggered from the GitHub Actions tab

## Configuration

### Environment Variables

You can set environment variables for the Cloud Function by modifying the `env_vars` section in the GitHub workflow:

```yaml
env_vars: |
  PYTHONPATH=/workspace
  YOUR_CUSTOM_VAR=value
```

### Function Settings

Adjust function settings in `.github/workflows/deploy-cloud-function.yml`:

- `memory`: Memory allocation (128Mi, 256Mi, 512Mi, 1Gi, 2Gi, 4Gi, 8Gi)
- `timeout`: Maximum execution time (up to 540s for HTTP functions)
- `region`: Deployment region

## Testing the Deployed Function

Once deployed, test your function:

```bash
# Get the function URL (replace with your function name and region if different)
FUNCTION_URL=$(gcloud functions describe api-function \
  --region=us-central1 \
  --format="value(serviceConfig.uri)")

# Test GET endpoint
curl $FUNCTION_URL/hello

# Test POST endpoint
curl -X POST $FUNCTION_URL/hello \
  -H "Content-Type: application/json" \
  -d '{"name": "Cloud Functions"}'
```

## Development Workflow

1. **Make changes** to `libs/api/` for shared functionality
2. **Update services** in `services/api-function/` for deployment-specific code
3. **Test locally** using Functions Framework
4. **Push to main branch** to trigger automatic deployment
5. **Monitor deployment** in GitHub Actions tab

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure `PYTHONPATH=/workspace` is set in function environment
2. **Dependency issues**: uv automatically generates `requirements.txt` during CI/CD deployment
3. **Permission errors**: Verify service account has required Cloud Functions permissions
4. **Memory/timeout errors**: Increase limits in the deployment workflow

### Debugging

- Check Cloud Functions logs: `gcloud functions logs read api-function --region=us-central1 --gen2`
- View GitHub Actions logs in the repository's Actions tab
- Test locally with Functions Framework before deploying
- For manual deployment: follow the complete build process including creating the `deploy-package` directory with wheel dependencies

## License

This project is licensed under the MIT License.
