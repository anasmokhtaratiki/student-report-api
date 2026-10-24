
from flask import Flask, jsonify, request
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity
)
from datetime import timedelta, datetime

app = Flask(__name__)

# Authentication configuration
app.config["JWT_SECRET_KEY"] = "change-this-secret-key-for-your-project"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=15)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=7)

jwt = JWTManager(app)


# =========================
# STUDENT CLASS
# =========================

class Student:
    def __init__(self, ID_S, FN, LN, DMjr, Level):
        self.ID_S = ID_S
        self.FN = FN
        self.LN = LN
        self.DMjr = DMjr
        self.Level = Level

    def to_dict(self):
        return {
            "ID_S": self.ID_S,
            "FN": self.FN,
            "LN": self.LN,
            "DMjr": self.DMjr,
            "Level": self.Level
        }


# =========================
# REPORT CLASS
# =========================

class Report:
    def __init__(self, ID_R, Title, Type, K1, K2, K3, Release_Date):
        self.ID_R = ID_R
        self.Title = Title
        self.Type = Type
        self.K1 = K1
        self.K2 = K2
        self.K3 = K3
        self.Release_Date = Release_Date

    def to_dict(self):
        return {
            "ID_R": self.ID_R,
            "Title": self.Title,
            "Type": self.Type,
            "K1": self.K1,
            "K2": self.K2,
            "K3": self.K3,
            "Release_Date": self.Release_Date
        }


# =========================
# TEMPORARY STORAGE
# =========================

students = []
reports = []


# =========================
# VALIDATION FUNCTIONS
# =========================

def is_positive_integer(value):
    return type(value) is int and value > 0


def validate_student(data):
    if not isinstance(data, dict):
        return "The JSON body must be an object."

    required = ["ID_S", "FN", "LN", "DMjr", "Level"]

    for field in required:
        if field not in data:
            return f"Missing field: {field}"

    if not is_positive_integer(data["ID_S"]):
        return "ID_S must be a positive integer."

    if not isinstance(data["FN"], str) or not data["FN"].strip():
        return "FN must be a non-empty string."

    if not isinstance(data["LN"], str) or not data["LN"].strip():
        return "LN must be a non-empty string."

    if type(data["DMjr"]) not in (bool, int) or data["DMjr"] not in (0, 1, False, True):
        return "DMjr must be true, false, 0, or 1."

    if type(data["Level"]) is not int or data["Level"] not in (1, 2, 3, 4):
        return "Level must be an integer from 1 to 4."

    return None


def validate_report(data):
    if not isinstance(data, dict):
        return "The JSON body must be an object."

    required = [
        "ID_R", "Title", "Type",
        "K1", "K2", "K3", "Release_Date"
    ]

    for field in required:
        if field not in data:
            return f"Missing field: {field}"

    if not is_positive_integer(data["ID_R"]):
        return "ID_R must be a positive integer."

    for field in ["Title", "Type", "K1", "K2", "K3"]:
        if not isinstance(data[field], str) or not data[field].strip():
            return f"{field} must be a non-empty string."

    if not isinstance(data["Release_Date"], str):
        return "Release_Date must be a string in YYYY-MM-DD format."

    try:
        datetime.strptime(data["Release_Date"], "%Y-%m-%d")
    except ValueError:
        return "Release_Date must be a valid date in YYYY-MM-DD format."

    return None


# =========================
# AUTHENTICATION
# =========================

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Send a valid JSON object."}), 400

    username = data.get("username")
    password = data.get("password")

    # Demo credentials for this assignment
    if username == "admin" and password == "admin123":
        access_token = create_access_token(identity=username)
        refresh_token = create_refresh_token(identity=username)

        return jsonify({
            "access_token": access_token,
            "refresh_token": refresh_token
        }), 200

    return jsonify({"error": "Invalid username or password."}), 401


@app.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    username = get_jwt_identity()
    new_access_token = create_access_token(identity=username)

    return jsonify({
        "access_token": new_access_token
    }), 200


# =========================
# STUDENT ENDPOINTS
# =========================

