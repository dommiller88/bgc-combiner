import pandas as pd
import os
from datetime import datetime, timedelta
import re

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
    #Remove all columns other than Those to the right of Tags
    df_for_counting = df.loc[:, 'Tags':]
    df_for_counting = df_for_counting.drop(columns=['Tags'])

    #Select alternating columns to eliminate the "out" columns
    df_for_counting = df_for_counting.loc[:, ::2]
    return df_for_counting

def get_df_for_checking(df):
    df_for_checking = df.loc[:, 'Tags':]
    df_for_checking = df_for_checking.drop(df_for_checking.columns[[0, 1]], axis=1)
    df_for_checking = df_for_checking.iloc[:, ::2]
    return df_for_checking

def read_dates(pth_in):
    #Read source file and parce dates out of row 1
    date_info = pd.read_excel(f'{pth_in}/{os.listdir(pth_in)[0]}', engine='openpyxl')
    date_ = date_info.columns[0]
    date_ = date_.split('for')[1].split('-')
    date1 = date_[0].strip().split(' ')
    date2 = date_[1].strip().split(' ')
    
    date1 = datetime.fromisoformat(f"{int(date1[2])}-{cal[date1[1].strip(',')]}-{date1[0]}")
    date2 = datetime.fromisoformat(f"{int(date2[2])}-{cal[date2[1].strip(',')]}-{date2[0]}")
    return (date1, date2)

def get_error_count(df):
    df_for_checking = get_df_for_checking(df)
    dash_outs = 0
    bulk_sign_outs = 0
    for i in range(len(df_for_checking.columns)):
        col_name = df_for_checking.columns[i]
        col = df_for_checking.loc[~df_for_checking[col_name].astype(str).str.contains('AM')]
        dash_outs += col.loc[col[col_name].astype(str).str.contains("--")].shape[0]
        time_stripped = col.iloc[:, i].astype(str).apply(lambda x: extract_time_from_string(x))
        dup_check = time_stripped.value_counts()
        print(dup_check)
        bulk_sign_outs += dup_check[dup_check >= 10].sum()
    return (dash_outs, bulk_sign_outs)


def generate_ADA(df, pth_in, pth_out, am):
    #dates = read_dates(pth_in)
    dates = (datetime.now(), datetime.now())
    #filter out am columns or non-am columns based on options passed
    if am:
        df2 = df
    else:
        df2 = df.loc[df['is_am'] == False]

    #Split rows into groups by Site
    # df2 = df2.drop_duplicates(subset=['IdXSite'])
    df2_splitter = df2.groupby(['Site', 'Age Band'])
    sites_only_splitter = df2.groupby(['Site'])
    ada_frames = []
    for group in df2_splitter.groups:
        weekday_dict = {
            0: [0, 0],
            1: [0, 0],
            2: [0, 0],
            3: [0, 0],
            4: [0, 0],
            5: [0, 0],
            6: [0, 0], 
        }
        cur = df2_splitter.get_group(group)

        #Calculate average duration of stay
        minute_count_df = cur.loc[cur['Average Time In'] != 0]
        minute_avg = minute_count_df['Average Time In'].mean()

        days = get_df_for_counting(cur)
        cumulative = 0
        max_day = 0
        min_day = 1000
        off_days = 0
        indiv_days = [] 
        day_of_week = dates[0].weekday()
        for i in range(len(days.columns)):
            site_only_df = get_df_for_counting(sites_only_splitter.get_group(group[0]))
            #Account for vacation days
            if am and days[days.columns[i]].astype(str).str.count('AM').sum() == 0:
                off_days = off_days + 1
            elif len(site_only_df[site_only_df.columns[i]].value_counts()) == 0:
                off_days = off_days + 1
            else:
                #Add attendance for day to cumulative period total
                if am:
                    num = days[days.columns[i]].astype(str).str.count('AM').sum()
                    print(num)
                else:
                    num = days[days.columns[i]].count()
                cumulative = cumulative + num
                indiv_days.append(num)
                weekday_dict[day_of_week][0] += num
                weekday_dict[day_of_week][1] += 1
                #Check to see if current day is min or max of period total.
                if num > max_day:
                    max_day = num
                if num < min_day:
                    min_day = num
            if day_of_week == 6:
                day_of_week = 0
            else:
                day_of_week += 1
        ada = 0
        if len(days.columns) - off_days > 0:
            ada = cumulative / (len(days.columns) - off_days)
        weekday_avgs = []
        for val in weekday_dict.values():
            if val[1] == 0:
                weekday_avgs.append(0)
            else:
                weekday_avgs.append(val[0] / val[1])

        print(f"Checking Errors for {group}\n\n\n")
        # error_counts = get_error_count(cur)
        
        #Create df from current group and append to combined ADA df.
        data = {
            'Site': [group],
            'ADA': [ada],
            'Max': [max_day],
            'Min': [min_day],
            'ADA_Std_Dev': [pd.Series(indiv_days).std()],
            'Average Time In': [minute_avg],
            'Monday Average': [weekday_avgs[0]],
            'Tuesday Average': [weekday_avgs[1]],
            'Wednesday Average': [weekday_avgs[2]],
            'Thursday Average': [weekday_avgs[3]],
            'Friday Average': [weekday_avgs[4]],
            # 'No Sign Outs': [error_counts[0]],
            # 'Bulk Sign Outs': [error_counts[1]]
        }
        temp_df = pd.DataFrame(data=data)
        temp_df.set_index('Site', inplace=True)
        ada_frames.append(temp_df)
    complete = pd.concat(ada_frames).reset_index()
    complete.set_index('Site', inplace=True)
    exp_filename = f"{pth_out}/ADA_report-{dates[0]}-{dates[1]}.xlsx"
    exp = (complete, exp_filename)
    return exp

