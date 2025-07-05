from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import crud, models, schemas, auth
from ..database import get_db

router = APIRouter(
    prefix="/credits",
    tags=["credits"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=schemas.Credit)
def create_credit(credit: schemas.CreditCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    return crud.create_credit_with_installments(db=db, credit=credit)

@router.get("/product/{product_id}", response_model=List[schemas.Credit])
def read_credits(product_id: int, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    credits = crud.get_credits(db, product_id=product_id)
    return credits

@router.get("/{credit_id}/installments", response_model=List[schemas.Installment])
def read_installments(credit_id: int, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    installments = crud.get_installments(db, credit_id=credit_id)
    return installments