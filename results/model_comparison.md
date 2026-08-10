# Model Performance Comparison Matrix — MoleculeScope

This table contains the comparative results of all 18 primary experiments and the majority-class baselines.

| Model | Representation | Split | Train N | Test N | Accuracy | Precision | Recall | F1 | Macro F1 | ROC-AUC | PR-AUC |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| baseline_majority | all | random | 6236 | 1559 | 0.6357 | 0.6357 | 1.0000 | 0.7773 | 0.3886 | 0.5000 | 0.8178 |
| baseline_majority | all | scaffold | 6236 | 1559 | 0.6094 | 0.6094 | 1.0000 | 0.7573 | 0.3786 | 0.5000 | 0.8047 |
| logistic | descriptors | random | 6236 | 1559 | 0.8069 | 0.7979 | 0.9324 | 0.8599 | 0.7747 | 0.8545 | 0.8831 |
| rf | descriptors | random | 6236 | 1559 | 0.8736 | 0.8788 | 0.9294 | 0.9034 | 0.8604 | 0.9382 | 0.9590 |
| xgb | descriptors | random | 6236 | 1559 | 0.8602 | 0.8510 | 0.9455 | 0.8958 | 0.8417 | 0.9301 | 0.9520 |
| logistic | fingerprints | random | 6236 | 1559 | 0.8653 | 0.8606 | 0.9405 | 0.8987 | 0.8488 | 0.9398 | 0.9604 |
| rf | fingerprints | random | 6236 | 1559 | 0.8435 | 0.8223 | 0.9617 | 0.8865 | 0.8172 | 0.9279 | 0.9527 |
| xgb | fingerprints | random | 6236 | 1559 | 0.8621 | 0.8470 | 0.9556 | 0.8981 | 0.8425 | 0.9349 | 0.9574 |
| logistic | combined | random | 6236 | 1559 | 0.8711 | 0.8671 | 0.9415 | 0.9028 | 0.8558 | 0.9466 | 0.9651 |
| rf | combined | random | 6236 | 1559 | 0.8627 | 0.8522 | 0.9485 | 0.8978 | 0.8444 | 0.9411 | 0.9621 |
| xgb | combined | random | 6236 | 1559 | 0.8717 | 0.8693 | 0.9395 | 0.9030 | 0.8568 | 0.9458 | 0.9646 |
| logistic | descriptors | scaffold | 6236 | 1559 | 0.7300 | 0.7195 | 0.9126 | 0.8046 | 0.6837 | 0.7648 | 0.7903 |
| rf | descriptors | scaffold | 6236 | 1559 | 0.7447 | 0.7599 | 0.8495 | 0.8022 | 0.7212 | 0.8017 | 0.8504 |
| xgb | descriptors | scaffold | 6236 | 1559 | 0.7255 | 0.7281 | 0.8768 | 0.7956 | 0.6888 | 0.7947 | 0.8457 |
| logistic | fingerprints | scaffold | 6236 | 1559 | 0.6876 | 0.6902 | 0.8842 | 0.7753 | 0.6316 | 0.7435 | 0.8172 |
| rf | fingerprints | scaffold | 6236 | 1559 | 0.6684 | 0.6550 | 0.9632 | 0.7797 | 0.5546 | 0.7448 | 0.8277 |
| xgb | fingerprints | scaffold | 6236 | 1559 | 0.6934 | 0.6829 | 0.9274 | 0.7866 | 0.6211 | 0.7614 | 0.8345 |
| logistic | combined | scaffold | 6236 | 1559 | 0.7146 | 0.7106 | 0.8968 | 0.7929 | 0.6668 | 0.7865 | 0.8445 |
| rf | combined | scaffold | 6236 | 1559 | 0.7178 | 0.7037 | 0.9274 | 0.8002 | 0.6599 | 0.8044 | 0.8630 |
| xgb | combined | scaffold | 6236 | 1559 | 0.7280 | 0.7206 | 0.9042 | 0.8021 | 0.6838 | 0.8138 | 0.8684 |

