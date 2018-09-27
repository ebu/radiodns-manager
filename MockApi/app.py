import os

from flask import Flask, jsonify, request, Response, send_from_directory

import config

UPLOAD_FOLDER_ROOT = "./uploads"

UPLOAD_FOLDERS = [
    UPLOAD_FOLDER_ROOT + '/32x32',
    UPLOAD_FOLDER_ROOT + '/112x32',
    UPLOAD_FOLDER_ROOT + '/128x128',
    UPLOAD_FOLDER_ROOT + '/320x240',
    UPLOAD_FOLDER_ROOT + '/600x600',
]

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER_ROOT

for folder in UPLOAD_FOLDERS:
    if not os.path.exists(folder):
        os.makedirs(folder)


@app.route('/')
def root():
    return jsonify({
        "version": "1.0",
        "description": "This is the MockApi server used in development until a staging environment is available."
    })


@app.route("/orga/<orgaId>")
def orga(orgaId):
    return jsonify({
        "codops": "standalone",
        "pk": 29,
        "name": "Abertis Telecom"
    })


def save_file(path):
    """
    Saves the file passed in the implicit request if any. Return 422 if the browser sent an empty part without
    a file. Otherwise save the file under the precised path if any and return 200.
    :param path: The path where to save the file. For example "32x32". You can also pass None if no path is available.
    :return: 422 if no file selected. 200 Otherwise.
    """
    if request.method == 'POST':
        if not path:
            path = ""
        else:
            path = "/" + path
        # check if the post request has the file part
        for filename in request.files:
            file = request.files[filename]

            if file.filename == '':
                return Response(status=422, response="No selected file!")

            file.save(os.path.join(app.config['UPLOAD_FOLDER'] + path, filename))
        return Response(status=200, response="ok")


@app.route('/uploads', methods=['POST'])
def upload_file():
    save_file(None)


@app.route('/uploads/<path:path>', methods=['POST'])
def upload_file_resized(path):
    save_file(path)


@app.route('/uploads/<path:path>')
def send_file(path):
    if not len(path.split("/")) == 2:
        return send_from_directory(app.config['UPLOAD_FOLDER'], path)

    size_prefix, filename = path.split("/")
    return send_from_directory(app.config['UPLOAD_FOLDER'] + "/" + size_prefix, filename)


if __name__ == '__main__':
    app.run(host=config.MOCK_API_HOST, port=config.MOCK_API_PORT, debug=config.DEBUG)
