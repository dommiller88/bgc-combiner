import pandas as pd
from datetime import datetime
from datetime import date
from datetime import timedelta
from datetime import time
import os
import numpy as np
from dateutil.relativedelta import relativedelta
from pprint import pprint
import yaml

def get_last_day(dt):
    first = dt.replace(day=1)
    last_month = first - timedelta(days=1)
    return datetime.combine(last_month, time())

def get_dict_count(unit_dict):
    add = 0
    for k in unit_dict.keys():
        add = add + unit_dict[k]
    return add

def is_teen(is_term_1, is_summer, dob):
    if pd.isnull(dob):
        return 0
    true_dob = datetime.strptime(str(dob), "%Y-%m-%d %H:%M:%S")
    return 1 if relativedelta(get_last_day(date.today()), true_dob).years >= 13 and relativedelta(get_last_day(date.today()), true_dob).years < 20 else 0
    #Code below for "dynamic age". Turn this on instead of the line above to calculate age based on which term a student last attended.
    # if is_term_1 == 1:
    #     return 1 if relativedelta(datetime(2023, 5, 26), true_dob).years >= 13 and relativedelta(datetime(2023, 5, 26), true_dob).years < 20 else 0
    # elif is_summer == 1:
    #     return 1 if relativedelta(datetime(2023, 7, 21), true_dob).years >= 13 and relativedelta(datetime(2023, 7, 21), true_dob).years < 20 else 0
    # else:
    #     return 1 if relativedelta(get_last_day(date.today()), true_dob).years >= 13 and relativedelta(get_last_day(date.today()), true_dob).years < 20 else 0
    
def calc_age(is_term_1, is_summer, is_term_2, dob, settings):
    if pd.isnull(dob):
        return np.nan 
    split_date_1 = settings['config']['end_dates']['term_1'].split('-')
    split_date_summer = settings['config']['end_dates']['summer'].split('-')
    split_date_2 = settings['config']['end_dates']['term_2'].split('-')
    true_dob = datetime.strptime(str(dob), "%Y-%m-%d %H:%M:%S")
    if is_term_1 == 1 and settings['config']['current_year'] != 1:
        return relativedelta(datetime(int(split_date_1[0]), int(split_date_1[1]), int(split_date_1[2])), true_dob).years
    elif is_summer == 1 and settings['config']['current_year'] != 2:
        return relativedelta(datetime(int(split_date_summer[0]), int(split_date_summer[1]), int(split_date_summer[2])), true_dob).years
    elif is_term_2 == 1 and settings['config']['current_year'] != 3:
        return relativedelta(datetime(int(split_date_2[0]), int(split_date_2[1]), int(split_date_2[2])), true_dob).years
    else:
        return relativedelta(get_last_day(date.today()), true_dob).years
    

