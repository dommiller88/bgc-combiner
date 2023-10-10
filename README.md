ombine

BGC Combiner is a tool for transforming and combining data from ProCare.  This can be used for individual reports, aggregate ADA data, and concatenating aggregate data on to existing documents.

## Installation

This program is designed to run on Linux, MacOs, and Windows Subsystem for Linux.
You will need to be sure that you have installed Python.

## Usage
In general, the tools will use pattern
```bash
bgcombine <command> <output_path> [--c <path_to_concatenate>]
```
### Commands
#### Info
Info is used for combining student and family data from ProCare (in the "all format"). It will also create an IdXSite field for unique multi-site identification along with the name of the site for each student. The function **requires** all source files to be prefixed with the site number. E.g. "101monthly_attendance_data" for the O.C.
#### Attendance
Attendance is used for combining attendance data from ProCare. It will create a by-student attendance count as well as a duplicated check, along with the IdXSite field for multi-site identification.  Attendance also generates an ADA report and can be combined with the --c option to concatenate that information onto an existing historical data document.
### Arguments
#### output_path
The repository for combined output files. Do not specify a file name at this time.
#### input_path
Once a command is entered, a user will see the following prompt:
```bash
Enter path to input folder:
```
User should input the absolute path to a directory that holds all of the ProCare files for the intended operation.

### Options
#### Concatenate (--c)
Concatenate is an option used to append ADA data to an existing document along with datestamps of when that info was generated.  Its argument is the path to the file that should be concatenated.
#### Filtered (--filtered)
Filtered is an option to use a site data file created with command Info as a filter on procare data.  It will populate the "is_active" field with true or false values based on if the students in the attendance file exist in the given site data file.


## License

[MIT](https://choosealicense.com/licenses/mit/)
