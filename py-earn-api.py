import utils
from pycnic.core import WSGI, Handler

roi = utils.pull_roi()


class Return(Handler):
    def get(self, address):
        if address == '':
            return 'Please provide vault address'

        for r in roi:
            if r['address'] == address:
                return r


class app(WSGI):
    routes = [
        ('/', Return()),
        ("\/api\/roi\/([\\w]+)", Return())
    ]
