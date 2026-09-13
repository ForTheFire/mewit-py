import hashlib
from pathlib import Path

prefix = ".mew"

### Utils
# Returns SHA1 of a string 
def hashCalc(data):
  return hashlib.sha1(data.encode()).hexdigest()

# Recursively find files in a directory
def isDir(directory):
  files = []

  ignored = {".mew", ".acf"}

  for path in Path(directory).rglob("*"):
    if any(part in ignored for part in path.parts):
      continue

    if path.is_file():
      files.append(str(path))

  return files

# Returns specific commit tree
def retrieveTree(commit):
  # Open tree and retrieve data
  with open(prefix + "/objects/commits/" + commit) as f:
    currentTree = f.readlines()[0].rstrip().removeprefix("tree ")
  return currentTree

# Read a blob and return content
def readBlob(hashNum):
  with open(prefix + "/objects/blobs/" + hashNum, 'r') as blob:
    return blob.read()

# Pretty self expleinatory
def normalize_path(path):
    return Path(path).as_posix().removeprefix("./")

