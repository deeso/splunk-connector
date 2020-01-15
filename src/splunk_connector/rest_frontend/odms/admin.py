from ..models import BaseSqla, BaseDocument, BaseEmbeddedDocument
from ..resources import BaseResource
from sqlalchemy import Column
import sqlalchemy as sqa_fields
from umongo import fields as umo_fields, validate
from quart import Response, request
import json

class PostgresAdmin(BaseSqla):
    uid = Column(sqa_fields.String(64), primary_key=True)
    username = Column(sqa_fields.String(4096), nullable=False)
    email = Column(sqa_fields.String(4096), nullable=False, unique=True)
