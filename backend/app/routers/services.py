from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import crud, models, schemas, auth
from ..database import get_db

router = APIRouter(
    prefix="/services",
    tags=["services"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=schemas.Service)
def create_service(service: schemas.ServiceCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """Crear un nuevo servicio/suscripción"""
    return crud.create_service(db=db, service=service, user_id=current_user.id)

@router.get("/", response_model=List[schemas.Service])
def read_services(is_active: Optional[bool] = None, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """Obtener todos los servicios del usuario"""
    services = crud.get_services(db, user_id=current_user.id, is_active=is_active)
    return services

@router.get("/upcoming", response_model=List[schemas.Service])
def read_upcoming_services(days_ahead: int = 7, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """Obtener servicios que vencen en los próximos N días"""
    services = crud.get_upcoming_services(db, user_id=current_user.id, days_ahead=days_ahead)
    return services

@router.get("/{service_id}", response_model=schemas.Service)
def read_service(service_id: int, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """Obtener un servicio específico"""
    db_service = crud.get_service(db, service_id=service_id, user_id=current_user.id)
    if db_service is None:
        raise HTTPException(status_code=404, detail="Service not found")
    return db_service

@router.put("/{service_id}", response_model=schemas.Service)
def update_service(service_id: int, service: schemas.ServiceCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """Actualizar un servicio"""
    db_service = crud.update_service(db, service_id=service_id, service=service, user_id=current_user.id)
    if db_service is None:
        raise HTTPException(status_code=404, detail="Service not found")
    return db_service

@router.delete("/{service_id}")
def delete_service(service_id: int, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """Eliminar un servicio"""
    success = crud.delete_service(db, service_id=service_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Service not found")
    return {"message": "Service deleted successfully"}