from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from src.models.puskesmas import Puskesmas
from src.schemas.puskesmas_schema import PuskesmasCreate, PuskesmasUpdate

class PuskesmasController:
    def __init__(self):
        pass
    
    async def create_puskesmas(self, db: Session, puskesmas_data: PuskesmasCreate) -> Puskesmas:
        """Create new Puskesmas"""
        # Check if kode already exists
        existing = db.query(Puskesmas).filter(Puskesmas.kode == puskesmas_data.kode).first()
        if existing:
            raise HTTPException(status_code=400, detail="Kode Puskesmas already exists")
        
        db_puskesmas = Puskesmas(**puskesmas_data.dict())
        db.add(db_puskesmas)
        db.commit()
        db.refresh(db_puskesmas)
        return db_puskesmas
    
    async def get_all_puskesmas(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        provinsi: Optional[str] = None,
        kabupaten: Optional[str] = None
    ) -> List[Puskesmas]:
        """Get all Puskesmas with optional filters"""
        query = db.query(Puskesmas).filter(Puskesmas.is_active == True)
        
        if provinsi:
            query = query.filter(Puskesmas.provinsi.ilike(f"%{provinsi}%"))
        if kabupaten:
            query = query.filter(Puskesmas.kabupaten.ilike(f"%{kabupaten}%"))
        
        return query.offset(skip).limit(limit).all()
    
    async def get_puskesmas_by_id(self, db: Session, puskesmas_id: int) -> Optional[Puskesmas]:
        """Get Puskesmas by ID"""
        return db.query(Puskesmas).filter(
            and_(Puskesmas.id == puskesmas_id, Puskesmas.is_active == True)
        ).first()
    
    async def update_puskesmas(
        self, 
        db: Session, 
        puskesmas_id: int, 
        puskesmas_data: PuskesmasUpdate
    ) -> Optional[Puskesmas]:
        """Update Puskesmas"""
        db_puskesmas = await self.get_puskesmas_by_id(db, puskesmas_id)
        if not db_puskesmas:
            return None
        
        update_data = puskesmas_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_puskesmas, field, value)
        
        db.commit()
        db.refresh(db_puskesmas)
        return db_puskesmas
    
    async def delete_puskesmas(self, db: Session, puskesmas_id: int) -> bool:
        """Soft delete Puskesmas"""
        db_puskesmas = await self.get_puskesmas_by_id(db, puskesmas_id)
        if not db_puskesmas:
            return False
        
        db_puskesmas.is_active = False
        db.commit()
        return True
    
    async def get_puskesmas_by_location(
        self, 
        db: Session, 
        latitude: float, 
        longitude: float, 
        radius_km: float = 10.0
    ) -> List[Puskesmas]:
        """Get Puskesmas within radius of given coordinates"""
        # Simple distance calculation (Haversine formula would be better for production)
        # For now, using bounding box approximation
        lat_range = radius_km / 111.0  # Approximate km per degree latitude
        lon_range = radius_km / (111.0 * abs(latitude))  # Approximate km per degree longitude
        
        return db.query(Puskesmas).filter(
            and_(
                Puskesmas.is_active == True,
                Puskesmas.latitude.between(latitude - lat_range, latitude + lat_range),
                Puskesmas.longitude.between(longitude - lon_range, longitude + lon_range)
            )
        ).all() 