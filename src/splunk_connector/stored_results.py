import uuid
from hashlib import sha3_256
from Crypto.Cipher import AES
from .config import *
import random
import string
import struct
from .results import SplunkResult

RANDOM_KEY = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(40))

class StoredSplunkResult(object):
    DATA_KEY = None
    DEFAULT_RESULTS = {
        SPLUNK_QUERY_SENSITIVE: lambda: False,
        STORED_RESULT_ID: lambda : None,
        HAS_RESULTS: lambda: False,
        SPLUNK_QUERY_RUNNING: lambda: False,
        CIPHER: lambda: None,
        DATA: lambda: None,
        DATA_HASH: lambda: None,
        SPLUNK_QUERY_NAME: lambda: None,
        EARLIEST: lambda: None,
        LATEST: lambda: None,
        FILENAME: lambda: None,
        JOB_ID: lambda: None,
        SPLUNK_QUERY: lambda: None,
        ERROR: lambda: False
    }

    RESULTS_DATA = [
        CIPHER,
        DATA,
        DATA_HASH,
    ]

    def __init__(self, salt=None, **kwargs):
        self.salt = salt
        self.init_keys = set()
        self.salt = salt

        if STORED_RESULT_ID in kwargs and \
            kwargs[STORED_RESULT_ID] is None:
            del kwargs[STORED_RESULT_ID]

        if ID in kwargs and \
                kwargs[ID] is not None and \
            STORED_RESULT_ID not in kwargs:
            kwargs[STORED_RESULT_ID] = str(kwargs.get(ID))

        elif STORED_RESULT_ID not in kwargs:
            kwargs[STORED_RESULT_ID] = str(uuid.uuid4())

        if self.salt is None:
            self.salt = kwargs.get(JOB_ID, None)

        for k, v in kwargs.items():
            if k in self.DEFAULT_RESULTS:
                setattr(self, k, v)

        for k, fn in self.DEFAULT_RESULTS.items():
            if not hasattr(self, k):
                setattr(self, k, fn())

        data = self.get_data()
        if data is not None and isinstance(data, str):
            self.set_data(data.encode('utf-8'))

    def has_plain_text(self):
        return self.get_data() is not None

    @classmethod
    def disable_encryption(cls):
        cls.DATA_KEY = None

    @classmethod
    def default_results(cls, salt=None):
       return cls(salt=salt, **cls.default_results_dict())

    @classmethod
    def default_results_dict(cls):
        return {k:v() for k, v in cls.DEFAULT_RESULTS.items()}

    @classmethod
    def get_data_key(cls):
        return cls.DATA_KEY

    @classmethod
    def set_data_key(cls, key=None, use_random=False):
        if use_random:
            key = RANDOM_KEY
        cls.DATA_KEY = key

    @classmethod
    def encrypt(cls, salt, data):
        if cls.DATA_KEY is None:
            return data, cls.do_data_hash_hex(data)
        km = cls.a2b(salt)+cls.a2b(cls.DATA_KEY)
        key = cls.do_data_hash(km)
        sz = struct.pack('<Q', len(data))
        raw = cls.a2b_pad(data)
        cipher = AES.new(key, AES.MODE_ECB).encrypt(cls.a2b(raw))
        return sz+cipher, cls.do_data_hash_hex(data)

    @classmethod
    def a2b(cls, data) -> bytes:
        _data = data if isinstance(data, bytes) else \
            data.encode('utf8') if isinstance(data, str) else b''
        return _data

    @classmethod
    def pad(cls, data: bytes, bs=16) -> bytes:
        return data + bytes(bs - len(data) % bs)

    @classmethod
    def a2b_pad(cls, data) -> bytes:
        _data = data if isinstance(data, bytes) else \
            data.encode('utf8') if isinstance(data, str) else b''
        return cls.pad(_data)

    @classmethod
    def do_data_hash_hex(cls, data):
        return sha3_256(cls.a2b(data)).hexdigest()

    @classmethod
    def do_data_hash(cls, data):
        return sha3_256(cls.a2b(data)).digest()

    @classmethod
    def decrypt(cls, salt, cipher, data_hash=None):
        if cls.DATA_KEY is None:
            return cipher, cls.do_data_hash_hex(cipher)
        km = cls.a2b(salt)+cls.a2b(cls.DATA_KEY)
        key = cls.do_data_hash(km)
        sz = struct.unpack('<Q', cipher[:8])[0]
        raw = AES.new(key, AES.MODE_ECB).decrypt(cls.a2b(cipher[8:]))
        clear = raw[:sz]
        if data_hash is None:
            return clear, cls.do_data_hash_hex(clear)
        if cls.do_data_hash_hex(clear) != data_hash:
            return None, None
        return clear, data_hash

    def get_id(self):
        return getattr(self, STORED_RESULT_ID, None)

    def set_id(self, stored_result_id):
        setattr(self, STORED_RESULT_ID, stored_result_id)

    def from_json(self, jd):
        for k, v in jd.items():
            if k in self.RESULTS_DATA:
                setattr(self, k, v)

    def to_json(self):
        return {k: getattr(self, k) for k in self.RESULTS_DATA}

    def get_has_results(self):
        return getattr(self, HAS_RESULTS, None)

    def get_splunk_query_running(self):
        return getattr(self, SPLUNK_QUERY_RUNNING, None)

    def get_cipher(self):
        return getattr(self, CIPHER, None)

    def get_data(self):
        return getattr(self, DATA, None)

    def get_data_hash(self):
        return getattr(self, DATA_HASH, None)

    def get_splunk_query_name(self):
        return getattr(self, SPLUNK_QUERY_NAME, None)

    def get_splunk_query(self):
        return getattr(self, SPLUNK_QUERY, None)

    def get_earliest(self):
        return getattr(self, EARLIEST, None)

    def get_latest(self):
        return getattr(self, LATEST, None)

    def get_filename(self):
        return getattr(self, FILENAME)

    def set_has_results(self, value=None):
        return setattr(self, HAS_RESULTS, value)

    def set_splunk_query_running(self, value=None):
        return setattr(self, SPLUNK_QUERY_RUNNING, value)

    def set_cipher(self, value=None):
        return setattr(self, CIPHER, value)

    def set_data(self, value=None):
        return setattr(self, DATA, value)

    def set_data_hash(self, value=None):
        return setattr(self, DATA_HASH, value)

    def set_splunk_query_name(self, value=None):
        return setattr(self, SPLUNK_QUERY_NAME, value)

    def set_earliest(self, value=None):
        return setattr(self, EARLIEST, value)

    def set_latest(self, value=None):
        return setattr(self, LATEST, value)

    def set_filename(self, value=None):
        return setattr(self, FILENAME, value)

    def get_job_id(self):
        return getattr(self, JOB_ID, None)

    def get_sensitive(self):
        return getattr(self, SPLUNK_QUERY_SENSITIVE)

    def check_result_entry_data_valid(self, salt):
        cipher = self.get_cipher()
        data_hash = self.get_data_hash()
        data = self.get_data()

        if cipher is None and data is None and data_hash is None:
            return False

        if data is not None and data_hash is None:
            return True
        elif data is not None and self.do_data_hash_hex(data) == data_hash:
            return True
        elif cipher is not None and data_hash is not None:
            data, ndh = self.decrypt(salt, cipher, data_hash)
            if data is None:
                return False
            return True
        return False

    def decrypt_data(self, in_place=False):
        data = self.get_data()
        cipher = self.get_cipher()
        data_hash = self.get_data_hash()

        if cipher is not None:
            data, data_hash = self.decrypt(self.salt, cipher, data_hash=data_hash)

        if in_place:
            self.set_cipher(None)
            self.set_data(data)
            self.set_data_hash(data_hash)
        return {DATA: data, DATA_HASH: data_hash, CIPHER: None}

    def encrypt_data(self, in_place=False):
        data = self.get_data()
        cipher = self.get_cipher()
        data_hash = self.get_data_hash()

        if data is not None:
            cipher, data_hash = self.encrypt(self.salt, data)
        if in_place:
            self.set_data(None)
            self.set_cipher(cipher)
            self.set_data_hash(data_hash)
        return {DATA: None, DATA_HASH: data_hash, CIPHER: cipher}

    def verify(self):
        if self.check_result_entry_data_valid(self.salt):
            return False
        return True

    def reset(self):
        for k, fn in self.DEFAULT_RESULTS.items():
            setattr(self, k, fn())

    def reset_invalid(self):
        reset = False
        if self.salt is None or not self.verify():
            self.reset()
            reset = True
        return reset

    def serialize(self):
        r = {k: getattr(self, k, None) for k in self.DEFAULT_RESULTS}
        if r[STORED_RESULT_ID] is not None:
            r[ID] = r[STORED_RESULT_ID]
        return r

    def serialize_store(self):
        results = self.serialize()
        results.update(self.encrypt_data())
        return results

    @classmethod
    def from_splunk_result(cls, splunk_results: SplunkResult, job_id=None, salt=None):
        data = splunk_results.get_data()
        kargs = {
            HAS_RESULTS: False if data is None else True,
            SPLUNK_QUERY_RUNNING: False,
            CIPHER: None,
            DATA: splunk_results.get_data(),
            DATA_HASH: cls.do_data_hash_hex(data),
            SPLUNK_QUERY_NAME: splunk_results.get_name(),
            EARLIEST: splunk_results.get_earliest(),
            LATEST: splunk_results.get_latest(),
            FILENAME: splunk_results.get_filename(),
            JOB_ID: job_id,
            SPLUNK_QUERY: splunk_results.get_query(),
            SPLUNK_QUERY_SENSITIVE: splunk_results.get_sensitive(),
            ERROR: False
        }
        return cls(salt=salt, **kargs)

    @classmethod
    def from_error(cls, earliest, latest, query_name, error, job_id=None, salt=None, sensitive=False):
        data = error
        kargs = {
            HAS_RESULTS: False if data is None else True,
            SPLUNK_QUERY_RUNNING: False,
            CIPHER: None,
            DATA: error,
            DATA_HASH: cls.do_data_hash_hex(data),
            SPLUNK_QUERY_NAME: query_name,
            EARLIEST: earliest,
            LATEST: latest,
            FILENAME: None,
            JOB_ID: job_id,
            SPLUNK_QUERY: None,
            SPLUNK_QUERY_SENSITIVE: sensitive,
            ERROR: True
        }
        return cls(salt=salt, **kargs)

    @classmethod
    def mongo_load(cls, mongo_service, oid=None):
        conn, db = mongo_service.get_conn_database()
        collection_name = mongo_service.get_query_results_collection()
        if oid is None:
            return None
        res = db[collection_name].find_one({'_id': oid})
        if res is None:
            return res
        conn.close()
        r = cls(**res)
        d = r.decrypt_data()
        if len(d['data']) > 0:
            r.decrypt_data(in_place=True)
        return r

    @classmethod
    def mongo_load_all(cls, mongo_service, job_id=None):
        query = {}
        conn, db = mongo_service.get_conn_database()
        collection_name = mongo_service.get_query_results_collection()
        if job_id is not None:
            query[JOB_ID] = job_id
        cur = db[collection_name].find(query)
        if cur is None:
            return None
        items = []
        for res in cur:
            r = cls(**res)
            d = r.decrypt_data()
            if len(d['data']) > 0:
                r.decrypt_data(in_place=True)
            items.append(r)
        conn.close()
        return items

    def mongo_insert(self, mongo_service):
        conn, db = mongo_service.get_conn_database()
        collection_name = mongo_service.get_query_results_collection()
        inserted_item = db[collection_name].insert_one(self.serialize_store())
        conn.close()
        return inserted_item

    def mongo_delete(self, mongo_service):
        conn, db = mongo_service.get_conn_database()
        collection_name = mongo_service.get_query_results_collection()
        r = db[collection_name].delete_one({'_id': self.get_id()})
        conn.close()
        return r

    def get_meta_data(self):
        return getattr(self, SPLUNK_QUERY_METADATA, {})

    def set_meta_data(self, meta_data):
        return setattr(self, SPLUNK_QUERY_METADATA, meta_data)

    def is_error(self):
        return getattr(self, ERROR, False)



