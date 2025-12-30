from sqlalchemy.orm import Session
from sqlalchemy import and_
from db.models import machines_model
from db.models import network_data_source_model
from db.models import main_tags
from db.models import related_tags


class Validator:
    def __init__(self, db: Session):
        self.db = db

    def check_if_exists(self, model, field, value):
        record = self.db.query(model).filter(field == value).first()
        if not record:
            raise ValueError(f"{model.__name__} with {field.key}={value} does not exist.")

    def check_if_unique(self, model, field, value):
        exists = self.db.query(model).filter(field == value).first()
        if exists:
            raise ValueError(f"{model.__name__} with {field.key}='{value}' already exists.")

    def check_fields_thesame(self, model, field, value):
        exists = self.db.query(model).filter(field == value).first()
        if exists:
            raise ValueError(f"{model.__name__} with {field.key}='{value}' already exists.")
        


class DataSourceValidator(Validator):
    def validate(self, data: network_data_source_model.NetworkDataSource):
        #check if id machine exist 
        self.check_if_exists(machines_model.Machines, machines_model.Machines.id, data.machine_id)

        exists = self.db.query(network_data_source_model.NetworkDataSource).filter(
            and_(
                network_data_source_model.NetworkDataSource.machine_id == data.machine_id,
                network_data_source_model.NetworkDataSource.protocol == data.protocol,
                network_data_source_model.NetworkDataSource.server_url == data.server_url,
                network_data_source_model.NetworkDataSource.port == data.port,
            )
        ).first()

        if exists:
            raise ValueError(
                f"A data source for this machine with the same protocol/server/port already exists."
            )
        

# CHANGE
# can be more tag for the same data source
#
class MachineTagValidator(Validator):
    def validate(self, data: main_tags.MainTags):
        self.check_if_exists(
            network_data_source_model.NetworkDataSource, 
            network_data_source_model.NetworkDataSource.id, 
            data.network_data_source_id
            )
        exists = self.db.query(main_tags.MainTags).filter(
            and_(
                # main_tags.MainTags.network_data_source_id == data.network_data_source_id,
                main_tags.MainTags.tag_address == data.tag_address,

            )
        ).first()

        if exists:
            raise ValueError(
                f"This tag_address already exists."
        )



class RelatedTagValidator(Validator):
    def validate(self, data: related_tags.RelatedTags):
        self.check_if_exists(
            main_tags.MainTags, 
            main_tags.MainTags.id, 
            data.main_tag_id
            )
        exists = self.db.query(related_tags.RelatedTags).filter(
            and_(
                related_tags.RelatedTags.main_tag_id == data.main_tag_id,
                related_tags.RelatedTags.tag_address == data.tag_address,
            )
        ).first()

        if exists:
            raise ValueError(
                f"A data source for this machine with the same data_source and tag_address already exists."
        )
