# Future Scope — MoleculeScope

This document outlines the roadmap and potential extensions for **MoleculeScope** to address the limitations and findings identified during Phase 5 evaluation.

---

## 1. Probability Calibration
*   **Context:** Currently, our models output raw, uncalibrated probability estimates (e.g., Random Forest fraction of voting trees). In the UI, these are presented strictly as "Predicted Probability of BBB+" rather than "confidence scores."
*   **Expansion:** Implement Platt Scaling or Isotonic Regression fit on validation folds. Calibrating these outputs ensures that a predicted probability of 80% corresponds to an empirical success rate of 80%, allowing the UI to present legitimate statistical confidence boundaries.

---

## 2. Transporter-Aware Feature Expansion
*   **Context:** Phase 5 error audits showed that passive descriptor models misclassify carrier-mediated entrants as BBB- (False Negatives) and polar-blocked structures as BBB+ (False Positives) because they bypass passive diffusion limits.
*   **Expansion:** Integrate binary indicators or binding affinity predictors for major blood-brain barrier transport systems (such as P-gp/ABCB1 efflux pumps, LAT1/SLC7A5 amino acid carriers, or GLUT1/SLC2A1 glucose carriers). Representing transport binding profiles explicitly as features would help resolve passive-only classification errors.

---

## 3. Graph-Based and Deep Representation Learning
*   **Context:** Morgan fingerprint-based models exhibited substantially poorer scaffold generalization than descriptor-based models under structural distribution shifts (Bemis-Murcko scaffold split), dropping to a Macro F1 of 0.55.
*   **Expansion:** Implement Graph Neural Networks (GNNs) or Message Passing Neural Networks (MPNNs) to learn structural representations dynamically from molecular graphs rather than relying on fixed hashed circular bits. Alternatively, pre-trained molecular transformers (e.g., ChemBERTa) could be leveraged to extract embeddings that generalize more effectively across novel scaffold classes.

---

## 4. logBB Numerical Regression Modeling
*   **Context:** The current MVP predicts the categorical target `BBB+/BBB-` over the full dataset.
*   **Expansion:** A subset of 1,058 B3DB compounds contains experimental numerical `logBB` partition coefficients. Future iterations can train regression algorithms (such as Ridge, Random Forest Regressor, or XGBoost Regressor) on this subset, allowing the UI to display both a binary permeability classification and a quantitative logBB partition coefficient estimate.

---

## 5. Interactive Molecule Drawing Canvas
*   **Context:** Currently, users type/paste SMILES strings or select example inputs.
*   **Expansion:** Integrate a lightweight JavaScript chemical drawing tool (e.g., JSME or Ketcher) directly into the frontend. This canvas will allow users to draw structures, dynamically generate SMILES on the client side, and send them to the backend for real-time RDKit property calculation and Random Forest inference.
