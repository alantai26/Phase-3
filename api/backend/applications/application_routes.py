from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import db
from mysql.connector import Error

# Create a Blueprint for applications
applications = Blueprint("applications", __name__)

# Get all applications for a specific student
@applications.route("/applications/<int:student_id>", methods=["GET"])
def get_student_applications(student_id):
    try:
        cursor = db.get_db().cursor()
        query = """
        SELECT 
            ja.companyName AS Company, 
            ja.stage AS Status, 
            r.label AS Resume_Used, 
            p.name AS Job_Board, 
            jl.postingURL AS App_Portal
        FROM JobApplication ja
        JOIN Resume r ON ja.resumeID = r.resumeID AND ja.studentID = r.studentID
        JOIN JobListing jl ON ja.listingID = jl.listingID AND ja.postingID = jl.postingID
        JOIN Platform p ON jl.platformID = p.platformID
        WHERE ja.studentID = %s
        """
        cursor.execute(query, (student_id,))
        column_names = [i[0] for i in cursor.description]
        apps = cursor.fetchall()
        cursor.close()

        return jsonify(apps), 200

    except Error as e:
        return jsonify({"error": str(e)}), 500