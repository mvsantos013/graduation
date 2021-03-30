import os

FILES_DIR = './files'

def fetch_files():
  ''' Fetch list of available files and returns as list. '''
  files = [f for f in os.listdir(FILES_DIR) if f.endswith('.txt')]
  return files

def read_file(filename):
  ''' Returns file content. '''
  with open(FILES_DIR + '/' + filename) as f:
    content = f.read()
    return content