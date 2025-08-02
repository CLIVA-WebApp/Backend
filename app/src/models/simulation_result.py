from sqlalchemy import Column, String, Float, Integer, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import json

from app.src.config.database import Base

class SimulationResult(Base):
    __tablename__ = "simulation_results"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    regency_id = Column(UUID(as_uuid=True), nullable=False)
    regency_name = Column(String(255), nullable=False)
    budget = Column(Float, nullable=False)
    facilities_recommended = Column(Integer, nullable=False)
    total_population_covered = Column(Integer, nullable=False)
    coverage_percentage = Column(Float, nullable=False)
    simulation_data = Column(Text, nullable=True)  # JSON string of full simulation data
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": str(self.id),
            "regency_id": str(self.regency_id),
            "regency_name": self.regency_name,
            "budget": self.budget,
            "facilities_recommended": self.facilities_recommended,
            "total_population_covered": self.total_population_covered,
            "coverage_percentage": self.coverage_percentage,
            "simulation_data": json.loads(self.simulation_data) if self.simulation_data else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_simulation_result(cls, simulation_result_dict, regency_id, regency_name):
        """Create a SimulationResult from a simulation result dictionary"""
        return cls(
            regency_id=regency_id,
            regency_name=regency_name,
            budget=simulation_result_dict.get("budget_used", 0),
            facilities_recommended=simulation_result_dict.get("facilities_recommended", 0),
            total_population_covered=simulation_result_dict.get("total_population_covered", 0),
            coverage_percentage=simulation_result_dict.get("coverage_percentage", 0),
            simulation_data=json.dumps(simulation_result_dict)
        ) 