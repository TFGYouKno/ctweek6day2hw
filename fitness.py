from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields, ValidationError
from connection import connection, Error
app = Flask(__name__)
ma = Marshmallow(app)


class MemberSchema(ma.Schema):
    id = fields.Int(dump_only= True) # dump_only means we don't have to input data for this field
    member_name = fields.String(required= True) # To be valid, this needs a value

    class Meta:
        fields = ("id", "member_name",)

member_schema = MemberSchema()
members_schema = MemberSchema(many= True)


@app.route('/')
def home():
    return "Hello, Flask!"

@app.route('/members', methods=['POST'])
def add_member():
    try:
        member_name = member_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    conn = connection()
    if conn is not None:
        try:
            cursor=conn.cursor()

            new_member = (member_name['member_name'])

            query = "INSERT INTO Members (member_name) VALUES (%s)"
            cursor.execute(query, (new_member,))
            conn.commit()

            return jsonify({"message": "New member added!"}), 201
        
        except Error as e:
            return jsonify(e.messages), 500
        finally:
            cursor.close()
            conn.close()
    else:
        return jsonify({"error": "Database connection failed"}), 500
        
@app.route('/members', methods=['GET'])
def get_members():
    conn = connection()
    if conn is not None:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM Members")
            members = cursor.fetchall()
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()
                return members_schema.jsonify(members)
    else:
        return jsonify({"error": "Database connection failed"}), 500
    
@app.route('/members/<int:id>', methods=['PUT'])
def update_member(id):
    try:
        member_name = member_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    conn = connection()
    if conn is not None:
        try:
            cursor=conn.cursor()

            check_query = "SELECT * FROM Members WHERE id = %s"
            cursor.execute(check_query, (id,))
            member = cursor.fetchone()
            if not member:
                return jsonify({"error": "Member not found"}), 404
            
            update_member = (member_name['member_name'], id)

            query = "UPDATE Members SET member_name = %s WHERE id = %s"
            cursor.execute(query, update_member)
            conn.commit()

            return jsonify({"message": f"Member successfully updated!{id}"}), 200
        except Error as e:
            return jsonify(e.messages), 500
        finally:
            cursor.close()
            conn.close()
    else:
        return jsonify({"error": "Database connection failed"}), 500



if __name__ == '__main__':
    app.run(debug=True)