from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import crud, models, schemas, auth
from ..database import get_db

router = APIRouter(
    prefix="/categories",
    tags=["categories"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=schemas.Category)
def create_category(category: schemas.CategoryCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    return crud.create_category(db=db, category=category, user_id=current_user.id)

@router.get("/", response_model=List[schemas.Category])
def read_categories(category_type: Optional[str] = None, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    categories = crud.get_categories(db, user_id=current_user.id, category_type=category_type)
    return categories

@router.get("/{category_id}", response_model=schemas.Category)
def read_category(category_id: int, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    db_category = crud.get_category(db, category_id=category_id, user_id=current_user.id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return db_category

@router.delete("/{category_id}")
def delete_category(category_id: int, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    success = crud.delete_category(db, category_id=category_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"message": "Category deleted successfully"}

@router.post("/initialize-defaults")
def initialize_default_categories(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """Crear categorías predeterminadas para un usuario"""
    crud.create_default_categories(db, user_id=current_user.id)
    return {"message": "Default categories created successfully"}