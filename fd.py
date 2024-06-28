from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:9849@localhost/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
ma = Marshmallow(app)

# Define FarmDetail model and schema
class FarmDetail(db.Model):
    __tablename__ = 'farm_details'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    farm_name = db.Column(db.String(100), unique=True, nullable=False)
    farmer_name = db.Column(db.String(100))
    farmer_phone = db.Column(db.String(20))
    caretaker = db.Column(db.String(100))
    caretaker_phone = db.Column(db.String(20))
    location = db.Column(db.String(100))
    devices = db.Column(db.String(255))
    num_cows = db.Column(db.Integer)
    num_calves = db.Column(db.Integer)
    date = db.Column(db.Date)

    def __init__(self, farm_name, farmer_name=None, farmer_phone=None, caretaker=None, caretaker_phone=None,
                 location=None, devices=None, num_cows=None, num_calves=None, date=None):
        self.farm_name = farm_name
        self.farmer_name = farmer_name
        self.farmer_phone = farmer_phone
        self.caretaker = caretaker
        self.caretaker_phone = caretaker_phone
        self.location = location
        self.devices = devices
        self.num_cows = num_cows
        self.num_calves = num_calves
        self.date = date

class FarmDetailSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = FarmDetail
        load_instance = True
        include_relationships = True

farm_detail_schema = FarmDetailSchema()
farm_details_schema = FarmDetailSchema(many=True)

# Define MilkDetail model and schema
class MilkDetail(db.Model):
    __tablename__ = 'milk_details'
    id = db.Column(db.Integer, primary_key=True)
    farm_name = db.Column(db.String(100), nullable=False)
    milk_liters = db.Column(db.Numeric, nullable=False)
    snf = db.Column(db.Numeric, nullable=False)
    snf_status = db.Column(db.String(20), nullable=False)
    alcohol = db.Column(db.Numeric, nullable=False)
    alcohol_status = db.Column(db.String(20), nullable=False)
    antibiotic = db.Column(db.Numeric, nullable=False)
    antibiotic_status = db.Column(db.String(20), nullable=False)
    date = db.Column(db.Date, nullable=False)

    def __init__(self, farm_name, milk_liters, snf, snf_status, alcohol, alcohol_status, antibiotic, antibiotic_status, date):
        self.farm_name = farm_name
        self.milk_liters = milk_liters
        self.snf = snf
        self.snf_status = snf_status
        self.alcohol = alcohol
        self.alcohol_status = alcohol_status
        self.antibiotic = antibiotic
        self.antibiotic_status = antibiotic_status
        self.date = date

class MilkDetailSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MilkDetail
        load_instance = True
        include_relationships = True

milk_detail_schema = MilkDetailSchema()
milk_details_schema = MilkDetailSchema(many=True)

# Routes for FarmDetail

@app.route('/api/farm_details', methods=['GET'])
def get_all_farm_details():
    farm_details = FarmDetail.query.all()
    return jsonify(farm_details_schema.dump(farm_details))

@app.route('/api/farm_details/<int:id>', methods=['GET'])
def get_farm_detail(id):
    farm_detail = FarmDetail.query.get_or_404(id)
    return jsonify(farm_detail_schema.dump(farm_detail))

@app.route('/api/farm_details', methods=['POST'])
def add_farm_detail():
    data = request.json
    new_farm_detail = FarmDetail(
        farm_name=data['farm_name'],
        farmer_name=data.get('farmer_name', None),
        farmer_phone=data.get('farmer_phone', None),
        caretaker=data.get('caretaker', None),
        caretaker_phone=data.get('caretaker_phone', None),
        location=data.get('location', None),
        devices=data.get('devices', None),
        num_cows=data.get('num_cows', None),
        num_calves=data.get('num_calves', None),
        date=datetime.strptime(data['date'], '%Y-%m-%d').date()
    )
    db.session.add(new_farm_detail)
    db.session.commit()
    return jsonify({'message': 'Farm detail added successfully', 'id': new_farm_detail.id}), 201

@app.route('/api/farm_details/<int:id>', methods=['PUT'])
def update_farm_detail(id):
    farm_detail = FarmDetail.query.get_or_404(id)
    data = request.json
    farm_detail.farm_name = data.get('farm_name', farm_detail.farm_name)
    farm_detail.farmer_name = data.get('farmer_name', farm_detail.farmer_name)
    farm_detail.farmer_phone = data.get('farmer_phone', farm_detail.farmer_phone)
    farm_detail.caretaker = data.get('caretaker', farm_detail.caretaker)
    farm_detail.caretaker_phone = data.get('caretaker_phone', farm_detail.caretaker_phone)
    farm_detail.location = data.get('location', farm_detail.location)
    farm_detail.devices = data.get('devices', farm_detail.devices)
    farm_detail.num_cows = data.get('num_cows', farm_detail.num_cows)
    farm_detail.num_calves = data.get('num_calves', farm_detail.num_calves)
    farm_detail.date = datetime.strptime(data.get('date'), '%Y-%m-%d') if data.get('date') else farm_detail.date
    db.session.commit()
    return jsonify({'message': 'Farm detail updated successfully'})

