from quart import Quart, jsonify, Response
from quart.views import MethodView
from quart import request
import json

class BasePage(MethodView):
    PATTERNS = ['/', ]
    NAME = 'basepage'
    CLASS_NAME = 'BasePage'

    @property
    def handler(cls):
        return cls.HANDLER

    @property
    def name(cls):
        return cls.NAME

    @classmethod
    def update_app(cls, app):
        for pattern in cls.PATTERNS:
            app.add_url_rule(pattern,
                             view_func=cls.as_view(cls.NAME))

    @classmethod
    def urls(cls):
        r = []
        for i in cls.PATTERNS:
            r.append(i)
            r.append(cls.CLASS_NAME)
        return r

    @classmethod
    def set_handler(cls, handler):
        cls.HANDLER = handler

    def handle_request(self, data):
        r = None
        rcode = 404
        if self.HANDLER is None:
            r = {'error': 'service handler not set'}
        else:
            r, rcode = self.handler(self.NAME, data)

        return Response(json.dumps(r), status=rcode, mimetype='application/json')


    async def get(self):
        data = request.get_json()
        return self.handle_request(data)

    async def post(self):
        data = request.get_json()
        return self.handle_request(data)
