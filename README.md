
# BGCombine
BGCombine is a tool for transforming and combining data from ProCare and Vision.  This can be used for individual reports, aggregate ADA data, and concatenating aggregate data on to existing documents as well as for monthly Lily cumulative enrollment counts.

## Installation

This program is designed to run on Linux, MacOs, and Windows Subsystem for Linux.
You will need to be sure that you have installed Python.

## Usage
In general, the tools will use pattern
```bash
bgcombine <command> [--o <output_path> [other_options...]]
```
### Commands
#### Info
```bash
bgcombine info --o ~/output
```
Info is used for combining student and family data from ProCare (in the "all format"). It will also create an IdXSite field for unique multi-site identification along with the name of the site for each student. The function **requires** all source files to be prefixed with the site number. E.g. "101monthly_attendance_data" for the O.C. If no output path is specified, the current working directory will be used.
#### Attendance
```bash
bgcombine attendance --o ~/output --c ~/Documents/concat_doc.xlsx --filtered ~/Documents/info_data_2023.xlsx --am
```
Attendance is used for combining attendance data from ProCare. It will create a by-student attendance count as well as a duplicated check, along with the IdXSite field for multi-site identification.  Attendance also generates an ADA report and can be combined with the --c option to concatenate that information onto an existing historical data document.  If no output path is specified, the current working directory will be used.
#### Enrollment
```bash
bgcombine enrollment --o ~/output
```
Enrollment is used for getting the number of enrolled students by site for each site.  Any vision file may be used for this as long as it includes the fields Unit Code and Membership Number. Results are output to the console. If an output path is specified, the result will also be output to an Excel spreadsheet in the intended location.
#### Cumulative
```bash
bgcombine cumulative --o ~/output --blacklist
```
Cumulative is used for getting a cumulative count of students (by site and total) across a given time frame.  It is designed to be used with Vision data containing "Member Full Name", Membership Number, and All Groups.  The program prints individual unit counts for both general studetns and teen students to the console along with total counts for both of those categories.  In addition, information on both general students and teens will be outputted to an Excel file, including which term the students last attended for as well as the specific location and program of that attendance.  If no output path is specified, the current working directory will be used.
#### attendance_special
```bash
bgcombine attendance_special --o ~/output
```

Attendance Special is a special use case for attendance in the annual report.  It requires a pre-combined attendance file with an age-banding column based on the requirements of the annual report.  The program will output an ADA report by site by age band.

### Arguments
#### input_path
Once a command is entered, a user will see the following prompt:
```bash
Enter path to input folder:
```
User should input the **absolute** path to a directory that holds all of the ProCare files for the intended operation.

### Options
#### Before-Care Only (--am)
Option used for attendance command.  By default, before-care only members are not included in ADA.  This flag can be used to get ADA specifically for before-care.
#### Output Unsorted Members (--blacklist)
Option for use in the cumulative command.  List of unsorted members will be output to console and to a file in the specified output directory.
#### Concatenate (--c)
Concatenate is an option used to append ADA data to an existing document along with datestamps of when that info was generated.  Its argument is the path to the file that should be concatenated.
#### Filtered (--filtered)
Filtered is an option to use a site data file created with command Info as a filter on procare data.  It will populate the "is_active" field with true or false values based on if the students in the attendance file exist in the given site data file.
#### Output Path (--o)
The repository for combined output files. Do not specify a file name at this time.

## Note to Developers
Some portions of these programs may need to be amended as file types shift.  The most notable change will be to the cumulative.py file.  The start and end dates of terms are hard-coded in such as in: 
```python
def is_teen(is_term_1, is_summer, dob):
    if pd.isnull(dob):
        return 0
    true_dob = datetime.strptime(str(dob), "%Y-%m-%d %H:%M:%S")
    if is_term_1 == 1:
        return 1 if relativedelta(datetime(2023, 5, 26), true_dob).years >= 13 and relativedelta(datetime(2023, 5, 26), true_dob).years < 20 else 0
    elif is_summer == 1:
        return 1 if relativedelta(datetime(2023, 7, 21), true_dob).years >= 13 and relativedelta(datetime(2023, 7, 21), true_dob).years < 20 else 0
    else:
        return 1 if relativedelta(datetime(2023, 9, 30), true_dob).years >= 13 and relativedelta(datetime(2023, 9, 30), true_dob).years < 20 else 0
```
(similar code in the get_age function) 
The dates in the datetime objects will need to be amended.

Another amendment will be the list of units for cumulative count, defined at the beginning of the main function.
```python
 units = ['101', '102', '110', '201', '202', '303', '304', '305', '306', '307', '308', '401', '402', '403', '404', '405', '406', '407', '501', '502', '601', '602', '603', '701', '503', '205', '411']
```
The unit codes of included units must be kept up to date, because the entire count hinges on which sites should be counted.

## License

[MIT](https://choosealicense.com/licenses/mit/)
