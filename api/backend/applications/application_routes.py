from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import db
from datetime import datetime

# Create a Blueprint for applications
applications = Blueprint("applications", __name__)

# Get all applications for a specific student
@applications.route("/applications/<int:student_id>", methods=["GET"])
def get_student_applications(student_id):
    try:
        cursor = db.get_db().cursor()
        query = """
        SELECT 
            ja.dateApplied AS Date_Applied,
            ja.companyName AS Company, 
            ja.position AS Position,
            ja.stage AS Status, 
            r.label AS Resume_Used, 
            COALESCE(ja.jobBoard, p.name, 'Manual Add') AS Job_Board, 
            COALESCE(jl.postingURL, '') AS App_Portal
        FROM JobApplication ja
        JOIN Resume r ON ja.resumeID = r.resumeID AND ja.studentID = r.studentID
        LEFT JOIN JobListing jl ON ja.listingID = jl.listingID AND ja.postingID = jl.postingID
        LEFT JOIN Platform p ON jl.platformID = p.platformID
        WHERE ja.studentID = %s
        """
        cursor.execute(query, (student_id,))
        column_names = [i[0] for i in cursor.description]
        apps = cursor.fetchall()
        cursor.close()

        return jsonify(apps), 200

    except Error as e:
        return jsonify({"error": str(e)}), 500

# Add a new job application for a specific student
@applications.route("/applications/<int:student_id>", methods=["POST"])
def add_application(student_id):
    try:
        data = request.get_json()
        
        company_name = data.get('company')
        position = data.get('position')
        stage = data.get('stage')
        date_applied = data.get('date_applied')
        resume_id = data.get('resume_id')
        job_board = data.get('job_board')
        
        last_updated = datetime.now() 
        
        listing_id = None  
        posting_id = None  

        if not company_name or not position or not stage or not resume_id:
            return jsonify({"error": "Missing required fields"}), 400

        cursor = db.get_db().cursor()

        cursor.execute("SELECT MAX(applicationID) AS max_id FROM JobApplication")
        row = cursor.fetchone()
        current_max = row['max_id'] if (row and row['max_id']) else 0
        new_app_id = current_max + 1

        query = """
        INSERT INTO JobApplication 
        (
            applicationID, 
            studentID, 
            companyName, 
            position, 
            stage,
            jobBoard,
            dateApplied, 
            lastUpdated, 
            resumeID, 
            listingID, 
            postingID
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(query, (
            new_app_id, 
            student_id, 
            company_name,
            position, 
            stage, 
            job_board,
            date_applied, 
            last_updated, 
            resume_id, 
            listing_id, 
            posting_id
        ))
        
        db.get_db().commit()
        cursor.close()

        return jsonify({"message": "Application added successfully", "appID": new_app_id}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500