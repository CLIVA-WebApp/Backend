from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from src.config.database import get_db
from src.schemas.puskesmas_schema import PuskesmasCreate, PuskesmasUpdate, PuskesmasResponse
from src.controllers.puskesmas_controller import PuskesmasController

router = APIRouter(prefix="/puskesmas", tags=["Puskesmas"])

@router.post("/", response_model=PuskesmasResponse, status_code=status.HTTP_201_CREATED)
async def create_puskesmas(puskesmas: PuskesmasCreate, db: Session = Depends(get_db)):
    """Create new Puskesmas"""
    controller = PuskesmasController()
    return await controller.create_puskesmas(db, puskesmas)

@router.get("/", response_model=List[PuskesmasResponse])
async def get_all_puskesmas(
    skip: int = 0, 
    limit: int = 100, 
    provinsi: str = None,
    kabupaten: str = None,
    db: Session = Depends(get_db)
):
    """Get all Puskesmas with optional filters"""
    controller = PuskesmasController()
    return await controller.get_all_puskesmas(db, skip, limit, provinsi, kabupaten)

@router.get("/{puskesmas_id}", response_model=PuskesmasResponse)
async def get_puskesmas(puskesmas_id: int, db: Session = Depends(get_db)):
    """Get Puskesmas by ID"""
    controller = PuskesmasController()
    puskesmas = await controller.get_puskesmas_by_id(db, puskesmas_id)
    if not puskesmas:
        raise HTTPException(status_code=404, detail="Puskesmas not found")
    return puskesmas

@router.put("/{puskesmas_id}", response_model=PuskesmasResponse)
async def update_puskesmas(
    puskesmas_id: int, 
    puskesmas: PuskesmasUpdate, 
    db: Session = Depends(get_db)
):
    """Update Puskesmas"""
    controller = PuskesmasController()
    updated_puskesmas = await controller.update_puskesmas(db, puskesmas_id, puskesmas)
    if not updated_puskesmas:
        raise HTTPException(status_code=404, detail="Puskesmas not found")
    return updated_puskesmas

@router.delete("/{puskesmas_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_puskesmas(puskesmas_id: int, db: Session = Depends(get_db)):
    """Delete Puskesmas"""
    controller = PuskesmasController()
    success = await controller.delete_puskesmas(db, puskesmas_id)
    if not success:
        raise HTTPException(status_code=404, detail="Puskesmas not found")
    return None 