#!/Users/dommiller88/.pyenv/versions/3.7.3/bin/python
#1. remove unnecessary fields
#2. save to proper paths
# deal with parent3 info not always being avail
#3. create new field
#4. combine
import pandas as pd
import os
import click
from datetime import datetime
import sys

@click.command()
@click.argument('pth_out')
def main(pth_out):
    pth_in = click.prompt("\n--------------------------------------------------\nenter path to child and family data input folder")
    frames = []
    for filename in os.listdir(pth_in):
        if ".xlsx" in filename:
            df = pd.read_excel(f'{pth_in}/{filename}', engine='openpyxl', skiprows=3)
            
            #some files have an address line. If so, re-read
            if 'Id' not in df:
                df = pd.read_excel(f'{pth_in}/{filename}', engine='openpyxl', skiprows=4)
            
            #pick out only keys we want
            selected_keys = ["First Name", "Last Name", "Tags", 'Dob']
            df_reshaped = df[selected_keys]
            
            #Grab site name
            df2 = pd.read_excel(f'{pth_in}/{filename}', engine='openpyxl', skiprows=1)
            df_reshaped['Site'] = df2.columns[0]
            
            frames.append(df_reshaped)
    combined = pd.concat(frames)
    combined.sort_values(by=['Site', 'First Name']).to_excel(f"{pth_out}/site_data_combined_{datetime.today()}.xlsx", index=False)


if __name__ == "__main__":
    main()