#TODO: make this work with the new error checking methods
#No Longer should this pre-chop days.
def generate_weekly_ADA(df, pth_in, pth_out, c, am):
    #make sure that data begins on a monday
    dates = read_dates(pth_in)
    base_cols = df.loc[:, :'Tags']
    base_cols = base_cols.reset_index(drop=True)
    if dates[0].weekday() != 0:
        print('\nError: please specify a date range beginning on a Monday')
        return    
    #make sure time frame is at least one complete week
    df_for_counting = df.loc[:, 'Tags':].drop(columns=['Tags'])
    if len(df_for_counting.columns) < 14:
        print('\nError: For concatenation, please provide at least 7 days of attendance data.')
        return
    #round down into multiple of seven days
    num_remainder_cols = len(df_for_counting.columns) % 14
    df_complete_weeks = df_for_counting.iloc[:, :len(df_for_counting.columns) - num_remainder_cols]
    #split into each date window
    mondays = df_complete_weeks.columns.tolist()[::14]
    print(mondays)
    sundays = df_complete_weeks.columns.tolist()[13::14]
    frames = []
    for i in range(len(mondays)):
        #use ADA function
        to_join = df_complete_weeks.loc[:, mondays[i]:sundays[i]]
        to_join = to_join.reset_index(drop=True)
        cur = base_cols.join(to_join)
        print(f'CHECK----------------------------------\ncolumns = {cur.columns}\n\n\n')
        cur_ada = generate_ADA(cur, pth_in, pth_out, am)[0]
        #take std deviation off and add date
        cur_ada = cur_ada.drop(columns=['ADA_Std_Dev'])
        cur_ada['Date'] = dates[0] + timedelta(days=7*i)
        frames.append(cur_ada)
    to_concat = pd.concat(frames)
    to_concat = to_concat.reset_index()
    prev_doc = pd.read_excel(c).reset_index(drop=True)
    print(prev_doc.dtypes)
    print(to_concat.dtypes)
    final = pd.concat([prev_doc, to_concat.astype(prev_doc.dtypes)], axis=0).to_excel(c, index=False)

def extract_time_from_string(input_string):
    # Define a regular expression pattern to match the time
    time_pattern = re.compile(r'\b(\d{1,2}:\d{2}(?: [APMapm]+)?)\b')

    # Search for the pattern in the input string
    if type(input_string) == str:
        match = time_pattern.search(input_string)
    else:
        return None

    if match:
        # Extract the matched time and parse it into a datetime object
        matched_time = match.group(1)
        parsed_time = datetime.strptime(matched_time, '%I:%M %p')  # Adjust the format if needed
        return parsed_time
    else:
        return None  # Return None if no time is found in the string

def time_elapse(row):
    total_mins = 0
    day_count = 0
    for i in range(0, len(row), 2):
        print(row.iloc[i])
        time_in = extract_time_from_string(row.iloc[i])
        time_out = extract_time_from_string(row.iloc[i + 1])
        if time_in and time_out:
            day_count += 1
            delta = time_out - time_in
            total_mins += delta.seconds / 60
    if day_count == 0:
        return 0
    else:
        return total_mins / day_count



