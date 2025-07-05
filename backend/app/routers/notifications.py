from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import crud, models, schemas, auth
from ..database import get_db

router = APIRouter(
    prefix="/notifications",
    tags=["notifications"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=List[schemas.Notification])
def read_notifications(is_read: Optional[bool] = None, limit: int = 50, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """Obtener notificaciones del usuario"""
    notifications = crud.get_notifications(db, user_id=current_user.id, is_read=is_read, limit=limit)
    return notifications

@router.get("/count")
def get_unread_count(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """Obtener cantidad de notificaciones no leídas"""
    count = crud.get_unread_notifications_count(db, user_id=current_user.id)
    return {"unread_count": count}

@router.post("/", response_model=schemas.Notification)
def create_notification(notification: schemas.NotificationCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """Crear una nueva notificación"""
    return crud.create_notification(db=db, notification=notification, user_id=current_user.id)

@router.put("/{notification_id}/read", response_model=schemas.Notification)
def mark_notification_read(notification_id: int, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """Marcar notificación como leída"""
    notification = crud.mark_notification_as_read(db, notification_id=notification_id, user_id=current_user.id)
    if notification is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification

@router.put("/read-all")
def mark_all_notifications_read(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """Marcar todas las notificaciones como leídas"""
    count = crud.mark_all_notifications_as_read(db, user_id=current_user.id)
    return {"message": f"Marked {count} notifications as read"}

@router.delete("/{notification_id}")
def delete_notification(notification_id: int, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """Eliminar una notificación"""
    success = crud.delete_notification(db, notification_id=notification_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"message": "Notification deleted successfully"}

@router.post("/service-due/{service_id}")
def create_service_due_notification(service_id: int, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """Crear notificación de vencimiento de servicio"""
    notification = crud.create_service_due_notification(db, service_id=service_id, user_id=current_user.id)
    if notification is None:
        raise HTTPException(status_code=404, detail="Service not found")
    return notification