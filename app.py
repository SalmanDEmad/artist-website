from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
import os
import secrets
import base64
app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
# MySQL database connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="magma",
    auth_plugin='mysql_native_password'
)

include_test=False

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/test')
def test():
    return render_template('portfolio.html')

@app.route('/test2')
def test2():
    return render_template('test2.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Handle form submission here
        pass
    return render_template('contact.html')

@app.route('/post_to_portfolio', methods=['POST'])
def post_to_portfolio():
    title = request.form['title']
    description = request.form['description']
    category_for_post = request.form['category_for_post']
    text_input_for_post = request.form['text_input_for_post']

    # Check if category_for_post is filled
    if category_for_post:
        category = category_for_post
    # If not, check if text_input_for_post is filled
    elif text_input_for_post:
        category = text_input_for_post
    # If neither is filled, return an error message
    else:
        return "Error: Please fill in either the category or the text input field."

    # Get the base64-encoded image data from the form
    image_data_base64 = request.form['croppedImageData']

    # Convert the base64-encoded image data to binary data
    image_data_binary = base64.b64decode(image_data_base64.split(',')[1])

    # Generate a random filename for the image
    filename = secrets.token_hex(3) + '.jpg'

    # Set the directory to the relative path of the images folder
    directory = os.path.join('static', 'images')

    # Save the image data to disk as a PNG file
    with open(os.path.join(directory, filename), 'wb') as f:
        f.write(image_data_binary)

    # Insert the image data into the database
    mycursor = db.cursor()
    query = ("INSERT INTO images (filename, directory, title, description, category) "
            "VALUES (%s, %s, %s, %s, %s)")

    data = (filename, directory, title, description, category)

    mycursor.execute(query, data)
    db.commit()

    mycursor.close()

    print("posted successfully I think")

    # redirect to portfolio page
    return redirect(url_for('portfolio'))



@app.route('/portfolio/', defaults={'category': None}, methods=['GET', 'POST'])
@app.route('/portfolio/<category>/', methods=['GET', 'POST'])
def portfolio(category):
    if category is None:
        category = ""
    if request.method == 'POST':
        category = request.form['category']
    mycursor = db.cursor()

    query = ("SELECT DISTINCT category FROM images")
    mycursor.execute(query)
    categories = [row[0] for row in mycursor.fetchall()]

    if category and category != "":
        query = ("SELECT id, filename, directory, title, description, category FROM images WHERE category = %s")
        mycursor.execute(query, (category,))
    else:
        query = ("SELECT id, filename, directory, title, description, category FROM images")
        mycursor.execute(query)


    images = []
    for (id, filename, directory, title, description, cat) in mycursor:
        # Create a dictionary for each row
        image = {
            'id': id,
            'filename': filename,
            'directory': directory,
            'title': title,
            'description': description,
            'category': cat,
            'image_path': os.path.join(directory, filename)
        }
        images.append(image)

    return render_template('portfolio.html', images=images, categories=categories, category=category, include_test=True)



@app.route('/vouch')
def vouch():
    return render_template('vouch.html')

if __name__ == '__main__':
    app.run(debug=True)