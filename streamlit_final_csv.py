import pandas as pd
from pandas import DataFrame
import datetime as dt
from datetime import date,timedelta,datetime
import plotly.express as px
import streamlit as st
import mysql.connector
from mysql.connector import errorcode
from pandas import DataFrame
from sqlalchemy import create_engine
import pymysql

st.set_page_config(layout="wide")

df1 = pd.read_csv('latest.csv')

df1.rename(
        columns={0: 'incident_date', 1: 'incident_parent', 2: 'location', 3: 'neighborhood', 4: 'council_district',
                 5: 'police_district'}, inplace=True)

df1['incident_date'] = pd.to_datetime(df1['incident_date'])
df1['incident_date_only'] = df1['incident_date'].dt.date
df1['incident_parent'] = df1['incident_parent'].astype('string')
df1['neighborhood'] = df1['neighborhood'].astype('string')
df1['council_district'] = df1['council_district'].astype('string')
df1['police_district'] = df1['police_district'].astype('string')

select_page = st.sidebar.selectbox('Page', ('Predictions', 'Past Statistics'))
if select_page == 'Predictions':
    pass
elif select_page == 'Past Statistics':
    frequency = ['Last 14 days', 'Last 1 month', 'Last 6 months']
    select_frequency = st.sidebar.radio('Select Frequency', frequency)
    col1, col2 = st.beta_columns([3, 1.9])
    col3, col4 = st.beta_columns([1, 0.7])
    if select_frequency == 'Last 14 days':
        df_14_days = df1[(df1['incident_date_only'] >= pd.Timestamp(2021, 3, 3) - timedelta(14))]
        geo_unit = ['Police District', 'Council District', 'Neighborhood']
        select_geo_regions = st.sidebar.selectbox('Select the Geographical region', geo_unit)

        if select_geo_regions == 'Police District':
            # Line trend
            a = pd.DataFrame(df_14_days.groupby(['incident_date_only', 'police_district']).agg('count'))
            a.reset_index(inplace=True)

            police_district = list(a['police_district'].unique())
            select_pol_district = col1.multiselect('Select Police District(s)', police_district,
                                                       default=['District A'])

            a.dropna(inplace=True)
            a = a.reindex(
                    columns=['incident_date_only', 'police_district', 'incident_parent'])
            a.rename(columns={'incident_parent': 'no_of_crimes'}, inplace=True)

            df_14_days_1 = a.copy()
            df_14_days_1.dropna(inplace=True)
            df_14_days_1 = df_14_days_1[df_14_days_1['police_district'].isin(select_pol_district)]

            if len(df_14_days_1) != 0:
                fig = px.scatter(df_14_days_1, x='incident_date_only', y='no_of_crimes',
                                     color=df_14_days_1['police_district'], height=548,
                                     width=620)
            else:
                fig = px.scatter(a, x='incident_date_only', y='no_of_crimes',
                                     color=a['police_district'], height=548, width=620)

            fig.update_traces(mode='lines')
            fig.update_layout(
                    title={
                        'text': "Past trend in the last 14 days",
                        'y': 1,
                        'x': 0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'}
                )

            col3.plotly_chart(fig)

            # bar chart
            d = pd.DataFrame(df_14_days.groupby(['incident_parent', 'police_district']).agg('count'))
            d.reset_index(inplace=True)

            o = pd.DataFrame(df_14_days.groupby(['police_district']).agg('count'))
            o.reset_index(inplace=True)

            inc_type = list(d['incident_parent'].unique())
            inc_type.insert(0, 'All')
            select_inc_type = col2.selectbox('Select type of Incident', inc_type)

            o.dropna(inplace=True)
            o = o.reindex(
                    columns=['incident_parent', 'police_district', 'location'])
            o.rename(columns={'location': 'no_of_crimes'}, inplace=True)

            df_14_days_1 = d.copy()
            df_14_days_1 = d.mask(d['incident_parent'] != select_inc_type)
            df_14_days_1.dropna(inplace=True)
            df_14_days_1 = df_14_days_1.reindex(columns=['incident_parent', 'police_district', 'location'])
            df_14_days_1.rename(columns={'location': 'no_of_crimes'}, inplace=True)

            if select_inc_type == 'All':
                fig = px.bar(o, x='police_district', y='no_of_crimes',
                                 height=545,
                                 width=495)

            else:
                fig = px.bar(df_14_days_1, x='police_district', y='no_of_crimes',
                                 height=545, width=495)

            fig.update_layout(bargap=0.5)
            col4.plotly_chart(fig)

        elif select_geo_regions == 'Council District':
            # Line Trend
            b = pd.DataFrame(df_14_days.groupby(['incident_date_only', 'council_district']).agg('count'))
            b.reset_index(inplace=True)

            council_district = list(b['council_district'].unique())
            select_council_district = col1.multiselect('Select Council District(s)', council_district,
                                                           default=['DELAWARE'])

            b.dropna(inplace=True)
            b = b.reindex(
                    columns=['incident_date_only', 'council_district', 'incident_parent'])
            b.rename(columns={'incident_parent': 'no_of_crimes'}, inplace=True)

            df_14_days_1 = b.copy()
            df_14_days_1.dropna(inplace=True)
            df_14_days_1 = df_14_days_1[df_14_days_1['council_district'].isin(select_council_district)]

            if len(df_14_days_1) != 0:
                fig = px.scatter(df_14_days_1, x='incident_date_only', y='no_of_crimes',
                                     color=df_14_days_1['council_district'], height=500,
                                     width=630)
            else:
                fig = px.scatter(b, x='incident_date_only', y='no_of_crimes',
                                     color=b['council_district'], height=500, width=630)

            fig.update_traces(mode='lines')
            fig.update_layout(
                    title={
                        'text': "Past trend in the last 14 days",
                        'y': 1,
                        'x': 0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'}
                )
            col3.plotly_chart(fig)

            # bar chart
            e = pd.DataFrame(df_14_days.groupby(['incident_parent', 'council_district']).agg('count'))
            e.reset_index(inplace=True)

            n = pd.DataFrame(df_14_days.groupby(['council_district']).agg('count'))
            n.reset_index(inplace=True)

            inc_type = list(e['incident_parent'].unique())
            inc_type.insert(0, 'All')
            select_inc_type = col2.selectbox('Select type of Incident', inc_type)

            n.dropna(inplace=True)
            n = n.reindex(
                    columns=['incident_parent', 'council_district', 'location'])
            n.rename(columns={'location': 'no_of_crimes'}, inplace=True)

            df_14_days_1 = e.copy()
            df_14_days_1 = e.mask(e['incident_parent'] != select_inc_type)
            df_14_days_1.dropna(inplace=True)
            df_14_days_1 = df_14_days_1.reindex(columns=['incident_parent', 'council_district', 'location'])
            df_14_days_1.rename(columns={'location': 'no_of_crimes'}, inplace=True)

            if select_inc_type == 'All':
                fig = px.bar(n, x='council_district', y='no_of_crimes',
                                 height=505,
                                 width=500)

            else:
                fig = px.bar(df_14_days_1, x='council_district', y='no_of_crimes',
                                 height=505, width=500)

            fig.update_layout(bargap=0.5)
            col4.plotly_chart(fig)

        elif select_geo_regions == 'Neighborhood':
            # Line Trend
            c = pd.DataFrame(df_14_days.groupby(['incident_date_only', 'neighborhood']).agg('count'))
            c.reset_index(inplace=True)

            neighborhood = list(c['neighborhood'].unique())
            select_neighborhood = col1.multiselect('Select Neighborhood', neighborhood, default=['Central Park'])

            c.dropna(inplace=True)
            c = c.reindex(
                    columns=['incident_date_only', 'neighborhood', 'incident_parent'])
            c.rename(columns={'incident_parent': 'no_of_crimes'}, inplace=True)

            df_14_days_1 = c.copy()
            df_14_days_1.dropna(inplace=True)
            df_14_days_1 = df_14_days_1[df_14_days_1['neighborhood'].isin(select_neighborhood)]
            if len(df_14_days_1) != 0:
                fig = px.scatter(df_14_days_1, x='incident_date_only', y='no_of_crimes',
                                     color=df_14_days_1['neighborhood'], height=500,
                                     width=630)
            else:
                fig = px.scatter(c, x='incident_date_only', y='no_of_crimes',
                                     color=c['neighborhood'], height=500, width=630)
            fig.update_traces(mode='lines')
            fig.update_layout(
                    title={
                        'text': "Past trend in the last 14 days",
                        'y': 1,
                        'x': 0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'}
                )
            col3.plotly_chart(fig)

            # bar chart
            f = pd.DataFrame(df_14_days.groupby(['incident_parent', 'neighborhood']).agg('count'))
            f.reset_index(inplace=True)

            m = pd.DataFrame(df_14_days.groupby(['neighborhood']).agg('count'))
            m.reset_index(inplace=True)

            inc_type = list(f['incident_parent'].unique())
            inc_type.insert(0, 'All')
            select_inc_type = col2.selectbox('Select type of Incident', inc_type)

            m.dropna(inplace=True)
            m = m.reindex(
                    columns=['incident_parent', 'neighborhood', 'location'])
            m.rename(columns={'location': 'no_of_crimes'}, inplace=True)

            df_14_days_1 = f.copy()
            df_14_days_1 = f.mask(f['incident_parent'] != select_inc_type)
            df_14_days_1.dropna(inplace=True)
            df_14_days_1 = df_14_days_1.reindex(columns=['incident_parent', 'neighborhood', 'location'])
            df_14_days_1.rename(columns={'location': 'no_of_crimes'}, inplace=True)

            if select_inc_type == 'All':
                fig = px.bar(m, x='neighborhood', y='no_of_crimes',
                                 height=570,
                                 width=500)

            else:
                fig = px.bar(df_14_days_1, x='neighborhood', y='no_of_crimes',
                                 height=570, width=500)

            fig.update_layout(bargap=0.5)
            col4.plotly_chart(fig)

    elif select_frequency == 'Last 1 month':
        df_1_month = df1[(df1['incident_date_only'] >= pd.Timestamp(2021, 3, 3) - timedelta(30))]
        geo_unit = ['Police District', 'Council District', 'Neighborhood']
        select_geo_regions = st.sidebar.selectbox('Select the Geographical region', geo_unit)
        if select_geo_regions == 'Police District':
            # Line trend
            a = pd.DataFrame(df_1_month.groupby(['incident_date_only', 'police_district']).agg('count'))
            a.reset_index(inplace=True)

            police_district = list(a['police_district'].unique())
            select_pol_district = col1.multiselect('Select Police District(s)', police_district,
                                                       default=['District A'])

            a.dropna(inplace=True)
            a = a.reindex(
                    columns=['incident_date_only', 'police_district', 'incident_parent'])
            a.rename(columns={'incident_parent': 'no_of_crimes'}, inplace=True)

            df_1_month_1 = a.copy()
            df_1_month_1.dropna(inplace=True)
            df_1_month_1 = df_1_month_1[df_1_month_1['police_district'].isin(select_pol_district)]

            if len(df_1_month_1) != 0:
                fig = px.scatter(df_1_month_1, x='incident_date_only', y='no_of_crimes',
                                     color=df_1_month_1['police_district'], height=500,
                                     width=630)
            else:
                fig = px.scatter(a, x='incident_date_only', y='no_of_crimes',
                                     color=a['police_district'], height=500, width=630)
            fig.update_traces(mode='lines')
            fig.update_layout(
                    title={
                        'text': "Past trend in the last 30 days",
                        'y': 1,
                        'x': 0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'}
                )
            col3.plotly_chart(fig)

            # bar chart
            d = pd.DataFrame(df_1_month.groupby(['incident_parent', 'police_district']).agg('count'))
            d.reset_index(inplace=True)

            l = pd.DataFrame(df_1_month.groupby(['police_district']).agg('count'))
            l.reset_index(inplace=True)

            inc_type = list(d['incident_parent'].unique())
            inc_type.insert(0, 'All')
            select_inc_type = col2.selectbox('Select type of Incident', inc_type)

            l.dropna(inplace=True)
            l = l.reindex(
                    columns=['incident_parent', 'police_district', 'location'])
            l.rename(columns={'location': 'no_of_crimes'}, inplace=True)

            df_1_month_1 = d.copy()
            df_1_month_1 = d.mask(d['incident_parent'] != select_inc_type)
            df_1_month_1.dropna(inplace=True)
            df_1_month_1 = df_1_month_1.reindex(columns=['incident_parent', 'police_district', 'location'])
            df_1_month_1.rename(columns={'location': 'no_of_crimes'}, inplace=True)

            if select_inc_type == 'All' or len(df_1_month_1) == 0:
                fig = px.bar(l, x='police_district', y='no_of_crimes',
                                 height=498,
                                 width=500)

            else:
                fig = px.bar(df_1_month_1, x='police_district', y='no_of_crimes',
                                 height=498, width=500)

            fig.update_layout(bargap=0.5)
            col4.plotly_chart(fig)

        elif select_geo_regions == 'Council District':
            # Line Trend
            b = pd.DataFrame(df_1_month.groupby(['incident_date_only', 'council_district']).agg('count'))
            b.reset_index(inplace=True)

            council_district = list(b['council_district'].unique())
            select_pol_district = col1.multiselect('Select Council District(s)', council_district,
                                                       default=['DELAWARE'])

            b.dropna(inplace=True)
            b = b.reindex(
                    columns=['incident_date_only', 'council_district', 'incident_parent'])
            b.rename(columns={'incident_parent': 'no_of_crimes'}, inplace=True)

            df_1_month_1 = b.copy()
            df_1_month_1.dropna(inplace=True)
            df_1_month_1 = df_1_month_1[df_1_month_1['council_district'].isin(select_pol_district)]
            if len(df_1_month_1) != 0:
                fig = px.scatter(df_1_month_1, x='incident_date_only', y='no_of_crimes',
                                     color=df_1_month_1['council_district'], height=500,
                                     width=630)
            else:
                fig = px.scatter(b, x='incident_date_only', y='no_of_crimes',
                                     color=b['council_district'], height=500, width=630)
            fig.update_traces(mode='lines')
            fig.update_layout(
                    title={
                        'text': "Past trend in the last 14 days",
                        'y': 1,
                        'x': 0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'}
                )
            col3.plotly_chart(fig)

            # bar chart
            e = pd.DataFrame(df_1_month.groupby(['incident_parent', 'council_district']).agg('count'))
            e.reset_index(inplace=True)

            k = pd.DataFrame(df_1_month.groupby(['council_district']).agg('count'))
            k.reset_index(inplace=True)

            inc_type = list(e['incident_parent'].unique())
            inc_type.insert(0, 'All')
            select_inc_type = col2.selectbox('Select type of Incident', inc_type)

            k.dropna(inplace=True)
            k = k.reindex(
                    columns=['incident_parent', 'council_district', 'location'])
            k.rename(columns={'location': 'no_of_crimes'}, inplace=True)

            df_1_month_1 = e.copy()
            df_1_month_1 = e.mask(e['incident_parent'] != select_inc_type)
            df_1_month_1.dropna(inplace=True)
            df_1_month_1 = df_1_month_1.reindex(columns=['incident_parent', 'council_district', 'location'])
            df_1_month_1.rename(columns={'location': 'no_of_crimes'}, inplace=True)

            if select_inc_type == 'All':
                fig = px.bar(k, x='council_district', y='no_of_crimes',
                                 height=503,
                                 width=500)

            else:
                fig = px.bar(df_1_month_1, x='council_district', y='no_of_crimes',
                                 height=503, width=500)

            fig.update_layout(bargap=0.5)
            col4.plotly_chart(fig)

        elif select_geo_regions == 'Neighborhood':
            # Line Trend
            c = pd.DataFrame(df_1_month.groupby(['incident_date_only', 'neighborhood']).agg('count'))
            c.reset_index(inplace=True)

            neighborhood = list(c['neighborhood'].unique())
            select_neighborhood = col1.multiselect('Select Neighborhood', neighborhood, default=['Central Park'])

            c.dropna(inplace=True)
            c = c.reindex(
                    columns=['incident_date_only', 'neighborhood', 'incident_parent'])
            c.rename(columns={'incident_parent': 'no_of_crimes'}, inplace=True)

            df_1_month_1 = c.copy()
            df_1_month_1.dropna(inplace=True)
            df_1_month_1 = df_1_month_1[df_1_month_1['neighborhood'].isin(select_neighborhood)]
            if len(df_1_month_1) != 0:
                fig = px.scatter(df_1_month_1, x='incident_date_only', y='no_of_crimes',
                                     color=df_1_month_1['neighborhood'], height=500,
                                     width=630)
            else:
                fig = px.scatter(c, x='incident_date_only', y='no_of_crimes',
                                     color=c['neighborhood'], height=500, width=630)
            fig.update_traces(mode='lines')
            fig.update_layout(
                    title={
                        'text': "Past trend in the last 14 days",
                        'y': 1,
                        'x': 0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'}
                )
            col3.plotly_chart(fig)

            # bar chart
            f = pd.DataFrame(df_1_month.groupby(['incident_parent', 'neighborhood']).agg('count'))
            f.reset_index(inplace=True)

            j = pd.DataFrame(f.groupby(['neighborhood']).agg('count'))
            j.reset_index(inplace=True)

            inc_type = list(f['incident_parent'].unique())
            inc_type.insert(0, 'All')
            select_inc_type = col2.selectbox('Select type of Incident', inc_type)

            j.dropna(inplace=True)
            j = j.reindex(
                    columns=['incident_parent', 'neighborhood', 'location'])
            j.rename(columns={'location': 'no_of_crimes'}, inplace=True)

            df_1_month_1 = f.copy()
            df_1_month_1 = f.mask(f['incident_parent'] != select_inc_type)
            df_1_month_1.dropna(inplace=True)
            df_1_month_1 = df_1_month_1.reindex(columns=['incident_parent', 'neighborhood', 'location'])
            df_1_month_1.rename(columns={'location': 'no_of_crimes'}, inplace=True)

            if select_inc_type == 'All':
                fig = px.bar(j, x='neighborhood', y='no_of_crimes',
                                 height=570,
                                 width=500)

            else:
                fig = px.bar(df_1_month_1, x='neighborhood', y='no_of_crimes',
                                 height=570, width=500)

            fig.update_layout(bargap=0.5)
            col4.plotly_chart(fig)

    elif select_frequency == 'Last 6 months':
        df_6_months = df1[(df1['incident_date_only'] >= pd.Timestamp(2021, 3, 3) - timedelta(180))]
        geo_unit = ['Police District', 'Council District', 'Neighborhood']
        select_geo_regions = st.sidebar.selectbox('Select the Geographical region', geo_unit)
        if select_geo_regions == 'Police District':
            # Line trend
            a = pd.DataFrame(df_6_months.groupby(['incident_date_only', 'police_district']).agg('count'))
            a.reset_index(inplace=True)

            police_district = list(a['police_district'].unique())
            select_pol_district = col1.multiselect('Select Police District(s)', police_district,
                                                       default=['District A'])

            a.dropna(inplace=True)
            a = a.reindex(
                    columns=['incident_date_only', 'police_district', 'incident_parent'])
            a.rename(columns={'incident_parent': 'no_of_crimes'}, inplace=True)

            df_6_months_1 = a.copy()
            df_6_months_1.dropna(inplace=True)
            df_6_months_1 = df_6_months_1[df_6_months_1['police_district'].isin(select_pol_district)]

            if len(df_6_months_1) != 0:
                fig = px.scatter(df_6_months_1, x='incident_date_only', y='no_of_crimes',
                                     color=df_6_months_1['police_district'], height=500,
                                     width=630)
            else:
                fig = px.scatter(a, x='incident_date_only', y='no_of_crimes',
                                     color=a['police_district'], height=500, width=630)
            fig.update_traces(mode='lines')
            fig.update_layout(
                    title={
                        'text': "Past trend in the last 30 days",
                        'y': 1,
                        'x': 0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'}
                )
            col3.plotly_chart(fig)

            # bar chart
            d = pd.DataFrame(df_6_months.groupby(['incident_parent', 'police_district']).agg('count'))
            d.reset_index(inplace=True)

            i = pd.DataFrame(df_6_months.groupby(['police_district']).agg('count'))
            i.reset_index(inplace=True)

            inc_type = list(d['incident_parent'].unique())
            inc_type.insert(0, 'All')
            select_inc_type = col2.selectbox('Select type of Incident', inc_type)

            i.dropna(inplace=True)

            i = i.reindex(
                    columns=['incident_parent', 'police_district', 'location'])
            i.rename(columns={'location': 'no_of_crimes'}, inplace=True)

            df_6_months_1 = d.copy()
            df_6_months_1 = d.mask(d['incident_parent'] != select_inc_type)
            df_6_months_1.dropna(inplace=True)
            df_6_months_1 = df_6_months_1.reindex(columns=['incident_parent', 'police_district', 'location'])
            df_6_months_1.rename(columns={'location': 'no_of_crimes'}, inplace=True)

            if select_inc_type == 'All':
                fig = px.bar(i, x='police_district', y='no_of_crimes',
                                 height=500,
                                 width=500)

            else:
                fig = px.bar(df_6_months_1, x='police_district', y='no_of_crimes',
                                 height=500, width=500)

            fig.update_layout(bargap=0.5)
            col4.plotly_chart(fig)

        elif select_geo_regions == 'Council District':
            # Line Trend
            b = pd.DataFrame(df_6_months.groupby(['incident_date_only', 'council_district']).agg('count'))
            b.reset_index(inplace=True)

            council_district = list(b['council_district'].unique())
            select_pol_district = col1.multiselect('Select Council District(s)', council_district,
                                                       default=['DELAWARE'])

            b.dropna(inplace=True)
            b = b.reindex(
                    columns=['incident_date_only', 'council_district', 'incident_parent'])
            b.rename(columns={'incident_parent': 'no_of_crimes'}, inplace=True)

            df_6_months_1 = b.copy()
            df_6_months_1.dropna(inplace=True)
            df_6_months_1 = df_6_months_1[df_6_months_1['council_district'].isin(select_pol_district)]
            if len(df_6_months_1) != 0:

                fig = px.scatter(df_6_months_1, x='incident_date_only', y='no_of_crimes',
                                     color=df_6_months_1['council_district'], height=500,
                                     width=630)
            else:
                fig = px.scatter(b, x='incident_date_only', y='no_of_crimes',
                                     color=b['council_district'], height=500, width=630)
            fig.update_traces(mode='lines')
            fig.update_layout(
                    title={
                        'text': "Past trend in the last 14 days",
                        'y': 1,
                        'x': 0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'}
                )
            col3.plotly_chart(fig)

            # bar chart
            e = pd.DataFrame(df_6_months.groupby(['incident_parent', 'council_district']).agg('count'))
            e.reset_index(inplace=True)

            h = pd.DataFrame(df_6_months.groupby(['council_district']).agg('count'))
            h.reset_index(inplace=True)

            inc_type = list(e['incident_parent'].unique())
            inc_type.insert(0, 'All')
            select_inc_type = col2.selectbox('Select type of Incident', inc_type)

            h.dropna(inplace=True)
            h = h.reindex(
                    columns=['incident_parent', 'council_district', 'location'])
            h.rename(columns={'location': 'no_of_crimes'}, inplace=True)

            df_6_months_1 = e.copy()
            df_6_months_1 = e.mask(e['incident_parent'] != select_inc_type)
            df_6_months_1.dropna(inplace=True)
            df_6_months_1 = df_6_months_1.reindex(columns=['incident_parent', 'council_district', 'location'])
            df_6_months_1.rename(columns={'location': 'no_of_crimes'}, inplace=True)

            if select_inc_type == 'All':
                fig = px.bar(h, x='council_district', y='no_of_crimes',
                                 height=500,
                                 width=500)

            else:
                fig = px.bar(df_6_months_1, x='council_district', y='no_of_crimes',
                                 height=500, width=500)

            fig.update_layout(bargap=0.5)
            col4.plotly_chart(fig)

        elif select_geo_regions == 'Neighborhood':
            # Line Trend
            c = pd.DataFrame(df_6_months.groupby(['incident_date_only', 'neighborhood']).agg('count'))
            c.reset_index(inplace=True)

            neighborhood = list(c['neighborhood'].unique())
            select_neighborhood = col1.multiselect('Select Neighborhood', neighborhood, default=['Central Park'])

            c.dropna(inplace=True)
            c = c.reindex(
                    columns=['incident_date_only', 'neighborhood', 'incident_parent'])
            c.rename(columns={'incident_parent': 'no_of_crimes'}, inplace=True)

            df_6_months_1 = c.copy()
            df_6_months_1.dropna(inplace=True)
            df_6_months_1 = df_6_months_1[df_6_months_1['neighborhood'].isin(select_neighborhood)]
            if len(df_6_months_1) != 0:
                fig = px.scatter(df_6_months_1, x='incident_date_only', y='no_of_crimes',
                                     color=df_6_months_1['neighborhood'], height=500,
                                     width=630)
            else:
                fig = px.scatter(c, x='incident_date_only', y='no_of_crimes',
                                     color=c['neighborhood'], height=500, width=630)
            fig.update_traces(mode='lines')
            fig.update_layout(
                    title={
                        'text': "Past trend in the last 14 days",
                        'y': 1,
                        'x': 0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'}
                )
            col3.plotly_chart(fig)

            # bar chart
            f = pd.DataFrame(df_6_months.groupby(['incident_parent', 'neighborhood']).agg('count'))
            f.reset_index(inplace=True)

            g = pd.DataFrame(df_6_months.groupby(['neighborhood']).agg('count'))
            g.reset_index(inplace=True)

            inc_type = list(f['incident_parent'].unique())
            inc_type.insert(0, 'All')
            select_inc_type = col2.selectbox('Select type of Incident', inc_type)
            g.dropna(inplace=True)
            g = g.reindex(
                    columns=['neighborhood', 'location'])
            g.rename(columns={'location': 'no_of_crimes'}, inplace=True)

            df_6_months_1 = f.copy()
            df_6_months_1 = f.mask(f['incident_parent'] != select_inc_type)
            df_6_months_1.dropna(inplace=True)
            df_6_months_1 = df_6_months_1.reindex(columns=['incident_parent', 'neighborhood', 'location'])
            df_6_months_1.rename(columns={'location': 'no_of_crimes'}, inplace=True)

            if select_inc_type == 'All':
                fig = px.bar(g, x='neighborhood', y='no_of_crimes',
                                 height=570,
                                 width=500)

            else:
                fig = px.bar(df_6_months_1, x='neighborhood', y='no_of_crimes',
                                 height=570, width=500)

            fig.update_layout(bargap=0.5)
            col4.plotly_chart(fig)



