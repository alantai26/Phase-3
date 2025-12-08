from flask import Blueprint, jsonify, request
from backend.db_connection import db
from mysql.connector import Error

# Create a Blueprint for hiring coordinator routes
hiring_coord = Blueprint("hiring_coord", __name__)


@hiring_coord.route("/coordinator/<int:coordinator_id>/applications", methods=["GET"])
def get_applications_by_coordinator(coordinator_id):
    """
    Returns all job applications for a given coordinator with platform info.
    """
    try:
        cursor = db.get_db().cursor()

        # Query to get applications with platform and posting info
        query = """
        SELECT 
            ja.applicationID,
            ja.studentID,
            ja.postingID,
            ja.listingID,
            ja.companyName,
            ja.position,
            ja.stage,
            ja.dateApplied,
            ja.lastUpdated,
            ja.jobBoard,
            jp.title AS postingTitle,
            jp.roleType,
            jp.location,
            jp.department,
            jl.platformID,
            p.name AS platform
        FROM JobApplication ja
        JOIN JobPosting jp ON ja.postingID = jp.postingID
        JOIN JobListing jl 
           ON ja.listingID = jl.listingID 
            AND ja.postingID = jl.postingID
        JOIN Platform p ON jl.platformID = p.platformID
        WHERE jp.coordinatorID = %s
        ORDER BY ja.dateApplied DESC
        """
        cursor.execute(query, (coordinator_id,))
        applications = cursor.fetchall()
        cursor.close()

        return jsonify(applications), 200

    except Error as e:
        return jsonify({"error": str(e)}), 500

# Get all job listings for a coordinator, including platform and status
@hiring_coord.route("/coordinator/<int:coordinator_id>/listings", methods=["GET"])
def get_coordinator_listings(coordinator_id):
    try:
        cursor = db.get_db().cursor()

        query = """
        SELECT
            jp.postingID,
            jp.title,
            jp.roleType,
            jp.status AS postingStatus,
            jl.listingID,
            jl.platformID,
            p.name AS platform,
            jl.listingStatus AS listingStatus
        FROM JobPosting jp
        LEFT JOIN JobListing jl ON jp.postingID = jl.postingID
        LEFT JOIN Platform p ON jl.platformID = p.platformID
        WHERE jp.coordinatorID = %s
        ORDER BY jp.datePosted DESC
        """

        cursor.execute(query, (coordinator_id,))
        result = cursor.fetchall()
        cursor.close()

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Get all the job postings for a coordinator
@hiring_coord.route("/coordinator/<int:coordinator_id>/postings", methods=["GET"])
def get_coordinator_postings(coordinator_id):
    try:
        if not coordinator_id:
            return jsonify({"error": "Invalid coordinator ID"}), 400

        cursor = db.get_db().cursor()
        query = """
        SELECT
            jp.postingID,
            jp.title,
            jp.roleType,
            jp.status,
            COUNT(DISTINCT ja.applicationID) AS totalApplicants
        FROM JobPosting jp
        LEFT JOIN JobApplication ja ON jp.postingID = ja.postingID
        WHERE jp.coordinatorID = %s
        GROUP BY jp.postingID, jp.title, jp.roleType, jp.location, 
                 jp.department, jp.status, jp.datePosted, jp.dateClosed
        ORDER BY jp.datePosted DESC
        """
        cursor.execute(query, (coordinator_id,))
        result = cursor.fetchall()
        cursor.close()

        return jsonify(result), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500


# Create a new job posting
@hiring_coord.route("/coordinator/<int:coordinator_id>/postings", methods=["POST"])
def create_job_posting(coordinator_id):
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['title', 'roleType', 'location', 'department']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        cursor = db.get_db().cursor()
        query = """
        INSERT INTO JobPosting (
            title,
            roleType,
            location,
            department,
            status,
            datePosted,
            coordinatorID
        )
        VALUES (%s, %s, %s, %s, %s, NOW(), %s)
        """
        cursor.execute(query, (
            data['title'],
            data['roleType'],
            data['location'],
            data['department'],
            data.get('status', 'Active'),
            coordinator_id
        ))
        db.get_db().commit()
        posting_id = cursor.lastrowid
        cursor.close()

        if not posting_id:
            return jsonify({"message": "Job posting creation failed"}), 404

        return jsonify({
            "message": "Job posting has been created successfully",
            "postingID": posting_id
        }), 201
    except Error as e:
        return jsonify({"error": str(e)}), 500

# Get the expiring listing notifications
@hiring_coord.route("/coordinator/<int:coordinator_id>/expiring-listings", methods=["GET"])
def get_expiring_listings(coordinator_id):
    try:
        # Find the days parameter (defaulted at 7 days)
        days = request.args.get('days', 7, type=int)

        cursor = db.get_db().cursor()
        query = """
        SELECT
            jl.listingID,
            jp.postingID,
            jp.title,
            p.name AS platformName,
            jl.expiresOn,
            jl.listingStatus,
            DATEDIFF(jl.expiresOn, NOW()) AS daysUntilExpiry
        FROM JobListing jl
        JOIN JobPosting jp ON jl.postingID = jp.postingID
        JOIN Platform p ON jl.platformID = p.platformID
        WHERE jp.coordinatorID = %s
          AND jl.listingStatus = 'Active'
          AND jl.expiresOn IS NOT NULL
          AND jl.expiresOn <= DATE_ADD(NOW(), INTERVAL %s DAY)
        ORDER BY jl.expiresOn ASC
        LIMIT 1
        """
        cursor.execute(query, (coordinator_id, days))
        result = cursor.fetchall()
        cursor.close()

        return jsonify(result), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500

# Delete a job posting
@hiring_coord.route("/postings/<int:posting_id>", methods=["DELETE"])
def delete_job_posting(posting_id):
    try:
        cursor = db.get_db().cursor()
        query = """
        DELETE FROM JobPosting
        WHERE postingID = %s
        """
        cursor.execute(query, (posting_id,))
        db.get_db().commit()
        rows_affected = cursor.rowcount
        cursor.close()

        if rows_affected == 0:
            return jsonify({"message": "Posting not found"}), 404

        return jsonify({
            "message": "Job posting has been deleted successfully",
            "postingID": posting_id
        }), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500