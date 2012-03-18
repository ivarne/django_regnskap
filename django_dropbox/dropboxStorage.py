from django.core.files.storage import Storage
from dropbox.rest import ErrorResponse
from datetime import datetime

class DropboxStorage(Storage):
    """
    Standard filesystem storage
    """

    def __init__(self, client):
        self.client = client
        self.metaCache = {}

    def _open(self, name, mode='rb'):
        (f, meta) = self.client.get_file(name)
        self.metaCache[name] = meta
        return f

    def _save(self, name, content):
        meta = self.client.put_file(name,content)
        self.metaCache[meta['path']] = meta
        return name

    def delete(self, name):
        try:
            self.client.file_delete(name)
        except ErrorResponse, e:
            if e.status != 404:
                raise e

    def exists(self, name):
        if self.metaCache.has_key(name):
            return True
        try:
            self.metaCache[name] = self.client.metadata(name, False)
            return True
        except ErrorResponse, e:
            if e.status != 404:
                raise e
            return False

    def listdir(self, path):
        directories, files = [], []
        self.meataCache[path] = self.client.metadata(path)
        for entry in self.meataCache[path]["contents"]:
            self.metaCache[entry["path"]] = entry
            if entry["is_dir"]:
                directories.append(entry["path"])
            else:
                files.append(entry["path"])
        return directories, files


    def size(self, name):
        if not name in self.metaCache:
            self.meataCache[name] = client.metadata(name, False)
        return self.metaCache[mane]["bytes"]

    def url(self, name):
        tmp = self.client.share(name)
        return tmp['url']

    def accessed_time(self, name):
        raise NotImplementedError()

    def created_time(self, name):
        raise NotImplementedError()

    def modified_time(self, name):
        if not name in self.metaCache:
            self.meataCache[name] = client.metadata(name, False)
        return datetime.strptime(self.metaCache[name]["modified"],"%a, %d %b %Y %H:%M:%S +0000")