from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from ..database import Base

class RelatedTags(Base):
    __tablename__ = "related_tags"

    id = Column(Integer, primary_key=True, index=True)
    main_tag_id = Column(Integer, ForeignKey("main_tags.id", ondelete="CASCADE"), nullable=False)
    tag_name = Column(String(100), nullable=False)
    tag_address = Column(String(255), nullable=False)
    type = Column(String(50), nullable=True)
    unit = Column(String(50), nullable=True)
    polls = Column(Float, nullable=False)

    main_tags = relationship("MainTags", back_populates="related_tags")