def average_time_in(df):
    df_for_counting = df.loc[:, 'Tags':]
    df_for_counting = df_for_counting.drop(columns=['Tags'])
    df_for_counting['Average Time In'] = df_for_counting.apply(lambda x: time_elapse(x), axis=1)
    return df_for_counting['Average Time In']

def count_zeroes(df, pth_in, pth_out):
    dates = read_dates(pth_in)
    zero_cnt = df.loc[df['Days Attended'] == 0, :'Tags']
    zero_cnt['Date'] = dates[0]
    zero_cnt.sort_values('Site').to_excel(f'{pth_out}/zero_attendance-{dates[0]}-{dates[1]}.xlsx', index=False)

def main(pth_in, pth_out, filtered, c, am):
    if not pth_out:
        pth_out = os.getcwd()
    # frames = []
    # for filename in os.listdir(pth_in):
    #     if ".xlsx" in filename:
    #         df = pd.read_excel(f'{pth_in}/{filename}', engine='openpyxl')
    #         skip = 1
    #         while 'First Name' not in df:
    #             df = pd.read_excel(f'{pth_in}/{filename}', engine='openpyxl', skiprows=skip)
    #             skip = skip + 1
    #         df.fillna({"First Name": "", "Last Name": ""}, inplace=True)
        
    #         #Begin Transformations
    #         df = df.drop([0])

            
    #         #naming in and out columns
    #         for i in range(len(df.columns)):
    #             if "Unnamed" in df.columns[i]:
    #                 df.rename(columns = {df.columns[i]: f'{df.columns[i - 1]}.out'}, inplace=True)
    #                 df.rename(columns = {df.columns[i - 1]: f'{df.columns[i - 1]}.in'}, inplace=True)
            
    #         #add AM/PM data
    #         def find_string(row, string, string2):
    #             return any([string in str(cell) for cell in row]) and not any([string2 in str(cell) for cell in row])

    #         string = 'AM'
    #         string2 = 'PM'

    #         mask = df.apply(lambda row: find_string(row, string, string2), axis=1)

    #         df.insert(5, "is_am", mask)
            
    #         #Counting days attended
    #         df_for_counting = get_df_for_counting(df)
    #         cnt = (df_for_counting.count(axis=1))
    #         cnt = cnt.clip(0)
    #         df.insert(5, "Days Attended", cnt)
            
    #         #adding full name
    #         df["First Name"] = df["First Name"].astype(str)
    #         df["Last Name"] = df["Last Name"].astype(str)
    #         full_name = df["First Name"] + " " + df["Last Name"]
    #         df.insert(2, "Full Name", full_name)
            
    #         #Grab site name
    #         df2 = pd.read_excel(f'{pth_in}/{filename}', engine='openpyxl', skiprows=1)
    #         site = None
    #         if 'nuner' in df2.columns[0].lower():
    #             site = '306- Nuner Fine Arts Academy'
    #         else:
    #             site = df2.columns[0]
            
    #         df.insert(0, "Site", site)
            
    #         idxsite = df['Record ID'].astype(str) + '-' + df['Site'].astype(str).str[:3]
    #         df.insert(5, "IdXSite", idxsite)
            
    #         #Check for Dups
    #         dup_check = df["IdXSite"].duplicated()
    #         df.insert(5, "Duplicate", dup_check)

    #         #Add is_active
    #         is_active = pd.Series()
    #         if filtered:
    #             df_filter = pd.read_excel(filtered)
    #             is_active = df.apply(lambda x: df_filter['IdXSite'].str.contains(x['IdXSite']).any(), axis=1)
    #         df.insert(5, 'is_active', is_active)
            
    #         frames.append(df)
    # print(len(frames))
    # # if len(frames) == 1:
    # #     combined = frames[0]
    # # else:
    # combined = pd.concat(frames)
    
    # combined.insert(5, 'Average Time In', average_time_in(combined))
    # combined.sort_values(by=['Site', 'First Name']).to_excel(f"{pth_out}/attendance_data_combined-{datetime.today()}.xlsx", index=False)

    combined = pd.read_excel(pth_in)
    ada = generate_ADA(combined, pth_in, pth_out, am)
    ada[0].to_excel(ada[1])
    if c:
        generate_weekly_ADA(combined, pth_in, pth_out, c, am)
    #count_zeroes(combined, pth_in, pth_out)


if __name__ == "__main__":
    main()


    