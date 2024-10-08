from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields, validate
from marshmallow import ValidationError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:%40Deblin312145@localhost/members_db'
db = SQLAlchemy(app)
ma = Marshmallow(app)

# Set up for schema of members table
class MembersSchema(ma.Schema):
    name = fields.String(required=True)
    age = fields.Integer(required=True)
    
    class Meta:
        fields = ("name", "id", "age")

customer_schema = MembersSchema()
customers_schema = MembersSchema(many=True)

# Set up for schema of sessions table
class WorkoutSessionsSchema(ma.Schema):
    member_id = fields.Integer(required=True)
    session_date = fields.Date(required=True)
    session_time = fields.String(required=True)
    activity = fields.String(required=True)

    class Meta:
        fields = ("session_id", "member_id", "session_date", "session_time", "activity")

workout_schema = WorkoutSessionsSchema()
workouts_schema = WorkoutSessionsSchema(many=True)


class Member(db.Model):
    # Define fields...
    __tablename__ = 'members'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    workout_sessions = db.relationship('WorkoutSession', backref='members')

class WorkoutSession(db.Model):
    # Define fields...
    __tablename__ = 'workoutsessions'
    session_id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'))
    session_date = db.Column(db.Date, nullable=False)
    session_time = db.Column(db.String(50), nullable=False)
    activity = db.Column(db.String(255), nullable=False)

class MemberAccount(db.Model):
    __tablename__ = "Member_Accounts"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('members.id'))
    member = db.relationship("Member", backref='member_account', uselist=False)

# CRUD Operations
@app.route('/', methods=['GET'])
def get_members():
    members = Member.query.all()
    return customer_schema.jsonify(members)

@app.route('/members', methods=['POST'])
def add_member():
    try:
        member_data = customer_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    new_member = Member(id=member_data['id'], name=member_data['name'], age=member_data['age'])
    db.session.add(new_member)
    db.session.commit()
    return jsonify({"Message": "New member added successfully"}), 201

@app.route('/members/<int:id>', methods=['PUT'])
def update_member(id):
    member = Member.query.get_or_404(id)
    try:
        member_data = customer_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    member.name = member_data['name']
    member.age = member_data['age']
    db.session.commit()
    return jsonify({"message": "Member details updated successfully"}), 200

@app.route('/members/<int:id>', methods=['DELETE'])
def delete_member(id):
    member = Member.query.get_or_404(id)
    db.session.delete(member)
    db.session.commit()
    return jsonify({"message": "Member removed successfully"}), 200

@app.route('/workoutsessions', methods=['GET'])
def get_workout_sessions():
    workout_sessions = WorkoutSession.query.all()
    return workouts_schema.jsonify(workout_sessions)

@app.route('/workoutsessions/add', methods=['POST'])
def add_session():
    try:
        workout_session_data = workout_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    new_session = WorkoutSession(workout_session_data["member_id"], workout_session_data['session_date'], workout_session_data['session_time'], workout_session_data['activity'])
    db.session.add(new_session)
    db.session.commit()
    return jsonify({"message": "New session added successfully"}), 201

@app.route('/workoutsessions/<int:id>', methods=['PUT'])
def update_session(id):
    ws = WorkoutSession.query.get_or_404(id)
    try:
        workout_data = workout_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    ws.session_date = workout_data['session_date']
    ws.session_time = workout_data['session_time']
    ws.activity = workout_data['activity']
    ws.session_id = workout_data['session_id']
    ws.member_id = workout_data['member_id']
    db.session.commit()
    return jsonify({"message": "Session has been updated."}), 200

@app.route('/workoutsessions/<int:id>', methods=['DELETE'])
def delete_session(id):
    ws = WorkoutSession.query.get_or_404(id)
    db.session.delete(ws)
    db.session.commit()
    return jsonify({"message": "Session has been deleted."}), 200

with app.app_context():
    db.create_all()

