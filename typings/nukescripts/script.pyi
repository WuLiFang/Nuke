"""
This type stub file was generated by pyright.
"""

kCommandField = 'Command:'
last_cmd = ''
def script_command(default_cmd):
  ...

def script_version_up():
  """Adds 1 to the _v## at the end of the script name and saves a new
  version."""
  ...

def script_and_write_nodes_version_up():
  """ Increments the versioning in the script name and the path of the timeline
  write nodes, then saves the new version. """
  ...

def get_script_data():
  ...

def script_data():
  ...

def script_directory():
  ...

