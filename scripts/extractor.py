import os
import pandas as pd

# List Directory
list_of_contents = os.listdir()
dir_list = []

# Create list of subdirectories that contain yearly stats
for item in list_of_contents:
    if os.path.isdir(item):
        dir_list.append(item)

for year_files in dir_list:
    # ensure Grade Report and register folder exist
    if os.path.exists(year_files+'\\GradeExport.xlsx') and os.path.exists(year_files+'\\registers'):
        # Open Grade Report
        gradesExport = pd.read_excel(year_files+'\\GradeExport.xlsx')

        # List all files inside register folder
        list_of_registers = [os.path.join(year_files+'\\registers', file) for file in os.listdir(year_files+'\\registers')]

        # Iterate over each found register file
        for register in list_of_registers:
            register_file = open(register, "r")

            # Create empty column then rename with register name
            gradesExport = gradesExport.assign(R=None)
            gradesExport = gradesExport.rename(columns={"R": register})

            # Whilst data to read from register
            while True:
                # Get student name and attendance record for that register
                student_name = register_file.readline()
                attendance = register_file.readline().strip()

                # if name and record are false then at the end of the file - break loop
                if not student_name or not attendance:
                    break #EOF

                # Student number is first item
                student_id = int(student_name.split()[0])

                # Grab row from dataframe
                row = gradesExport.loc[gradesExport["USERNAME"] == student_id]
                # If row is empty - ignore entry - cannot find student grade details
                if row.empty:
                    continue

                # If non attendance - included not required and absense - record as 0
                # Record 1 if attended
                # Raise exception if unexpected record (catch for options in attendance software)
                if attendance == 'Not Attended' or attendance == 'Not Required' or attendance == 'Notified Absence':
                    gradesExport.at[row.index, register] = 0
                elif attendance == 'Attended':
                    gradesExport.at[row.index, register] = 1
                else:
                    raise Exception('Opps, {} does not have an understood entry'.format(student_name))

            # close register
            register_file.close()
        # Once all registers added to Grade Report - save
        gradesExport.to_excel(year_files+'\\GradeReport.xlsx')