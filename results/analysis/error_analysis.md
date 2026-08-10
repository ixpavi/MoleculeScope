# Detailed Error Analysis — MoleculeScope

This document outlines the failure modes and property distributions for errors produced on the Bemis-Murcko Scaffold split by the best generalizing model (**Random Forest on Descriptors**).

---

## 1. Property Means by Prediction Status

| Prediction Status | Sample Count | Mean MW | Mean LogP | Mean TPSA | Mean HBD |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Correct** | 1161 | 339.82 | 2.59 | 69.57 | 1.55 |
| **False Positives (FPs)** | 255 | 329.76 | 3.15 | 61.13 | 1.19 |
| **False Negatives (FNs)** | 143 | 345.71 | 1.71 | 97.67 | 2.41 |

---

## 2. Key Insights and Property Trends

### A. False Positives (FPs)
*   **Definition:** BBB- (impermeable) compounds predicted as BBB+ (permeable).
*   **Property Characteristics:**
    *   *Observation:* False Positives show a significantly lower mean TPSA (**61.13** Å²) and lower Hydrogen Bond Donors count (**1.19**) compared to correct predictions.
    *   *Rationale:* In structural pharmacology, lower polarity (TPSA < 90 Å²) and low hydrogen-bonding counts are strong signals for passive membrane partition. When an impermeable compound possesses these features (for example, due to a highly polar but uncharged moiety or a specific quaternary nitrogen that impedes entry despite favorable bulk parameters), the model falsely classifies it as BBB+ due to its favorable bulk indicators.

### B. False Negatives (FNs)
*   **Definition:** BBB+ (permeable) compounds predicted as BBB- (impermeable).
*   **Property Characteristics:**
    *   *Observation:* False Negatives show a higher mean TPSA (**97.67** Å²) and higher Hydrogen Bond Donors (**2.41**).
    *   *Rationale:* Highly polar molecules with many donor groups are generally predicted as BBB- because the bulk descriptors strongly align with impermeability. A potential biological explanation is that certain permeable compounds bypass passive diffusion limits via active transport mechanisms (for example, targeting glucose transporters or peptide carriers). Since our descriptor model is restricted to passive physicochemical indices, it may misclassify these potentially transporter-mediated entrants as BBB-.

---

## 3. Representative Error Compounds

### A. False Positives (Predicted BBB+, True BBB-)
*   **efavirenz** (SMILES: `CC(C)(C)c1ccc(C(=O)CCCN2CCC(OC(c3ccccc3)c3ccccc3)CC2)cc1`): MW: `469.67`, LogP: `7.22`, TPSA: `29.54`, Prob(BBB+): `0.6402`
*   **hydroflumethiazide** (SMILES: `COc1cc2c(cc1OC)CN(C(=O)CC1NC(=O)N(c3ccc(C(C)C)cc3)C1=O)CC2`): MW: `451.52`, LogP: `3.23`, TPSA: `88.18`, Prob(BBB+): `0.6193`
*   **hydroflumethiazide** (SMILES: `COc1cc2c(cc1OC)CN(C(=O)C[C@@H]1NC(=O)N(c3ccc(C(C)C)cc3)C1=O)CC2`): MW: `451.52`, LogP: `3.23`, TPSA: `88.18`, Prob(BBB+): `0.6193`
*   **doxazosin mesylate** (SMILES: `COc1cc2nc(N3CCN(C(=O)C4COc5ccccc5O4)CC3)nc(N)c2cc1OC`): MW: `451.48`, LogP: `1.72`, TPSA: `112.27`, Prob(BBB+): `0.5428`
*   **etozolin** (SMILES: `CCOC(=O)C=C1SC(N2CCCCC2)C(=O)N1C`): MW: `284.38`, LogP: `1.41`, TPSA: `49.85`, Prob(BBB+): `0.8783`


### B. False Negatives (Predicted BBB-, True BBB+)
*   **(s)-bicalutamide** (SMILES: `C[C@@](O)(CS(=O)(=O)c1ccc(F)cc1)C(=O)Nc1ccc(C#N)c(C(F)(F)F)c1`): MW: `430.38`, LogP: `2.88`, TPSA: `107.26`, Prob(BBB+): `0.2676`
*   **nortriptyline** (SMILES: `O=C(O)CC[C@]1(CCC(=O)NCc2cc3cc(F)ccc3[nH]2)CCC(=O)N1`): MW: `375.40`, LogP: `2.22`, TPSA: `111.29`, Prob(BBB+): `0.3002`
*   **phenobarbital** (SMILES: `COc1ccc(NC(=O)C[C@H]2OC(=O)c3c2ccc(OC)c3OC)cc1N1CCCS1(=O)=O`): MW: `476.51`, LogP: `2.49`, TPSA: `120.47`, Prob(BBB+): `0.4241`
*   **(s)-terazosin** (SMILES: `COc1cc2nc(N3CCN(C(=O)[C@@H]4CCCO4)CC3)nc(N)c2cc1OC`): MW: `387.44`, LogP: `1.06`, TPSA: `103.04`, Prob(BBB+): `0.4311`
*   **sulindac** (SMILES: `CC1=C(CC(=O)O)c2cc(F)ccc2/C1=C/c1ccc([S+](C)[O-])cc1`): MW: `356.42`, LogP: `4.37`, TPSA: `60.36`, Prob(BBB+): `0.4637`

