import json, gzip, codecs

def open_text_file (filename, encoding = 'latin1'):
  """open a binary file and return a readable handle.
     check for compressed files and open with decompression.
  """
  first_bytes = open (filename, 'rb').read (2)
  if first_bytes == b'\x1f\x8b':
    # looks like a gzipped file.
    ifh = gzip.open (filename, 'rb')
  else:
    ifh = open (filename, 'rb')
  return codecs.getreader (encoding) (ifh)

def read_json_data (filename, **kwarg):
  """open the (possibly compressed) file and return its json data.
     the only supported kw-arg at the moment is 'encoding'
  """
  return json.load (open_text_file (filename, **kwarg))
