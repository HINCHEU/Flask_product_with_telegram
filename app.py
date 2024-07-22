from flask import Flask, render_template, request, url_for, redirect
from datetime import date, datetime
import requests
from werkzeug.utils import secure_filename
import os
import sqlite3
import base64

UPLOAD_FOLDER = 'static/image/product'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()
product_cart =[]

@app.route('/')
def hello_world():
    #Renders the product list page
    products = fetch_products_from_db()
    return render_template('product.html', products=products)


@app.route('/product')
def product():
    #Redirects to the main product list page
    return redirect(url_for('hello_world'))


def fetch_products_from_db():
    #Fetches all products from the database
    cursor.execute("""SELECT * FROM product""")
    rows = cursor.fetchall()
    products = [
        {
            'id': row[0],
            'title': row[1],
            'price': row[3],
            'description': row[4],
            'category': row[5],
            'image': row[6],
            'qty': row[7],
        }
        for row in rows
    ]
    return products

def card_product():
    if 'product_id' in request.form:
        product_id = int(request.form['product_id'])
        cursor.execute("SELECT * FROM product WHERE id=?", (product_id,))
        row = cursor.fetchone()
        product= next((item for item in product_cart if item['id'] == product_id), None)
        if row and not product:
            current_product = {
                'id': row[0],
                'title': row[1],
                'price': row[3],
                'description': row[4],
                'category': row[5],
                'image': row[6],
                'qty': row[7],
            }
            product_cart.append(current_product)
    else:
        return product_cart


@app.route('/product_detail')
def product_detail():
    #Renders the product detail page.
    product_id = request.args.get('id')
    cursor.execute("SELECT * FROM product WHERE id=?", (product_id,))
    row = cursor.fetchone()
    if row:
        current_product = {
            'id': row[0],
            'title': row[1],
            'price': row[3],
            'description': row[4],
            'category': row[5],
            'image': row[6],
            'qty': row[7],
        }
        return render_template('productdetail.html', current_product=current_product)
    else:
        return "Product not found", 404


@app.route('/product_management')
def product_management():
    #Renders the product management page.
    message = request.args.get('message')
    products = fetch_products_from_db()
    return render_template('product_managment.html', products=products, message=message)


@app.route('/submit_new_product', methods=['POST'])
def submit_new_product():
    #Submits a new product and adds it to the database.
    product_title = request.form.get('product_name')
    product_price = request.form.get('price')
    product_description = request.form.get('description')
    product_category = request.form.get('category')
    product_qty = request.form.get('qty')
    cropped_image_base64 = request.form.get('cropped_image')

    if not cropped_image_base64:
        return "No image data", 400

    # Decode the base64 image data
    header, encoded = cropped_image_base64.split(",", 1)
    data = base64.b64decode(encoded)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    new_filename = f"{timestamp}_cropped.png"

    # Save the decoded image to the project file
    with open(os.path.join(app.config['UPLOAD_FOLDER'], new_filename), "wb") as f:
        f.write(data)

    # Add the product to the database
    new_product_sql = """INSERT INTO product (title, price, qty, description, category, image) VALUES (?, ?, ?, ?, ?, ?)"""
    cursor.execute(new_product_sql, (product_title, product_price, product_qty, product_description, product_category, new_filename))
    conn.commit()

    return redirect(url_for('product_management', message='Add Product Successfully'))


@app.route('/product_delete', methods=['GET', 'POST'])
def delete_product():
    #Deletes a product from the database
    product_id = request.args.get('id')
    cursor.execute("DELETE FROM product WHERE id=?", (product_id,))
    conn.commit()
    return redirect(url_for('product_management'))


