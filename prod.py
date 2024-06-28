from flask import Flask, jsonify, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:9849@localhost/postgres'
db = SQLAlchemy(app)

# Enable CORS for the entire application
CORS(app)

# Define the ProductsDispatched model
class ProductsDispatched(db.Model):
    __tablename__ = 'products_dispatched'
    id = db.Column(db.Integer, primary_key=True)
    milk = db.Column(db.Integer)
    curd = db.Column(db.Integer)
    paneer = db.Column(db.Integer)
    butter = db.Column(db.Integer)
    ghee = db.Column(db.Integer)
    honey = db.Column(db.Integer)
    cheese = db.Column(db.Integer)
    date = db.Column(db.Date)

# Route to create a new products dispatched record        
@app.route('/api/products_dispatched', methods=['POST'])
def add_products_dispatched():
    data = request.json
    new_record = ProductsDispatched(
        milk=data.get('milk'),
        curd=data.get('curd'),
        paneer=data.get('paneer'),
        butter=data.get('butter'),
        ghee=data.get('ghee'),
        honey=data.get('honey'),
        cheese=data.get('cheese'),
        date=datetime.now().date()  # Store only the date
    )
    db.session.add(new_record)
    db.session.commit()  
    return jsonify({'message': 'Products dispatched record created successfully'}), 201

# Route to get all products dispatched records
@app.route('/api/products_dispatched', methods=['GET'])
def get_all_products_dispatched():
    all_records = ProductsDispatched.query.all()
    result = [{
        'id': record.id,
        'milk': record.milk,
        'curd': record.curd,
        'paneer': record.paneer,
        'butter': record.butter,
        'ghee': record.ghee,
        'honey': record.honey,
        'cheese': record.cheese,
        'date': record.date.strftime('%Y-%m-%d')
    } for record in all_records]
    return jsonify(result)

# Route to get a single products dispatched record by ID
@app.route('/api/products_dispatched/<int:id>', methods=['GET'])
def get_products_dispatched(id):
    record = ProductsDispatched.query.get_or_404(id)
    result = {
        'id': record.id,
        'milk': record.milk,
        'curd': record.curd,
        'paneer': record.paneer,
        'butter': record.butter,
        'ghee': record.ghee,
        'honey': record.honey,
        'cheese': record.cheese,
        'date': record.date.strftime('%Y-%m-%d')
    }
    return jsonify(result)

# Route to update a products dispatched record
@app.route('/api/products_dispatched/<int:id>', methods=['PUT'])
def update_products_dispatched(id):
    record = ProductsDispatched.query.get_or_404(id)
    data = request.json
    record.milk = data.get('milk', record.milk)
    record.curd = data.get('curd', record.curd)
    record.paneer = data.get('paneer', record.paneer)
    record.butter = data.get('butter', record.butter)
    record.ghee = data.get('ghee', record.ghee)
    record.honey = data.get('honey', record.honey)
    record.cheese = data.get('cheese', record.cheese)
    record.date = datetime.now().date()  # Update to store only the date
    db.session.commit()
    return jsonify({'message': 'Products dispatched record updated successfully'})

# Route to delete a products dispatched record
@app.route('/api/products_dispatched/<int:id>', methods=['DELETE'])
def delete_products_dispatched(id):
    record = ProductsDispatched.query.get_or_404(id)
    db.session.delete(record)
    db.session.commit()
    return jsonify({'message': 'Products dispatched record deleted successfully'})

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5004)