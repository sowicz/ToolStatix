from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base
from datetime import datetime

class TagsData(Base):
    __tablename__ = "tags_data"

    id = Column(Integer, primary_key=True, index=True)
    main_tag_id = Column(Integer, ForeignKey("main_tags.id", ondelete="CASCADE"), nullable=False)
    tag_name = Column(String(255), nullable=False)
    min = Column(Float, nullable=True)
    max = Column(Float, nullable=True)
    avg = Column(Float, nullable=True)
    work_time = Column(Integer)

    main_tags = relationship("MainTags", back_populates="tags_data")
