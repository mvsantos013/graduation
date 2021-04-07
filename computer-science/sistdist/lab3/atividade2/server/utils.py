import json

def count_occurrences(text, words_limit = 10):
  ''' Get 10 most frequent words in text.
      Output example:
      { word1: count, word2: count, ... }
  '''
  result = {}
  words = text.split()
  for word in words:
    word = word.strip()
    # Check if result can be edited.
    if((len(result) < words_limit or word in result) and word):
      result[word] = result[word] + 1 if word in result else 1
  sorted_keys = sorted(result.items(), key=lambda item: item[1], reverse=True)
  sorted_result = { k: v for k, v in sorted_keys }
  return sorted_result


def encode_message(data, status = 200):
    return json.dumps({ 'body': data, 'status': status }).encode()


def decode_message(msg):
    return Message(json.loads(msg.decode('utf-8')))


class Message():
  def __init__(self, msg):
    self.body = msg['body']
    self.status = msg['status']