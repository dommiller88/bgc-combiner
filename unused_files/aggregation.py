import pandas as pd
#total col
#distinct
df = pd.read_csv('/Users/dommiller88/Documents/bgc_reports/data/csv/site_data_combined.csv')
df2 = df.groupby(['Site'])[['Parent1 Name', 'Parent2 Name', 'Parent3 Name']].nunique().sum(axis=1).reset_index(name='Parents')
df3 = df.groupby(['Site'])[['Parent1 Phone', 'Parent2 Phone', 'Parent3 Phone']].nunique().sum(axis=1).reset_index(name='Phone')
df4 = df.groupby(['Site'])[['Parent1 Email', 'Parent2 Email', 'Parent3 Email']].nunique().sum(axis=1).reset_index(name='Email')
#df2['total_parents'] = df2[['Parent1 Name', 'Parent2 Name', 'Parent3 Name']].sum(axis=1)
df2.set_index('Site',inplace=True)
df3.set_index('Site',inplace=True)
df4.set_index('Site',inplace=True)
df5 = pd.concat([df2, df3, df4], axis=1).reset_index()
df5.to_csv('/Users/dommiller88/Documents/bgc_reports/data/csv/aggregate_sheet.csv')
