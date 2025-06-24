# GitHub Actions Deployment to Google Cloud Run

This document explains how to set up and use the GitHub Actions workflow for deploying the Finance Collector application to Google Cloud Run.

## Prerequisites

Before you can use the GitHub Actions workflow, you need to:

1. Have a Google Cloud Platform (GCP) account
2. Create a GCP project
3. Enable the required APIs in your GCP project:
   - Cloud Run API
   - Container Registry API
   - Cloud Build API
   - IAM API

## Setting Up Service Account

1. Create a service account in your GCP project with the following roles:
   - Cloud Run Admin (`roles/run.admin`)
   - Storage Admin (`roles/storage.admin`)
   - Service Account User (`roles/iam.serviceAccountUser`)
   - Cloud Build Editor (`roles/cloudbuild.builds.editor`)

2. Create and download a JSON key for this service account.

## Setting Up GitHub Secrets

Add the following secrets to your GitHub repository:

### Required for Google Cloud Deployment:
1. `GCP_PROJECT_ID`: Your Google Cloud Platform project ID
2. `GCP_SA_KEY`: The entire content of the service account JSON key file

### Required for Application Environment Variables:
3. `CLIENT_ID`: Your client ID for authentication
4. `CLIENT_SECRET`: Your client secret for authentication
5. `JWT_SECRET_KEY`: Secret key for JWT token generation
6. `API_KEY`: API key for authentication

### Optional Environment Variables (with defaults):
7. `JWT_ALGORITHM`: Algorithm for JWT (defaults to HS256 if not provided)
8. `JWT_EXPIRATION_MINUTES`: JWT token expiration in minutes (defaults to 30 if not provided)

To add these secrets:
1. Go to your GitHub repository
2. Click on "Settings" > "Secrets and variables" > "Actions"
3. Click "New repository secret"
4. Add each secret with its respective name and value

These environment variables will be passed to your Cloud Run service during deployment, ensuring your application has access to all required configuration without hardcoding sensitive information in your codebase.

## Workflow Configuration

The workflow is configured to:

1. Trigger on pushes to the `main` branch or manual triggering
2. Build a Docker image from your Dockerfile
3. Push the image to Google Container Registry (GCR)
4. Deploy the image to Google Cloud Run

## Customizing the Workflow

You may want to customize the following variables in the workflow file (`.github/workflows/deploy-to-cloud-run.yml`):

- `SERVICE_NAME`: The name of your Cloud Run service
- `REGION`: The GCP region where your service will be deployed
- `flags`: Remove `--allow-unauthenticated` if you want to require authentication for your service

## Manual Deployment

You can manually trigger the workflow by:

1. Going to the "Actions" tab in your GitHub repository
2. Selecting the "Deploy to Google Cloud Run" workflow
3. Clicking "Run workflow"
4. Selecting the branch you want to deploy from
5. Clicking "Run workflow"

## Monitoring Deployments

After a deployment is triggered, you can monitor its progress in the "Actions" tab of your GitHub repository. Once the deployment is complete, the workflow will output the URL of your deployed service.
