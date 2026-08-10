from sklearn.model_selection import train_test_split

def generate_random_stratified_split(df, target_col="BBB+/BBB-", test_size=0.20, seed=42):
    """
    Generates a stratified random split.
    
    Args:
        df (pd.DataFrame): Cleaned input DataFrame.
        target_col (str): Target column for stratification.
        test_size (float): Proportional size of test set.
        seed (int): Reproducibility random state seed.
        
    Returns:
        tuple: (train_indices, test_indices)
    """
    indices = df.index.tolist()
    targets = df[target_col].tolist()
    
    train_idx, test_idx = train_test_split(
        indices,
        test_size=test_size,
        stratify=targets,
        random_state=seed
    )
    
    return train_idx, test_idx
