import os
from glob import glob

import colortransfer
from flask import Flask, render_template, session, redirect, url_for, request, flash
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField, Form, StringField, PasswordField, validators

from dbadapter import DBAdapter

app = Flask(__name__)
app.config['SECRET_KEY'] = 'I have a dream'
app.config['UPLOADED_PHOTOS_DEST'] = os.getcwd()
db_filename = 'users.db'
db = DBAdapter(db_filename)

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app)  # set maximum file size, default is 16MB


class RegistrationForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')


class LoginForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    password = StringField('Password')


class UploadSourceForm(FlaskForm):
    source_photo = FileField(validators=[FileAllowed(photos, u'Image only!'),
                                         FileRequired(u'File was empty!')])
    submit = SubmitField(u'Upload Source')


class UploadTargetForm(FlaskForm):
    target_photo = FileField(validators=[FileAllowed(photos, u'Image only!'),
                                         FileRequired(u'File was empty!')])
    submit = SubmitField(u'Upload Target')


@app.route('/')
def index():
    if 'username' in session:
        source_fn = db.get_image_fn('source_image', username=session['username'])
        source_url = photos.url(source_fn) if source_fn else None
        target_fn = db.get_image_fn('target_image', username=session['username'])
        target_url = photos.url(target_fn) if target_fn else None
        result_fn = db.get_image_fn('result_image', username=session['username'])
        result_url = photos.url(result_fn) if result_fn else None
        return render_template('index.html',
                               username=session['username'],
                               source_image=source_url,
                               target_image=target_url,
                               result_image=result_url)
    else:
        return render_template('index.html', username=None)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        if db.user_exists(form.username.data):
            return render_template('register.html', error='That username is taken')
        else:
            username = db.register_user(form.username.data,
                                        form.password.data)
            flash('Thanks for registering, {}'.format(username))
            return redirect(url_for('login'))
    elif request.method == 'POST' and not form.validate():
        return render_template('register.html', error='Invalid username or password')
    else:
        return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    error = None
    if request.method == 'POST' and form.validate():
        if db.login_user(form.username.data,
                         form.password.data):
            session['username'] = request.form['username']
            flash('Login successful!')
            return redirect(url_for('index'))
        else:
            error = "Invalid username or password"
            flash(error)
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


@app.route('/upload_source', methods=['GET', 'POST'])
def upload_source():
    source_form = UploadSourceForm()
    if request.method == 'POST' and source_form.validate_on_submit():
        list(map(os.remove, glob('data/{}/source_image.*'.format(session['username']))))
        db.remove_image('source_image', session['username'])
        source_filename = photos.save(source_form.source_photo.data,
                                      name='data/{}/source_image.'.format(session['username']))
        # source_url = photos.url(source_filename)
        db.store_image_fn('source_image', source_filename, session['username'])
        return redirect(url_for('index'))
    else:
        source_filename = None

    return render_template('upload_source.html',
                           form=source_form,
                           source_url=photos.url(db.get_image_fn('source_image', session['username'])),
                           username=session['username'])


@app.route('/upload_target', methods=['GET', 'POST'])
def upload_target():
    target_form = UploadTargetForm()
    if request.method == 'POST' and target_form.validate_on_submit():
        list(map(os.remove, glob('data/{}/target_image.*'.format(session['username']))))
        db.remove_image('target_image', session['username'])
        target_filename = photos.save(target_form.target_photo.data,
                                      name='data/{}/target_image.'.format(session['username']))
        # target_url = photos.url(target_filename)
        db.store_image_fn('target_image', target_filename, session['username'])
        return redirect(url_for('index'))
    else:
        target_filename = None

    return render_template('upload_target.html',
                           form=target_form,
                           target_url=photos.url(db.get_image_fn('target_image', session['username'])),
                           username=session['username'])


@app.route('/transfer_colors', methods=['GET', 'POST'])
def transfer_colors():
    source_fn = db.get_image_fn('source_image', session['username'])
    target_fn = db.get_image_fn('target_image', session['username'])
    result_fn = 'data/{}/result_image.png'.format(session['username'])
    colortransfer.color_transfer(source_fn, target_fn, result_fn)
    db.store_image_fn('result_image', result_fn, session['username'])
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()
