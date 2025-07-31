from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List
from app.src.models.health_facility import HealthFacility, HealthFacilityType
from app.src.schemas.puskesmas_schema import HealthFacilityCreate, HealthFacilityUpdate, HealthFacilityResponse
from uuid import UUID

class HealthFacilityController:
    def __init__(self):
        pass
    
    async def create_health_facility(self, facility: HealthFacilityCreate, db: Session) -> HealthFacility:
        """Create a new health facility"""
        try:
            # Convert to WKT point geometry
            geom_wkt = f"POINT({facility.longitude} {facility.latitude})"
            
            db_facility = HealthFacility(
                name=facility.name,
                type=facility.type,
                subdistrict_id=facility.subdistrict_id,
                geom=geom_wkt
            )
            db.add(db_facility)
            db.commit()
            db.refresh(db_facility)
            return db_facility
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create health facility: {str(e)}"
            )
    
    async def get_health_facility(self, facility_id: UUID, db: Session) -> HealthFacility:
        """Get a specific health facility by ID"""
        try:
            facility = db.query(HealthFacility).filter(HealthFacility.id == facility_id).first()
            if not facility:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Health facility not found"
                )
            return facility
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get health facility: {str(e)}"
            )
    
    async def update_health_facility(self, facility_id: UUID, facility: HealthFacilityUpdate, db: Session) -> HealthFacility:
        """Update a health facility"""
        try:
            db_facility = db.query(HealthFacility).filter(HealthFacility.id == facility_id).first()
            if not db_facility:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Health facility not found"
                )
            
            # Update fields
            update_data = facility.dict(exclude_unset=True)
            
            # Handle geometry update if coordinates changed
            if 'latitude' in update_data or 'longitude' in update_data:
                lat = update_data.get('latitude', db_facility.latitude)
                lng = update_data.get('longitude', db_facility.longitude)
                update_data['geom'] = f"POINT({lng} {lat})"
                # Remove individual coordinate fields as they're not in the model
                update_data.pop('latitude', None)
                update_data.pop('longitude', None)
            
            for key, value in update_data.items():
                setattr(db_facility, key, value)
            
            db.commit()
            db.refresh(db_facility)
            return db_facility
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update health facility: {str(e)}"
            )
    
    async def delete_health_facility(self, facility_id: UUID, db: Session) -> dict:
        """Delete a health facility"""
        try:
            db_facility = db.query(HealthFacility).filter(HealthFacility.id == facility_id).first()
            if not db_facility:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Health facility not found"
                )
            
            db.delete(db_facility)
            db.commit()
            return {"message": "Health facility deleted successfully"}
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete health facility: {str(e)}"
            )
    
    async def get_health_facilities_by_type(self, facility_type: HealthFacilityType, db: Session) -> List[HealthFacility]:
        """Get all health facilities of a specific type"""
        try:
            facilities = db.query(HealthFacility).filter(HealthFacility.type == facility_type).all()
            return facilities
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get health facilities: {str(e)}"
            )
    
    async def get_health_facilities_by_subdistrict(self, subdistrict_id: UUID, db: Session) -> List[HealthFacility]:
        """Get all health facilities in a specific sub-district"""
        try:
            facilities = db.query(HealthFacility).filter(HealthFacility.subdistrict_id == subdistrict_id).all()
            return facilities
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get health facilities: {str(e)}"
            )

# Legacy PuskesmasController for backward compatibility
class PuskesmasController:
    def __init__(self):
        self.health_facility_controller = HealthFacilityController()
    
    async def create_puskesmas(self, puskesmas, db: Session):
        """Create a new puskesmas (legacy method)"""
        # Convert legacy puskesmas data to health facility format
        facility_data = HealthFacilityCreate(
            name=puskesmas.nama,
            type=HealthFacilityType.PUSKESMAS,
            latitude=puskesmas.latitude,
            longitude=puskesmas.longitude
        )
        return await self.health_facility_controller.create_health_facility(facility_data, db)
    
    async def get_puskesmas(self, puskesmas_id: UUID, db: Session):
        """Get a specific puskesmas by ID (legacy method)"""
        return await self.health_facility_controller.get_health_facility(puskesmas_id, db)
    
    async def update_puskesmas(self, puskesmas_id: UUID, puskesmas, db: Session):
        """Update a puskesmas (legacy method)"""
        # Convert legacy puskesmas data to health facility format
        facility_data = HealthFacilityUpdate(
            name=puskesmas.nama if hasattr(puskesmas, 'nama') else None,
            latitude=puskesmas.latitude if hasattr(puskesmas, 'latitude') else None,
            longitude=puskesmas.longitude if hasattr(puskesmas, 'longitude') else None
        )
        return await self.health_facility_controller.update_health_facility(puskesmas_id, facility_data, db)
    
    async def delete_puskesmas(self, puskesmas_id: UUID, db: Session):
        """Delete a puskesmas (legacy method)"""
        return await self.health_facility_controller.delete_health_facility(puskesmas_id, db) 