from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.src.config.database import get_db
from app.src.schemas.puskesmas_schema import PuskesmasCreate, PuskesmasUpdate, PuskesmasResponse
from app.src.controllers.puskesmas_controller import PuskesmasController

router = APIRouter(prefix="/puskesmas", tags=["Puskesmas"])

@router.post("/", response_model=PuskesmasResponse)
async def create_puskesmas(
    puskesmas: PuskesmasCreate,
    db: Session = Depends(get_db)
):
    """Create a new puskesmas"""
    controller = PuskesmasController()
    return await controller.create_puskesmas(puskesmas, db)

@router.get("/{puskesmas_id}", response_model=PuskesmasResponse)
async def get_puskesmas(
    puskesmas_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific puskesmas by ID"""
    controller = PuskesmasController()
    return await controller.get_puskesmas(puskesmas_id, db)

@router.put("/{puskesmas_id}", response_model=PuskesmasResponse)
async def update_puskesmas(
    puskesmas_id: int,
    puskesmas: PuskesmasUpdate,
    db: Session = Depends(get_db)
):
    """Update a puskesmas"""
    controller = PuskesmasController()
    return await controller.update_puskesmas(puskesmas_id, puskesmas, db)

@router.delete("/{puskesmas_id}")
async def delete_puskesmas(
    puskesmas_id: int,
    db: Session = Depends(get_db)
):
    """Delete a puskesmas"""
    controller = PuskesmasController()
    return await controller.delete_puskesmas(puskesmas_id, db) 