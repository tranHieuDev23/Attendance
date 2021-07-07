from typing import Optional, List
from tempfile import TemporaryDirectory
from os import path
from fastapi import FastAPI, UploadFile, Response
from fastapi.params import File, Form
from starlette.responses import HTMLResponse
from attendance import handle_attendance


def create_app():
    app = FastAPI()

    @app.get("/")
    async def index():
        with open(path.join("frontend", "index.html")) as html_file:
            return HTMLResponse(html_file.read())

    @app.post("/api/check-attendance")
    async def check_attendance(
            class_list_file: UploadFile = File(...),
            csv_files: List[UploadFile] = File(...),
            min_attendance_minute: Optional[str] = Form(None)):
        """Using data from CSV files, export an attendance Excel file.

        Arguments:
        - **class_list_file**: A CSV file containing information about students in the class.
        - **csv_files**: CSV files containing information about students' attendance.
        - **min_attendance_minute**: Minimum time of attendance required, in minute. If left blank,
        will use 1/3 of the average attendance time of all student.
        """
        try:
            min_attendance_second = float(min_attendance_minute) * 60
        except:
            min_attendance_second = None

        with TemporaryDirectory() as tmpdirname:
            excel_filepath = path.join(tmpdirname, "Attendance Scores.xlsx")
            handle_attendance(class_list_file, csv_files,
                              min_attendance_second, excel_filepath)

            with open(excel_filepath, "rb") as excel_file:
                headers = {
                    "Content-Disposition": 'attachment; filename="Attendance score_fixed.xlsx"'
                }
                return Response(
                    content=excel_file.read(),
                    headers=headers,
                    media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    return app
