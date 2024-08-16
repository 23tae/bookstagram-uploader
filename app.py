from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)

app.secret_key = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'upload/'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


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
