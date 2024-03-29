from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import schemas, crud, database

router = APIRouter(
    prefix="/teams",
    tags=["teams"],
)

@router.post("/", response_model=schemas.Team)
def create_team(team: schemas.TeamCreate, db: Session = Depends(database.get_db)):
    return crud.create_team(db=db, team=team)

@router.get("/{team_id}", response_model=schemas.Team)
def read_team(team_id: int, db: Session = Depends(database.get_db)):
    db_team = crud.get_team(db, team_id=team_id)
    if db_team is None:
        raise HTTPException(status_code=404, detail="Team not found")
    return db_team