import pandas as pd
from datetime import datetime

def main(pth_in, pth_out):
    df = pd.read_excel(pth_in)
    df = df.drop_duplicates(subset=['Membership Number'])
    df = df['Unit'].value_counts()
    df = df.sort_index()
    if pth_out:
        df.to_excel(f'{pth_out}/site_enrollment_counts_{datetime.now()}.xlsx')
    print(df)