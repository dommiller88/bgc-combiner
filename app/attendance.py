import pandas as pd
import os
from datetime import datetime, timedelta

cal = {
    "January": "01",
    "February": "02",
    "March": "03",
    "April": "04",
    "May": "05",
    "June": "06",
    "July": "07",
    "August": "08",
    "September": "09",
    "October": "10",
    "November": "11",
    "December": "12"
}

def get_df_for_counting(df):
    df_for_counting = df.loc[:, 'Tags':]
    df_for_counting = df_for_counting.drop(columns=['Tags'])
    df_for_counting = df_for_counting.loc[:, ::2]
    return df_for_counting

def read_dates(pth_in):
    date_info = pd.read_excel(f'{pth_in}/{os.listdir(pth_in)[1]}', engine='openpyxl')
    date_ = date_info.columns[0]
    date_ = date_.split('for')[1].split('-')
    date1 = date_[0].strip().split(' ')
    date2 = date_[1].strip().split(' ')
    
    date1 = datetime.fromisoformat(f"{int(date1[2])}-{cal[date1[1].strip(',')]}-{date1[0]}")
    date2 = datetime.fromisoformat(f"{int(date2[2])}-{cal[date2[1].strip(',')]}-{date2[0]}")
    return (date1, date2)

def elapsed_business_days(date1, date2):
    # generating dates
    dates = (date1 + timedelta(idx + 1)
            for idx in range((date2 - date1).days))
    
    # summing all weekdays
    total_days = sum(1 for day in dates if day.weekday() < 5)
    if date2.weekday() < 5:
        total_days = total_days + 1
    return total_days

def generate_ADA(df, pth_in, pth_out):
    dates = read_dates(pth_in)
    df2 = df.loc[df['is_am'] == False]
    df2 = df2.drop_duplicates(subset=['IdXSite'])
    df2_splitter = df2.groupby(['Site'])
    ada_frames = []
    for group in df2_splitter.groups:
        cur = df2_splitter.get_group(group)
        days = get_df_for_counting(cur)
        cumulative = 0
        max_day = 0
        min_day = 1000
        off_days = 0
        indiv_days = []
        for i in range(len(days.columns)):
            if len(days[days.columns[i]].value_counts()) == 0:
                off_days = off_days + 1
            else:
                num = days[days.columns[i]].count()
                cumulative = cumulative + num
                indiv_days.append(num)
                if num > max_day:
                    max_day = num
                if num < min_day:
                    min_day = num
        ada = cumulative / (len(days.columns) - off_days)
        data = {
            'Site': [group],
            'ADA': [ada],
            'Max': [max_day],
            'Min': [min_day],
            'ADA_Std_Dev': [pd.Series(indiv_days).std()]
        }
        temp_df = pd.DataFrame(data=data)
        temp_df.set_index('Site', inplace=True)
        ada_frames.append(temp_df)
    complete = pd.concat(ada_frames).reset_index()
    complete.set_index('Site', inplace=True)
    exp_filename = f"{pth_out}/ADA_report-{dates[0]}-{dates[1]}.xlsx"
    exp = (complete, exp_filename)
    return exp

def generate_weekly_ADA(df, pth_in, pth_out, c):
    #make sure that data begins on a monday
    dates = read_dates(pth_in)
    base_cols = df.loc[:, :'Tags']
    base_cols = base_cols.reset_index(drop=True)
    if dates[0].weekday() != 0:
        print('\nError: please specify a date range beginning on a Monday')
        return    
    #make sure time frame is at least one complete week
    df_for_counting = get_df_for_counting(df)
    if len(df_for_counting.columns) < 7:
        print('\nError: For concatenation, please provide at least 7 days of attendance data.')
        return
    #round down into multiple of seven days
    num_remainder_cols = len(df_for_counting.columns) % 7
    df_complete_weeks = df_for_counting.iloc[:, :len(df_for_counting.columns) - num_remainder_cols]
    #split into each date window
    mondays = df_complete_weeks.columns.tolist()[::7]
    sundays = df_complete_weeks.columns.tolist()[6::7]
    frames = []
    for i in range(len(mondays)):
        #use ADA function
        print(base_cols.shape)
        print(df_complete_weeks.shape)
        to_join = df_complete_weeks.loc[:, mondays[i]:sundays[i]]
        to_join = to_join.reset_index(drop=True)
        cur = base_cols.join(to_join)
        cur_ada = generate_ADA(cur, pth_in, pth_out)[0]

        #take std deviation off and add date
        cur_ada = cur_ada.drop(columns=['ADA_Std_Dev'])
        cur_ada['Date'] = dates[0] + timedelta(days=7*i)
        frames.append(cur_ada)
    to_concat = pd.concat(frames)
    to_concat = to_concat.reset_index()
    prev_doc = pd.read_excel(c).reset_index(drop=True)
    final = pd.concat([prev_doc, to_concat]).reset_index(drop=True).to_excel(c, index=False)
    
    

        
    

