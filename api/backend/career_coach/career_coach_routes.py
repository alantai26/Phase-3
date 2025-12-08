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

# Get all messages between a coach and a student
@career_coach.route("/career_coach/<int:coach_id>/messages/<int:student_id>", methods=["GET"])
def get_messages(coach_id, student_id):

    try:
        cursor = db.get_db().cursor()
        
        query = """
        SELECT m.messageID, m.content, m.dateTimeSent, 'Coach' AS sender
        FROM Message m
        WHERE m.studentID = %s AND m.coachID = %s
        ORDER BY m.dateTimeSent ASC
        """
        cursor.execute(query, (student_id, coach_id))
        messages = cursor.fetchall()
        cursor.close()

        return jsonify(messages), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@career_coach.route("/career_coach/<int:coach_id>/send_message", methods=["POST"])
def send_message(coach_id):
    data = request.get_json()
    student_id = data.get("studentID")
    content = data.get("content")

    if not student_id or not content:
        return jsonify({"error": "Missing studentID or content"}), 400

    try:
        conn = db.get_db()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO Notification (type, isRead, dateTimeSent, coachID, studentID)
            VALUES (%s, %s, NOW(), %s, %s)
        """, ("Message", False, coach_id, student_id))
        notification_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO Message (content, dateTimeSent, studentID, coachID, notificationID)
            VALUES (%s, NOW(), %s, %s, %s)
        """, (content, student_id, coach_id, notification_id))

        conn.commit()
        cursor.close()
        return jsonify({"message": "Message sent successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Get notifications for a coach
@career_coach.route("/career_coach/<int:coach_id>/notifications", methods=["GET"])
def get_notifications(coach_id):
    try:
        cursor = db.get_db().cursor()
        cursor.execute("""
            SELECT notificationID, type, isRead, studentID
            FROM Notification
            WHERE coachID = %s
            ORDER BY dateTimeSent DESC
        """, (coach_id,))
        notifications = cursor.fetchall()
        cursor.close()
        return jsonify(notifications), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Toggle notifications read/unread
@career_coach.route("/career_coach/<int:coach_id>/notifications/toggle", methods=["PUT"])
def toggle_notifications(coach_id):
    data = request.get_json()
    ids = data.get("notification_ids", [])
    mark_read = data.get("mark_read", True)  # True = mark as read, False = mark as unread

    if not ids:
        return jsonify({"error": "No notification IDs provided"}), 400

    try:
        placeholders = ",".join(["%s"] * len(ids))
        cursor = db.get_db().cursor()
        cursor.execute(
            f"UPDATE Notification SET isRead = %s WHERE coachID = %s AND notificationID IN ({placeholders})",
            [mark_read, coach_id] + ids
        )
        db.get_db().commit()
        cursor.close()
        action = "read" if mark_read else "unread"
        return jsonify({"message": f"{len(ids)} notifications marked as {action}. "
                        + "Click again to confirm"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Add student to coach
@career_coach.route("/career_coach/<int:coach_id>/add_student", methods=["POST"])
def add_student(coach_id):
    data = request.get_json()
    student_id = data.get("student_id")
    if not student_id:
        return jsonify({"error": "Missing student_id"}), 400
    try:
        cursor = db.get_db().cursor()
        cursor.execute("UPDATE Student SET coachID = %s WHERE studentID = %s", (coach_id, student_id))
        db.get_db().commit()
        cursor.close()
        return jsonify({"message": f"Student {student_id} assigned to coach {coach_id}"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Unassign a student from a career coach
@career_coach.route("/career_coach/<int:coach_id>/remove_student/<int:student_id>", methods=["PUT"])
def remove_student(coach_id, student_id):
    try:
        conn = db.get_db()
        cursor = conn.cursor()

        # Set the coachID of the student to -1 (unassign)
        cursor.execute("""
            UPDATE Student
            SET coachID = -1
            WHERE studentID = %s AND coachID = %s
        """, (student_id, coach_id))

        conn.commit()
        cursor.close()

        if cursor.rowcount == 0:
            return jsonify({"message": "No student removed. Check student ID and coach ID."}), 404
        return jsonify({"message": f"Student {student_id} removed from coach {coach_id}."}), 200

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500


# Get each student's job applications for a specific career coach
@career_coach.route("/career_coach/<int:coach_id>/student_applications", methods=["GET"])
def get_student_applications(coach_id):
    """
    Returns each student's job applications, including stage and dateApplied.
    Useful for charts like stage distribution and offer counts.
    """
    try:
        cursor = db.get_db().cursor()

        query = """
        SELECT
            s.studentID,
            CONCAT(s.firstName, ' ', s.lastName) AS studentName,
            ja.applicationID,
            ja.companyName,
            ja.stage,
            ja.dateApplied,
            ja.lastUpdated
        FROM Student s
        LEFT JOIN JobApplication ja
            ON ja.studentID = s.studentID
        WHERE s.coachID = %s;
        """
        cursor.execute(query, (coach_id,))
        result = cursor.fetchall()
        cursor.close()

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Get student activity for a specific career coach
@career_coach.route("/career_coach/<int:coach_id>/student_activity", methods=["GET"])
def get_student_activity(coach_id):
    try:
        cursor = db.get_db().cursor()

        query = """
        SELECT
            s.studentID AS ID,
            CONCAT(s.firstName, ' ', s.lastName) AS Name,
            ja.stage AS Stage,
            ja.lastUpdated AS Last_Update
        FROM Student s
        LEFT JOIN JobApplication ja
            ON ja.studentID = s.studentID
            AND ja.lastUpdated = (
                SELECT MAX(j2.lastUpdated)
                FROM JobApplication j2
                WHERE j2.studentID = s.studentID
            )
        WHERE s.coachID = %s
        ORDER BY Last_Update DESC;
        """
        cursor.execute(query, (coach_id,))
        results = cursor.fetchall()
        cursor.close()

        return jsonify(results), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Get the number of active students for a specific career coach
@career_coach.route("/career_coach/<int:coach_id>/active_students", methods=["GET"])
def get_active_students(coach_id):
    try:
        cursor = db.get_db().cursor()

        # Query to count Active Students
        cursor.execute("""
        SELECT COUNT(*) AS Active_Students
        FROM Student s
        WHERE coachID = %s AND s.status = 'Active'
        """, (coach_id,))
        
        active_students = cursor.fetchone()        
        cursor.close()

        # Return the result as a JSON response
        return jsonify([active_students]), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Get the number of roles secured for a specific career coach
@career_coach.route("/career_coach/<int:coach_id>/roles_secured", methods=["GET"])
def get_roles_secured(coach_id):
    try:
        cursor = db.get_db().cursor()

        # Query to count Roles Secured (Stage = 'Offered')
        cursor.execute("""
        SELECT COUNT(DISTINCT ja.studentID) AS Roles_Secured
        FROM JobApplication ja
        JOIN Student s ON ja.studentID = s.studentID
        JOIN CareerCoach cc ON s.coachID = cc.coachID
        WHERE cc.coachID = %s AND ja.stage = 'Offered'
        """, (coach_id,))
        roles_secured = cursor.fetchall()
        cursor.close()

        # Return the result as a JSON response
        return jsonify(roles_secured), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Get the number of in-progress students for a specific career coach
@career_coach.route("/career_coach/<int:coach_id>/in_progress", methods=["GET"])
def get_in_progress(coach_id):
    try:
        cursor = db.get_db().cursor()

        # Query to count In Progress (Stage = 'Applied' or 'Interviewing')
        cursor.execute("""
        SELECT COUNT(DISTINCT ja.studentID) AS In_Progress
        FROM JobApplication ja
        JOIN Student s ON ja.studentID = s.studentID
        JOIN CareerCoach cc ON s.coachID = cc.coachID
        WHERE cc.coachID = %s AND ja.stage IN ('Applied', 'Interviewing')
        """, (coach_id,))
        in_progress = cursor.fetchall()
        cursor.close()

        # Return the result as a JSON response
        return jsonify(in_progress), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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
    

@career_coach.route("/career_coach/all", methods=["GET"])
def get_all_coaches():
    try:
        cursor = db.get_db().cursor()

        # Query to get all coaches with their details
        cursor.execute("""
        SELECT 
            coachID, firstName, lastName, email
        FROM CareerCoach
        """)

        coaches = cursor.fetchall()
        cursor.close()

        # Check if coaches are found
        if coaches:
            # Return the list of coaches as JSON
            return jsonify(coaches), 200
        else:
            return jsonify({"message": "No coaches found."}), 404

    except Exception as e:
        # Return an error message if the query fails
        return jsonify({"error": str(e)}), 500