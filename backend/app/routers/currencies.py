from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import crud, models, schemas, auth
from ..database import get_db

router = APIRouter(
    prefix="/currencies",
    tags=["currencies"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=List[schemas.Currency])
def read_currencies(db: Session = Depends(get_db)):
    """Obtener todas las monedas disponibles"""
    currencies = crud.get_currencies(db)
    return currencies

@router.get("/{currency_id}", response_model=schemas.Currency)
def read_currency(currency_id: int, db: Session = Depends(get_db)):
    """Obtener una moneda específica por ID"""
    db_currency = crud.get_currency(db, currency_id=currency_id)
    if db_currency is None:
        raise HTTPException(status_code=404, detail="Currency not found")
    return db_currency

@router.get("/code/{code}", response_model=schemas.Currency)
def read_currency_by_code(code: str, db: Session = Depends(get_db)):
    """Obtener una moneda específica por código (ej: ARS, USD)"""
    db_currency = crud.get_currency_by_code(db, code=code.upper())
    if db_currency is None:
        raise HTTPException(status_code=404, detail="Currency not found")
    return db_currency

@router.post("/", response_model=schemas.Currency)
def create_currency(currency: schemas.CurrencyCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """Crear una nueva moneda"""
    # Verificar que no exista una moneda con el mismo código
    db_currency = crud.get_currency_by_code(db, code=currency.code.upper())
    if db_currency:
        raise HTTPException(status_code=400, detail="Currency code already exists")
    
    # Normalizar código a mayúsculas
    currency.code = currency.code.upper()
    return crud.create_currency(db=db, currency=currency)