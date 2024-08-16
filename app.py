from flask import Flask, render_template, request, redirect, url_for, flash
import os
import dotenv


app = Flask(__name__)

dotenv.load_dotenv()

app.secret_key = os.getenv('FLASK_SECRET_KEY')
app.config['UPLOAD_FOLDER'] = 'upload/'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

instagram_username = os.getenv('INSTAGRAM_USERNAME')
instagram_password = os.getenv('INSTAGRAM_PASSWORD')


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def uploader(book_info, content, image_path):
    processed_image = process_image(image_path)
    caption = f"{content}\n\n{book_info}"
    processed_image_path = os.path.join(app.config['UPLOAD_FOLDER'],
                                        f"processed_{os.path.basename(image_path)}")
    processed_image.save(processed_image_path)
    upload_instagram(caption, processed_image_path)


@app.route('/', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        book_info = request.form['book_info']
        content = request.form['content']
        image = request.files['image']

        if image and allowed_file(image.filename):
            filename = image.filename
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(image_path)

            uploader(book_info, content, image_path)

            flash("Upload success!")
            return redirect(url_for('upload'))

    return render_template('upload.html')


if __name__ == '__main__':
    app.run(debug=True)
