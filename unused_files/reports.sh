#!/bin/zsh
echo "\nWelcome to report generator!"
dt=$(date '+%d:%m:%Y_%H-%M-%S')
if [ $# -eq 0 ];
then
    dt_string="report_output_${dt}"
    mkdir $dt_string
    set -- "$(pwd)/${dt_string}"
else
    if [ -d $1 ];
    then
        mkdir $1/report_output_${dt}
        set -- "$1/report_output_${dt}"
    else   
        echo "designated output path is not a directory!"
        exit 1
    fi
fi
out_path=python3 personal_info.py $1
python3 attendance.py $1 $out_path