"""
Functionality for annotating files with new information.
"""

import pandas as pd
from sklearn.externals import joblib
import numpy as np

def hour_to_tod(hour):
    """
    Convert hour to time of day description: AM transition, day, PM transition,
    night.
    """
    if 5 <= hour < 9:
        return "AM Transition"
    if 9 <= hour < 17:
        return "Day"
    if 17 <= hour < 21:
        return "PM Transition"
    return "Night"


def message_to_type(msg):
    """
    Extract ALS or BLS from message.
    """
    if 'ALS' in msg:
        return 'ALS'
    return 'BLS'


def type_of_call_to_call_category(toc):
    """
    Transform type of call to a broader category.
    """
    if toc in ('Fall/injuries', 'MVA', 'Bleeding', 'Assault'):
        return 'Trauma'
    if toc in ('EDP', 'Medic Alert', 'Lift Assist', 'Intox', 'Standby', 'Unspecified'):
        return 'Other'
    return 'Medical'

def summarize(df, name, index):
    """
    Summarize a dataframe column by sorted value counts.
    """
    df_sum = pd.DataFrame(index=index)
    df_sum['Count'] = df[name].value_counts().astype(np.int64)
    df_sum.fillna(0, inplace=True)
    df_sum.reset_index(inplace=True)
    df_sum.columns = [name, 'Count']
    df_sum.sort_values(by='Count', ascending=False, inplace=True)
    return df_sum

def add_chart(df, writer, workbook, sheet_name, chart_series, chart_type, chart_title):
    """
    Create a new chart with values in df.
    """
    df.to_excel(writer, sheet_name=sheet_name, index=False)

    chart = workbook.add_chart({'type': chart_type,
                                'title': chart_title})
    chart.add_series({'values': chart_series})

    worksheet = workbook.get_worksheet_by_name(sheet_name)
    worksheet.insert_chart('D2', chart)

def annotate_file(infile, outfile, model_path):
    """
    Augment a dataframe with new columns 'Time of Day', 'Type', 'Type of Call',
    and 'Call Category'. In addition, add tables and charts summarizing type of
    call, call category, and time of day.
    """
    # read file - it has .xls extension but is .html
    df = pd.read_html(infile, header=0, parse_dates=['Date'])[0]

    # add time of day and type (als/bls)
    times = pd.to_datetime(df['Time'], format='%H:%M:%S')
    df['Time of Day'] = times.dt.hour.apply(hour_to_tod)
    df['Type'] = df['Message'].apply(message_to_type)

    # predict types of calls (cardiac, fall/injuries etc.)
    clf = joblib.load(model_path)
    df['Type of Call'] = clf.predict(df)

    # add call category (trauma/medical/other)
    df['Call Category'] = df['Type of Call'] \
        .apply(type_of_call_to_call_category)

    # reformat time and date
    df['Date'] = df['Date'] \
        .apply(lambda t: '{:02d}/{:02d}/{:02d}'.format(t.month, t.day, t.year))
    df['Time'] = times \
        .apply(lambda t: '{:02d}:{:02d}:{:02d}'.format(t.hour, t.minute, t.second))

    # generate auxiliary tables
    df_toc = summarize(df, 'Type of Call', clf.clf_.classes_)
    df_cc = summarize(df, 'Call Category', ['Medical', 'Trauma', 'Other'])
    df_tod = summarize(df, 'Time of Day', ['AM Transition', 'Day', 'PM Transition', 'Night'])

    # prepare new excel file, write primary data
    writer = pd.ExcelWriter(outfile, engine='xlsxwriter')
    workbook = writer.book
    df.to_excel(writer, sheet_name='Calls', index=False)

    # add charts
    # TOC chart
    add_chart(df_toc, writer, workbook, 'TOC', '=TOC!$B$1:$B$25', 'column', 'Type of Call')
    add_chart(df_cc, writer, workbook, 'CC', '=CC!$B$1:$B$4', 'pie', 'Call Category')
    add_chart(df_tod, writer, workbook, 'TOD', '=TOD!$B$1:$B$5', 'pie', 'Time of Day')

    # save
    writer.save()
