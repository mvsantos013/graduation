import json

def encode_message(data, status = 200):
    return json.dumps({ 'body': data, 'status': status }).encode()

def decode_message(msg):
    return Message(json.loads(msg.decode('utf-8')))

class Message():
  def __init__(self, msg):
    self.body = msg['body']
    self.status = msg['status']