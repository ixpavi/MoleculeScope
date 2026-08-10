# Report-Ready Performance Summaries — MoleculeScope

This document provides copy-pasteable paragraphs summarizing the machine learning results, generalization gaps, selection rationales, and limitations for college reports and presentations.

---

## 1. Model Performance & Comparative Summary
"We evaluated three machine learning architectures—Logistic Regression, Random Forest, and XGBoost—across three molecular feature representations: 11 physicochemical descriptors, 2048-bit binary Morgan circular fingerprints (ECFP4 equivalent), and a 2059-dimension combined feature set. Under baseline in-distribution conditions (stratified random split), all models achieved strong predictive signal, comfortably outperforming the majority-class baseline of 63.57%. The top in-distribution classifier was the Random Forest model trained on physicochemical descriptors, achieving a peak accuracy of 87.36% and a Macro F1-score of 0.8604. For probabilistic ranking, the combined representation achieved superior discrimination, with Logistic Regression yielding a peak ROC-AUC of 0.9466."

---

## 2. Generalization Gap & Scaffold Shift Summary
"To evaluate the structural generalization capability of our classifiers, we tested them on structurally novel chemistry using Bemis-Murcko scaffold splitting with zero train/test scaffold overlap. Every model exhibited a distinct performance drop, highlighting the generalization gap under out-of-distribution shifts. Fingerprint-based models showed substantially poorer scaffold generalization than descriptor-based models in this dataset and experimental setup, with the Random Forest fingerprints model experiencing a drop in Macro F1 from 0.8172 to 0.5546. This may reflect that circular fingerprints do not generalize as well to unseen ring configurations. Conversely, descriptors-only models showed greater robustness to scaffold shift than fingerprint-only models in our experiments: the descriptors-based Random Forest evaluation model dropped by only 0.1392 Macro F1 points (retaining a Macro F1 of 0.7212 and an accuracy of 74.47%), suggesting that bulk physical parameters like polar surface area and hydrogen donor counts generalize more effectively across structural classes."

---

## 3. Final Model Selection & Rationale
"We select the Random Forest classifier trained on the 11 molecular descriptors as the final production architecture. Under the scaffold split generalization test, the evaluation model achieved a classification accuracy of 74.47% and a Macro F1-score of 0.7212. While XGBoost on combined features yielded a slightly higher evaluation ROC-AUC (0.8138 vs. 0.8017), the descriptors-only Random Forest provides the ideal balance of generalization robustness, low operational complexity, and chemical explainability. Phase 6 will retrain this selected architecture on the full cleaned dataset of 7,795 molecules for production deployment, while preserving the scaffold evaluation metrics as the baseline generalization benchmark."

---

## 4. Modeling Limitations & Failure Modes
"Error audits on the scaffold split reveal different descriptor distributions for classification errors. First, False Positives (impermeable compounds predicted as permeable) typically occur in structures with lower Topological Polar Surface Area (mean TPSA = 61.13 Å²) and lower hydrogen-bond donor counts (mean HBD = 1.19); a potential explanation is that these may be blocked from entering the brain by specific efflux networks or charged moieties not fully captured by bulk descriptors. Second, False Negatives (permeable compounds predicted as impermeable) occur in more polar structures (mean TPSA = 97.67 Å², mean HBD = 2.41); a potential biological explanation is that these compounds may bypass passive lipid diffusion limits via active, carrier-mediated transport mechanisms (e.g., glucose or amino acid channels) which are not explicitly represented in our passive physicochemical features."
