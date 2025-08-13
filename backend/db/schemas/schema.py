from pydantic import BaseModel
from typing import Optional, Literal


# ---=== Machine data scheme ===---

class MachinesBase(BaseModel):
    name: str
    description: Optional[str] = None

class MachinesCreate(MachinesBase):
    pass

class MachinesRead(MachinesBase):
    id: int

    class Config:
        orm_mode = True



# ---=== Network Data source scheme ===---

class NetworkDataSourceBase(BaseModel):
    machine_id: int
    protocol: Literal["modbus-tcp", "opc-ua"]
    server_url: str
    port: int
    extra_config: Optional[str]

class NetworkDataSourceCreate(NetworkDataSourceBase):
    pass

class NetworkDataSourceRead(NetworkDataSourceBase):
    id: int

    class Config:
        orm_mode = True



# ---=== Main Tags Table scheme ===---

class MainTagsBase(BaseModel):
    network_data_source_id: int
    tag_name: str
    tag_address: str
    type: Optional[str] = None
    unit: Optional[str] = None
    threshold: float
    polls: float


class MainTagsCreate(MainTagsBase):
    pass

class MainTagsRead(MainTagsBase):
    id: int

    class Config:
        orm_mode = True



# ---=== Related tags scheme ===---

class RelatedTagsBase(BaseModel):
    main_tag_id: int
    tag_name: str
    tag_address: str
    type: Optional[str] = None
    unit: Optional[str] = None
    polls: float

class RelatedTagsCreate(RelatedTagsBase):
    pass

class RelatedTagsRead(RelatedTagsBase):
    id: int

    class Config:
        orm_mode = True



# ---=== Tags data schema ===---

class TagsDataBase(BaseModel):
    main_tag_id: int
    tag_name: str
    min: Optional[float]
    max: Optional[float]
    avg: Optional[float]
    work_time: int

class TagsDataCreate(TagsDataBase):
    pass

class TagsDataResponse(TagsDataBase):
    id: int

    class Config:
        orm_mode = True



# ---=== Report Schema ===---

class TagStatsResponse(BaseModel):
    tag_name: str
    min: float | None
    max: float | None
    avg: float | None
    work_time: int | None

    class Config:
        orm_mode = True
