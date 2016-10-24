from couchdbkit import Server


class Coucher:

  def __init__(self):
    self.server = Server()
    self.db = self.server.get_or_create_db("south")

  def handle(self, fid, fdata):
    self.db[fid] = fdata


