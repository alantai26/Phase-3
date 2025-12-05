from flask import Blueprint, jsonify, request
from backend.db_connection import db
from mysql.connector import Error

# Create a Blueprint for system administration routes
sys_admin = Blueprint("sys_admin", __name__)

# Get system statistics
@sys_admin.route("/sysadmin/stats", methods=["GET"])
def get_system_stats():
    try:
        requested_metric = request.args.get('type')
        days = request.args.get('days', '1')
        
        if not requested_metric:
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
        cursor.execute(query, (requested_metric, days))
        result = cursor.fetchall()
        cursor.close()
        
        if not result:
            return jsonify({"message": "No data found for the specified metric type"}), 404

        return jsonify(result[0]), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500