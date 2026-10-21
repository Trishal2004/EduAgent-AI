from sqlalchemy.orm import Session
from app.models.notification import Notification
from app.DTOs.notification import NotificationCreate

class NotificationService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_notifications(self, user_id: int, limit: int = 20):
        return self.db.query(Notification).filter(
            Notification.user_id == user_id
        ).order_by(Notification.created_at.desc()).limit(limit).all()

    def create_notification(self, user_id: int, notif_in: NotificationCreate):
        notif = Notification(
            user_id=user_id,
            title=notif_in.title,
            message=notif_in.message,
            type=notif_in.type
        )
        self.db.add(notif)
        self.db.commit()
        self.db.refresh(notif)
        return notif

    def mark_as_read(self, user_id: int, notification_id: int):
        notif = self.db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()
        if notif:
            notif.is_read = True
            self.db.commit()
            self.db.refresh(notif)
        return notif

    def mark_all_read(self, user_id: int):
        self.db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).update({"is_read": True})
        self.db.commit()
        return {"status": "success"}
