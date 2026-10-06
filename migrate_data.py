import sqlite3
from app import app, db, Category, Product, Admin

sqlite_conn = sqlite3.connect("instance/database.db")
sqlite_conn.row_factory = sqlite3.Row
cursor = sqlite_conn.cursor()

with app.app_context():

    # Categories
    cursor.execute("SELECT * FROM category")
    for row in cursor.fetchall():
        if not Category.query.get(row["id"]):
            db.session.add(
                Category(
                    id=row["id"],
                    name=row["name"]
                )
            )

    db.session.commit()

    # Admins
    cursor.execute("SELECT * FROM admin")
    for row in cursor.fetchall():
        if not Admin.query.get(row["id"]):
            db.session.add(
                Admin(
                    id=row["id"],
                    username=row["username"],
                    password=row["password"]
                )
            )

    db.session.commit()

    # Products
    cursor.execute("SELECT * FROM product")
    for row in cursor.fetchall():
        if not Product.query.get(row["id"]):
            db.session.add(
                Product(
                    id=row["id"],
                    name=row["name"],
                    category_id=row["category_id"],
                    description=row["description"],
                    price=row["price"],
                    image=row["image"]
                )
            )

    db.session.commit()

print("Migration completed successfully!")
