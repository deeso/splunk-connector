from src.rest_service.models import BaseSqla, BaseDocument, BaseEmbeddedDocument
from src.rest_service.resources import BaseResource
from sqlalchemy import Column
import sqlalchemy as sqa_fields
from umongo import fields as umo_fields, validate
from quart import Response, request
import json


class QueryRsrc(BaseResource):
    PATTERNS = ['/query/id/<int:query_id>',
                '/query/<str:queryname>',
                '/query/'
                ]

    async def get(self, *args, **kwargs):
        '''
        Get Example view
        '''
        #TODO get the server user if it is valid
        raise Exception("Not implemenented")
        return Response(json.dumps({'result': 'server example works'}), status=300, mimetype='application/json')


    async def post(self, *args, **kwargs):
        '''
        Get Example view
        '''
        # TODO create the server user if it is valid
        raise Exception("Not implemenented")
        return Response(json.dumps({'result': 'server example works'}), status=300, mimetype='application/json')

    async def put(self, *args, **kwargs):
        '''
        Get Example view
        '''
        # TODO update the server user if it is valid
        raise Exception("Not implemenented")
        return Response(json.dumps({'result': 'server example works'}), status=300, mimetype='application/json')

    async def delete(self, *args, **kwargs):
        '''
        Get Example view
        '''
        # TODO delete the server user if it is valid
        raise Exception("Not implemenented")
        return Response(json.dumps({'result': 'server example works'}), status=300, mimetype='application/json')


class ExecuteQueryRsrc(BaseResource):
    PATTERNS = ['/execute/query/<int:query_id>',
                '/execute/query/<str:queryname>',
                ]

    async def post(self, *args, **kwargs):
        '''
        Get Example view
        '''
        # TODO create the server user if it is valid
        raise Exception("Not implemenented")
        return Response(json.dumps({'result': 'server example works'}), status=300, mimetype='application/json')


class CreateQueryRsrc(BaseResource):
    PATTERNS = ['/execute/query/<int:query_id>',
                '/execute/query/<str:queryname>',
                ]

    async def post(self, *args, **kwargs):
        '''
        Get Example view
        '''
        # TODO create the server user if it is valid
        raise Exception("Not implemenented")
        return Response(json.dumps({'result': 'server example works'}), status=300, mimetype='application/json')
