from flask import (
    Blueprint,
    request,
    jsonify,
    make_response,
    current_app,
    redirect,
    url_for,
)

from backend.db_connection import db

# Create a Blueprint for career_coach
career_coach = Blueprint("career_coach", __name__)

# Get all students for a specific career coach
@career_coach.route("/career_coach/<int:coach_id>/students", methods=["GET"])
def get_coach_students(coach_id):
    try:
        cursor = db.get_db().cursor()
        query = """
        SELECT 
            s.studentID AS Student_ID,
            s.firstName AS First_Name,
            s.lastName AS Last_Name,
            s.email AS Email
        FROM Student s
        JOIN CareerCoach cc ON s.coachID = cc.coachID
        WHERE cc.coachID = %s
        """
        cursor.execute(query, (coach_id,))
        students = cursor.fetchall()
        cursor.close()

        return jsonify(students), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500