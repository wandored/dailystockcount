"""
Import R365 stock count detials and produce a variance report
"""

import json
from datetime import datetime
from datetime import date
import pandas as pd
import PySimpleGUI as sg


TODAY = date.today().strftime("%m/%d/%y")
TIME = datetime.time(datetime.now())

# Define the window's contents
times = ['Opening', 'Closing']
layout = [[sg.Text('Enter the Inventory Date {dd/mm/yy}')],
          [sg.Input(size=(30, 1), default_text=TODAY,
                    enable_events=True, key='-INPUT-')],
          [sg.Text('Select Opening or Closing count')],
          #          [sg.Listbox(times, size=(10, 2), select_mode='single',
          #                      enable_events=True, key='-LBOX-')],
          [sg.Radio('Opening', "RADIO1", default=False, key="-BUT1-")],
          [sg.Radio('Closing', "RADIO1", default=True, key="-BUT2-")],
          [sg.Button('CONFIRM')]]


window = sg.Window('Enter New Inventory', layout, size=(300, 300))


def removedups(x):
    """Turn the list into a dict then back to a list to remove duplicates"""
    return list(dict.fromkeys(x))


def make_dataframe(x):
    """Separates each store into it's own dataframe"""
    df = meat_count.drop(meat_count[meat_count.Item != x].index)
    return df


while True:
    # Call GUI
    event, values = window.read()
    if event in (sg.WIN_CLOSED, 'Exit'):
        break
    if event == 'CONFIRM':
        DATE = values['-INPUT-']
        try:  # strptime throws an exception if the input doesn't match the pattern
            datetime.strptime(DATE, "%m/%d/%y")
            if values['-BUT1-']:
                AM_PM = 'Opening'
            else:
                AM_PM = 'Closing'
            break
        except:
            sg.popup('Date is not correct, please try again')
window.close()

U_of_M = pd.read_csv('UofM.csv')
df_stock_count = pd.read_csv('Stock Count Sheet Export.csv', sep=',')
df_stock_count.drop(
    columns=(['StorageLocation', 'SLSort', 'ItemSort']), inplace=True)
with open('UofM.json') as f:
    u_of_m = json.load(f)

# Split dataframe into 3
stk_cnt1 = df_stock_count.drop(columns=(['UofM2', 'Qty2', 'UofM3', 'Qty3']))
stk_cnt2 = df_stock_count.drop(columns=(['UofM', 'Qty', 'UofM3', 'Qty3']))
stk_cnt3 = df_stock_count.drop(columns=(['UofM', 'Qty', 'UofM2', 'Qty2']))

# Merge each dataframe with UofM and calculate total each units
count1 = pd.merge(stk_cnt1, U_of_M, how='inner',
                  left_on='UofM', right_on='pack')
count1['Tot'] = count1['Qty'] * count1['each']
count1.drop(columns=['pack', 'ounce', 'Qty', 'each'], inplace=True)
count2 = pd.merge(stk_cnt2, U_of_M, how='inner',
                  left_on='UofM2', right_on='pack')
count2['Tot2'] = count2['Qty2'] * count2['each']
count2.drop(columns=['pack', 'ounce', 'Qty2', 'each'], inplace=True)
count3 = pd.merge(stk_cnt3, U_of_M, how='inner',
                  left_on='UofM3', right_on='pack')
count3['Tot3'] = count3['Qty3'] * count3['each']
count3.drop(columns=['pack', 'ounce', 'Qty3', 'each'], inplace=True)

# Merge back into 1 dataframe
values = {'Tot': 0, 'Tot2': 0, 'Tot3': 0}
count1 = pd.merge(count1, count2, how='left', on='Item')
count1 = pd.merge(count1, count3, how='left', on='Item')
count1.fillna(value=values, inplace=True)
count1.drop(columns=['UofM', 'UofM2', 'UofM3'], inplace=True)
count1['Count_Total'] = count1['Tot'] + count1['Tot2'] + count1['Tot3']
count1.drop(columns=['Tot', 'Tot2', 'Tot3'], inplace=True)

# Merge totals back into main dataframe
df_stock_count = pd.merge(df_stock_count, count1, how='left', on='Item')
df_stock_count['Date'] = DATE
df_stock_count['Open/Close'] = AM_PM
stock_count = df_stock_count.reindex(columns=['Date', 'Open/Close', 'Item',
                                              'UofM', 'Qty', 'UofM2', 'Qty2',
                                              'UofM3', 'Qty3', 'Count_Total'])
stock_count.to_csv('./output/Meat_Count.csv',
                   header=None, index=False, mode='a')

with open('./output/Meat_Count.csv') as mc:
    meat_count = pd.read_csv(mc)
    meat_count.drop_duplicates(subset=['Date', 'Open/Close',
                                       'Item'], keep='last', inplace=True)

item_list = meat_count['Item']
# item_list = removedups('item_list')
mc_dict = {item: make_dataframe(item) for item in item_list}
for item in item_list:
    df_item = mc_dict[item]
    df_item.drop(columns={'UofM', 'Qty', 'UofM2',
                 'Qty2', 'UofM3', 'Qty3'}, inplace=True)
    print(df_item)
    df_item['daily_var'] = df_item.apply(
        lambda row: row.Count_Total - row.df_item.loc[row.Date == str(row.date(-1))])
    print(df_item)

meat_count.to_csv('./output/Meat_Count.csv', index=False, mode='w')
