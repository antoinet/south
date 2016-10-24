from couchdbkit import Server


class Coucher:

  def __init__(self, uri='http://127.0.0.1:5984'):
    self.server = Server(uri=uri)
    self.db = self.server.get_or_create_db("south")

  def handle(self, fid, fdata):
    self.db[fid] = fdata