@app.route('/api/farm_details/<int:id>', methods=['DELETE'])
def delete_farm_detail(id):
    farm_detail = FarmDetail.query.get_or_404(id)
    db.session.delete(farm_detail)
    db.session.commit()
    return jsonify({'message': 'Farm detail deleted successfully'})

# Routes for MilkDetail

@app.route('/api/milk_details', methods=['POST'])
def add_milk_detail():
    try:
        data = request.json
        required_fields = ['farm_name', 'milk_liters', 'snf', 'snf_status', 'alcohol', 'alcohol_status', 'antibiotic', 'antibiotic_status', 'date']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Check if farm name exists
        if not db.session.query(db.exists().where(FarmDetail.farm_name == data['farm_name'])).scalar():
            return jsonify({"error": f"Farm name '{data['farm_name']}' does not exist."}), 400

        # Convert date string to datetime object with the correct format
        date = datetime.strptime(data['date'], '%d/%m/%Y').date()  # Adjust format here

        new_milk_detail = MilkDetail(
            farm_name=data['farm_name'],
            milk_liters=data['milk_liters'],
            snf=data['snf'],
            snf_status=data['snf_status'],
            alcohol=data['alcohol'],
            alcohol_status=data['alcohol_status'],
            antibiotic=data['antibiotic'],
            antibiotic_status=data['antibiotic_status'],
            date=date
        )

        db.session.add(new_milk_detail)
        db.session.commit()

        return jsonify(milk_detail_schema.dump(new_milk_detail)), 201
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 400  # Handle date format errors
    
    except KeyError as e:
        return jsonify({"error": f"Missing JSON key: {str(e)}"}), 400  # Handle missing JSON keys
    
    except Exception as e:
        db.session.rollback()  # Rollback in case of any exception
        return jsonify({"error": str(e)}), 400


@app.route('/api/milk_details', methods=['GET'])
def get_all_milk_details():
    all_milk_details = MilkDetail.query.all()
    result = milk_details_schema.dump(all_milk_details)
    return jsonify(result)

@app.route('/api/milk_details/<int:id>', methods=['GET'])
def get_milk_detail(id):
    milk_detail = MilkDetail.query.get_or_404(id)
    return jsonify(milk_detail_schema.dump(milk_detail))

@app.route('/api/milk_details/<int:id>', methods=['PUT'])
def update_milk_detail(id):
    milk_detail = MilkDetail.query.get_or_404(id)
    try:
        data = request.json
        milk_detail.farm_name = data['farm_name']
        milk_detail.milk_liters = data['milk_liters']
        milk_detail.snf = data['snf']
        milk_detail.snf_status = data['snf_status']
        milk_detail.alcohol = data['alcohol']
        milk_detail.alcohol_status = data['alcohol_status']
        milk_detail.antibiotic = data['antibiotic']
        milk_detail.antibiotic_status = data['antibiotic_status']
        milk_detail.date = datetime.strptime(data['date'], '%d/%m/%Y').date()

        db.session.commit()
        return jsonify(milk_detail_schema.dump(milk_detail))
    except Exception as e:
        db.session.rollback()  # Rollback in case of any exception
        return jsonify({"error": str(e)}), 400

@app.route('/api/milk_details/<int:id>', methods=['DELETE'])
def delete_milk_detail(id):
    milk_detail = MilkDetail.query.get_or_404(id)
    db.session.delete(milk_detail)
    db.session.commit()
    return jsonify(milk_detail_schema.dump(milk_detail))

# Routes for Farms

@app.route('/api/farm_names', methods=['GET'])
def get_farm_names():
    farms = db.session.query(FarmDetail.farm_name).all()
    farm_names = [farm[0] for farm in farms]
    return jsonify(farm_names)

# Routes for SNFStatus

@app.route('/api/snf_statuses', methods=['GET'])
def get_snf_statuses():
    snf_statuses = db.session.query(MilkDetail.snf_status).distinct().all()
    statuses = [status[0] for status in snf_statuses]
    return jsonify(statuses)

# Routes for AlcoholStatus

@app.route('/api/alcohol_statuses', methods=['GET'])
def get_alcohol_statuses():
    alcohol_statuses = db.session.query(MilkDetail.alcohol_status).distinct().all()
    statuses = [status[0] for status in alcohol_statuses]
    return jsonify(statuses)

# Routes for AntibioticStatus

@app.route('/api/antibiotic_statuses', methods=['GET'])
def get_antibiotic_statuses():
    antibiotic_statuses = db.session.query(MilkDetail.antibiotic_status).distinct().all()
    statuses = [status[0] for status in antibiotic_statuses]
    return jsonify(statuses)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5005)