def main(pth_in, pth_out, pth_filter, c):
    frames = []
    for filename in os.listdir(pth_in):
        if ".xlsx" in filename:
            df = pd.read_excel(f'{pth_in}/{filename}', engine='openpyxl')
            skip = 1
            while 'First Name' not in df:
                df = pd.read_excel(f'{pth_in}/{filename}', engine='openpyxl', skiprows=skip)
                skip = skip + 1
            df.fillna({"First Name": "", "Last Name": ""}, inplace=True)
        
            #Begin Transformations
            df = df.drop([0])

            
            #naming in and out columns
            for i in range(len(df.columns)):
                if "Unnamed" in df.columns[i]:
                    df.rename(columns = {df.columns[i]: f'{df.columns[i - 1]}.out'}, inplace=True)
                    df.rename(columns = {df.columns[i - 1]: f'{df.columns[i - 1]}.in'}, inplace=True)
            
            #add AM/PM data
            def find_string(row, string, string2):
                return any([string in str(cell) for cell in row]) and not any([string2 in str(cell) for cell in row])

            string = 'AM'
            string2 = 'PM'

            mask = df.apply(lambda row: find_string(row, string, string2), axis=1)

            df.insert(5, "is_am", mask)
            
            #Counting days attended
            df_for_counting = get_df_for_counting(df)
            cnt = (df_for_counting.count(axis=1) - 1)
            cnt = cnt.clip(0)
            df.insert(5, "Days Attended", cnt)
            
            #adding full name
            df["First Name"] = df["First Name"].astype(str)
            df["Last Name"] = df["Last Name"].astype(str)
            full_name = df["First Name"] + " " + df["Last Name"]
            df.insert(2, "Full Name", full_name)
            
            #Grab site name
            df2 = pd.read_excel(f'{pth_in}/{filename}', engine='openpyxl', skiprows=1)
            site = None
            if 'nuner' in df2.columns[0].lower():
                site = '306- Nuner Fine Arts Academy'
            else:
                site = df2.columns[0]
            
            df.insert(0, "Site", site)
            
            idxsite = df['Record ID'].astype(str) + '-' + df['Site'].astype(str).str[:3]
            df.insert(5, "IdXSite", idxsite)
            
            #Check for Dups
            dup_check = df["IdXSite"].duplicated()
            df.insert(5, "Duplicate", dup_check)

            #Add is_active
            df_filter = pd.read_excel(pth_filter)
            # print(df_filter['IdXSite'])
            # print(df['IdXSite'])
            is_active = df.apply(lambda x: df_filter['IdXSite'].str.contains(x['IdXSite']).any(), axis=1)
            df.insert(5, 'is_active', is_active)
            
            frames.append(df)
    combined = pd.concat(frames)
    
    
    combined.sort_values(by=['Site', 'First Name']).to_excel(f"{pth_out}/attendance_data_combined-{datetime.today()}.xlsx", index=False)
    ada = generate_ADA(combined, pth_in, pth_out)
    ada[0].to_excel(ada[1])
    if c:
        generate_weekly_ADA(combined, pth_in, pth_out, c)


if __name__ == "__main__":
    main()


    