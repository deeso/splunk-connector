from src.rest_service.models import BaseSqla, BaseDocument, BaseEmbeddedDocument
from src.rest_service.resources import BaseResource
from sqlalchemy import Column
import sqlalchemy as sqa_fields
from umongo import fields as umo_fields, validate
from quart import Response, request
import json


class ResultsRsrc(BaseResource):
    PATTERNS = ['/results/id/<int:result_id>',
                '/results/<str:jobname>',
                '/results/'
                ]

    async def get(self, *args, **kwargs):
        '''
        Get Example view
        '''
        #TODO get the results user if it is valid
        raise Exception("Not implemenented")
        return Response(json.dumps({'result': 'results example works'}), status=300, mimetype='application/json')


    async def delete(self, *args, **kwargs):
        '''
        Get Example view
        '''
        # TODO delete the results user if it is valid
        raise Exception("Not implemenented")
        return Response(json.dumps({'result': 'results example works'}), status=300, mimetype='application/json')
