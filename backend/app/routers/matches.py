from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import schemas, crud, database

router = APIRouter(
    prefix="/matches",
    tags=["matches"],
)

@router.post("/", response_model=schemas.Match)
def create_match(match: schemas.MatchCreate, db: Session = Depends(database.get_db)):
    return crud.create_match(db=db, match=match)

@router.get("/{match_id}", response_model=schemas.Match)
def read_match(match_id: int, db: Session = Depends(database.get_db)):
    db_match = crud.get_match(db, match_id=match_id)
    if db_match is None:
        raise HTTPException(status_code=404, detail="Match not found")
    return db_match