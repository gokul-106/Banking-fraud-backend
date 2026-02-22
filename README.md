# Banking Fraud Detection Backend

## Overview

Backend-based banking fraud detection system built in Python to identify potentially fraudulent financial transactions. The system processes transaction data, performs preprocessing, applies fraud detection logic, and returns a classification result.

## Purpose

Designed to simulate how financial institutions automatically monitor transactions and flag suspicious activity for risk review.

## Key Features

* Transaction data preprocessing and validation
* Fraud classification logic for suspicious activity detection
* Automated backend prediction workflow
* Structured handling of financial transaction records

## Tech Stack

Python, data preprocessing, machine learning classification concepts.

## How to Run

git clone https://github.com/gokul-106/Banking-fraud-backend.git
cd Banking-fraud-backend

pip install fastapi uvicorn pandas numpy python-dotenv

python -m uvicorn server:app --reload

*(Update the entry script if different in your project.)*

## Author

Gokul Krishna
https://github.com/gokul-106
## API Demo

### Request Example
![API Request](api_request.png)

### Response Example
![API Response](api_response.png)
