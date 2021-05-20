#!/usr/bin/env python3
from flask import Flask, redirect, url_for, flash
from flask import make_response, render_template, abort, request
from werkzeug.utils import secure_filename

from string import Template
import subprocess, shlex
import os
from io import StringIO

app = Flask(__name__)
app.secret_key = "SSCsupersekrit"  # Replace this with your own secret!
app.config['UPLOAD_FOLDER']="./build"

# curl -X POST http://localhost:5000/build -F "files[]=@Singularity.lolcow" -F sif_name=lolcow.sif -F sif_recipe=Singularity.lolcow
@app.route("/build", methods=['GET', 'POST'])
def build(file_element_name="files[]"):
  ip= request.remote_addr

  if request.method == 'POST':
    # get list of files uploaded
    files = request.files.getlist(file_element_name)
    try:
      user_id=    request.form["user_id"]
      sif_name=   os.path.join(app.config['UPLOAD_FOLDER'],  user_id, request.form["sif_name"])
      sif_recipe= os.path.join(app.config['UPLOAD_FOLDER'],  user_id, request.form["sif_recipe"])
    except:
      print("Wrong sif_name sif_recipe")
      response= make_response('Wrong sif_name or sif_recipe', 404)
      abort(403)

    user_folder= os.path.join(app.config['UPLOAD_FOLDER'], user_id)
    if not os.path.exists(user_folder):
      os.makedirs(user_folder)

    # loop through uploaded files, saving
    for ifile in files:
      try:
        filename = secure_filename(ifile.filename)
        print(f"uploading file {filename} of type {ifile.content_type}")
        ifile.save(os.path.join(user_folder, filename))
        flash(f"Just uploaded: {filename}")
      except OSError as e:
        flash("ERROR writing file " + filename + " to disk: " + StringIO(str(e)).getvalue()) 

    cmd_txt= f"sudo singularity build -F {sif_name} {sif_recipe}"
    cmd=shlex.split(cmd_txt)
    print(">>> cmd: " + cmd_txt)

    flog= open(f"{sif_recipe}.log","w")
    proc= subprocess.Popen(cmd, stdout=flog, stderr=flog, close_fds=True)
    #stdout, stderr = proc.communicate()
    #print(stdout.decode())
    #print(stderr.decode())

  #return redirect(url_for("build_log"))
  response= make_response("Starting build...", 200)
  response.mimetype = "text/plain"
  return response


@app.route("/build_log", methods=['GET'])
def build_log():

  
  response_tmp= Template("${stdout}\nDone").substitute(stdout=stdout.decode(), stderr=stderr.decode)
  response= make_response(response_tmp, 200)
  response.mimetype = "text/plain"
  return response


#=======================================================================================
@app.route("/")
def index():
  return "SSC singularity test"
#============================================================================

if __name__ == '__main__':
  app.run(host="0.0.0.0", port=7878, debug=True)

