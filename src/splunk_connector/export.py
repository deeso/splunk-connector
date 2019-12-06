from threading import Thread
import json

class BackgroundReaderObject(Thread):
    def __init__(self, **kargs):
        self.response = None
        self.data = None
        self.service = None
        self.query = None
        self.key = 'result'

        self.keep_reading = False
        self.data = b''
        self.sz = 0
        self.json_lines = []
        self.complete = False

        super(BackgroundReaderObject, self).__init__()
        for k, v in kargs.items():
            setattr(self, k, v)


    def add_data(self, data):
        self.data = self.data + data
        self.sz += len(data)

    def add_json_line(self, line, key=None):
        self.sz += len(line)
        jd = json.loads(line)
        if key in jd:
            self.json_lines.append(jd[key])
        else:
            self.json_lines.append(jd)

    def is_complete(self):
        return self.complete

    def run(self):
        self.keep_reading = True
        while not self.response.empty and self.response.readable:
            data = self.response.readline()
            self.add_json_line(data, key=self.key)
            if not self.keep_reading:
                break
        self.complete = self.response.empty and not self.response.readable

        if self.is_complete():
            self.cleanup()

    def cleanup(self):
        if self.service is not None:
            self.service.logout()

        if self.response is not None:
            try:
                self.response.close()
            except:
                pass
            self.response = None
