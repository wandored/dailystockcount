"""
Enter purchases for Meat Count
"""

import pandas as pd
import PySimpleGUI as sg

# Define sales window contents


# def make_dataframe(x):
#    """Separates each store into it's own dataframe"""
#    df = meat_count.drop(meat_count[meat_count.Item != x].index)
#    return df


def removedups(x):
    """Turn the list into a dict then back to a list to remove duplicates"""
    return list(dict.fromkeys(x))


with open('./output/purchase.csv') as purc:
    purchase_items = pd.read_csv(purc)

# Define purchas window contents
layout_pur = [[sg.Text('Enter Purchases', font='ANY 15', size=(30, 2))]]
for index, row in purchase_items.iterrows():
    layout_pur += [[sg.Text(row['Item'])] +
                   [sg.Input(size=(10, 1), default_text=0)]]
layout_pur += [[sg.Button('Submit Purchases', key='-SUBMIT-')]]

window_pur = sg.Window('PURCHASES', layout_pur)

while True:
    event, values = window_pur.read()
    if event in (sg.WINDOW_CLOSED, '-SUBMIT-'):
        break
purch = []
for i in range(len(purchase_items)):
    purch.append(int(values[i]))
purchase_items['Case_Tot'] = purch
window_pur.close()
print(purchase_items)

purchase_items['Purchase_Tot'] = purchase_items.apply(
    lambda row: row.each * row.Case_Tot, axis=1)
print(purchase_items)
##
## meat_count.to_csv('./output/Meat_Count.csv', index=False, mode='w')
