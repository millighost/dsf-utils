from collections import namedtuple

# tokenizer for pz3 files.
# due to some braindamaged syntax quirks, in particular:
# - file references may be given in different syntaxes some supporting
#   multi-line file names
# - some multi line statements can contain empty lines
# - some tokens (multi-line) must use left context to be unambiguous
# the tokenizer must examine every single letter, and is therefore
# extremely slow (500 K/s).
#

# general rules:
# 1 if a word starts with ':' it extends to the end of the line
# 2 if a word starts with '"' it extends to the next '"'
# 3 a comment starts with '//' and extends to the end of the line.
class word_splitter (object):
  """split a poser pz3 file into segments.
     each segment is of one of these types:
     - blank: only whitespace in this segment; not generated by get ()
     - comment: a comment starting with a '/'; not generated by get ()
     - string: a quoted string ("...."); may contain space
     - ref: a file reference starting with a colon
     - word: everything else; never contains spaces
     - eof: only at the end of the data.
  """
  def __init__ (self, ifh):
    self.buffer = ifh.read ()
    self.index = 0
    self.limit = len (self.buffer)
    self.line_number = 1
  def position (self):
    if len (self.buffer) == 0:
      return 1
    else:
      return self.index / len (self.buffer)
  def get_word (self):
    start = self.index
    while self.index != self.limit and not self.buffer[self.index].isspace ():
      self.index += 1
    end = self.index
    return (start, end)
  def get_string (self):
    start = self.index
    assert (self.buffer[self.index] == '"')
    self.index += 1
    while self.index != self.limit and self.buffer[self.index] != '"':
      self.index += 1
    if self.index < self.limit:
      self.index += 1
    end = self.index
    return (start, end)
  def get_eol (self):
    start = self.index
    while self.index != self.limit and self.buffer[self.index] != '\n':
      self.index += 1
    end = self.index
    return (start, end)
  def get_space (self):
    start = self.index
    while self.index != self.limit and self.buffer[self.index].isspace ():
      self.index += 1
    end = self.index
    return (start, end)
  def get_simple (self):
    if self.buffer[self.index].isspace ():
      (s, e) = self.get_space ()
      type = 'blank'
    elif self.buffer[self.index] == '"':
      (s, e) = self.get_string ()
      type = 'string'
    elif self.buffer[self.index] == ':':
      (s, e) = self.get_eol ()
      type = 'ref'
    elif self.buffer[self.index] == '/':
      (s, e) = self.get_eol ()
      type = 'comment'
    else:
      (s, e) = self.get_word ()
      type = 'word'
    return (type, self.buffer[s:e])
  ignore_types = set ({ 'comment', 'blank' })
  def get (self):
    """get the next token and count line number.
    """
    if self.index == self.limit:
      return ('eof', None)
    else:
      (type, data) = self.get_simple ()
      self.line_number += data.count ('\n')
      return (type, data)

class tokenizer (object):
  def __init__ (self, ifh):
    self.splitter = word_splitter (ifh)
    self.at_bol = True
    self.quote_count = 0
  def position (self):
    return self.splitter.position ()
  def quote_next (self, count):
    assert (self.quote_count == 0)
    self.quote_count = count
  def classify_word (self, word):
    if self.quote_count > 0:
      return 'word'
    elif word in ['{', '}']:
      return 'key'
    elif self.at_bol:
      if ':' in word:
        return 'word'
      else:
        return 'key'
    else:
      return 'word'
  def get_cooked (self):
    (ttype, tval) = self.splitter.get ()
    if ttype == 'word':
      cooked_type = self.classify_word (tval)
    else:
      cooked_type = ttype
    if ttype == 'blank':
      if  '\n' in tval:
        self.at_bol = True
      else:
        # bol-state is unchanged
        pass
    else:
      self.at_bol = False
    return (cooked_type, tval)
  ignore_types = set ({'blank', 'comment'})
  def get (self):
    (ttype, tval) = self.get_cooked ()
    while ttype in self.ignore_types:
      (ttype, tval) = self.get_cooked ()
    if self.quote_count > 0:
      self.quote_count -= 1
    return (ttype, tval)

class joiner (object):
  """main class to parse an input stream into statements.
  """
  def __init__ (self, ifh):
    self.tizer = tokenizer (ifh)
    self.look_ahead = None
  def position (self):
    return self.tizer.position ()
  # fix_args takes place of an actual grammar. Only required for
  # statements in the pz3 that have a fixed number of arguments, that
  # can also be keywords
  fix_args = {
    'valueOpDeltaAdd': 4,
    'addChild': 2,
  }
  def get_quoted (self):
    (ttyp, tval) = token = self.tizer.get ()
    if ttyp == 'key' and tval in self.fix_args:
      self.tizer.quote_next (self.fix_args[tval])
    return token
  def tokens (self):
    """iterates over a list of statements.
       a statement is a list, the first element is the keyword,
       remaining elements are arguments grouped to that keyword.
    """
    look_ahead = self.get_quoted ()
    while look_ahead[0] != 'eof':
      tlist = [look_ahead[1]]
      look_ahead = self.get_quoted ()
      while look_ahead[0] not in ['key', 'eof']:
        tlist.append (look_ahead[1])
        look_ahead = self.get_quoted ()
      yield tlist
    return

def main (argv):
  j = joiner (open (sys.argv[1], 'r'))
  pct = 0
  count = 0
  for t in j.tokens ():
    npct = int (j.position () * 100)
    if npct != pct:
      pct = npct
      print ("%02.0f %s" % (pct, t))
    count += 1
if __name__ == '__main__':
  import sys
  main (sys.argv)