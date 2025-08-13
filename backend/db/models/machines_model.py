from sqlalchemy import Column, Integer, String, Text
from ..database import Base     #import declared Base from database file
from sqlalchemy.orm import relationship


class Machines(Base):
    __tablename__ = "machines"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)

    network_data_sources = relationship("NetworkDataSource", back_populates="machines", cascade="all, delete")
