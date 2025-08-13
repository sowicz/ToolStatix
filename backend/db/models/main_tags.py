from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from ..database import Base
from .cleanup_tags import CleanupTags
from .related_tags import RelatedTags
from .network_data_source_model import NetworkDataSource



class MainTags(Base):
    __tablename__ = "main_tags"

    id = Column(Integer, primary_key=True, index=True)
    network_data_source_id = Column(Integer, ForeignKey("network_data_sources.id", ondelete="CASCADE"), nullable=False)
    tag_name = Column(String(100), nullable=False)
    tag_address = Column(String(255), nullable=False)
    type = Column(String(50), nullable=True)
    unit = Column(String(50), nullable=True)
    threshold = Column(Float, nullable=False)
    polls = Column(Float, nullable=False)

    network_data_sources = relationship("NetworkDataSource", back_populates="main_tags")
    related_tags = relationship("RelatedTags", back_populates="main_tags", cascade="all, delete")
    cleanup_tags = relationship("CleanupTags", uselist=False, back_populates="main_tags", cascade="all, delete")
    tags_data = relationship("TagsData", back_populates="main_tags", cascade="all, delete")

