# Project Limitations — MoleculeScope

This document outlines the scientific, cheminformatics, and data-driven limitations identified during the modeling and evaluation phases of **MoleculeScope**.

---

## 1. No Medical or Clinical Validity
*   **Academic Nature:** MoleculeScope is a student machine learning demonstration and is not clinically or medically validated. It does not replace experimental assays (e.g., in vitro PAMPA-BBB assays or in vivo pharmacokinetic studies) and must not be used for therapeutic design or diagnostic decision-making.
*   **Passive-Only Features:** The underlying machine learning model is trained on 11 passive physicochemical descriptors (such as TPSA, LogP, and H-Bond Donors). It does not explicitly represent complex dynamic biological systems, such as active influx/efflux transporters or enzymatic degradation.

---

## 2. Evaluation Model Failure Modes (Error Analysis)

Detailed analysis of the evaluation model's errors (scaffold-split Random Forest on descriptors) on the scaffold test set reveals distinct descriptor distributions for false positives and false negatives:

### A. False Positives (Impermeable Predicted as Permeable)
*   **Sample Count:** 255 molecules
*   **Mean Properties:** MW = `329.76`, LogP = `3.15`, TPSA = `61.13` Å², H-Bond Donors (HBD) = `1.19`
*   **Possible Explanation:** These compounds have lower polarity and lower hydrogen-bonding counts, which are strong signals for passive membrane partition. A potential explanation for their impermeability is that they may be blocked from entering the brain by specific efflux networks (such as P-glycoprotein) or feature charged/polar moieties not fully represented by bulk descriptors.

### B. False Negatives (Permeable Predicted as Impermeable)
*   **Sample Count:** 143 molecules
*   **Mean Properties:** MW = `345.71`, LogP = `1.71`, TPSA = `97.67` Å², HBD = `2.41`
*   **Possible Explanation:** These compounds are highly polar and feature high donor counts, which exceed standard passive diffusion limits (meaning they are predicted as impermeable). A potential biological explanation for their entry is that they may bypass passive diffusion constraints via active, carrier-mediated transport mechanisms (e.g., targeting glucose or amino acid channels). Since our model is restricted to passive physicochemical indices, it may misclassify these transporter-mediated entrants as BBB-.

---

## 3. Cheminformatics & Feature Representation Limitations

### A. Valency and Parsing Rules
*   RDKit parses SMILES strings using standard chemical valence rules. Unusual structural motifs or organometallics (e.g., the complex quaternary configurations of mepenzolate bromide and tiotidine in the raw dataset) are rejected, meaning certain compounds are automatically excluded during preprocessing.

### B. Fingerprint Scaffold Generalization Defect
*   **Observed Generalization Gap:** Fingerprint-based models showed substantially poorer scaffold generalization than descriptor-based models in this dataset and experimental setup. The Random Forest fingerprints model experienced a drop in Macro F1 from 0.8172 (random split) to 0.5546 (scaffold split).
*   **Reasoning:** Hashed circular fingerprints (ECFP4) represent highly specific structural sub-environments. This may reflect that circular fingerprints do not generalize as well to unseen ring configurations, causing models relying on them to overfit training motifs. Descriptors-only models showed greater robustness to scaffold shift in our experiments (dropping by only -0.1392 Macro F1 points), as general rules regarding size, polarity, and charge remain consistent across structural classes.

---

## 4. Dataset Biases and Literature Noise
*   **Experimental Label Noise:** B3DB aggregates data from 50 separate published literature sources that use differing criteria (varying logBB thresholds, in vitro models, or in vivo animal assays) to define BBB permeability. This literature noise introduces label inconsistencies, where structurally identical molecules can have contradictory labels in the raw dataset.
*   **Imbalance Bias:** The dataset features a moderate class skew (63.5% BBB+ / 36.5% BBB-). While we mitigate this using Macro F1 and class-balanced tree bagging in Random Forest, predictions near the decision boundary remain sensitive to this skew.
