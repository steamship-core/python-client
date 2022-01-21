import io
import os
import zipfile

def create_zip_bytes(self, api_file="test_app/api.py") -> bytes:
  full_path = os.path.join(os.path.dirname(__file__), api_file)
  zip_buffer = io.BytesIO()

  files = []
  files.append('api.py', io.BytesIO(open(full_path, 'r').read()))

  with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:    
    for file_name, data in files:
      zip_file.writestr(file_name, data.getvalue())
  
  return zip_buffer.getvalue()
