#!/usr/bin/env python3
"""
GCP Deployment Setup Utility

This script sets up Google Cloud Platform resources and permissions
needed for GitHub Actions to deploy Cloud Functions.
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], description: str) -> bool:
    """Run a shell command and handle errors."""
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)

        if result.returncode == 0:
            print("✅ Success")
            if result.stdout.strip():
                print(f"Output: {result.stdout.strip()}")
            return True
        else:
            print("❌ Failed")
            print(f"Error: {result.stderr.strip()}")
            return False

    except Exception as e:
        print(f"❌ Exception: {e}")
        return False


def validate_gcloud_auth() -> bool:
    """Check if gcloud is authenticated and configured."""
    print("\n🔍 Validating gcloud authentication...")

    # Check if gcloud is installed
    try:
        subprocess.run(["gcloud", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ gcloud CLI not found. Please install it first.")
        return False

    # Check authentication
    result = subprocess.run(
        ["gcloud", "auth", "list", "--filter=status:ACTIVE", "--format=value(account)"],
        capture_output=True,
        text=True,
    )

    if not result.stdout.strip():
        print("❌ No active gcloud authentication found.")
        print("Run: gcloud auth login")
        return False

    print(f"✅ Authenticated as: {result.stdout.strip()}")
    return True


def setup_project(project_id: str) -> bool:
    """Set up the GCP project and enable required APIs."""
    print(f"\n🚀 Setting up GCP project: {project_id}")

    # Set the project
    if not run_command(
        ["gcloud", "config", "set", "project", project_id],
        f"Setting project to {project_id}",
    ):
        return False

    # Enable required APIs
    apis = [
        "cloudfunctions.googleapis.com",
        "cloudbuild.googleapis.com",
        "artifactregistry.googleapis.com",
    ]

    for api in apis:
        if not run_command(["gcloud", "services", "enable", api], f"Enabling {api}"):
            return False

    return True


def create_service_account(project_id: str) -> bool:
    """Create the GitHub Actions service account."""
    print(f"\n👤 Creating service account for project: {project_id}")

    # Create service account
    return run_command(
        [
            "gcloud",
            "iam",
            "service-accounts",
            "create",
            "github-actions",
            "--display-name",
            "GitHub Actions",
        ],
        "Creating GitHub Actions service account",
    )


def grant_permissions(project_id: str) -> bool:
    """Grant necessary IAM permissions to the service account."""
    print(f"\n🔐 Granting IAM permissions for project: {project_id}")

    service_account = f"github-actions@{project_id}.iam.gserviceaccount.com"

    roles = [
        "roles/cloudfunctions.admin",
        "roles/cloudbuild.builds.editor",
        "roles/iam.serviceAccountUser",
    ]

    for role in roles:
        if not run_command(
            [
                "gcloud",
                "projects",
                "add-iam-policy-binding",
                project_id,
                f"--member=serviceAccount:{service_account}",
                f"--role={role}",
            ],
            f"Granting {role}",
        ):
            return False

    return True


def create_service_account_key(project_id: str, key_path: Path) -> bool:
    """Create and download the service account key."""
    print(f"\n🔑 Creating service account key: {key_path}")

    service_account = f"github-actions@{project_id}.iam.gserviceaccount.com"

    return run_command(
        [
            "gcloud",
            "iam",
            "service-accounts",
            "keys",
            "create",
            str(key_path),
            f"--iam-account={service_account}",
        ],
        f"Creating service account key at {key_path}",
    )


def main():
    """Main setup function."""
    parser = argparse.ArgumentParser(
        description="Set up GCP deployment for GitHub Actions"
    )
    parser.add_argument("project_id", help="Google Cloud Project ID")
    parser.add_argument(
        "--key-path",
        default="key.json",
        help="Path for service account key file (default: key.json)",
    )
    parser.add_argument(
        "--skip-project-setup",
        action="store_true",
        help="Skip project creation and API enabling",
    )

    args = parser.parse_args()

    print("🎯 GCP Deployment Setup for GitHub Actions")
    print(f"Project ID: {args.project_id}")
    print(f"Key file: {args.key_path}")

    # Validate prerequisites
    if not validate_gcloud_auth():
        sys.exit(1)

    # Setup project and APIs (optional)
    if not args.skip_project_setup:
        if not setup_project(args.project_id):
            print("\n❌ Project setup failed")
            sys.exit(1)

    # Create service account
    if not create_service_account(args.project_id):
        print("\n⚠️  Service account creation failed (may already exist)")

    # Grant permissions
    if not grant_permissions(args.project_id):
        print("\n❌ Permission granting failed")
        sys.exit(1)

    # Create service account key
    key_path = Path(args.key_path)
    if not create_service_account_key(args.project_id, key_path):
        print("\n❌ Service account key creation failed")
        sys.exit(1)

    # Final instructions
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print(f"1. Add the contents of '{key_path}' as a GitHub secret named 'GCP_SA_KEY'")
    print("2. Update the GitHub workflow with your project ID if needed")
    print("3. Push code to trigger deployment")
    print(
        f"\n⚠️  Remember to secure '{key_path}' and don't commit it to version control!"
    )


if __name__ == "__main__":
    main()
