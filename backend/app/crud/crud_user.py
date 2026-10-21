from sqlalchemy.orm import Session
from app.models.user import User

class CRUDUser:
    def get(self, db: Session, id: int):
        # Query the database to find a user by their ID
        return db.query(User).filter(User.id == id).first()

    def get_by_email(self, db: Session, email: str):
        # Query the database to find a user by their email
        return db.query(User).filter(User.email == email).first()

    def create(self, db: Session, user_dict: dict) -> User:
        # Create a new User database model instance
        db_user = User(**user_dict)
        db.add(db_user)      # Add it to the session
        db.commit()          # Save to the database
        db.refresh(db_user)  # Refresh to get the auto-generated ID
        return db_user

    def update_password(self, db: Session, user: User, new_password_hash: str) -> User:
        user.password_hash = new_password_hash
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

# Export an instance so we can easily import it in our services
user_crud = CRUDUser()