class StoredSplunkResults(object):

    def __init__(self, name, results=[], salt=None):
        self.salt = salt
        self.stored_results = {}
        self.name = name
        for result in results:
            if isinstance(result, SplunkResult):
                self.add_splunk_result(result)
            elif isinstance(result, StoredSplunkResult):
                self.add_stored_result(result)

    def add_stored_result(self, stored_splunk_result: StoredSplunkResult):
        earliest = stored_splunk_result.get_earliest()
        self.stored_results[earliest] = stored_splunk_result

    def add_stored_result_json(self, json_result):
        result = StoredSplunkResult(salt=self.salt, **json_result)
        self.add_stored_result(result)

    def add_splunk_result(self, result: SplunkResult, salt=None):
        ssr = StoredSplunkResult.from_splunk_result(result, salt=self.salt)
        self.add_stored_result(ssr)

    def add_splunk_result_json(self, json_result):
        result = SplunkResult(**json_result)
        self.add_splunk_result(result)

    def get_results(self):
        return list(self.results.values())

    def serialize(self):
        keys = sorted(self.stored_results.keys())
        return [self.stored_results[k].serialize() for k in keys]

    def serialize_store(self):
        keys = sorted(self.stored_results.keys())
        return [self.stored_results[k].serialize_store() for k in keys]