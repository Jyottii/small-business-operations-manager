from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog
from app.models.notification import Notification

class AuditService:
    @staticmethod
    def log(db: Session, business_id: str, action: str, entity_type: str, entity_id: str, description: str, user_id: str = "SYSTEM"):
        log = AuditLog(
            business_id=business_id,
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            description=description
        )
        db.add(log)
        db.flush()

class NotificationService:
    @staticmethod
    def notify(db: Session, business_id: str, title: str, message: str, notif_type: str = "INFO", related_entity_type: str = None, related_entity_id: str = None, user_id: str = "SYSTEM"):
        notif = Notification(
            business_id=business_id,
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notif_type,
            related_entity_type=related_entity_type,
            related_entity_id=related_entity_id
        )
        db.add(notif)
        db.flush()
