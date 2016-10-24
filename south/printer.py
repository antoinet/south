from bunch import bunchify

def printer(fid, fdata):
  fdata = bunchify(fdata)
  fdata.trail = None
  print "-------"
  print fid
  print fdata
