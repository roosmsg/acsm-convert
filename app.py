from flask import Flask, request, send_file, Response, render_template_string
import subprocess
import os
import shutil
import xml.etree.ElementTree as ET

app = Flask(__name__)

# Directories inside the container
UPLOAD_FOLDER = '/home/libgourou/files'
ADEPT_DIR    = '/home/libgourou/.adept'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Bootstrap-based template
TEMPLATE = '''
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <title>ACSM Converter</title>
    <style>
      body { padding-top: 40px; }
      .container { max-width: 500px; }
    </style>
  </head>
  <body>
    <div class="container">
      <h1 class="mb-4 text-center">ACSM Converter</h1>
      {% if error %}
        <div class="alert alert-danger">{{ error }}</div>
      {% endif %}
      <form method="post" enctype="multipart/form-data">
        <div class="form-group">
          <label for="fileInput">Choose a .acsm file</label>
          <input type="file" class="form-control-file" id="fileInput" name="file" accept=".acsm" required>
        </div>
        <button type="submit" class="btn btn-primary btn-block">Convert</button>
      </form>
      {% if download_url %}
        <hr>
        <a href="{{ download_url }}" class="btn btn-success btn-block">Download your ebook</a>
      {% endif %}
    </div>
    <script src="https://cdn.jsdelivr.net/npm/jquery@3.5.1/dist/jquery.slim.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/js/bootstrap.bundle.min.js"></script>
  </body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    error = None
    download_url = None
    if request.method == 'POST':
        # Clean upload directory
        for fname in os.listdir(UPLOAD_FOLDER):
            fpath = os.path.join(UPLOAD_FOLDER, fname)
            try:
                if os.path.isfile(fpath) or os.path.islink(fpath):
                    os.unlink(fpath)
                elif os.path.isdir(fpath):
                    shutil.rmtree(fpath)
            except Exception as e:
                app.logger.error(f"Failed to remove {fpath}: {e}")

        # Save ACSM
        file = request.files.get('file')
        if not file:
            error = 'No file uploaded.'
            return render_template_string(TEMPLATE, error=error)
        acsm_filename = file.filename
        acsm_path = os.path.join(UPLOAD_FOLDER, acsm_filename)
        file.save(acsm_path)

        # Determine output name
        try:
            tree = ET.parse(acsm_path)
            ns = {'dc': 'http://purl.org/dc/elements/1.1/'}
            title = tree.findtext('.//dc:title', namespaces=ns) or os.path.splitext(acsm_filename)[0]
            safe_title = title.strip().replace('/', '_')
            fmt = tree.findtext('.//dc:format', namespaces=ns) or 'application/epub+zip'
            ext = '.pdf' if 'pdf' in fmt.lower() else '.epub'
        except Exception:
            safe_title = os.path.splitext(acsm_filename)[0]
            ext = '.epub'

        # Step 1: download DRM file
        drm_file = os.path.join(UPLOAD_FOLDER, 'ebook.drm')
        cmd1 = ['acsmdownloader', '--adept-directory', ADEPT_DIR, '--output-file', 'ebook.drm', acsm_path, '-O', UPLOAD_FOLDER]
        try:
            subprocess.run(cmd1, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            error = f"Download error: {e.stderr or e.stdout}"
            return render_template_string(TEMPLATE, error=error)

        # Step 2: remove DRM
        output_name = safe_title + ext
        cmd2 = ['adept_remove', '--adept-directory', ADEPT_DIR, '-O', UPLOAD_FOLDER, '-o', output_name, drm_file]
        try:
            subprocess.run(cmd2, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            error = f"DRM removal error: {e.stderr or e.stdout}"
            return render_template_string(TEMPLATE, error=error)

        # Provide download link
        download_url = f"/{output_name}"
    return render_template_string(TEMPLATE, error=error, download_url=download_url)

# Serve static eBooks
@app.route('/<path:filename>')
def serve_ebook(filename):
    return send_file(os.path.join(UPLOAD_FOLDER, filename), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
