```python
from flask import Flask, request

app = Flask(__name__)

students = [
    {
        "id_s": 1,
        "Fname": "Ali",
        "Lname": "Mastouri",
        "reports": [
            {
                "id_r": 1,
                "title": "balbalah",
                "type": "Mini senior project"
            }
        ]
    }
]


# GET: Get all students
@app.get("/students")
def get_students():
    return students


# GET: Get a student by ID
@app.get("/students/<int:student_id>")
def get_student_by_id(student_id):
    student = next(
        (s for s in students if s["id_s"] == student_id),
        None
    )

    if student is None:
        return {"error": "Student not found"}, 404

    return student, 200


# GET: Get a student by ID (alternative endpoint)
@app.get("/student/<int:student_id>")
def get_student_by_id_new(student_id):
    for student in students:
        if student["id_s"] == student_id:
            return {"student": student}, 200

    return {"message": "Student not found"}, 404


# GET: Get all reports belonging to a student
@app.get("/students/<int:student_id>/reports")
def get_student_reports(student_id):
    student = next(
        (s for s in students if s["id_s"] == student_id),
        None
    )

    if student is None:
        return {"error": "Student not found"}, 404

    return student["reports"], 200


# GET: Get one report by ID
@app.get("/report/<int:report_id>")
def get_report_by_id(report_id):
    for student in students:
        for report in student["reports"]:
            if report["id_r"] == report_id:
                return {"report": report}, 200

    return {"message": "Report not found"}, 404


# POST: Add a new student
@app.post("/students")
def add_student():
    request_data = request.get_json()

    new_id = max(
        (s["id_s"] for s in students),
        default=0
    ) + 1

    new_student = {
        "id_s": new_id,
        "Fname": request_data.get("Fname"),
        "Lname": request_data.get("Lname"),
        "reports": request_data.get("reports", [])
    }

    students.append(new_student)

    return new_student, 201


# POST: Add a report to a student
@app.post("/student/<int:student_id>")
def add_report(student_id):
    request_data = request.get_json()

    student = next(
        (s for s in students if s["id_s"] == student_id),
        None
    )

    if student is None:
        return {"error": "Student not found"}, 404

    new_report_id = max(
        (r["id_r"] for r in student["reports"]),
        default=0
    ) + 1

    new_report = {
        "id_r": new_report_id,
        "title": request_data.get("title"),
        "type": request_data.get("type")
    }

    student["reports"].append(new_report)

    return new_report, 201


if __name__ == "__main__":
    app.run(debug=True, port=5001)
```