@app.route("/students", methods=["POST"])
def add_student():
    data = request.get_json(silent=True)
    error = validate_student(data)

    if error:
        return jsonify({"error": error}), 400

    for student in students:
        if student.ID_S == data["ID_S"]:
            return jsonify({"error": "Student ID already exists."}), 409

    student = Student(
        data["ID_S"],
        data["FN"].strip(),
        data["LN"].strip(),
        bool(data["DMjr"]),
        data["Level"]
    )

    students.append(student)

    return jsonify(student.to_dict()), 201


@app.route("/students", methods=["GET"])
@jwt_required()
def get_students():
    return jsonify([student.to_dict() for student in students]), 200


@app.route("/students/<int:student_id>", methods=["GET"])
@jwt_required()
def get_student(student_id):
    for student in students:
        if student.ID_S == student_id:
            return jsonify(student.to_dict()), 200

    return jsonify({"error": "Student not found."}), 404


@app.route("/students/<int:student_id>", methods=["PUT"])
def update_student(student_id):
    student = next(
        (s for s in students if s.ID_S == student_id),
        None
    )

    if student is None:
        return jsonify({"error": "Student not found."}), 404

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Send a valid JSON object."}), 400

    updated_data = student.to_dict()
    updated_data.update(data)

    error = validate_student(updated_data)

    if error:
        return jsonify({"error": error}), 400

    if updated_data["ID_S"] != student_id:
        return jsonify({"error": "Changing a student's ID is not allowed."}), 400

    student.FN = updated_data["FN"].strip()
    student.LN = updated_data["LN"].strip()
    student.DMjr = bool(updated_data["DMjr"])
    student.Level = updated_data["Level"]

    return jsonify(student.to_dict()), 200


@app.route("/students/<int:student_id>", methods=["DELETE"])
def delete_student(student_id):
    for student in students:
        if student.ID_S == student_id:
            students.remove(student)
            return jsonify({"message": "Student deleted successfully."}), 200

    return jsonify({"error": "Student not found."}), 404


# =========================
# REPORT ENDPOINTS
# =========================

@app.route("/reports", methods=["POST"])
def add_report():
    data = request.get_json(silent=True)
    error = validate_report(data)

    if error:
        return jsonify({"error": error}), 400

    for report in reports:
        if report.ID_R == data["ID_R"]:
            return jsonify({"error": "Report ID already exists."}), 409

    report = Report(
        data["ID_R"],
        data["Title"].strip(),
        data["Type"].strip(),
        data["K1"].strip(),
        data["K2"].strip(),
        data["K3"].strip(),
        data["Release_Date"]
    )

    reports.append(report)

    return jsonify(report.to_dict()), 201


@app.route("/reports", methods=["GET"])
def get_reports():
    return jsonify([report.to_dict() for report in reports]), 200


@app.route("/reports/<int:report_id>", methods=["GET"])
def get_report(report_id):
    for report in reports:
        if report.ID_R == report_id:
            return jsonify(report.to_dict()), 200

    return jsonify({"error": "Report not found."}), 404


@app.route("/reports/<int:report_id>", methods=["PUT"])
def update_report(report_id):
    report = next(
        (r for r in reports if r.ID_R == report_id),
        None
    )

    if report is None:
        return jsonify({"error": "Report not found."}), 404

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Send a valid JSON object."}), 400

    updated_data = report.to_dict()
    updated_data.update(data)

    error = validate_report(updated_data)

    if error:
        return jsonify({"error": error}), 400

    if updated_data["ID_R"] != report_id:
        return jsonify({"error": "Changing a report's ID is not allowed."}), 400

    report.Title = updated_data["Title"].strip()
    report.Type = updated_data["Type"].strip()
    report.K1 = updated_data["K1"].strip()
    report.K2 = updated_data["K2"].strip()
    report.K3 = updated_data["K3"].strip()
    report.Release_Date = updated_data["Release_Date"]

    return jsonify(report.to_dict()), 200


@app.route("/reports/<int:report_id>", methods=["DELETE"])
def delete_report(report_id):
    for report in reports:
        if report.ID_R == report_id:
            reports.remove(report)
            return jsonify({"message": "Report deleted successfully."}), 200

    return jsonify({"error": "Report not found."}), 404


# =========================
# HOME
# =========================

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "My API is working!"}), 200


# =========================
# RUN THE APPLICATION
# =========================

if __name__ == "__main__":
    app.run(debug=True)
