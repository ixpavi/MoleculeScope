from fastapi import APIRouter, Query
from ..schemas.prediction import MoleculeSearchResponse
from ..services.molecule_search import molecule_search_service

router = APIRouter()


@router.get(
    "/molecules/search",
    response_model=MoleculeSearchResponse,
    summary="Search compounds by name from the cleaned B3DB dataset"
)
def search_molecules(
    q: str = Query(..., min_length=1, description="Compound name or partial name to search for."),
    limit: int = Query(20, ge=1, le=50, description="Maximum number of results to return."),
):
    """
    Lets a user find a molecule by name instead of typing SMILES directly, backed by the
    7,795-molecule cleaned B3DB dataset. Compound names are taken as-is from the source
    dataset and are not independently verified against their SMILES, so results should be
    visually confirmed via the rendered structure before relying on them.
    """
    results = molecule_search_service.search(q, limit=limit)
    return {"results": results}
