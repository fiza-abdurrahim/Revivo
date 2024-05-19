import base64
import datetime
import hmac
import hashlib
from werkzeug.security import check_password_hash, generate_password_hash
from flask import Flask, render_template, request,redirect, url_for, flash, get_flashed_messages, abort, session
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/revivo_db'
app.config['SECRET_KEY'] = 'Fiza_Ashfaq_09'


# Configuration
JAZZCASH_MERCHANT_ID = "<JAZZCASH_MERCHANT_ID>"
JAZZCASH_PASSWORD = "<JAZZCASH_PASSWORD>"
JAZZCASH_RETURN_URL = "<JAZZCASH_RETURN_URL>"
JAZZCASH_INTEGRITY_SALT = "<JAZZCASH_INTEGRITY_SALT>"

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(254), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)


# model to create table in database
class LenderForm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(100), nullable=False)
    lname = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(10), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    lender_city = db.Column(db.String(100), nullable=False)
    Dres_type = db.Column(db.String(100), nullable=False)
    other_lender_city = db.Column(db.String(100), nullable=True)
    price_of_a_dress = db.Column(db.Integer, nullable=True)
    Brand = db.Column(db.String(100), nullable=True)
    Size = db.Column(db.String(100), nullable=True)
    date_of_purchase = db.Column(db.Date, nullable=True)
    dress_info = db.Column(db.Text, nullable=True)
    image = db.Column(db.LargeBinary, nullable=True)


class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)

@app.route("/")
def index():
    return render_template('home.html')

#login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('/auth/Login.html')


# logout route
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))

#Sign Up route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email address already exists', 'danger')
            return redirect(url_for('signup'))

        # Create new user
        new_user = User(username=username, email=email, password=generate_password_hash(password, method='pbkdf2:sha256'))
        db.session.add(new_user)
        db.session.commit()
        
        # flash('Account created successfully', 'success')
        return redirect(url_for('login'))

    return render_template('/auth/SignUp.html')

# Payment route
@app.route('/checkout')
def checkout():
    product_id = request.args.get('product_id')
    product_name = request.args.get('product_name')
    product_price = request.args.get('product_price')
    # print(product_price, product_name)
    
    if product_price is None:
        return "Product price not provided", 400

    try:
        pp_Amount = int(float(product_price) * 100)  # Convert to paisas (1 PKR = 100 paisas)
    except ValueError:
        return "Invalid product price", 400

    current_datetime = datetime.datetime.now()
    pp_TxnDateTime = current_datetime.strftime('%Y%m%d%H%M%S')
    expiry_datetime = current_datetime + datetime.timedelta(hours=1)
    pp_TxnExpiryDateTime = expiry_datetime.strftime('%Y%m%d%H%M%S')
    pp_TxnRefNo = 'T' + pp_TxnDateTime

    post_data = {
        "pp_Version": "1.0",
        "pp_TxnType": "",
        "pp_Language": "EN",
        "pp_MerchantID": JAZZCASH_MERCHANT_ID,
        "pp_SubMerchantID": "",
        "pp_Password": JAZZCASH_PASSWORD,
        "pp_BankID": "TBANK",
        "pp_ProductID": "RETL",
        "pp_TxnRefNo": pp_TxnRefNo,
        "pp_Amount": pp_Amount,
        "pp_TxnCurrency": "PKR",
        "pp_TxnDateTime": pp_TxnDateTime,
        "pp_BillReference": "billRef",
        "pp_Description": "Description of transaction",
        "pp_TxnExpiryDateTime": pp_TxnExpiryDateTime,
        "pp_ReturnURL": JAZZCASH_RETURN_URL,
        "pp_SecureHash": "",
        "ppmpf_1": "1",
        "ppmpf_2": "2",
        "ppmpf_3": "3",
        "ppmpf_4": "4",
        "ppmpf_5": "5"
    }

    sorted_string = '&'.join(f"{key}={value}" for key, value in sorted(post_data.items()) if value != "")
    pp_SecureHash = hmac.new(
        JAZZCASH_INTEGRITY_SALT.encode(),
        sorted_string.encode(),
        hashlib.sha256
    ).hexdigest()
    post_data['pp_SecureHash'] = pp_SecureHash

    return render_template('checkout.html', product_name=product_name, product_price=product_price, post_data=post_data)

@app.route("/home")
def home():
    username = session.get('username')
    return render_template("home.html", username=username)


@app.route("/renting_process")
def renting_process():
    return render_template("renting_process.html")

@app.route("/lender_form", methods=["GET","POST"])
def lender_form():
    if request.method == "POST":
        # Retrieve form data
        fname = request.form.get("fname")
        lname = request.form.get("lname")
        phone = request.form.get("phone")
        email = request.form.get("email")
        lender_city = request.form.get("lender_city")
        Dres_type = request.form.get("Dres_type")
        other_lender_city = request.form.get("other_lender_city")
        price_of_a_dress = request.form.get("price_of_a_dress")
        Brand = request.form.get("Brand")
        Size = request.form.get("Size")
        date_of_purchase = request.form.get("date_of_purchase")
        dress_info = request.form.get("dress_info")
        image = request.files['image'].read()
        
        # Create a LenderForm object
        form_data = LenderForm(
            fname=fname,
            lname=lname,
            phone=phone,
            email=email,
            lender_city=lender_city,
            Dres_type=Dres_type,
            other_lender_city=other_lender_city,
            price_of_a_dress=price_of_a_dress,
            Brand=Brand,
            Size=Size,
            date_of_purchase=date_of_purchase,
            dress_info=dress_info,
            image=image
        )
        
        # Add the LenderForm object to the database session
        db.session.add(form_data)

        # Commit the changes to the database
        db.session.commit()

        # Redirect to a thank you page or home page
        # return redirect(url_for("thank_you"))
        flash('Your Data has been successully inserted.')
        return render_template("lender_form.html")
    else:
        return render_template("lender_form.html")
    


