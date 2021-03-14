import mysql.connector
import pandas as pd
from pandas import DataFrame
import datetime as dt
from datetime import date,timedelta,datetime
import plotly.express as px
import streamlit as st

mydb = mysql.connector.connect(
  host="caskeycoding.com",
  database="caskey5_buffaloCrime",
  user="caskey5_cassinEdwin",
  password="QD8HCCLN7P4y2Ft"
)
mycursor = mydb.cursor()

mycursor.execute('DESCRIBE full_incidents')
df = DataFrame(mycursor.fetchall())

mycursor.execute("Select * from full_incidents")
df1 = DataFrame(mycursor.fetchall())
df1.columns = df[0]
df1 = df1.sort_values(by = 'incident_date',ignore_index = True)



st.sidebar.selectbox('',('Predictions','Past Statistics'))
frequency = ['Last 14 days','Last 1 month','Last 6 months']
select_frequency= st.radio('Select Frequency',frequency)
geo_unit = ['Police District', 'Council District', 'Neighborhood']
select_geo_regions = st.selectbox('Select the Geographical region',geo_unit)
police_district = df1['police_district'].unique()
select_pol_district = st.selectbox('Select Police District',police_district)
