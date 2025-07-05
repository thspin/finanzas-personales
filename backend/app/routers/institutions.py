from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import crud, models, schemas, auth
from ..database import get_db

router = APIRouter(
    prefix="/institutions",
    tags=["institutions"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=List[schemas.Institution])
def read_institutions(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """Obtener todas las instituciones del usuario"""
    institutions = crud.get_institutions(db, user_id=current_user.id)
    return institutions

@router.get("/{institution_id}", response_model=schemas.Institution)
def read_institution(institution_id: int, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """Obtener una institución específica"""
    institution = crud.get_institution(db, institution_id=institution_id, user_id=current_user.id)
    if institution is None:
        raise HTTPException(status_code=404, detail="Institution not found")
    return institution

@router.post("/", response_model=schemas.Institution)
def create_institution(institution: schemas.InstitutionCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """Crear una nueva institución"""
    return crud.create_institution(db=db, institution=institution, user_id=current_user.id)

@router.delete("/{institution_id}")
def delete_institution(institution_id: int, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """Eliminar una institución"""
    success = crud.delete_institution(db, institution_id=institution_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Institution not found")
    return {"message": "Institution deleted successfully"}