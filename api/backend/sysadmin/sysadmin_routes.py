from flask import Blueprint, jsonify, request
from backend.db_connection import db
from mysql.connector import Error
from datetime import datetime

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
    
# Initiate a system backup
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
            100,
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

# Get the most recent backup
@sys_admin.route("/sysadmin/backups/latest", methods=["GET"])
def get_latest_backup():
    try:
        cursor = db.get_db().cursor()
        query = """
        SELECT
            backupID,
            datePerformed,
            size,
            status,
            health
        FROM Backup
        ORDER BY datePerformed DESC
        LIMIT 1
        """
        cursor.execute(query)
        
        rows = cursor.fetchall()
        cursor.close()
        
        if not rows:
            return jsonify({"message": "No backups found"}), 404
        
        return jsonify(rows[0]), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Get resource usage statistics  
@sys_admin.route("/sysadmin/resource-usage/<int:days>", methods=["GET"])
def get_resource_usage(days):
    try:
        cursor = db.get_db().cursor()
        query = """
        SELECT
            DATE(timeStamp) AS usg_date,
            AVG(activeUsers) AS avg_active_users,
            MAX(activeUsers) AS max_active_users,
            AVG(numApplications) AS avg_applications,
            MAX(numApplications) AS max_applications,
            AVG(cpuUsagePct) AS avg_cpu_usage
        FROM ResourceUsage
        WHERE timeStamp >= NOW() - INTERVAL %s DAY
        GROUP BY usg_date
        ORDER BY usg_date DESC
        """
        cursor.execute(query, (days,))
        
        rows = cursor.fetchall()
        cursor.close()
        
        return jsonify(rows), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Get audit logs for the past specified hours  
@sys_admin.route("/sysadmin/audit-logs/<int:hours>", methods=["GET"])
def get_audit_logs(hours):
    try:
        cursor = db.get_db().cursor()
        query = """
        SELECT
            auditID,
            timeStamp,
            action,
            tableName,
            recordID,
            summary,
            studentID,
            coachID,
            coordinatorID,
            adminID
        FROM Audit
        WHERE timeStamp >= NOW() - INTERVAL %s HOUR
        ORDER BY timeStamp DESC
        LIMIT 100
        """
        cursor.execute(query, (hours,))
        
        rows = cursor.fetchall()
        cursor.close()
        
        return jsonify(rows), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# Get unresolved critical alerts
@sys_admin.route("/sysadmin/alerts/unresolved", methods=["GET"])
def get_unresolved_alerts():
    try:
        cursor = db.get_db().cursor()
        query = """
        SELECT
            alertID,
            type,
            severity,
            message,
            timeStamp,
            TIMESTAMPDIFF(MINUTE, timeStamp, NOW()) AS mins_ago
        FROM Alert
        WHERE isResolved = FALSE
        ORDER BY
            timeStamp ASC
        """
        cursor.execute(query)
        
        rows = cursor.fetchall()
        cursor.close()
        
        return jsonify(rows), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

# Resolve an alert by its ID
@sys_admin.route("/sysadmin/alerts/<int:alert_id>/resolve", methods=["PUT"])
def resolve_alert(alert_id):
    try:
        cursor = db.get_db().cursor()
        query = """
        UPDATE Alert
        SET isResolved = 1
        WHERE alertID = %s
        """
        cursor.execute(query, (alert_id,))
        db.get_db().commit()
        cursor.close()
        
        return jsonify({
            "message": "Alert resolved successfully",
            "alertID": alert_id
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Create a new system configuration
@sys_admin.route("/sysadmin/config/<int:admin_id>", methods=["POST"])
def create_system_config(admin_id):
    try:
        data = request.get_json()
        
        cursor = db.get_db().cursor()
        query = """
        INSERT INTO SystemConfigurations (
            backupSchedule,
            daysToBackup,
            alertThresholdQueryTime,
            alertThresholdCPU,
            dataRetentionTime,
            maintenanceStartDateTime,
            maintenanceEndDateTime,
            lastModifiedDate,
            adminID
        )
        VALUES (
            %s, %s, %s, %s, %s, %s, %s, NOW(), %s
        )
        """


        cursor.execute(query, (
            data.get('backupSchedule', '2025-01-01 00:00:00'),
            data.get('daysToBackup', 30),
            data.get('alertThresholdQueryTime', 0),
            data.get('alertThresholdCPU', 0),
            data.get('dataRetentionTime', 30),
            data.get('maintenanceStartDateTime', '2025-01-01 00:00:00'),
            data.get('maintenanceEndDateTime', '2025-01-01 00:00:00'),
            admin_id
        ))
        db.get_db().commit()
        
        config_id = cursor.lastrowid
        cursor.close()
        
        return jsonify({
            "message": "Configuration created successfully",
            "configID": config_id
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Get the most recent system configuration    
@sys_admin.route("/sysadmin/config/current", methods=["GET"])
def get_current_config():
    try:
        cursor = db.get_db().cursor()
        query = """
        SELECT
            sc.configID,
            sc.backupSchedule,
            sc.daysToBackup,
            sc.alertThresholdQueryTime,
            sc.alertThresholdCPU,
            sc.dataRetentionTime,
            sc.maintenanceStartDateTime,
            sc.maintenanceEndDateTime,
            sc.lastModifiedDate,
            CONCAT(sa.fName, ' ', sa.lName) AS modified_by
        FROM SystemConfigurations sc
        JOIN SystemAdmin sa ON sc.adminID = sa.adminID
        ORDER BY sc.lastModifiedDate DESC
        LIMIT 1
        """
        cursor.execute(query)
        
        rows = cursor.fetchall()
        cursor.close()
        
        if not rows:
            return jsonify({"message": "No configuration found"}), 404
        
        config = rows[0]
        config['backupSchedule'] = config['backupSchedule'].strftime('%Y-%m-%d %H:%M:%S')
        config['maintenanceStartDateTime'] = config['maintenanceStartDateTime'].strftime('%Y-%m-%d %H:%M:%S')
        config['maintenanceEndDateTime'] = config['maintenanceEndDateTime'].strftime('%Y-%m-%d %H:%M:%S')
        config['lastModifiedDate'] = config['lastModifiedDate'].strftime('%Y-%m-%d')


        return jsonify(config), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500