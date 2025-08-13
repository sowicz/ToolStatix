from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship
from ..database import Base

class NetworkDataSource(Base):
    __tablename__ = "network_data_sources"

    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(Integer, ForeignKey("machines.id", ondelete="CASCADE"), nullable=False)
    protocol = Column(String(50), nullable=False)
    server_url = Column(String(255), nullable=False)
    port = Column(Integer, nullable=False)
    extra_config = Column(JSON, nullable=True)

    machines = relationship("Machines", back_populates="network_data_sources")
    main_tags = relationship("MainTags", back_populates="network_data_sources", cascade="all, delete")