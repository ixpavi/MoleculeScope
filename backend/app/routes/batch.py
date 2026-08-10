import csv
import io
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from ..schemas.prediction import BatchPredictionResponse
from ..services.predictor import predict_smiles_batch

router = APIRouter()

MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024
READ_CHUNK_SIZE = 1024 * 1024

@router.post(
    "/predict/batch",
    response_model=BatchPredictionResponse,
    summary="Predict BBB permeability for a batch of molecules from CSV"
)
async def predict_batch(file: UploadFile = File(...)):
    """
    Accepts a CSV file containing a list of SMILES notation strings, computes 11 descriptors
    for each valid structure in a single optimized batch run, and scores the frozen production
    Random Forest classifier.

    File-level constraints:
    - Maximum size: 5 MB
    - Maximum data rows: 5,000 records (excluding header)
    - Required 'smiles' column (case-insensitive, e.g. smiles, SMILES, Smiles).
    """
    # 1. Read the upload in bounded chunks, rejecting oversized files as soon as the limit
    # is crossed rather than buffering an arbitrarily large upload into memory first.
    chunks = []
    total_size = 0
    while True:
        chunk = await file.read(READ_CHUNK_SIZE)
        if not chunk:
            break
        total_size += len(chunk)
        if total_size > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size exceeds the 5 MB limit."
            )
        chunks.append(chunk)
    contents = b"".join(chunks)

    # 2. Decode the CSV bytes to string safely. "utf-8-sig" transparently strips a leading
    # UTF-8 byte-order-mark if present (which Excel's "CSV UTF-8" export always adds) while
    # behaving identically to plain "utf-8" when no BOM is present.
    try:
        csv_text = contents.decode("utf-8-sig")
    except UnicodeDecodeError:
        try:
            csv_text = contents.decode("latin-1")
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to decode uploaded file. Ensure it is a valid text CSV file."
            )
            
    # 3. Structural checks on CSV
    csv_file = io.StringIO(csv_text)
    reader = csv.reader(csv_file)
    
    try:
        header = next(reader)
    except StopIteration:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded CSV file is empty."
        )
        
    if not header or all(not col.strip() for col in header):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded CSV file is empty."
        )
        
    # 4. SMILES column check (case-insensitive matching)
    smiles_indices = []
    for idx, col in enumerate(header):
        if col.strip().lower() == "smiles":
            smiles_indices.append(idx)
            
    if len(smiles_indices) > 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Conflicting duplicate SMILES columns detected in CSV."
        )
        
    if not smiles_indices:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing required SMILES column in CSV. Found columns: {header}"
        )
        
    smiles_col_idx = smiles_indices[0]
    
    # 5. Parse rows while enforcing row limits and skipping completely blank rows
    batch_inputs = []
    row_count = 0
    
    try:
        for row in reader:
            # Skip completely blank lines
            if not row or all(not cell.strip() for cell in row):
                continue
                
            row_count += 1
            if row_count > 5000:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Number of data rows exceeds the 5,000-record limit."
                )
                
            # Extract SMILES value safely
            smiles_val = row[smiles_col_idx].strip() if smiles_col_idx < len(row) else ""
            
            # Extract extra columns
            extra_cols = {}
            for col_idx, col_name in enumerate(header):
                if col_idx != smiles_col_idx:
                    val = row[col_idx].strip() if col_idx < len(row) else ""
                    extra_cols[col_name] = val
                    
            batch_inputs.append({
                "row_index": row_count,
                "smiles": smiles_val,
                "extra_columns": extra_cols
            })
    except csv.Error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or malformed CSV file structure."
        )
        
    if not batch_inputs:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded CSV file is empty."
        )
        
    # 6. Execute batch prediction
    results = predict_smiles_batch(batch_inputs)
    
    # 7. Compute summary statistics
    processed_count = sum(1 for r in results if r["status"] == "success")
    failed_count = sum(1 for r in results if r["status"] == "error")
    bbb_plus_count = sum(1 for r in results if r["prediction"] == "BBB+")
    bbb_minus_count = sum(1 for r in results if r["prediction"] == "BBB-")
    
    summary = {
        "filename": file.filename or "uploaded_file.csv",
        "total_rows": row_count,
        "processed_rows": processed_count,
        "failed_rows": failed_count,
        "bbb_plus_count": bbb_plus_count,
        "bbb_minus_count": bbb_minus_count
    }
    
    return {
        "summary": summary,
        "results": results
    }
