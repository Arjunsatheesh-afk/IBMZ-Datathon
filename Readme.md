The STARK Paradox — IBM Z Datathon 2026

Event Code: SSF2026
Theme: AI Secured: Innovation Without Exposure

🔍 Overview

The STARK Paradox is a privacy-preserving fraud detection project designed to identify potentially fraudulent financial transactions while protecting customer identities.

The project combines transaction tokenization, encrypted identity storage, fraud detection models, and an interactive dashboard to support secure transaction analysis on IBM LinuxONE.

🎯 Key Features

- Privacy-Preserving Tokenization: Uses HMAC-SHA256 tokens to represent customer identifiers.
- Encrypted Token Vault: Protects original identifiers using AES-GCM encryption.
- Fraud Detection: Analyzes transactions and produces risk scores with explanations.
- Analyst Dashboard: Allows analysts to view and filter tokenized transaction alerts.
- Reviewer Workflow: Supports re-identification requests with a reviewer name and reason.
- Audit Logging: Records re-identification attempts for traceability.
- IBM LinuxONE Integration: Designed to host the scoring service on IBM LinuxONE.

🛠️ Technology Stack

Python · Pandas · Streamlit · FastAPI · HMAC-SHA256 · AES-GCM · Docker · IBM LinuxONE

📊 Dataset

The project uses the PaySim synthetic mobile-money transaction dataset.

Dataset source: "PaySim on Kaggle" (https://www.kaggle.com/datasets/ealaxi/paysim1)

📁 Project Documentation

- Detailed README: ""docs/README.md"" (docs/README.md)
- Architecture Diagram: ""docs/architecture.drawio"" (docs/architecture.drawio)
- Demo Script: ""docs/demo_script.md"" (docs/demo_script.md)

🔐 Security

- Original customer identifiers are protected through tokenization and encryption.
- The AES encryption key must be stored outside the Git repository.
- Sensitive vault files and audit logs must not be committed.
- Reviewer re-identification requires a name and written reason.

🤖 AI Tool Disclosure

Parts of this project were developed with assistance from Claude (Anthropic). All code was written during the IBM Z Datathon event window (17–18 October 2026).