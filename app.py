from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
import dotenv
from PIL import Image, ImageOps
from instagrapi import Client


app = Flask(__name__)

dotenv.load_dotenv()

app.secret_key = os.getenv('FLASK_SECRET_KEY')
app.config['UPLOAD_FOLDER'] = 'upload/'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

instagram_username = os.getenv('INSTAGRAM_USERNAME')
instagram_password = os.getenv('INSTAGRAM_PASSWORD')

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def process_image(image_path):
    image = Image.open(image_path)

    if image.size[0] != image.size[1]:
        image = ImageOps.pad(
            image, (max(image.size), max(image.size)), color='black')
    return image


def upload_instagram(caption, image_path):
    client = Client()
    client.login(instagram_username, instagram_password)
    client.photo_upload(image_path, caption)
    client.logout()


def uploader(book_info, content, image_path):
    processed_image = process_image(image_path)
    caption = f"{content}\n\n{book_info}"
    processed_image_path = os.path.join(app.config['UPLOAD_FOLDER'],
                                        f"processed_{os.path.basename(image_path)}")
    processed_image.save(processed_image_path)
    upload_instagram(caption, processed_image_path)


@app.route('/', methods=['GET'])
def get_form():
    # 세션에 저장된 최근 3개의 book_info를 불러옴
    recent_book_infos = session.get('recent_book_infos', [])
    return render_template('upload.html', recent_book_infos=recent_book_infos)


@app.route('/', methods=['POST'])
def upload_file():
    book_info = request.form['book_info']
    content = request.form['content']
    image = request.files['image']

    # 세션에 book_info를 저장 (최대 3개만 유지)
    recent_book_infos = session.get('recent_book_infos', [])
    if book_info not in recent_book_infos:
        recent_book_infos.insert(0, book_info)
        if len(recent_book_infos) > 3:
            recent_book_infos.pop()
        session['recent_book_infos'] = recent_book_infos

    if image and allowed_file(image.filename):
        filename = image.filename
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(image_path)

        uploader(book_info, content, image_path)

        flash("Upload success!")
        return redirect(url_for('get_form'))

    return redirect(url_for('get_form'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
