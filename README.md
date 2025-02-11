# Bulletiner-AWS-EB

An open-source solution to scrape, store, classify, geocode, and present daily police bulletins for North Macedonia. Deployed on AWS Elastic Beanstalk with a PostgreSQL RDS, Lambda-based ingestion and classification, and an interactive web map powered by Flask, Leaflet.js, and OpenAI-based text processing.

## Table of Contents
- [Project Overview](#project-overview)
- [Features](#features)
- [Installation & Setup](#installation--setup)
- [Usage](#usage)
- [Tech Stack](#tech-stack)
- [License](#license)
- [Contributing](#contributing)
- [Contact](#contact)

---

## Project Overview

**Bulletiner-AWS-EB** automates the retrieval and classification of daily police bulletins from the official police portal of North Macedonia. The system:

1. **Scrapes** bulletins daily with AWS Lambda.
2. **Stores** raw entries in a PostgreSQL RDS instance.
3. **Classifies** bulletins (crime category, location extraction) using OpenAI GPT via another Lambda function.
4. **Geocodes** location references using local OSM data (Overpass Turbo) plus Nominatim as a fallback.
5. **Visualizes** bulletins on a public web map (Flask + Leaflet.js) deployed via AWS Elastic Beanstalk.

Visit [**Biltenot.mk**](https://biltenot.mk) to see the live system.

---

## Features

- **Daily Scraping**  
  - A Lambda function retrieves raw bulletins from the police portal and inserts them into PostgreSQL.

- **Text Classification**  
  - Another Lambda function reads unprocessed bulletins, uses OpenAI GPT to categorize incidents and extract location mentions, then updates the database.

- **Geocoding**  
  - Local dataset from Overpass Turbo is used for quick, offline fuzzy matching.
  - Falls back to [Nominatim](https://nominatim.org/) for unknown or ambiguous locations.

- **Interactive Map**  
  - A Flask web app (Python 3.11 on Amazon Linux 2023) with Leaflet.js to display bulletins as markers, allowing searches by category, date range, or location.

- **Continuous Deployment**  
  - Source hosted on this GitHub repoitory is integrated with AWS CodePipeline for automatic deployment to AWS Elastic Beanstalk upon each commit.

- **AWS Infrastructure**  
  - Uses a VPC, on a EC2 instance coneected to a RDS (PostgreSQL) instance, Elastic Load Balancer (with SSL), RDS (PostgreSQL), and Lambda.  
  - Domain registration and SSL certificate for a secure, custom domain.

---

## Installation & Setup

### Prerequisites

1. **Python 3.11** (Locally, if you want to run or test the Flask app).
2. **AWS Account** with:
   - Elastic Beanstalk
   - RDS (PostgreSQL)
   - Lambda
   - CodePipeline
3. **OpenAI API Key** (for classification).
4. **Overpass Turbo** data (in GeoJSON) if you want offline fuzzy geocoding.

### Steps

1. **Clone** the repository:
   ```bash
   git clone https://github.com/Manchov/Bulletiner-AWS-EB.git
   cd Bulletiner-AWS-EB
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate   # on Linux/Mac
   # or venv\Scripts\activate on Windows
   ```

3. Install Requirements:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables for local testing:
   - OPENAI_API_KEY, DB_URI, etc.

5. Run the Flask app locally (optional):
   ```bash
   flask run
   ```

6. Deploy to AWS:
   - Create an AWS Elastic Beanstalk environment (Linux + Python 3.11).
   - CodePipeline integrated with your GitHub repository for CI/CD.
   - Create or update Lambdas for scraping & classification with the relevant code.

---

## Usage

1. **Daily**:
   - The **Scraping Lambda** runs on a daily schedule (e.g., via EventBridge/CloudWatch) to fetch new bulletins.
   - The **Classification Lambda** also runs daily to classify new bulletins & geocode them.
2. **View** bulletins:
   - Navigate to [Biltenot.mk](https://biltenot.mk) to see the interactive map.
   - Filter by date, category, location, etc.
3. **Monitor** logs on AWS (Elastic Beanstalk logs, Lambda logs in CloudWatch, etc.).

---

## Tech Stack

- **Backend**: Python Flask  
- **Database**: PostgreSQL (AWS RDS)  
- **Cloud**: AWS (EC2, Elastic Beanstalk, RDS, CodePipeline, Lambda, VPC, Load Balancer)  
- **AI**: OpenAI GPT for text classification/location extraction  
- **Geocoding**: Overpass Turbo data + Nominatim fallback
- **Frontend**: Leaflet.js, HTML/CSS/JavaScript  
- **Deployment**: GitHub → CodePipeline → Elastic Beanstalk

---

## License

This project is licensed under the [MIT License](LICENSE). You’re free to **use**, **modify**, and **distribute** it, provided you include the original license and attribution. See [LICENSE](LICENSE) for details.

---
