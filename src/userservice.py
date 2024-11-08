from typing import List, Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from .databaseservice import DatabaseService, get_db
from .models import User, UserCreate, UserUpdate

class UserService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def create_user(self, user: UserCreate) -> User:
        db_user = User(**user.dict())
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        return self.db.query(User).offset(skip).limit(limit).all()

    def update_user(self, user_id: int, user_update: UserUpdate) -> User:
        db_user = self.get_user_by_id(user_id)
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        for field, value in user_update.dict(exclude_unset=True).items():
            setattr(db_user, field, value)
        
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def delete_user(self, user_id: int) -> bool:
        db_user = self.get_user_by_id(user_id)
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        self.db.delete(db_user)
        self.db.commit()
        return True
