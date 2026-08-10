# MoleculeScope

**Molecular Property Prediction for Early-Stage Drug Discovery Using Traditional Machine Learning**

MoleculeScope is an academic machine learning project designed to predict whether a chemical compound is likely to cross the blood-brain barrier (BBB) based on its molecular structure. The project leverages traditional machine learning classifiers trained on features derived from the Blood-Brain Barrier Database (B3DB).

---

## 1. Project Architecture

The application is split into two main components:
*   **Backend:** A Python service built on FastAPI that performs SMILES structural validation, calculates RDKit descriptors/Morgan fingerprints, runs inference using saved ML models, and generates local SHAP explanations.
*   **Frontend:** A modern single-page application built on React (Vite) and styled with custom Vanilla CSS that visualizes molecular structures, renders interactive metric dashboards, and handles single-molecule and batch screening.

---

## 2. Directory Structure

```
c:\MoleculeScope\
├── backend/                  # FastAPI Backend & ML Pipeline
│   ├── app/                  # FastAPI application code
│   │   ├── main.py           # REST API endpoints
│   │   ├── schemas.py        # Pydantic request/response validation
│   │   ├── predictor.py      # Feature generation and model inference
│   │   └── utils.py          # RDKit drawing & SMILES validation
│   ├── data/                 # Raw B3DB and cached processed dataset
│   ├── models/               # Saved trained ML models (.joblib files)
│   ├── src/                  # ML pipeline modules
│   │   ├── inspect_dataset.py# Phase 0 analysis script
│   │   ├── data_loader.py    # Downloads B3DB
│   │   ├── preprocessor.py   # Cleaning and duplicate checks
│   │   ├── features.py       # Descriptor & fingerprint builders
│   │   ├── train.py          # Model fitting scripts
│   │   └── evaluate.py       # Stratified/Scaffold split evaluators
│   ├── requirements.txt      # Python dependencies
│   └── venv/                 # Python virtual environment
├── frontend/                 # React Frontend Client
│   ├── src/
│   │   ├── assets/           # Custom Vanilla CSS styles
│   │   ├── components/       # Layout, Predictor, Screener, Dashboard, Explainer
│   │   ├── App.jsx           # Main React App routing/tabs
│   │   └── main.jsx          # Entry point
│   ├── package.json          # Node dependencies
│   └── vite.config.js        # Vite configuration
├── docs/                     # Academic & Project Documentation
│   ├── PROJECT_OVERVIEW.md
│   ├── DATASET.md
│   ├── DATA_PREPROCESSING.md
│   ├── FEATURE_ENGINEERING.md
│   ├── MODELING.md
│   ├── EVALUATION_METHODOLOGY.md
│   ├── EXPERIMENTS.md
│   ├── MODEL_COMPARISON.md
│   ├── WEB_APP.md
│   ├── API.md
│   ├── DEPLOYMENT.md
│   ├── LIMITATIONS.md
│   ├── FUTURE_SCOPE.md
│   ├── VIVA_QUESTIONS.md
│   ├── REPORT_OUTLINE.md
│   ├── PRESENTATION_OUTLINE.md
│   └── RESULTS.md
├── README.md                 # Project quickstart
└── CHANGELOG.md              # Project history log
```

---

## 3. Environment Setup & Installation

### Prerequisite Environment
*   **Python:** 3.13.x
*   **Node.js:** v22.x

### Backend Setup
1.  Navigate to the `backend/` directory:
    ```bash
    cd backend
    ```
2.  Set up the virtual environment:
    ```bash
    python -m venv venv
    ```
3.  Activate the virtual environment:
    *   **Windows (PowerShell):**
        ```powershell
        .\venv\Scripts\Activate.ps1
        ```
    *   **Windows (cmd):**
        ```cmd
        .\venv\Scripts\activate.bat
        ```
    *   **Mac/Linux:**
        ```bash
        source venv/bin/activate
        ```
4.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Frontend Setup
1.  Navigate to the `frontend/` directory:
    ```bash
    cd ../frontend
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```

---

## 4. Running the Project

### Running Phase 0 Dataset Inspection
To download and inspect the B3DB classification dataset, run from the project root:
```bash
.\backend\venv\Scripts\python.exe backend/src/inspect_dataset.py
```

### Future Phases Running Commands
*   **Preprocessing & Cleaning:** `.\backend\venv\Scripts\python.exe backend/src/preprocessor.py`
*   **Feature Extraction:** `.\backend\venv\Scripts\python.exe backend/src/features.py`
*   **Model Training:** `.\backend\venv\Scripts\python.exe backend/src/train.py`
*   **API Server:** `.\backend\venv\Scripts\uvicorn app.main:app --reload --port 8000` (run from the `backend/` folder)
*   **Frontend Development:** `npm run dev` (run from the `frontend/` folder)
