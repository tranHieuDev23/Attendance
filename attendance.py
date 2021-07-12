from typing import List
from io import BytesIO
from fastapi import UploadFile
import pandas as pd
from chardet import detect


def handle_attendance(
        class_list_file: UploadFile,
        csv_files: List[UploadFile],
        min_attendance_second: float,
        output_path: str):
    excel_engine = 'xlrd' if class_list_file.filename.endswith(
        '.xls') else 'openpyxl'
    class_list_file_bytes = class_list_file.file.read()
    class_list = pd.read_excel(
        BytesIO(class_list_file_bytes), engine=excel_engine)
    # If CTSV format
    if 'MSSV' in class_list.columns and 'Tên sinh viên' in class_list.columns:
        class_list = class_list[['MSSV', 'Tên sinh viên']]
    # If qldt format
    else:
        class_list = pd.read_excel(
            BytesIO(class_list_file_bytes), header=1, engine=excel_engine)
        if 'StudentId' in class_list.columns and 'StudentName' in class_list.columns:
            class_list = class_list[['StudentId', 'StudentName']]
            class_list.rename(
                columns={'StudentId': 'MSSV', 'StudentName': 'Tên sinh viên'}, inplace=True)

    class_lst_time_details = class_list.copy()

    def to_seconds(t):
        sec = 0
        h = t.find('h')
        m = t.find('m')
        s = t.find('s')
        if s != -1:
            sec += int(t[t.rfind(' ') + 1:s])
        if h != -1:
            sec += int(t[:h]) * 3600
        if m != -1:
            sec += int(t[t[:m].rfind(' ') + 1: m]) * 60
        return sec

    for csv_file in csv_files:
        csv_file_byte = csv_file.file.read()
        csv_file_encoding = detect(csv_file_byte)
        # read meeting info
        info_df = pd.read_csv(
            BytesIO(csv_file_byte),
            encoding=csv_file_encoding['encoding'],
            skiprows=range(0, 1),
            nrows = 2,
            sep=None,
            engine="python")
        meeting_info = ''
        for _, row in info_df.iterrows():
            tmp = row[1]
            meeting_info += (tmp if tmp.find(',') < 0 else tmp[:tmp.find(',')]) + ' '

        # read attendance data
        dataframe = pd.read_csv(
            BytesIO(csv_file_byte),
            encoding=csv_file_encoding['encoding'],
            skiprows=range(0, 6),
            sep=None,
            engine="python")
        dataframe = dataframe[dataframe['Role'] != 'Organizer']
        id_list = []
        times = []
        for _, row in dataframe.iterrows():
            try:
                temp = row[0]
                if temp.endswith('M'):
                    stud_id = '20' + temp[-7:]
                else:
                    stud_id = '20' + temp[-6:]
                id_list.append(stud_id)
                times.append(to_seconds(row[3]))
            except:
                continue

        summary = pd.DataFrame({'mssv': id_list, 'time': times}).groupby(
            'mssv').sum().reset_index()
        sum_list = summary.values.tolist()
        time_list = []

        for _, student in class_list.iterrows():
            found = 0
            mssv = student[0]
            for pair in sum_list:
                if str(mssv) == pair[0]:
                    found = pair[1]
                    break
            time_list.append(found)

        class_lst_time_details[csv_file.filename] = time_list

        if min_attendance_second is None:
            avg_time = summary[summary['time'] > 0]['time'].mean()
            min_attendance_second = avg_time / 3

        time_list = ['+' if t > min_attendance_second else '-' for t in time_list]
        class_list[csv_file.filename] = time_list
    
    class_list['Số buổi vắng'] = class_list.apply(lambda row: sum(row[2:] == '-'), axis = 1)

    with pd.ExcelWriter(output_path) as writer:
        class_list.to_excel(writer, sheet_name = 'Attendance report')
        class_lst_time_details.to_excel(writer, sheet_name = 'Attendance Time Details')
