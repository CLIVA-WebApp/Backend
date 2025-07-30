from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from app.src.models.puskesmas import Puskesmas
from app.src.schemas.puskesmas_schema import PuskesmasCreate, PuskesmasUpdate

class PuskesmasController:
    def __init__(self):
        pass
    
    async def create_puskesmas(self, puskesmas: PuskesmasCreate, db: Session) -> Puskesmas:
        """Create a new puskesmas"""
        try:
            db_puskesmas = Puskesmas(**puskesmas.dict())
            db.add(db_puskesmas)
            db.commit()
            db.refresh(db_puskesmas)
            return db_puskesmas
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create puskesmas: {str(e)}"
            )
    
    async def get_puskesmas(self, puskesmas_id: int, db: Session) -> Puskesmas:
        """Get a specific puskesmas by ID"""
        try:
            puskesmas = db.query(Puskesmas).filter(Puskesmas.id == puskesmas_id).first()
            if not puskesmas:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Puskesmas not found"
                )
            return puskesmas
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get puskesmas: {str(e)}"
            )
    
    async def update_puskesmas(self, puskesmas_id: int, puskesmas: PuskesmasUpdate, db: Session) -> Puskesmas:
        """Update a puskesmas"""
        try:
            db_puskesmas = db.query(Puskesmas).filter(Puskesmas.id == puskesmas_id).first()
            if not db_puskesmas:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Puskesmas not found"
                )
            
            for key, value in puskesmas.dict(exclude_unset=True).items():
                setattr(db_puskesmas, key, value)
            
            db.commit()
            db.refresh(db_puskesmas)
            return db_puskesmas
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update puskesmas: {str(e)}"
            )
    
    async def delete_puskesmas(self, puskesmas_id: int, db: Session) -> dict:
        """Delete a puskesmas"""
        try:
            db_puskesmas = db.query(Puskesmas).filter(Puskesmas.id == puskesmas_id).first()
            if not db_puskesmas:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Puskesmas not found"
                )
            
            db.delete(db_puskesmas)
            db.commit()
            return {"message": "Puskesmas deleted successfully"}
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete puskesmas: {str(e)}"
            ) 