@app.route("/lender_data")
def lender_data():
    lender_data = LenderForm.query.all()

    # Iterate through each LenderForm object to encode its image to base64
    for form_data in lender_data:
        form_data.image_base64 = base64.b64encode(form_data.image).decode('utf-8') if form_data.image else None

    return render_template("lender_data.html", lenders_data=lender_data)


@app.route("/mahndi_dresses")
def mahndi_dresses():
    # Query the database to fetch dresses with type "Mahndi"
    mahndi_dresses = LenderForm.query.filter_by(Dres_type="Mahndi").all()
    
    # Iterate through each dress object to encode its image to base64
    for dress in mahndi_dresses:
        dress.image_base64 = base64.b64encode(dress.image).decode('utf-8') if dress.image else None
    
    return render_template("mahndi_dresses.html", mahndi_dresses=mahndi_dresses)

@app.route("/valima_dresses")
def valima_dresses():
    # Query the database to fetch dresses with type "Valima"
    valima_dresses = LenderForm.query.filter_by(Dres_type="Valima").all()
    
    # Iterate through each dress object to encode its image to base64
    for dress in valima_dresses:
        dress.image_base64 = base64.b64encode(dress.image).decode('utf-8') if dress.image else None
    
    return render_template("valima_dresses.html", valima_dresses=valima_dresses)
@app.route("/nikkah_dresses")
def nikkah_dresses():
    # Query the database to fetch dresses with type "Nikkah"
    nikkah_dresses = LenderForm.query.filter_by(Dres_type="Nikkah").all()
    
    # Iterate through each dress object to encode its image to base64
    for dress in nikkah_dresses:
        dress.image_base64 = base64.b64encode(dress.image).decode('utf-8') if dress.image else None
    
    return render_template("Nikkah.html", Nikkah_dresses=nikkah_dresses)

@app.route("/baraat_dresses")
def baraat_dresses():
    # Query the database to fetch dresses with type "Baraat"
    baraat_dresses = LenderForm.query.filter_by(Dres_type="Baraat").all()
    
    # Iterate through each dress object to encode its image to base64
    for dress in baraat_dresses:
        dress.image_base64 = base64.b64encode(dress.image).decode('utf-8') if dress.image else None
    
    return render_template("Baraat_dresses.html", Baraat_dresses=baraat_dresses)

# formal routes
@app.route("/sarees")
def sarees():
    Sarees_dress=LenderForm.query.filter_by(Dres_type="Saree").all()
    for dress in Sarees_dress:
        dress.image_base64=base64.b64encode(dress.image).decode('utf-8') if dress.image else None   
    return render_template('sarees.html', Sarees_dress=Sarees_dress)

@app.route("/lehnga")
def lehnga():
    lehnga_dreses= LenderForm.query.filter_by(Dres_type="Lehnga").all()
    for dress in lehnga_dreses:
        dress.image_base64=base64.b64encode(dress.image).decode('utf-8') if dress.image else None   
    return render_template('Lehnga.html', Lehnga_dresses=lehnga_dreses)
@app.route("/gharas")
def gharas():
     # Query the database to fetch dresses with type "Gharas"
    gharas_dresses = LenderForm.query.filter_by(Dres_type="Gharas").all()
    
    # Iterate through each dress object to encode its image to base64
    for dress in gharas_dresses:
        dress.image_base64 = base64.b64encode(dress.image).decode('utf-8') if dress.image else None
    return render_template('gharas.html', Gharas_dresses=gharas_dresses)
@app.route("/other_dresses")
def other_dresses():
    # Query the database to fetch dresses with type "Baraat"
    other_dresses = LenderForm.query.filter_by(Dres_type="Other").all()
    
    # Iterate through each dress object to encode its image to base64
    for dress in other_dresses:
        dress.image_base64 = base64.b64encode(dress.image).decode('utf-8') if dress.image else None
    return render_template('other_dresses.html', Other_dresses=other_dresses)

# dress details route
@app.route("/dress_details/<int:dress_id>")
def dress_details(dress_id):
    # Query the database to fetch the dress with the given dress_id
    dress = LenderForm.query.get(dress_id)

    if not dress:
        abort(404)  # Handle if dress_id does not exist

    # Encode dress image to base64 if it exists
    image_base64 = base64.b64encode(dress.image).decode('utf-8') if dress.image else None

    return render_template("dress_details.html", dress=dress, image_base64=image_base64)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        
        # Retrieve form data
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")
        feedback = Feedback(name=name, email=email, message=message)
        
        # Add the Feedback object to the database session
        db.session.add(feedback)
        
        # Commit the changes to the database
        db.session.commit()
        
        # return redirect(url_for("thank_you"))
        flash('Thanks for your message')
        return render_template("contact.html")
    else:
        return render_template("contact.html")




if __name__== "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", debug=True)