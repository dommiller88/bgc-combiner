#!/Users/dommiller88/.pyenv/versions/3.7.3/bin/python
#1. remove unnecessary fields
#2. save to proper paths
# deal with parent3 info not always being avail
#3. create new field
#4. combine
import pandas as pd
import os
from datetime import datetime
import sys

def main(pth_in, pth_out):
    frames = []
    for filename in os.listdir(pth_in):
        print(filename)
        if ".xlsx" in filename and 'Identifier' not in filename:
            df = pd.read_excel(f'{pth_in}/{filename}', engine='openpyxl', skiprows=2)
            
            #some files have an address line. If so, re-read
            if 'First Name' not in df:
                df = pd.read_excel(f'{pth_in}/{filename}', engine='openpyxl', skiprows=3)
            
            # #pick out only keys we want
            # selected_keys = ["First Name", "Last Name", "Room", "Parent1 First Name", "Parent1 Last Name", "Parent1 Email", "Parent1 Mobile Phone", "Parent2 First Name", "Parent2 Last Name", "Parent2 Email", "Parent2 Mobile Phone",]
            # df_reshaped = df[selected_keys]
            
            #Grab site name
            df['Site'] = filename[:3]
            df['IdXSite'] = df['Record ID'] + '-' + df['Site']
            
            frames.append(df)
    combined = pd.concat(frames)
    out_name = f"{pth_out}/site_data_combined_{datetime.today()}.xlsx"
    combined.sort_values(by=['Site', 'First Name']).to_excel(out_name, index=False)
    print(out_name)


if __name__ == "__main__":
    main()