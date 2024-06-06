import base64
import streamlit as st
from pymongo import MongoClient
from bson.objectid import ObjectId
import pandas as pd
from werkzeug.security import generate_password_hash, check_password_hash
from db_utils import get_database, add_menu_item, get_all_menu_items, update_menu_item, delete_menu_item, \
                     add_reservation, get_all_reservations, update_reservation, delete_reservation, \
                     add_order, get_all_orders, update_order, delete_order, \
                     add_staff, get_all_staff, update_staff, delete_staff, \
                     add_user, authenticate_user

st.set_page_config(layout="wide")


hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# MongoDB connection
db = get_database()

# Background setup
def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_background(png_file):
    bin_str = get_base64(png_file)
    page_bg_img = '''
    <style>
    .stApp {
    background-image: linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.5)),url('data:image/png;base64,%s');
    background-size: cover;
    }
    </style>
    ''' % bin_str
    st.markdown(page_bg_img, unsafe_allow_html=True)

set_background('background.jpg')

# Authentication
def login():
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if authenticate_user(db, username, password):
            st.session_state['logged_in'] = True
            st.session_state['username'] = username
            st.success("Logged in successfully!")
            st.rerun()
        else:
            st.error("Invalid username or password")

def signup():
    st.subheader("Sign Up")
    username = st.text_input("Choose a Username")
    password = st.text_input("Choose a Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    if st.button("Sign Up"):
        if password != confirm_password:
            st.error("Passwords do not match")
        else:
            add_user(db, username, password)
            st.success("Account created successfully! Please log in.")
            st.rerun()

# Main app
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    auth_mode = st.sidebar.selectbox("Select Mode", ["Login", "Sign Up"])
    if auth_mode == "Login":
        login()
    else:
        signup()
else:
    st.title("SHETTY's CAFE")

    # Sidebar menu
    menu = ["Home", "About Us", "Manage Menu", "Manage Reservations", "Manage Orders", "Manage Staff", "Logout"]
    selected_option = st.sidebar.radio("Menu", menu)

    if selected_option == "Logout":
        st.session_state['logged_in'] = False
        st.experimental_rerun()

    elif selected_option == "Home":
        st.subheader("Home")
        st.write("""
                 Welcome to Shetty's Cafe!!

    At Shetty's Cafe, we understand that managing a restaurant is more than just serving delicious food—it's about creating unforgettable experiences for your customers while streamlining operations to maximize efficiency and profitability. Our state-of-the-art restaurant management system is designed to simplify your day-to-day tasks, allowing you to focus on what truly matters: delighting your guests.

    With features tailored to meet the unique needs of your establishment, our comprehensive platform offers:

    - *Intuitive Order Management:* Seamlessly handle orders from multiple channels—dine-in, takeout, and delivery—with real-time updates and efficient processing.
    - *Inventory Control:* Keep track of stock levels, manage suppliers, and reduce waste.
    - *Staff Scheduling:* Optimize your workforce with smart scheduling, shift management, and time tracking to ensure peak performance during busy hours.
    - *Customer Relationship Management:* Build lasting relationships with your customers through personalized promotions, loyalty programs, and feedback collection.
    - *Sales Analytics:* Gain valuable insights into your restaurant's performance with detailed reports and analytics to make data-driven decisions.

    Join countless satisfied restaurant owners who have transformed their operations with [Your Restaurant Name] Management System. Explore our features, and discover how we can help you elevate your restaurant to new heights of success.

    Ready to streamline your restaurant operations and enhance your customer experience? Sign up for a free demo today!
                 """)

        # Dashboard
        st.subheader("Dashboard")
        menu_count = db.menu.count_documents({})
        reservations_count = db.reservations.count_documents({})
        orders_count = db.orders.count_documents({})
        staff_count = db.staff.count_documents({})

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Menu Items", menu_count)
        with col2:
            st.metric("Total Reservations", reservations_count)
        with col3:
            st.metric("Total Orders", orders_count)
        with col4:
            st.metric("Total Staff", staff_count)

    elif selected_option == "About Us":
        st.subheader("About Us")
        st.write("""
        Our Story

        Established in 2020, our restaurant has been dedicated to providing exceptional culinary experiences. Our chefs use the finest ingredients to create mouth-watering dishes that satisfy all taste buds.

        Our Vision

        To be a leading restaurant known for quality, service, and innovation.

        Our Mission

        To provide a memorable dining experience through exceptional service, delicious food, and a welcoming atmosphere.

        Our Values

        - Quality: We never compromise on the quality of our ingredients.
        - Customer Satisfaction: Our customers' happiness is our top priority.
        - Integrity: We operate with honesty and transparency in everything we do.

        Thank you for choosing us. We look forward to serving you!
        """)

    elif selected_option == "Manage Menu":
        st.subheader("Manage Menu")

        tab1, tab2, tab3 = st.tabs(["Add Menu Item", "View Menu", "Update/Delete Menu Item"])

        with tab1:
            st.subheader("Add New Menu Item")
            name = st.text_input("Menu Item Name")
            price = st.number_input("Price", min_value=0.0, format="%.2f")

            if st.button("Add Item"):
                if name and price:
                    add_menu_item(db, name, price)
                    st.success(f"Added {name} to menu!")
                else:
                    st.error("Please fill in all fields.")

        with tab2:
            st.subheader("View Menu")
            menu_items = get_all_menu_items(db)

            for item in menu_items:
                st.write(f"{item['name']}")
                st.write(f"Price: ${item['price']:.2f}")
                st.write("---")

        with tab3:
            st.subheader("Update/Delete Menu Item")
            menu_items = get_all_menu_items(db)
            menu_item_list = [(item['name'], item['_id']) for item in menu_items]

            selected_item = st.selectbox("Select Menu Item", menu_item_list, format_func=lambda x: x[0])

            if selected_item:
                item = db.menu.find_one({"_id": ObjectId(selected_item[1])})
                new_name = st.text_input("Menu Item Name", value=item['name'])
                new_price = st.number_input("Price", min_value=0.0, format="%.2f", value=item['price'])

                if st.button("Update Item"):
                    update_menu_item(db, selected_item[1], new_name, new_price)
                    st.success("Menu item updated!")

                if st.button("Delete Item"):
                    delete_menu_item(db, selected_item[1])
                    st.success("Menu item deleted!")

    elif selected_option == "Manage Reservations":
        st.subheader("Manage Reservations")

        tab1, tab2, tab3 = st.tabs(["Make a Reservation", "View Reservations", "Update/Delete Reservation"])

        with tab1:
            st.subheader("Make a Reservation")
            name = st.text_input("Your Name")
            date = st.date_input("Reservation Date")
            time = st.time_input("Reservation Time")
            party_size = st.number_input("Party Size", min_value=1)

            if st.button("Book Reservation"):
                if name and date and time and party_size:
                    add_reservation(db, name, date, time, party_size)
                    st.success("Reservation made successfully!")
                else:
                    st.error("Please fill in all fields.")

        with tab2:
            st.subheader("View Reservations")
            reservations = get_all_reservations(db)

            for res in reservations:
                st.write(f"Name: {res['name']}")
                st.write(f"Date: {res['date']}")
                st.write(f"Time: {res['time']}")
                st.write(f"Party Size: {res['party_size']}")
                st.write("---")

        with tab3:
            st.subheader("Update/Delete Reservation")
            reservations = get_all_reservations(db)
            reservation_list = [(res['name'], res['_id']) for res in reservations]

            selected_reservation = st.selectbox("Select Reservation", reservation_list, format_func=lambda x: x[0])

            if selected_reservation:
                res = db.reservations.find_one({"_id": ObjectId(selected_reservation[1])})
                new_name = st.text_input("Your Name", value=res['name'])
                new_date = st.date_input("Reservation Date", value=pd.to_datetime(res['date']))
                new_time = st.time_input("Reservation Time", value=pd.to_datetime(res['time']).time())
                new_party_size = st.number_input("Party Size", min_value=1, value=res['party_size'])

                if st.button("Update Reservation"):
                    update_reservation(db, selected_reservation[1], new_name, new_date, new_time, new_party_size)
                    st.success("Reservation updated!")

                if st.button("Delete Reservation"):
                    delete_reservation(db, selected_reservation[1])
                    st.success("Reservation deleted!")

    elif selected_option == "Manage Orders":
        st.subheader("Manage Orders")

        tab1, tab2, tab3 = st.tabs(["Add Order", "View Orders", "Update/Delete Order"])

        with tab1:
            st.subheader("Add New Order")
            customer_name = st.text_input("Customer Name")
            date = st.date_input("Order Date")
            items = st.text_area("Items (format: item1: quantity, item2: quantity)")

            if st.button("Add Order"):
                if customer_name and date and items:
                    add_order(db, customer_name, date, items)
                    st.success(f"Added order for {customer_name}!")
                else:
                    st.error("Please fill in all fields.")

        with tab2:
            st.subheader("View Orders")
            orders = get_all_orders(db)

            for order in orders:
                st.write(f"Customer: {order['customer_name']}")
                st.write(f"Date: {order['date']}")
                st.write("Items:")
                for item in order['items']:
                    st.write(f" - {item['name']}: {item['quantity']}")
                st.write("---")

        with tab3:
            st.subheader("Update/Delete Order")
            orders = get_all_orders(db)
            order_list = [(order['customer_name'], order['_id']) for order in orders]

            selected_order = st.selectbox("Select Order", order_list, format_func=lambda x: x[0])

            if selected_order:
                order = db.orders.find_one({"_id": ObjectId(selected_order[1])})
                new_customer_name = st.text_input("Customer Name", value=order['customer_name'])
                new_date = st.date_input("Order Date", value=pd.to_datetime(order['date']))
                new_items = st.text_area("Items (format: item1: quantity, item2: quantity)", value=", ".join([f"{item['name']}: {item['quantity']}" for item in order['items']]))

                if st.button("Update Order"):
                    update_order(db, selected_order[1], new_customer_name, new_date, new_items)
                    st.success("Order updated!")

                if st.button("Delete Order"):
                    delete_order(db, selected_order[1])
                    st.success("Order deleted!")

    elif selected_option == "Manage Staff":
        st.subheader("Manage Staff")

        tab1, tab2, tab3 = st.tabs(["Add Staff", "View Staff", "Update/Delete Staff"])

        with tab1:
            st.subheader("Add New Staff Member")
            name = st.text_input("Name")
            positions = ["Manager", "Chef", "Waiter", "Cashier", "Cleaner", "Host", "Bartender"]
            position = st.selectbox("Position",positions)
            contact = st.text_input("Contact")

            if st.button("Add Staff Member"):
                if name and position and contact:
                    add_staff(db, name, position, contact)
                    st.success(f"Added staff member {name}!")
                else:
                    st.error("Please fill in all fields.")

        with tab2:
            st.subheader("View Staff")
            staff = get_all_staff(db)

            for member in staff:
                st.write(f"Name: {member['name']}")
                st.write(f"Position: {member['position']}")
                st.write(f"Contact: {member['contact']}")
                st.write("---")

        with tab3:
            st.subheader("Update/Delete Staff Member")
            staff = get_all_staff(db)
            staff_list = [(member['name'], member['_id']) for member in staff]

            selected_staff = st.selectbox("Select Staff Member", staff_list, format_func=lambda x: x[0])

            if selected_staff:
                member = db.staff.find_one({"_id": ObjectId(selected_staff[1])})
                new_name = st.text_input("Name", value=member['name'])
                positions = ["Manager", "Chef", "Waiter", "Cashier", "Cleaner", "Host", "Bartender"]
                new_position = st.selectbox("Position", positions, index=positions.index(member['position']))
                new_contact = st.text_input("Contact", value=member['contact'])

                if st.button("Update Staff Member"):
                    update_staff(db, selected_staff[1], new_name, new_position, new_contact)
                    st.success("Staff member updated!")

                if st.button("Delete Staff Member"):
                    delete_staff(db, selected_staff[1])
                    st.success("Staff member deleted!")