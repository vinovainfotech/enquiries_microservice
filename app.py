from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
print("this is app.py")
# Configure PostgreSQL (NeonDB)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://neondb_owner:npg_AgyBXn35pVuL@ep-rough-violet-a1ugvcux-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Define model
class Enquiry(db.Model):
    __tablename__ = 'enquiries'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone_no = db.Column(db.String(20), nullable=False)
    client_name = db.Column(db.String(300), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)

@app.route('/')
def index():
    return "this is app.py"

# POST: Add new enquiry
@app.route('/api/enquire', methods=['POST'])
def enquire():
    data = request.get_json()
    try:
        new_enquiry = Enquiry(
            name=data['name'],
            phone_no=data['phone_no'],
            client_name=data['client_name'],
            email=data['email'],
            message=data['message']
        )
        db.session.add(new_enquiry)
        db.session.commit()
        return jsonify({"message": "Enquiry submitted successfully."}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
# Updated User model
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(300), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    email_provider = db.Column(db.String(50))



# Signup API
@app.route('/api/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        pwd = generate_password_hash(data.get('password'))
        is_admin = data.get('is_admin', False)

        provider = email.split('@')[1].split('.')[0] if email else None

        if User.query.filter_by(email=email).first():
            return jsonify({"message": "User already exists."}), 409
        print(pwd)
        new_user = User(
            name=name,
            email=email,
            password= pwd,
            is_admin=is_admin,
            email_provider=provider
        )
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": "User registered successfully."}), 201

    except Exception as e:
        print("Signup Error:", str(e))
        return jsonify({"error": "Something went wrong", "details": str(e)}), 500


#Login API
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()

    try:
        email = data['email']
        password = data['password']

        user = User.query.filter_by(email=email).first()

        if not user:
            return jsonify({"message": "User not found."}), 404

        if not check_password_hash(user.password, password):
            return jsonify({"message": "Incorrect password."}), 401

        return jsonify({
            "message": "Login successful.",
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "is_admin": user.is_admin
            }
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
    
# # GET: Fetch all enquiries
# @app.route('/api/enquiries', methods=['GET'])
# def get_all_enquiries():
#     enquiries = Enquiry.query.all()
#     result = [
#         {
#             "id": e.id,
#             "name": e.name,
#             "phone_no": e.phone_no,
#             "client_name": e.client_name,
#             "email": e.email,
#             "message": e.message
#         }
#         for e in enquiries
#     ]
#     return jsonify(result), 200

# # GET: Fetch single enquiry by ID
# @app.route('/api/enquiries/<int:id>', methods=['GET'])
# def get_enquiry_by_id(id):
#     enquiry = Enquiry.query.get_or_404(id)
#     return jsonify({
#         "id": enquiry.id,
#         "name": enquiry.name,
#         "phone_no": enquiry.phone_no,
#         "client_name": enquiry.client_name,
#         "email": enquiry.email,
#         "message": enquiry.message
#     })

# # PUT: Update enquiry by ID
# @app.route('/api/enquiries/<int:id>', methods=['PUT'])
# def update_enquiry(id):
#     enquiry = Enquiry.query.get_or_404(id)
#     data = request.get_json()
#     try:
#         enquiry.name = data.get('name', enquiry.name)
#         enquiry.phone_no = data.get('phone_no', enquiry.phone_no)
#         enquiry.client_name = data.get('client_name', enquiry.client_name)
#         enquiry.email = data.get('email', enquiry.email)
#         enquiry.message = data.get('message', enquiry.message)
#         db.session.commit()
#         return jsonify({"message": "Enquiry updated successfully."})
#     except Exception as e:
#         return jsonify({"error": str(e)}), 400

# # DELETE: Delete enquiry by ID
# @app.route('/api/enquiries/<int:id>', methods=['DELETE'])
# def delete_enquiry(id):
#     enquiry = Enquiry.query.get_or_404(id)
#     db.session.delete(enquiry)
#     db.session.commit()
#     return jsonify({"message": "Enquiry deleted successfully."})

if __name__ == '__main__':
    app.run(debug=True)
