from flask import Flask, render_template, request
from flask.ext.uploads import UploadSet, configure_uploads, IMAGES

app = Flask(__name__)

photos = UploadSet('photos', IMAGES)

app.config['UPLOADED_PHOTOS_DEST'] = 'static/img'
configure_uploads(app, photos)

@app.route('/', methods=['GET', 'POST'])
def hello_world():
    return 'Hello World!'

if __name__ == '__main__':
    app.run()
