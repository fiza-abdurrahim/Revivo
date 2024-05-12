import base64
from flask import Flask, render_template, request,redirect, url_for
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/revivo_db'


db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

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

@app.route("/home")
def home():
    return render_template("home.html")

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
        return redirect(url_for("thank_you"))
    else:
        return render_template("lender_form.html")
    


@app.route("/lender_data")
def lender_data():
    lender_data = LenderForm.query.all()

    # Iterate through each LenderForm object to encode its image to base64
    for form_data in lender_data:
        form_data.image_base64 = base64.b64encode(form_data.image).decode('utf-8') if form_data.image else None

    return render_template("lender_data.html", lenders_data=lender_data)


# @app.route("/pagination/<int:page>")
# def pagination(page):
#     per_page = 10  # Number of items per page
#     paginated_data = LenderForm.query.paginate(page, per_page, False)
#     return render_template("paginated_cards.html", paginated_data=paginated_data)

# @app.route("/details/<int:id>")
# def details(id):
#     item = LenderForm.query.get_or_404(id)
#     return render_template("details.html", item=item)

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
        
        return redirect(url_for("thank_you"))
    else:
        return render_template("contact.html")

@app.route("/thank_you")
def thank_you():
    return "<h1>Thank you for your message!</h1>"


if __name__== "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", debug=True)