@app.route('/product_update', methods=['POST'])
def update_product():
    #Updates a product in the database
    product_id = request.form.get('id')
    product_title = request.form.get('title')
    product_price = request.form.get('price')
    product_description = request.form.get('description')
    product_category = request.form.get('category')
    product_qty = request.form.get('qty')
    cropped_image_base64 = request.form.get('cropped_image')

    new_filename = None

    if cropped_image_base64:
        # Decode the base64 image data
        header, encoded = cropped_image_base64.split(",", 1)
        data = base64.b64decode(encoded)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        new_filename = f"{timestamp}_cropped.png"

        # Save the decoded image to the file system
        with open(os.path.join(app.config['UPLOAD_FOLDER'], new_filename), "wb") as f:
            f.write(data)
    else:
        # If no new image is uploaded, keep the old one
        cursor.execute("SELECT image FROM product WHERE id=?", (product_id,))
        new_filename = cursor.fetchone()[0]

    # Update the product in the database
    update_product_sql = """UPDATE product SET title=?, price=?, qty=?, description=?, category=?, image=? WHERE id=?"""
    cursor.execute(update_product_sql, (product_title, product_price, product_qty, product_description, product_category, new_filename, product_id))
    conn.commit()

    return redirect(url_for('product_management', message='Update Product Successfully'))



def allowed_file(filename):
    #Check if the filename is allowed based on its extension
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/product_edit')
def edit_product():
    #Edit View
    product_id = request.args.get('id')
    cursor.execute("SELECT * FROM product WHERE id=?", (product_id,))
    row = cursor.fetchone()
    if row:
        current_product = {
            'id': row[0],
            'title': row[1],
            'price': row[3],
            'description': row[4],
            'category': row[5],
            'image': row[6],
            'qty': row[7],
        }
        return render_template('edit_product.html', current_product=current_product)
    else:
        return "Product not found", 404

@app.route('/check_out', methods =['POST','GET'])
def check_out():
    #Check out View
    # product_id = request.args.get('id')
    # qty = request.args.get('qty')
    # cursor.execute("SELECT * FROM product WHERE id=?", (product_id,))
    # row = cursor.fetchone()
    # if row:
    #     current_product = {
    #         'id': row[0],
    #         'title': row[1],
    #         'price': row[3],
    #         'description': row[4],
    #         'category': row[5],
    #         'image': row[6],
    #         'qty': row[7],
    #     }
    #     return render_template('check_out.html', current_product=current_product, qty=qty)
    # else:
    #     return "Product not found", 404
    card_product()
    return render_template('check_out.html', current_product=product_cart )

@app.route('/submit_order', methods=['POST'])
def submit_order():
    name = request.form['fullname'] 
    phone = request.form['phone']
    email = request.form['email']

    bot_token = '6490003594:AAHGad1MucESpYtWXfUXDjcvGi-RucdmzaE'
    chat_id = '843851538'

    customer_details = (
        f"<code>📆 {date.today()}</code>\n"
        f"<code>==From customer==</code>\n"
        f"<code>Name : {name}</code>\n"
        f"<code>Phone : {phone}</code>\n"
        f"<code>Email : {email}</code>\n"
        f"<code>==Ordered Products==</code>\n"
    )

    full_message = customer_details

    for product in product_cart:
        product_id = product['id']
        product_name = product['title']
        price = product['price']    
        image_filename = product['image']
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)

        product_details = (
            f"<code>Product id={product_id}</code>\n"
            f"<code>Product Name={product_name}</code>\n"
            f"<code>Price={price}</code>\n"
        )
        full_message += product_details

    # Send the full message without images
    data = {'chat_id': chat_id, 'text': full_message, 'parse_mode': 'HTML'}
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    res = requests.post(url, data=data)
    print(res.json())

    # Send each image with its product details
    for product in product_cart:
        product_id = product['id']
        product_name = product['title']
        price = product['price']
        image_filename = product['image']
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)

        product_html = (
            f"<code>Product id={product_id}</code>\n"
            f"<code>Product Name={product_name}</code>\n"
            f"<code>Price={price}</code>\n"
        )

        with open(image_path, 'rb') as image_file:
            files = {'photo': image_file}
            data = {'chat_id': chat_id, 'caption': product_html, 'parse_mode': 'HTML'}
            url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"

            res = requests.post(url, files=files, data=data)
            print(res.json())



    return redirect(url_for('product', message="Your Order has been submitted"))

if __name__ == '__main__':
    app.run(debug=True)
