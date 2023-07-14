terraform {
  backend "gcs" {
    bucket = "flight-app-demo-bucket"
    prefix = "terraform"
    credentials = "C:\\Users\\Alon\\PycharmProjects\\project1\\venv\\flight-app-demo\\key.json"
  }
  required_providers {
    google = {
      source = "hashicorp/google"
      version = "4.66.0"
    }
  }
}

provider "google" {
  credentials = file(var.key_path)
  project = var.gcp_project
}