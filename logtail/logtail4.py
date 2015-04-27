#!/usr/bin/python2

import cgi, os, re, sys, tempfile, time
import itertools
from logtailconf import *

STR_TOPIC_JOIN = '-!- Topic for #aioc: '
STR_TOPIC_CHANGED = '-!- ChanServ!ChanServ@services. changed topic of #aioc to: '


def identity_mutator(match):
  return match

def const_mutator(result):
  def _(match):
    return result
  return _

def link_mutator(match):
  return '<a href="' + match + '">[link]</a>'

mutators = [
  (r'https?://[^ "()]*',   link_mutator),
  (r'\bkappa\b',           const_mutator('<img src="/kappa.png">')),
  (r'\blambda\b',          const_mutator('<img src="/kappa.png" style="transform: scaleY(-1)">')),
  (r'\bwow\b',             const_mutator('<img src="/doge.gif">')),
  (r'\+1\b',               const_mutator('<img src="/plus-1.png">')),
  (r'\b(?:top)?kek\b',     const_mutator('<img src="/topkek.png">')),
]

global_matcher = '|'.join('(' + pattern + ')' for pattern, _ in mutators)
global_matcher = re.compile(global_matcher, re.I)
mutators = [mutator for _, mutator in mutators]
mutators.insert(0, identity_mutator)


class Msg(object):
  def __init__(self, timestamp, sender, text, action, server):
    self.timestamp = timestamp
    self.sender = sender
    self.text = text.decode('utf-8', 'ignore')
    self.action = action
    self.server = server

  def html(self):
    def nickhash(nick):
      h = sum(map(ord, nick))
      h %= len(COLOURS)
      return h

    if self.action:
      fmt = '<span class="timestamp">%s</span> <span class="action">* %s %s</span>'
    elif self.server:
      fmt = '<span class="timestamp">%s</span> <span class="server">!! %s %s</span>'
    else:
      colour = COLOURS[nickhash(self.sender)]
      fmt = '<span class="timestamp">%s</span> <span class="nick" style="color: {colour}">&lt;%s&gt;</span> %s'
      fmt = fmt.format(colour=colour)

    fmt += '<br>'

    return fmt % (self.timestamp, self.sender, self.text)

  def __str__(self):
    return str((self.timestamp, self.sender, self.text))


def get_lines(filename, num):
  with open(filename) as f:
    lines = f.readlines()[-num:]
    lines = map(str.strip, lines)
  return lines

def get_topic(lines):
  for s in reversed(lines):
    s = s[20:]
    if s.startswith(STR_TOPIC_JOIN):
      topic = s[len(STR_TOPIC_JOIN):]
      break
    elif s.startswith(STR_TOPIC_CHANGED):
      topic = s[len(STR_TOPIC_CHANGED):]
      break
  else:
    return None  # No topic

  topic = topic.decode('utf-8', 'ignore')
  topic = escape_html(topic)
  topic = execute_mutators(topic)

  return topic

def split_lines(ss):
  res = []
  for s in ss:
    # Extract the timestamp
    timestamp = s[:19]
    s = s[20:]

    # And the sender... can be an ACTION or a server message
    action = False
    server = False

    if s.startswith('-!-'):
      s = s[4:]
      sender = ''
      server = True
    elif s.startswith('> * '):
      s = s[4:]
      sender, s = s.split(' ', 1)
      action = True
    elif s.startswith('< * '):
      s = s[4:]
      sender, s = s.split(' ', 1)
      action = True
    elif s.startswith('> '):
      s = s[2:]
      sender, s = s.split(' ', 1)
    elif s.startswith('< '):
      s = s[2:]
      if ' ' not in s:
        sender, s = s, 'I am a teapot: fat and retarded'
      else:
        sender, s = s.split(' ', 1)

    if '!' in sender:
      sender = sender[:sender.find('!')]

    if sender.endswith(':'):
      sender = sender[:-1]

    if server and '!' in s:
      sender = s[:s.find('!')]
      s = s.split(' ', 1)[1]

    res.append(Msg(timestamp, sender, s, action, server))
  return res


def escape_html(text):
  try:
    return cgi.escape(text).encode('ascii', 'xmlcharrefreplace')
  except UnicodeDecodeError:
    return 'fuck a duck, unicode broke'


def escape_html_list(ss):
  for s in ss:
    s.text = escape_html(s.text)


def execute_mutators(text):
  fragments = []
  for fragment, mutator in itertools.izip(global_matcher.split(text),
                                          itertools.cycle(mutators)):
    if fragment is not None:
      fragments.append(mutator(fragment))
  return ''.join(fragments)


def execute_mutators_list(ss):
  for s in ss:
    s.text = execute_mutators(s.text)


def detect_addressing(ss):
  for s in ss:
    if '#aioc' in s.text and not s.server:
      s.text = '<b>' + s.text + '</b>'
    else:
      m = re.search(r'([a-z]{2,4}?)\1\1', s.text)
      # Drop things like "hahaha" and "looooool"
      if m and all(bad not in m.groups() for bad in ['ha', 'ah', 'oo']):
        s.text = '<b>' + s.text + '</b>'


def generate_file(topic, ss, filename):
  f = open(filename, 'w')

  print >> f, PROLOGUE
  print >> f, ('<p><span class="topic-header">' + '&nbsp;' * 7 + 'Latest topic</span> ' +
      '<span class="topic" id="topic">%s</span>' +
      '</p>') % topic

  for s in ss:
    print >> f, s.html()

  print >> f, EPILOGUE


def file_replace_atomic(file_to, file_from):
  os.rename(file_from, file_to)


def message_pipeline(ss):
  ss = split_lines(ss)
  escape_html_list(ss)
  execute_mutators_list(ss)
  detect_addressing(ss)
  return ss


def main(file_in, file_out, num, msg_callback=None):
  # Parse
  lines = get_lines(file_in, 0)  # Keep all lines in memory
  topic = get_topic(lines)
  ss = message_pipeline(lines[-num:])  # But only parse last few lines

  # Generate and atomically move
  temp_fd, temp = tempfile.mkstemp(suffix='.log', prefix='logtail', dir='/tmp')
  os.fchmod(temp_fd, 0644)
  generate_file(topic, ss, temp)
  file_replace_atomic(file_out, temp)


  # Open up the infile (race here, but fuck it)
  # TODO rework by removing get_lines() function
  # Spin waiting for new lines
  fd = os.open(file_in, os.O_RDONLY)
  os.lseek(fd, 0, os.SEEK_END)


  # Spin waiting for new lines
  part = ''
  while True:
    part += os.read(fd, 9001)
    if not part or '\n' not in part:
      time.sleep(1)
      continue

    # Cool, got some shit. Run it through the same pipeline.
    lines = part.split('\n')
    lines, part = lines[:-1], lines[-1]

    topic = get_topic(lines) or topic
    new_data = message_pipeline(lines)
    ss += new_data
    ss = ss[-num:]

    generate_file(topic, ss, temp)
    file_replace_atomic(file_out, temp)

    if msg_callback is not None:
      for datum in new_data:
        msg_callback(topic, datum.html())


if __name__ == '__main__':
  main(sys.argv[1], sys.argv[2], int(sys.argv[3]))
