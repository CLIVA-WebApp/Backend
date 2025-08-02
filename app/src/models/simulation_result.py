from sqlalchemy import Column, String, Float, Integer, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import json

from app.src.config.database import Base

class SimulationResult(Base):
    """Model for storing simulation results for chatbot context"""
    __tablename__ = "simulation_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    regency_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    regency_name = Column(String, nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)  # Add user_id field
    budget = Column(Float, nullable=False)
    facilities_recommended = Column(Integer, nullable=False)
    total_population_covered = Column(Integer, nullable=False)
    coverage_percentage = Column(Float, nullable=False)
    automated_reasoning = Column(Text, nullable=True)  # Add automated reasoning field
    simulation_data = Column(Text, nullable=False)  # JSON string of full simulation data
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "id": str(self.id),
            "regency_id": str(self.regency_id),
            "regency_name": self.regency_name,
            "user_id": str(self.user_id),  # Include user_id
            "budget": self.budget,
            "facilities_recommended": self.facilities_recommended,
            "total_population_covered": self.total_population_covered,
            "coverage_percentage": self.coverage_percentage,
            "automated_reasoning": self.automated_reasoning,  # Include automated reasoning
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

    @classmethod
    def from_simulation_result(cls, simulation_data: dict, regency_id: str, regency_name: str, user_id: str) -> 'SimulationResult':
        """Create from simulation result data"""
        return cls(
            regency_id=regency_id,
            regency_name=regency_name,
            user_id=user_id,  # Add user_id
            budget=simulation_data.get('budget', 0),
            facilities_recommended=len(simulation_data.get('recommendations', [])),
            total_population_covered=0,  # Would need to calculate this
            coverage_percentage=simulation_data.get('simulation_summary', {}).get('projected_coverage', 0),
            automated_reasoning=simulation_data.get('automated_reasoning', ''),  # Add automated reasoning
            simulation_data=simulation_data
        ) 