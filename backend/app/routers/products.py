from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import crud, models, schemas, auth
from ..database import get_db

router = APIRouter(
    prefix="/products",
    tags=["products"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=List[schemas.Product])
def read_products(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """Obtener todos los productos del usuario"""
    products = crud.get_products(db, user_id=current_user.id)
    return products

@router.get("/{product_id}", response_model=schemas.Product)
def read_product(product_id: int, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """Obtener un producto específico"""
    product = crud.get_product(db, product_id=product_id, user_id=current_user.id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.post("/", response_model=schemas.Product)
def create_product(product: schemas.ProductCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """Crear un nuevo producto"""
    return crud.create_product(db=db, product=product, user_id=current_user.id)

@router.delete("/{product_id}")
def delete_product(product_id: int, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """Eliminar un producto"""
    success = crud.delete_product(db, product_id=product_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}