#TODO: add tiebreaker function for students with 2+ sites in the current term.
def main(pth_in, pth_out, show_blacklist, config):
    if not config:
        print("No config file specified. Please pass the path to a config.yaml file by using the --config option.")
        return
    settings = yaml.safe_load(open(config))
    if not pth_out:
        pth_out = os.getcwd()
    df = pd.read_excel(pth_in)
    #Whitelist for lily counting
    units = settings['config']['units']
    #units = ['101', '102', '110', '201', '202', '204', '303', '304', '305', '306', '307', '308', '401', '402', '403', '404', '405', '406', '407', '501', '502', '504', '601', '602', '603', '701', '503', '205', '411']
    df = df.loc[:,:'All Groups']
    df['All Groups'] = df['All Groups'].fillna('0')
    #Disclude 301 and 000
    df = df[(~df['All Groups'].astype(str).str.contains('301')) & (~df['All Groups'].astype(str).str.contains('000'))]
    df['mem_unique'] = df['Membership Number'].astype(str) + df['Member Full Name']
    grps = df.groupby(['mem_unique'])


    unit_dict = dict.fromkeys(units, 0)
    unsorted = []
    df_for_merging = pd.DataFrame(columns=['mem_unique', 'is_term_1', 'is_summer', 'is_term_2', 'used_tag'])
    year_no = settings['config']['current_year'][-2:]
    for x in grps.groups:
        prefix = None
        cur = grps.get_group(x)
        
        #Normal tagging process. Can be updated. Reads tags to see most recently tagged program
        a = cur.loc[cur['All Groups'].str.contains(str(int(year_no) + 1))]
        b = cur.loc[cur['All Groups'].str.contains('Summer') & (cur['All Groups'].str.contains(year_no))]
        c = cur.loc[(cur['All Groups'].str.contains(str(int(year_no) - 1))) & (cur['All Groups'].str.contains(year_no))]
        found = False
        if a.shape[0] > 0:
            for index, row in a.iterrows():
                if (row['All Groups'][:3] in unit_dict and settings['config']['current_term'] != 3) or (row['All Groups'][:3] in unit_dict and settings['config']['current_term'] == 3 and row['All Groups'][:3] == str(row['Unit'])):
                    prefix = row['All Groups'][:3]
                    df_temp = pd.DataFrame(data={'mem_unique': [x], 'is_term_1': [0], 'is_summer': [0], 'is_term_2': [1], 'used_tag': [row['All Groups']]})
                    df_for_merging = pd.concat([df_for_merging, df_temp], ignore_index=True)
                    found = True
                    unit_dict[prefix] = unit_dict[prefix] + 1
                    break
        if b.shape[0] > 0 and found == False:
            for index, row in b.iterrows():
                if (row['All Groups'][:3] in unit_dict and settings['config']['current_term'] != 2) or (row['All Groups'][:3] in unit_dict and settings['config']['current_term'] == 2 and row['All Groups'][:3] == str(row['Unit'])):
                    prefix = row['All Groups'][:3]
                    df_temp = pd.DataFrame(data={'mem_unique': [x], 'is_term_1': [0], 'is_summer': [1], 'is_term_2': [0], 'used_tag': [row['All Groups']]})
                    df_for_merging = pd.concat([df_for_merging, df_temp], ignore_index=True)
                    found = True
                    unit_dict[prefix] = unit_dict[prefix] + 1
                    break
        if c.shape[0] > 0 and found == False:
            for index, row in c.iterrows():
                if (row['All Groups'][:3] in unit_dict and settings['config']['current_term'] != 1) or (row['All Groups'][:3] in unit_dict and settings['config']['current_term'] == 1 and row['All Groups'][:3] == str(row['Unit'])): 
                    prefix = row['All Groups'][:3]
                    df_temp = pd.DataFrame(data={'mem_unique': [x], 'is_term_1': [1], 'is_summer': [0], 'is_term_2': [0], 'used_tag': [row['All Groups']]})
                    df_for_merging = pd.concat([df_for_merging, df_temp], ignore_index=True)
                    found = True
                    unit_dict[prefix] = unit_dict[prefix] + 1
                    break
        if found == False:
            unsorted.append(cur.iloc[0]['Member Full Name'])
        
    df_no_dups = df.drop_duplicates(subset=['mem_unique'])
    merged = df_no_dups.merge(df_for_merging, on='mem_unique', how='inner')
    counted_students = get_dict_count(unit_dict)
    num_students = df_for_merging.shape[0]
    if counted_students != num_students:
        print(f'\n----------------------WARNING-----------------------------\nNot all students were sorted!\n\nTotal number of Students: {num_students}\nNumber of Counted Students: {counted_students}\n\nList of students not counted:\n{unsorted}\n----------------------WARNING-----------------------------\n')

    print(f'\nCount by site:\n\n')
    pprint(unit_dict)
    print(f'\nTotal: {counted_students}') 

    #Show unsorted members if option is selected
    if show_blacklist:
        print('Members not shown: \n')
        pprint(unsorted)
        unsorted = pd.Series(unsorted)
        unsorted.to_excel(f'{pth_out}/blacklist_{datetime.now()}.xlsx')


    
    merged['is_teen'] = merged.apply(lambda x: is_teen(x['is_term_1'], x['is_summer'], x['Date of Birth (Member)']), axis=1)
    merged['age_as_of_last_term_attended'] = merged.apply(lambda x: calc_age(x['is_term_1'], x['is_summer'], x['is_term_2'], x['Date of Birth (Member)'], settings), axis=1)
    merged.to_excel(f'{pth_out}/cumulative_count_{datetime.now()}.xlsx')

    df_teens = merged.loc[merged['is_teen'] == 1]
    grps = df_teens.groupby(['mem_unique'])

    unit_dict_teens = dict.fromkeys(units, 0)
    unsorted = []
    #Do a teen head count
    for x in grps.groups:
        cur = grps.get_group(x)
        if cur.iloc[0]['used_tag'][:3] in unit_dict_teens:
            prefix = cur.iloc[0]['used_tag'][:3]
            unit_dict_teens[prefix] = unit_dict_teens[prefix] + 1  
    print(f'\nCount of teens by site:\n\n')
    pprint(unit_dict_teens)
    df_teens.to_excel(f'{pth_out}/teens_{datetime.now()}.xlsx')
    counted_teens = get_dict_count(unit_dict_teens)
    num_teens = df_teens.shape[0]
    if counted_teens != num_teens:
        print(f'\n----------------------WARNING-----------------------------\nNot all teens were sorted!\n\nTotal number of teens: {num_teens}\nNumber of Counted teens: {counted_teens}\n\nList of teens not counted:\n{unsorted}\n----------------------WARNING-----------------------------\n')
    print(f'\nTotal Teens: {counted_teens}')

