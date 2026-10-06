import cloudinary
import cloudinary.uploader
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask import request, redirect, url_for, session
from werkzeug.utils import secure_filename
import os
from flask_bcrypt import Bcrypt
from flask import flash;
from dotenv import load_dotenv
import os
from flask_migrate import Migrate


cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)
config = cloudinary.config()

print("Cloud Name:", config.cloud_name)
print("API Key:", config.api_key)
print("API Secret:", config.api_secret)

app = Flask(__name__)
load_dotenv()
app.secret_key = os.getenv("SECRET_KEY")

database_url = os.getenv("DATABASE_URL")
print("DATABASE_URL:", database_url)




ADMIN_USERNAME = "Sawara"
ADMIN_PASSWORD = "Sawara2018"

#database_url = os.getenv("DATABASE_URL")

database_url = os.getenv("DATABASE_URL")


if not database_url:
    raise RuntimeError(
        "DATABASE_URL not found. Check your .env file."
    )

if database_url.startswith("postgres://"):
    database_url = database_url.replace(
        "postgres://",
        "postgresql://",
        1
    )

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False



db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)


class Category(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    def __repr__(self):
        return self.name

class Product(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(200), nullable=False)

    category_id = db.Column(
    db.Integer,
    db.ForeignKey('category.id'),
    nullable=False
)

    category = db.relationship(
    'Category',
    backref='products'
)

    description = db.Column(db.Text)

    price = db.Column(db.Float)

    image = db.Column(db.String(255))

    def __repr__(self):
        return f"<Product {self.name}>"


class Admin(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )

    def __repr__(self):
        return self.username
    


    

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/products')
def products():

    products = Product.query.all()
    categories = Category.query.all()

    return render_template(
        'products.html',
        products=products,
        categories=categories
    )
@app.route("/about")
def about():
    return render_template("about.html")


@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/services')
def services():
    return render_template('services.html')


@app.route('/admin')
def admin_dashboard():

    if not session.get('admin_logged_in'):
        return redirect('/admin/login')

    total_products = Product.query.count()

    return render_template(
        'admin/dashboard.html',
        total_products=total_products
    )

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():

    error = None

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        admin = Admin.query.filter_by(
            username=username
        ).first()

        if (
            admin
            and bcrypt.check_password_hash(
                admin.password,
                password
            )
        ):

            session['admin_logged_in'] = True
            session['admin_id'] = admin.id

            return redirect('/admin')

        else:

            flash('Invalid username or password.', 'danger')

    return render_template(
        'admin/login.html',
        error=error
    )

@app.route('/admin/logout')
def admin_logout():

    session.clear()

    return redirect('/admin/login')


@app.before_request
def require_login():

    protected_routes = [

        'admin_dashboard',
        'admin_products',
        'admin_add_product',
        'edit_product',
        'delete_product'

    ]

    if (
        request.endpoint in protected_routes
        and not session.get('admin_logged_in')
    ):

        return redirect('/admin/login')
        
@app.route('/admin/change-password', methods=['GET', 'POST'])
def change_password():

    if not session.get('admin_logged_in'):
        return redirect('/admin/login')

    message = None
    error = None

    admin = Admin.query.get(session['admin_id'])

    if request.method == 'POST':

        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        # Verify current password
        if not bcrypt.check_password_hash(
            admin.password,
            current_password
        ):
            error = "Current password is incorrect"

        elif new_password != confirm_password:
            error = "New passwords do not match"

        else:

            hashed_password = bcrypt.generate_password_hash(
                new_password
            ).decode('utf-8')

            admin.password = hashed_password

            db.session.commit()

            message = "Password updated successfully"

    return render_template(
        'admin/change_password.html',
        message=message,
        error=error
    )


@app.route('/admin/products')
def admin_products():

    if not session.get('admin_logged_in'):
      return redirect('/admin/login')

    products = Product.query.all()

    return render_template(
        'admin/products.html',
        products=products
    )


@app.route('/admin/add-product', methods=['GET', 'POST'])
@app.route('/admin/add-product', methods=['GET', 'POST'])
def admin_add_product():

    if not session.get('admin_logged_in'):
        return redirect('/admin/login')

    if request.method == 'POST':

        image = request.files.get('image')

        image_url = ""

        if image and image.filename:

            upload_result = cloudinary.uploader.upload(
                image,
                folder="sawara-products"
            )

            image_url = upload_result["secure_url"]

        product = Product(

            name=request.form['name'],

            category_id=int(request.form['category_id']),

            description=request.form['description'],

            price=float(request.form['price']),

            image=image_url

        )

        db.session.add(product)

        db.session.commit()

        flash("Product added successfully!", "success")

        return redirect('/admin/products')

    categories = Category.query.all()

    return render_template(
        'admin/add_product.html',
        categories=categories
    )

@app.route('/admin/edit-product/<int:id>', methods=['GET', 'POST'])
def edit_product(id):

    if not session.get('admin_logged_in'):
        return redirect('/admin/login')

    product = Product.query.get_or_404(id)
    categories = Category.query.all()

    if request.method == 'POST':

        product.name = request.form['name']
        product.category_id = int(request.form['category_id'])
        product.description = request.form['description']
        product.price = float(request.form['price'])

        image = request.files.get("image")

        # Only upload if a new image was selected
        if image and image.filename != "":

            upload_result = cloudinary.uploader.upload(
                image,
                folder="sawara-products"
            )

            product.image = upload_result["secure_url"]

        db.session.commit()

        flash("Product updated successfully!", "success")

        return redirect('/admin/products')

    return render_template(
        'admin/edit_product.html',
        product=product,
        categories=categories
    )


@app.route('/admin/delete-product/<int:id>')
def delete_product(id):
    if not session.get('admin_logged_in'):
      return redirect('/admin/login')

    product = Product.query.get_or_404(id)

    db.session.delete(product)

    db.session.commit()

    return redirect('/admin/products')

@app.route('/create-categories')
def create_categories():

    categories = [
        'Taps',
        'Pressure Controls',
        'Tubes',
        'Soap Dispensers',
        'Shower Heads',
        'Plastic Valves',
        'Bathroom and Toilet Fittings',
        'Valves'
    ]

    for name in categories:

        existing = Category.query.filter_by(
            name=name
        ).first()

        if not existing:

            db.session.add(
                Category(name=name)
            )

    db.session.commit()

    return "Categories created successfully"

@app.route('/view-categories')
def view_categories():

    categories = Category.query.all()

    result = ""

    for category in categories:
        result += f"{category.id} - {category.name}<br>"

    return result

@app.route('/delete-category/<int:id>')
def delete_category(id):

    category = Category.query.get_or_404(id)

    db.session.delete(category)
    db.session.commit()

    return f"Category {category.name} deleted successfully"


@app.route('/test-categories')
def test_categories():

    categories = Category.query.all()

    for category in categories:
        print(category.id, category.name)

    return f"Found {len(categories)} categories"

@app.route('/view-admins')
def view_admins():

    admins = Admin.query.all()

    result = ""

    for admin in admins:
        result += f"{admin.id} - {admin.username}<br>"

    return result


    
if __name__ == "__main__":

    app.run(debug=True)

    