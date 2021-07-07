from typing import List
from fastapi import UploadFile
import pandas as pd


def handle_attendance(
        class_list_file: UploadFile,
        csv_files: List[UploadFile],
        min_attendance_second: float,
        output_path: str):

    class_list = pd.read_csv(class_list_file.file, header=0)
    class_list = class_list[['Student ID', 'Name', 'Board', '31/3/2021']]

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
        dataframe = pd.read_csv(csv_file.file, header=6)
        dataframe = dataframe[dataframe['Role'] != 'Organizer']
        id_list = []
        times = []
        for _, row in dataframe.iterrows():
            temp = row[0]
            stud_id = '20' + temp[-6:]
            id_list.append(stud_id)
            times.append(to_seconds(row[3]))

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

        if min_attendance_second is None:
            avg_time = summary[summary['time'] > 0]['time'].mean()
            min_attendance_second = avg_time / 3

        time_list = ['+' if t >
                     min_attendance_second else '-' for t in time_list]
        class_list[csv_file.filename] = time_list

    with pd.ExcelWriter(output_path) as writer:
        class_list.to_excel(writer)
