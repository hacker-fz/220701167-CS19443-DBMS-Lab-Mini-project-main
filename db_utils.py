from pymongo import MongoClient
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

def get_database():
    CONNECTION_STRING = "mongodb://localhost:27017/"
    client = MongoClient(CONNECTION_STRING)
    return client['restaurant_db']

# Menu operations
def add_menu_item(db, name, price):
    menu_item = {"name": name, "price": price}
    db.menu.insert_one(menu_item)

def get_all_menu_items(db):
    return list(db.menu.find())

def update_menu_item(db, item_id, new_name, new_price):
    db.menu.update_one(
        {"_id": ObjectId(item_id)},
        {"$set": {"name": new_name, "price": new_price}}
    )

def delete_menu_item(db, item_id):
    db.menu.delete_one({"_id": ObjectId(item_id)})

# Reservation operations
def add_reservation(db, name, date, time, party_size):
    reservation = {
        "name": name,
        "date": date.strftime("%Y-%m-%d"),
        "time": time.strftime("%H:%M"),
        "party_size": party_size
    }
    db.reservations.insert_one(reservation)

def get_all_reservations(db):
    return list(db.reservations.find())

def update_reservation(db, reservation_id, new_name, new_date, new_time, new_party_size):
    db.reservations.update_one(
        {"_id": ObjectId(reservation_id)},
        {"$set": {"name": new_name, "date": new_date.strftime("%Y-%m-%d"), "time": new_time.strftime("%H:%M"), "party_size": new_party_size}}
    )

def delete_reservation(db, reservation_id):
    db.reservations.delete_one({"_id": ObjectId(reservation_id)})

# Order operations
def add_order(db, customer_name, date, items):
    items_list = [{"name": item.split(":")[0].strip(), "quantity": int(item.split(":")[1].strip())} for item in items.split(",")]
    order = {
        "customer_name": customer_name,
        "date": date.strftime("%Y-%m-%d"),
        "items": items_list
    }
    db.orders.insert_one(order)

def get_all_orders(db):
    return list(db.orders.find())

def update_order(db, order_id, new_customer_name, new_date, new_items):
    new_items_list = [{"name": item.split(":")[0].strip(), "quantity": int(item.split(":")[1].strip())} for item in new_items.split(",")]
    db.orders.update_one(
        {"_id": ObjectId(order_id)},
        {"$set": {"customer_name": new_customer_name, "date": new_date.strftime("%Y-%m-%d"), "items": new_items_list}}
    )

def delete_order(db, order_id):
    db.orders.delete_one({"_id": ObjectId(order_id)})

# Staff operations
def add_staff(db, name, position, contact):
    staff_member = {"name": name, "position": position, "contact": contact}
    db.staff.insert_one(staff_member)

def get_all_staff(db):
    return list(db.staff.find())

def update_staff(db, staff_id, new_name, new_position, new_contact):
    db.staff.update_one(
        {"_id": ObjectId(staff_id)},
        {"$set": {"name": new_name, "position": new_position, "contact": new_contact}}
    )

def delete_staff(db, staff_id):
    db.staff.delete_one({"_id": ObjectId(staff_id)})

# User authentication operations
def add_user(db, username, password):
    hashed_password = generate_password_hash(password)
    db.users.insert_one({"username": username, "password": hashed_password})

def authenticate_user(db, username, password):
    user = db.users.find_one({"username": username})
    if user and check_password_hash(user['password'], password):
        return True
    return False