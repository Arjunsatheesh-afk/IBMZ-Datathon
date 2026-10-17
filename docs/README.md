The STARK Paradox — IBM Z Datathon 2026

1. Project Overview

The STARK Paradox is a privacy-preserving fraud detection project developed for the IBM Z Datathon 2026 under the AI Secured theme.

The project aims to detect potentially fraudulent transactions while protecting customer identities through tokenization and encryption.

2. Objectives

- Detect potentially fraudulent financial transactions.
- Protect customer identities using HMAC-SHA256 tokenization.
- Store original customer IDs in an AES-GCM encrypted token vault.
- Compare fraud detection models trained on raw and tokenized data.
- Provide an Analyst and Reviewer dashboard.
- Record reviewer re-identification actions in an audit log.
- Run the scoring API on IBM LinuxONE.

3. System Architecture

The system processes transaction data through tokenization and fraud detection models. A FastAPI scoring service produces risk scores and explanations, which are stored in "alerts.csv" for the Streamlit dashboard.

Analysts can view and filter tokenized alerts. Reviewers can request re-identification by providing their name and a reason. The action is recorded in an audit log.

See "architecture.drawio" for the architecture diagram.

4. Technology Stack

- Programming language: Python
- Dashboard: Streamlit
- Data processing: Pandas
- API: FastAPI
- Tokenization: HMAC-SHA256
- Encryption: AES-GCM
- Deployment platform: IBM LinuxONE
- Containerization: Docker
- Dataset: PaySim

5. Dataset

The project uses the PaySim synthetic mobile-money transaction dataset.

The planned model scope focuses on "TRANSFER" and "CASH_OUT" transaction types. Balance-related fields and "isFlaggedFraud" are excluded from model inputs to reduce data leakage.

Dataset source: https://www.kaggle.com/datasets/ealaxi/paysim1

6. Dashboard Features

Analyst View

- View tokenized transaction alerts.
- Filter alerts by transaction type and risk score.
- Review risk scores and the top reason for an alert.

Reviewer View

- Submit a reviewer name and written reason.
- Request re-identification of an authorized token.
- View audit records of re-identification attempts.

7. Project Structure

IBMZ-Datathon/
├── dashboard/
│   ├── app.py
│   └── data/
│       ├── alerts.csv
│       └── vault.py
├── infra/
├── pipeline/
└── docs/
    ├── architecture.drawio
    ├── README.md
    └── demo_script.md

This is the intended high-level structure; update it if the final repository differs.

8. Setup and Execution

Create and activate a Python virtual environment, then install the required dependencies:

python -m pip install streamlit pandas pycryptodome fastapi uvicorn

Run the dashboard from the repository root:

python -m streamlit run dashboard/app.py

The dashboard requires the expected alerts CSV and, for reviewer re-identification, the encrypted vault and AES key at the configured paths.

Do not place the AES key in the repository or commit sensitive vault data.

9. Security Considerations

- HMAC-SHA256 tokens replace original customer identifiers.
- Original IDs are stored in an AES-GCM encrypted vault.
- The AES key must be stored separately from the repository.
- Reviewer name and reason are required for re-identification.
- Re-identification attempts are recorded in an audit log.
- Never commit encryption keys, sensitive vault files, or audit logs containing sensitive information.

10. Open-Source Libraries and Licenses

List the actual libraries and versions used by the project, together with their applicable licenses. Include links to the official project pages and the PaySim dataset source and license information.

11. Demo

See "demo_script.md" for the planned demonstration sequence.

The demonstration should cover the problem, dataset, solution, dashboard, security approach, and IBM LinuxONE deployment. Report only results verified by the team.

12. AI Tool Disclosure

Parts of this project were developed with help from Claude (Anthropic). All code was written during the Datathon window (17–18 October 2026).
How to Run

Install dependencies: "python -m pip install -r dashboard/requirements.txt"
Run the dashboard: "python -m streamlit run dashboard/app.py"
Open the local URL shown in the terminal.