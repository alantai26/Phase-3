DROP DATABASE IF EXISTS `appliTracker`;
CREATE DATABASE IF NOT EXISTS `appliTracker`;
USE `appliTracker`;

DROP TABLE IF EXISTS SystemAdmin;
CREATE TABLE SystemAdmin
(
    fName VARCHAR(50) NOT NULL,
    lName VARCHAR(50) NOT NULL,
    email VARCHAR(75) NOT NULL UNIQUE,
    adminID INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    INDEX indexAdminID (adminID)
);

DROP TABLE IF EXISTS SystemConfigurations;
CREATE TABLE SystemConfigurations
(
    daysToBackup INT NOT NULL,
    dataRetentionTime INT,
    backupSchedule DATETIME NOT NULL,
    alertThresholdCPU BOOLEAN NOT NULL DEFAULT FALSE,
    lastModifiedDate DATE,
    alertThresholdQueryTime BOOLEAN NOT NULL DEFAULT FALSE,
    maintenanceStartDateTime DATETIME,
    maintenanceEndDateTIme DATETIME,
    configID INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    adminID INT NOT NULL,
    CONSTRAINT fk_0 FOREIGN KEY (adminID)
        REFERENCES SystemAdmin (adminID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    INDEX indexConfigID (configID)
);

DROP TABLE IF EXISTS ResourceUsage;
CREATE TABLE ResourceUsage
(
    timeStamp TIMESTAMP NOT NULL,
    activeUsers INT NOT NULL DEFAULT 0,
    numApplications INT NOT NULL DEFAULT 0,
    dbSize VARCHAR(50) NOT NULL,
    cpuUsagePct DOUBLE NOT NULL,
    usageID INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    adminID INT NOT NULL,
    CONSTRAINT fk_1 FOREIGN KEY (adminID)
        REFERENCES SystemAdmin (adminID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    INDEX indexUsageID (usageID)
);

DROP TABLE IF EXISTS PerformanceMetric;
CREATE TABLE PerformanceMetric
(
    type VARCHAR(50) NOT NULL,
    unit VARCHAR(50) NOT NULL,
    measurement DOUBLE NOT NULL,
    timeStamp TIMESTAMP NOT NULL,
    metricID INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    adminID INT NOT NULL,
    CONSTRAINT fk_2 FOREIGN KEY (adminID)
        REFERENCES SystemAdmin (adminID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    INDEX indexMetricID (metricID)
);

DROP TABLE IF EXISTS Backup;
CREATE TABLE Backup
(
    size DOUBLE NOT NULL,
    status VARCHAR(50) NOT NULL,
    health VARCHAR(50) NOT NULL,
    datePerformed DATE,
    backupID INT PRIMARY KEY AUTO_INCREMENT,
    adminID INT NOT NULL,
    CONSTRAINT fk_3 FOREIGN KEY (adminID)
        REFERENCES SystemAdmin (adminID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    INDEX indexBackupID (backupID)
);

DROP TABLE IF EXISTS SystemUpdate;
CREATE TABLE SystemUpdate
(
    updateDate DATE,
    status VARCHAR(50) NOT NULL,
    updatedVersion VARCHAR(50),
    currentVersion VARCHAR(50) NOT NULL,
    patchNotes VARCHAR(50),
    updateID INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    adminID INT NOT NULL,
    CONSTRAINT fk_4 FOREIGN KEY (adminID)
        REFERENCES SystemAdmin (adminID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    INDEX indexUpdateID (updateID)
);

DROP TABLE IF EXISTS Alert;
CREATE TABLE Alert
(
    type VARCHAR(50) NOT NULL,
    severity VARCHAR(50),
    message VARCHAR(50),
    isResolved BOOLEAN NOT NULL DEFAULT FALSE,
    timeStamp TIMESTAMP NOT NULL,
    alertID INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    adminID INT NOT NULL,
    usageID INT,
    backupID INT,
    metricID INT,
    updateID INT,
    CONSTRAINT fk_5 FOREIGN KEY (adminID)
        REFERENCES SystemAdmin (adminID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT fk_6 FOREIGN KEY (usageID)
        REFERENCES ResourceUsage (usageID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT fk_7 FOREIGN KEY (backupID)
        REFERENCES Backup (backupID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT fk_8 FOREIGN KEY (metricID)
        REFERENCES PerformanceMetric (metricID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT fk_9 FOREIGN KEY (updateID)
        REFERENCES SystemUpdate (updateID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    INDEX indexAlertID (alertID)
);

DROP TABLE IF EXISTS CareerCoach;
CREATE TABLE CareerCoach
(
    firstName VARCHAR(50) NOT NULL,
    lastName VARCHAR(50) NOT NULL,
    email VARCHAR(50) NOT NULL UNIQUE,
    coachID INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    INDEX indexCoachID (coachID)
);

DROP TABLE IF EXISTS Student;
CREATE TABLE Student
(
    firstName VARCHAR(50) NOT NULL,
    lastName VARCHAR(50) NOT NULL,
    email VARCHAR(50) NOT NULL UNIQUE,
    major VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'Active',
    graduationDate DATE,
    studentID INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    coachID INT NOT NULL,
    CONSTRAINT fk_14 FOREIGN KEY (coachID)
        REFERENCES CareerCoach (coachID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    INDEX indexStudentID (studentID)
);

DROP TABLE IF EXISTS HiringCoordinator;
CREATE TABLE HiringCoordinator
(
    fName VARCHAR(50) NOT NULL,
    lName VARCHAR(50) NOT NULL,
    email VARCHAR(50) NOT NULL UNIQUE,
    companyName VARCHAR(50) NOT NULL,
    coordinatorID INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    INDEX indexCoordinatorID (coordinatorID)
);

DROP TABLE IF EXISTS Audit;
CREATE TABLE Audit
(
    summary VARCHAR(50) NOT NULL,
    tableName VARCHAR(50) NOT NULL,
    action VARCHAR(50) NOT NULL,
    timeStamp TIMESTAMP NOT NULL,
    recordID INT,
    auditID INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    adminID INT,
    studentID INT,
    coordinatorID INT,
    coachID INT,
    CONSTRAINT fk_10 FOREIGN KEY (adminID)
        REFERENCES SystemAdmin (adminID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT fk_11 FOREIGN KEY (studentID)
        REFERENCES Student (studentID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT fk_12 FOREIGN KEY (coordinatorID)
        REFERENCES HiringCoordinator (coordinatorID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT fk_13 FOREIGN KEY (coachID)
        REFERENCES CareerCoach (coachID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    INDEX indexAuditID (auditID)
);

DROP TABLE IF EXISTS JobPosting;
CREATE TABLE JobPosting
(
    title VARCHAR(50) NOT NULL,
    roleType VARCHAR(50) NOT NULL,
    location VARCHAR(50) NOT NULL,
    department VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'Active',
    datePosted DATE NOT NULL,
    dateClosed DATE,
    postingID INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    coordinatorID INT NOT NULL,
    CONSTRAINT fk_15 FOREIGN KEY (coordinatorID)
        REFERENCES HiringCoordinator (coordinatorID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    INDEX indexPostingID (postingID)
);

DROP TABLE IF EXISTS Platform;
CREATE TABLE Platform
(
    name VARCHAR(50) NOT NULL,
    platformType VARCHAR(50) NOT NULL,
    baseURL VARCHAR(50) NOT NULL,
    platformID INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    INDEX indexPlatformID (platformID)
);

DROP TABLE IF EXISTS StudentProgressMetrics;
CREATE TABLE StudentProgressMetrics
(
    lastActivityDate DATE NOT NULL,
    offersReceived INT NOT NULL DEFAULT 0,
    interviewsScheduled INT NOT NULL DEFAULT 0,
    numJobApplied INT NOT NULL DEFAULT 0,
    progressID INT NOT NULL,
    studentID INT NOT NULL,
    PRIMARY KEY (progressID, studentID) AUTO_INCREMENT,
    CONSTRAINT fk_16 FOREIGN KEY (studentID)
        REFERENCES Student (studentID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    INDEX indexProgressIDStudentID (progressID, studentID),
    INDEX indexStudentID (studentID)
);

DROP TABLE IF EXISTS JobListing;
CREATE TABLE JobListing
(
    listingStatus VARCHAR(50) NOT NULL,
    datePublished DATE NOT NULL,
    expiresOn DATETIME ,
    lastChecked DATETIME,
    postingURL VARCHAR(50) NOT NULL,
    listingID INT NOT NULL,
    postingID INT NOT NULL,
    PRIMARY KEY (listingID, postingID) AUTO_INCREMENT,
    platformID INT NOT NULL,
    CONSTRAINT fk_17 FOREIGN KEY (platformID)
        REFERENCES Platform (platformID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT fk_18 FOREIGN KEY (postingID)
        REFERENCES JobPosting (postingID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    INDEX indexListingIDPostingID (listingID, postingID),
    INDEX indexPostingID (postingID)
);

DROP TABLE IF EXISTS Report;
CREATE TABLE Report
(
    generatedDate DATE NOT NULL,
    summary VARCHAR(50) NOT NULL,
    reportID INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    coachID INT NOT NULL,
    CONSTRAINT fk_19 FOREIGN KEY (coachID)
        REFERENCES CareerCoach (coachID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    INDEX indexReportID (reportID)
);

DROP TABLE IF EXISTS ReportItem;
CREATE TABLE ReportItem
(
    recommendations VARCHAR(50) NOT NULL,
    notes VARCHAR(50) NOT NULL,
    keyFindings VARCHAR(50) NOT NULL,
    itemID INT NOT NULL,
    reportID INT NOT NULL,
    PRIMARY KEY (itemID, reportID) AUTO_INCREMENT,
    studentID INT NOT NULL,
    CONSTRAINT fk_20 FOREIGN KEY (reportID)
        REFERENCES Report (reportID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_21 FOREIGN KEY (studentID)
        REFERENCES Student (studentID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    INDEX indexItemIDReportID (itemID, reportID),
    INDEX indexReportID (reportID)
);

DROP TABLE IF EXISTS coachSPM;
CREATE TABLE coachSPM
(
    coachID INT NOT NULL,
    progressID INT NOT NULL,
    studentID INT NOT NULL,
    PRIMARY KEY (coachID, progressID, studentID) AUTO_INCREMENT,
    CONSTRAINT fk_22 FOREIGN KEY (coachID)
        REFERENCES CareerCoach (coachID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_23 FOREIGN KEY (progressID, studentID)
        REFERENCES StudentProgressMetrics (progressID, studentID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    INDEX indexCoachID (coachID),
    INDEX indexProgressIDStudentID (progressID, studentID)
);

DROP TABLE IF EXISTS Resume;
CREATE TABLE Resume
(
    imageURl VARCHAR(50) NOT NULL,
    label VARCHAR(50) NOT NULL,
    resumeID INT NOT NULL AUTO_INCREMENT,
    studentID INT NOT NULL,
    PRIMARY KEY (resumeID) AUTO_INCREMENT,
    CONSTRAINT fk_24 FOREIGN KEY (studentID)
        REFERENCES Student (studentID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    INDEX indexResumeIDStudentID (resumeID, studentID),
    INDEX indexStudentID (studentID)
);

DROP TABLE IF EXISTS JobApplication;
CREATE TABLE JobApplication
(
    companyName VARCHAR(50) NOT NULL,
    position VARCHAR(50) NOT NULL,
    stage VARCHAR(50),
    dateApplied DATE,
    lastUpdated DATETIME NOT NULL,
    applicationID INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    jobBoard VARCHAR(50),
    studentID INT NOT NULL,
    listingID INT NOT NULL,
    postingID INT NOT NULL,
    resumeID INT NOT NULL,
    CONSTRAINT fk_25 FOREIGN KEY (studentID)
        REFERENCES Student (studentID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT fk_26 FOREIGN KEY (listingID, postingID)
        REFERENCES JobListing (listingID, postingID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT fk_27 FOREIGN KEY (resumeID, studentID)
        REFERENCES Resume (resumeID, studentID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    INDEX indexApplicationID (applicationID)
);

DROP TABLE IF EXISTS Notification;
CREATE TABLE Notification
(
    type VARCHAR(50) NOT NULL,
    isRead BOOLEAN NOT NULL DEFAULT FALSE,
    dateTimeSent DATETIME NOT NULL,
    notificationID INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    coachID INT,
    studentID INT,
    applicationID INT,
    coordinatorID INT,
    listingID INT,
    postingID INT,
    CONSTRAINT fk_31 FOREIGN KEY (coachID)
        REFERENCES CareerCoach (coachID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT fk_32 FOREIGN KEY (studentID)
        REFERENCES Student (studentID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT fk_33 FOREIGN KEY (applicationID)
        REFERENCES JobApplication (applicationID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT fk_34 FOREIGN KEY (coordinatorID)
        REFERENCES HiringCoordinator (coordinatorID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT fk_35 FOREIGN KEY (listingID, postingID)
        REFERENCES JobListing (listingID, postingID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    INDEX indexNotificationID (notificationID)
);

DROP TABLE IF EXISTS Message;
CREATE TABLE Message
(
    content VARCHAR(50) NOT NULL,
    dateTimeSent DATETIME NOT NULL,
    messageID INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    studentID INT NOT NULL,
    coachID INT NOT NULL,
    notificationID INT NOT NULL,
    CONSTRAINT fk_28 FOREIGN KEY (studentID)
        REFERENCES Student (studentID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT fk_29 FOREIGN KEY (coachID)
        REFERENCES CareerCoach (coachID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT fk_30 FOREIGN KEY (notificationID)
        REFERENCES Notification (notificationID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    INDEX indexMessageID (messageID)
);

INSERT INTO SystemAdmin (fName, lName, email, adminID)
VALUES ('John', 'Joe', 'johnjoe@gmail.com', 000001);

INSERT INTO SystemConfigurations (daysToBackup, dataRetentionTime,
                                  backupSchedule, alertThresholdCPU,
                                  lastModifiedDate, alertThresholdQueryTime,
                                  maintenanceStartDateTime, maintenanceEndDateTIme,
                                  configID, adminID)
VALUES (20, NULL, '2025-07-10 15:41:00',
        FALSE, NULL, FALSE,
        NULL, NULL,
        111111, 000001),
       (30, NULL, '2026-07-10 15:41:00',
        TRUE,NULL, FALSE,
        NULL, NULL,
        111112, 000001);

INSERT INTO ResourceUsage (timeStamp, activeUsers, numApplications,
                           dbSize, cpuUsagePct, usageID, adminID)
VALUES ('2025-10-10 15:41:00', 1, 2,
        '100 GB', 0.67, 222221, 000001),
       ('2025-10-10 15:41:00', 0, 0,
        '1 GB', 0.50, 222222, 000001);

INSERT INTO PerformanceMetric (type, unit, measurement, timeStamp, metricID, adminID)
VALUES ('response time', 'ms', 100.00,
        '2025-10-10 15:41:00', 333331, 000001),
       ('query frequency', 'queries/min', 5.00,
        '2025-10-10 12:31:14', 333332, 000001),
       ('response time', 'ms', 200.00,
        '2025-10-11 15:41:00', 333333, 000001);

INSERT INTO Backup (size, status, health, datePerformed, adminID)
VALUES (100.00, 'Good', 'Healthy', NULL,
        000001),
       (50.00, 'Bad', 'Unhealthy', Null,
        000001);
INSERT INTO SystemUpdate (updateDate, status, updatedVersion, currentVersion, patchNotes, updateID, adminID)
VALUES (NULL, 'Good', NULL, '1.0.0',
        NULL, 555551, 000001),
       (NULL, 'BAD', NULL, '0.0.1',
        NULL, 555552, 000001);

INSERT INTO Alert (type, severity, message, isResolved, timeStamp, alertID, adminID, usageID, backupID, metricID, updateID)
VALUES ('Backup', 'Low', NULL, TRUE, '2025-10-10 15:21:31',
        666661, 000001, NULL, 444441, NULL, NULL),
       ('SystemUpdate', 'Low', NULL, TRUE, '2025-10-10 15:22:31',
        666662, 000001, NULL, NULL, NULL, 555551);

INSERT INTO CareerCoach (firstName, lastName, email, coachID)
VALUES ('Marcus', 'Smith', 'marcussmith@gmail.com', 777771),
       ('Joe', 'Johnson', 'joeJohnson@gmail.com', 777772);

INSERT INTO Student (firstName, lastName, email, major, graduationDate, studentID, coachID)
VALUES ('James', 'Jane', 'jamesjane@gmail.com', 'Computer Science',
        NULL, 888881, 777771),
       ('Alice', 'Bob', 'alicebob@gmail.com', 'Math',
        NULL, 888882, 777772);

INSERT INTO HiringCoordinator (fName, lName, email, companyName, coordinatorID)
VALUES ('Sophia', 'Soap', 'sophiasoap@gmail.com', 'Amazon', 999991),
       ('Dirt', 'Dog', 'dirtdog@gmail.com', 'Chewy', 999992);

INSERT INTO Audit (summary, tableName, action, timeStamp, recordID, auditID, adminID, studentID, coordinatorID, coachID)
VALUES ('Good', 'Student', 'Applied Job',
        '2025-10-10 15:41:31', 0, 122221, 000001,
        888881, NULL, NULL),
       ('Good activity', 'Coach', 'Helping Student',
        '2025-10-10 16:31:41', 1, 122222, 000001, NULL, NULL, 777771);

INSERT INTO JobPosting (title, roleType, location, department, datePosted, dateClosed, postingID, coordinatorID)
VALUES ('Mcdonald flipper', 'Burger Flipper', 'Boston', 'Kitchen',
        '2025-07-10', NULL, 133331, 999991),
       ('SWE', 'SWE', 'Seattle', 'AWS',
        '2020-06-11', NULL, 133332, 999992);

INSERT INTO Platform (name, platformType, baseURL, platformID)
VALUES ('LinkedIn', 'Online', 'https://www.linkedin.com/', 144441),
       ('NUworks', 'Online', 'https://northeastern-csm.symplicity.com/students/', 144442);

INSERT INTO StudentProgressMetrics (lastActivityDate, offersReceived, interviewsScheduled, numJobApplied, progressID, studentID)
VALUES ('2024-06-10', 0, 0, 0, 155551, 888881),
       ('2025-06-10', 1, 1, 1, 155552, 888882);

INSERT INTO JobListing (listingStatus, datePublished, expiresOn, lastChecked, postingURL, listingID, postingID, platformID)
VALUES ('Up', '2024-06-10', NULL, NULL, 'https://www.linkedin.com/jobs/123',
        166661, 133331, 144441),
       ('Down', '2024-06-10', '2024-06-10', NULL,
        'https://northeastern.com/students/jobs/321', 166662, 133332, 144442);

INSERT INTO Report (generatedDate, summary, reportID, coachID)
VALUES ('2024-06-10', 'I did not listen', 177771, 777771),
       ('2025-06-10', 'Good guy', 177772, 777772);

INSERT INTO ReportItem (recommendations, notes, keyFindings, itemID, reportID, studentID)
VALUES ('idk', 'none', 'none', 188881, 177771, 888881),
       ('Apply to more', 'applied to little', 'needs to apply to more',
        188882, 177772, 888882);

INSERT INTO coachSPM (coachID, progressID, studentID)
VALUES (777771, 155551, 888881),
       (777772, 155552, 888882);

INSERT INTO Resume (imageURl, label, resumeID, studentID)
VALUES ('imageurl.com', 'Final Resume', 199991, 888881),
       ('word.com', 'Updated Resume', 199992, 888882),
       ('/docs/resumes/student_888881.pdf', 'Software Engineer Focused', 199992, 888881);

INSERT INTO JobApplication (companyName, position, stage, dateApplied,
                            lastUpdated, applicationID, studentID,
                            listingID, postingID, resumeID)
VALUES ('Mcdonald\'s', 'burger flipper', 'applied',
        '2024-10-10', '2024-10-10', 211111,
        888881, 166661, 133331, 199991),
       ('Amazon', 'SWE', 'Rejected',
        '2024-10-11', '2024-10-11', 211112,
        888882, 166662, 133332, 199992);

INSERT INTO Notification (type, dateTimeSent, notificationID,
                          coachID, studentID, applicationID,
                          coordinatorID, listingID, postingID)
VALUES ('Job application', '2024-10-10 15:41:00', 233331,
        777771, 888881, 211111, NULL, 166661,
        133331),
       ('Message', '2024-10-11 15:41:00', 233332,
        777772, 888882, NULL, NULL, NULL,
        NULL),
       ('Message', '2024-10-11 15:41:01', 233333, NULL,
        888882, NULL, NULL, NULL, NULL);

INSERT INTO Message (content, dateTimeSent, messageID, studentID, coachID, notificationID)
VALUES ('coach is right', '2024-10-11 15:41:00', 244441, 888882,
        777772, 233332),
       ('hello', '2024-10-11 15:41:01', 244442, 888882,
        777772, 233333);
