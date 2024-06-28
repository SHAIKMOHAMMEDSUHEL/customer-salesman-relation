from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS

# Initialize Flask application
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:9849@localhost/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
ma = Marshmallow(app)
CORS(app)

# Define FarmDetail model
class FarmDetail(db.Model):
    __tablename__ = 'farm_details'
    id = db.Column(db.Integer, primary_key=True)
    farm_name = db.Column(db.String(100), unique=True, nullable=False)
    farmer_name = db.Column(db.String(100))
    farmer_phone = db.Column(db.String(20))
    caretaker = db.Column(db.String(100))
    caretaker_phone = db.Column(db.String(20))
    location = db.Column(db.String(100))
    devices = db.Column(db.Integer)
    num_cows = db.Column(db.Integer)
    num_calves = db.Column(db.Integer)
    date = db.Column(db.Date)

# Define FarmDetailSchema
class FarmDetailSchema(ma.SQLAlchemySchema):
    class Meta:
        model = FarmDetail
    id = ma.auto_field()
    farm_name = ma.auto_field()
    farmer_name = ma.auto_field()
    farmer_phone = ma.auto_field()
    caretaker = ma.auto_field()
    caretaker_phone = ma.auto_field()
    location = ma.auto_field()
    devices = ma.auto_field()
    num_cows = ma.auto_field()
    num_calves = ma.auto_field()
    date = ma.auto_field()

farm_detail_schema = FarmDetailSchema()
farm_details_schema = FarmDetailSchema(many=True)

# Define Payments model
class Payments(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True)
    farm_name = db.Column(db.String(100), db.ForeignKey('farm_details.farm_name'), nullable=False)
    liters_per_month = db.Column(db.Numeric)
    liters_returned = db.Column(db.Numeric)
    amount_per_liter = db.Column(db.Numeric)
    total_amount = db.Column(db.Numeric)
    status = db.Column(db.String(20))

# Define PaymentsSchema
class PaymentsSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Payments
    id = ma.auto_field()
    farm_name = ma.auto_field()
    liters_per_month = ma.auto_field()
    liters_returned = ma.auto_field()
    amount_per_liter = ma.auto_field()
    total_amount = ma.auto_field()
    status = ma.auto_field()

payments_schema = PaymentsSchema()
payments_schemas = PaymentsSchema(many=True)

# Ensure tables are created within the application context
with app.app_context():
    db.create_all()

# Endpoint to fetch payment status options
@app.route('/api/payment-status', methods=['GET'])
def get_payment_status_options():
    try:
        status_options = ['paid', 'pending']  # Assuming these are the status options
        return jsonify(status_options)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Route to create a new payment record
@app.route('/api/payments', methods=['POST'])
def add_payment():
    try:
        # Extract data from request JSON
        farm_name = request.json.get('farm_name')
        liters_per_month = request.json.get('liters_per_month')
        liters_returned = request.json.get('liters_returned')
        amount_per_liter = request.json.get('amount_per_liter')
        total_amount = request.json.get('total_amount')
        status = request.json.get('status')

        # Validate if all required fields are present
        if not farm_name or not liters_per_month or not liters_returned or not amount_per_liter or not total_amount or not status:
            return jsonify({"error": "All fields are required."}), 400

        # Check if farm_name exists in farm_details table
        farm_detail = FarmDetail.query.filter_by(farm_name=farm_name).first()

        if not farm_detail:
            return jsonify({"error": f"Farm name '{farm_name}' does not exist in farm_details table."}), 404

        # Create new payment instance
        new_payment = Payments(farm_name=farm_name,
                               liters_per_month=liters_per_month,
                               liters_returned=liters_returned,
                               amount_per_liter=amount_per_liter,
                               total_amount=total_amount,
                               status=status)

        # Add to database session and commit
        db.session.add(new_payment)
        db.session.commit()

        # Return the newly created payment as JSON response
        return payments_schema.jsonify(new_payment), 201

    except KeyError as e:
        return jsonify({"error": f"Missing JSON key: {str(e)}"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

# Route to get all payment details
@app.route('/api/payments', methods=['GET'])
def get_all_payments():
    try:
        all_payments = Payments.query.all()
        result = payments_schemas.dump(all_payments)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Route to get a single payment record by ID
@app.route('/api/payments/<int:id>', methods=['GET'])
def get_payment(id):
    try:
        payment = Payments.query.get_or_404(id)
        return payments_schema.jsonify(payment)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Route to update a payment record
@app.route('/api/payments/<int:id>', methods=['PUT'])
def update_payment(id):
    try:
        payment = Payments.query.get_or_404(id)

        payment.farm_name = request.json['farm_name']
        payment.liters_per_month = request.json['liters_per_month']
        payment.liters_returned = request.json['liters_returned']
        payment.amount_per_liter = request.json['amount_per_liter']
        payment.total_amount = request.json['total_amount']
        payment.status = request.json['status']

        db.session.commit()

        return payments_schema.jsonify(payment)

    except KeyError as e:
        return jsonify({"error": f"Missing JSON key: {str(e)}"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

# Route to delete a payment record
@app.route('/api/payments/<int:id>', methods=['DELETE'])
def delete_payment(id):
    try:
        payment = Payments.query.get_or_404(id)
        db.session.delete(payment)
        db.session.commit()

        return payments_schema.jsonify(payment)

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5001)