import os
import pandas as pd
import hashlib

# List Directory
list_of_contents = os.listdir()
dir_list = []

def formatUsername(x):
    return hashlib.sha256(str(x).encode('utf-8')).hexdigest()

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

    # Once all registers added to Grade Report - Calculate attendance, calculate e.attendance, practical attendance, lecture attendance
    # Get number of columns and reduce by three
    col_list = list(gradesExport)
    col_list.remove('USERNAME')
    col_list.remove('GRADE')
    col_list.remove('SYMBOL')

    prac_a_list = []
    prac_b_list = []
    lec_list = []

    # Create column name list for Practicals Group A and B + Lecture Group
    for item in col_list:
        if "Practical1" in item or "Group A" in item:
            prac_a_list.append(item)
        elif "Practical2" in item or "Group B" in item:
            prac_b_list.append(item)
        else:
            lec_list.append(item)

    if len(prac_a_list) != len(prac_b_list):
        print("Different number of A and B practicals")
 
    # Create attendance percentage
    gradesExport['ATTENDANCE PERCENT'] = round((gradesExport[col_list].sum(axis=1) / len(col_list)) * 100.0, 0)
    # Expected Attendance Percentage
    gradesExport['ATTENDANCE EXPECTED PERCENT'] = round((gradesExport[col_list].sum(axis=1) / (len(prac_a_list) + len(lec_list))) * 100.0, 0)
    # Practical Percentage
    gradesExport['PRACTICAL PERCENT'] = round((gradesExport[prac_a_list+prac_b_list].sum(axis=1) / len(prac_a_list)) * 100.0, 0)
    # Lecture Percent
    gradesExport['LECTURE PERCENT'] = round((gradesExport[lec_list].sum(axis=1) / len(lec_list)) * 100.0, 0)

    # Add MLS use number
    if os.path.exists(year_files+'\\Data.xlsx'):
        data_df = pd.read_excel(year_files+'\\Data.xlsx', 'VLE Use Per Student')
        username_df = gradesExport['USERNAME']
        new_column = pd.DataFrame(columns=['Student', 'Activity count'])
        for index, row in username_df.items():
            row_df = data_df.loc[data_df['Student'].str.contains(str(row))]
            new_column = new_column.append(row_df,ignore_index=True)
        new_column = new_column.drop('Student', axis=1)
        normalised_column = new_column
        new_column = new_column.rename(columns={"Activity count":"ACTIVITY COUNT"})
        normalised_column = normalised_column.rename(columns={"Activity count":"NORMALISED ACTIVITY COUNT"})
        normalised_column=(normalised_column-normalised_column.min())/(normalised_column.max()-normalised_column.min())
        new_column = new_column.join(normalised_column)
        gradesExport = gradesExport.join(new_column)

    # Save Report
    gradesExport = gradesExport.sample(frac=1).reset_index(drop=True)
    gradesExport['USERNAME'] = gradesExport['USERNAME'].map(formatUsername)
    gradesExport.to_csv('GradeReport{}.csv'.format(year_files), index=False)