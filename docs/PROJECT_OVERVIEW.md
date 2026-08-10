# Project Overview — MoleculeScope

## 1. Project Significance & Scope
In drug discovery, particularly for central nervous system (CNS) therapeutic targets, a compound's ability to cross the blood-brain barrier (BBB) is a critical pharmacokinetics parameter. Predicting this property early in the pipeline prevents costly failures in late-stage clinical trials. 

**MoleculeScope** demonstrates how traditional machine learning and cheminformatics can be used for early-stage screening of small molecules. It is an academic project designed to investigate generalization behaviors, feature importance, and performance differences when small molecules are evaluated on randomly split sets versus structurally distinct scaffold splits.

---

## 2. Core Objectives
*   **Establish a Clean Data Pipeline:** Create a reproducible workflow for fetching, cleaning, and sanitizing the B3DB database using the RDKit engine.
*   **Extract Molecular Representations:** Calculate 11 physicochemical descriptors and 2048-bit circular Morgan fingerprints (radius=2) for all valid compounds.
*   **Implement Traditional Models:** Train and tune Logistic Regression, Random Forest, and XGBoost classifiers.
*   **Analyze Generalization:** Contrast stratified random splitting with Bemis-Murcko scaffold splitting to evaluate how models handle structurally novel chemistries (the generalization gap).
*   **Build a Research Tool UI:** Create a React + FastAPI web application providing single-molecule prediction, batch virtual screening, model explainability plots, and experimental performance dashboards.

---

## 3. Core Research Questions

### RQ1: Classifier Performance
*Which traditional machine learning model family performs best for binary BBB permeability classification?*

### RQ2: Molecular Representations
*Which molecular representation (physicochemical descriptors, circular fingerprints, or combined) yields the strongest prediction scores?*

### RQ3: Generalization Gap
*How much does performance (specifically Macro F1, ROC-AUC, and PR-AUC) change when models are tested on structurally novel Bemis-Murcko scaffolds compared to random stratified splits?*

### RQ4: Feature Attribution
*Which molecular characteristics (e.g., TPSA, lipophilicity, circular substructures) contribute most to model predictions?*
