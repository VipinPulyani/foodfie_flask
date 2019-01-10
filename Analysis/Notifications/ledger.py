import sys
import datetime
import pandas as pd
from pandas import ExcelWriter


def create_ledger(excelPath, startdate, enddate):

    data = [('Customer No.','Posting Date', 'Document Type', 'External Document No.', 'Description','Original Amount')]
    df = pd.read_excel(excelPath)
    startdate =  datetime.datetime.strptime(startdate, '%Y-%m-%d')
    enddate = datetime.datetime.strptime(enddate, '%Y-%m-%d')
    remainingAmount, closingBalance, count = 0, 0, 0

    for index, row in df.iterrows():
        if row[0] <= startdate:
            remainingAmount += row['Original Amount']
        elif row[0] >= startdate and row[0] <= enddate:
            if count == 0:
                data.append((
                    '',
                    '',
                    '',
                    '',
                    'Opening Balance'
                    ,remainingAmount
                            ))
                closingBalance += remainingAmount
            data.append((
                    row['Customer No.'],
                    datetime.datetime.strftime(row['Posting Date'], '%d-%m-%Y'),
                    row['Document Type'],
                    row['External Document No.'],
                    row['Description'],
                    row['Original Amount']
                        ))
            count += 1
            closingBalance += row['Original Amount']

    data.append((
                    '',
                    '',
                    '',
                    '',
                    'Closing Balance'
                    ,closingBalance
                            ))

    df1 = pd.DataFrame.from_records(data)

    writer = ExcelWriter('Ledger.xlsx')
    df1.to_excel(writer, sheet_name='Customer Ledger Entries', index=False, header=False)
    writer.save()


create_ledger(sys.argv[1], sys.argv[2], sys.argv[3])
