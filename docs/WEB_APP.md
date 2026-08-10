# Web Application Specification — MoleculeScope

This document outlines the React + Vite single-page application design, component hierarchy, page tabs, and styling rules.

---

## 1. Visual Theme & Styling Guidelines

To ensure the application looks like a professional scientific/cheminformatics research tool (rather than a generic AI dashboard or commercial SaaS tool), we apply these design constraints:

*   **Colors:** Semantically mapped to clear purposes:
    *   **Background:** Deep slate (`#0b0f19`).
    *   **Cards/Containers:** Dark charcoal (`#111827`) with thin neutral borders (`#1f2937`). No excessive glowing highlights.
    *   **Primary Accent:** Teal/Cyan (`#06b6d4`) for normal interactions, titles, and tabs.
    *   **BBB+ (Permeable):** Emerald green (`#10b981`).
    *   **BBB- (Impermeable):** Rose red (`#f43f5e`).
    *   **Neutral Text:** Light gray (`#f3f4f6`) and muted slate (`#9ca3af`).
*   **Typography:** Outfit or Inter fonts imported from Google Fonts. Clean spacing, uniform weights.
*   **Animations:** Subtle transition fades between tabs, slow scaling on hover, and smooth progress bar loaders. No flashy particle systems or revolving card graphics.
*   **Central Visuals:** The 2D molecular structure rendering is the central focus of the prediction page.

---

## 2. Page Navigation & Component Hierarchy

The application layout features a static sidebar/header navigation with four distinct tabs:

### Page 1: Single Molecule Predictor (Core MVP)
*   **Purpose:** Allows instant validation and prediction on individual SMILES inputs.
*   **Sections:**
    *   **Verified Examples Panel:** A grid of example molecules (Caffeine, Aspirin, Ibuprofen, Paracetamol, Dopamine, L-DOPA, Diazepam) mapped only to their validated SMILES strings.
    *   **SMILES Input Form:** A text input field with real-time validation indicator.
    *   **Structure Drawing Canvas:** Displays the 2D molecule using the vector SVG path returned by the FastAPI backend.
    *   **Results Panel:** Displays the prediction status (**BBB+** or **BBB-**) and the probability (e.g. **Predicted probability of BBB+: [VALUE]%**). Includes a table of calculated physicochemical descriptors.
*   **Safety Footer:** Persistent disclaimer regarding the computational screening nature of predictions.

### Page 2: Model Performance Dashboard (Core MVP)
*   **Purpose:** Summarizes the project's experimental findings (loaded from serialized metrics).
*   **Sections:**
    *   **Performance Table:** Comparison of metrics across all three classifiers.
    *   **Graph Panel:** Interactive ROC curves and PR curves comparing the stratified split with the scaffold split.
    *   **Confusion Matrices Grid:** Interactive matrix cards.
    *   **Research Summary Note:** A text card explaining the "Generalization Gap" observed during scaffold split training.

### Page 3: Explainability Hub (SHOULD HAVE)
*   **Purpose:** Educates users on what molecular characteristics drive prediction.
*   **Sections:**
    *   **Global Importances:** Interactive bar chart of descriptor importances.
    *   **Local SHAP Waterfall:** Force plot indicating descriptor contributions for the active molecule.

### Page 4: Batch Virtual Screener (SHOULD HAVE)
*   **Purpose:** Enables batch screening of SMILES collections.
*   **Sections:**
    *   **Uploader Card:** Drag-and-drop CSV uploader (requires a `SMILES` header column).
    *   **Interactive Table:** Paginated results displaying valid structures, predicted classes, predicted probabilities of BBB+, and MW/LogP.
    *   **Toolbar:** Filters results by class, search by compound name, and an "Export Results" CSV downloader.
