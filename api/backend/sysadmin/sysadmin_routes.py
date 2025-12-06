from flask import Blueprint, jsonify, request
from backend.db_connection import db
from mysql.connector import Error

# Create a Blueprint for system administration routes
sys_admin = Blueprint("sys_admin", __name__)

# Get system statistics
@sys_admin.route("/sysadmin/stats/<string:metric_type>/<int:days>", methods=["GET"])
def get_system_stats(metric_type, days):
    try:
        
        if not metric_type:
            return jsonify({"error": "Missing 'type' parameter"}), 400
        
        cursor = db.get_db().cursor()
        query = """
        SELECT
            type,
	        AVG(measurement) AS avg_val,
	        MAX(measurement) AS max_val,
	        MIN(measurement) AS min_val,
	        unit,
            COUNT(*) AS measurement_count
        FROM PerformanceMetric
        WHERE type = %s
            AND timeStamp >= NOW() - INTERVAL %s DAY
        GROUP BY type, unit
        ORDER BY avg_val DESC;
        """
        cursor.execute(query, (metric_type, days))
        result = cursor.fetchall()
        cursor.close()
        
        if not result:
            return jsonify({"message": "No data found for the specified metric type"}), 404

        return jsonify(result[0]), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500
    
@sys_admin.route("/sysadmin/backup/<int:admin_id>", methods=["POST"])
def initiate_backup(admin_id):
    try:
        
        if not admin_id:
            return jsonify({"error": "Invalid admin ID"}), 400
        
        cursor = db.get_db().cursor()
        query = """
        INSERT INTO Backup (
            datePerformed,
            size,
            status,
            health,
            adminID
        )
        VALUES (
            NOW(),
            '100',
            'In Progress',
            'Healthy',
            %s
        )
        """
        cursor.execute(query, (admin_id,))
        db.get_db().commit()
        backup_id = cursor.lastrowid
        cursor.close()
        
        if not backup_id:
            return jsonify({"message": "Backup initiation failed"}), 404

        return jsonify({
            "message": "Backup initiated successfully",
            "backupID": backup_id,
        }), 201
    except Error as e:
        return jsonify({"error": str(e)}), 500