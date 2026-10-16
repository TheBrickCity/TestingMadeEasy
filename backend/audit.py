from sqlalchemy.orm import Session

import models


def log_action(db: Session, user_id: int, action_type: str) -> None:
    db.add(models.Log(user_id=user_id, action_type=action_type))
    db.commit()