#### Imports
import streamlit as st
import pandas as pd
import numpy as np


#### pagina indeling
st.set_page_config(layout="centered")

#### cache
@st.cache_data(show_spinner="Fao data laden")
def load_FAO(FAOSTAT_data):
  FAO_data = pd.read_csv(FAOSTAT_data)
  return FAO_data

@st.cache_data(show_spinner="Rampen laden")
def load_Disasters(disasters_data):
  Rampen = pd.read_csv(disasters_data, compression='zip')
  return Rampen

@st.cache_data(show_spinner="Pivotten Fao")
def pivot_FAO(FAO_data):
  FAO_pivot = FAO_data.pivot_table(
    index=['Domain Code', 'Domain', 'Area Code (M49)', 'Area', 'Item Code (CPC)',
           'Item', 'Year Code', 'Year', 'Flag', 'Flag Description'],
    columns='Element',
    values=['Unit', 'Value'],
    aggfunc='first',
  ).reset_index()

  #aanpassen en toevoegen kolommen units en values pivot
  FAO_pivot.columns = [
    '_'.join(col).strip('_') if col[1] else col[0]
    for col in FAO_pivot.columns]

  #nieuwe kolom voor totale yield
  FAO_pivot['Yield Quantities'] = FAO_pivot['Value_Area harvested'] * FAO_pivot['Value_Yield']

  return FAO_pivot

#### session status
if "FAO_data" not in st.session_state:
    st.session_state["FAO_data"] = load_FAO("FAOSTAT_data_en_4-17-2026.csv")

if "Rampen" not in st.session_state:
    st.session_state["Rampen"] = load_Disasters("1900_2021_DISASTERS.xlsx - emdat data.csv.zip")

if "FAO_pivot" not in st.session_state:
    st.session_state["FAO_pivot"] = pivot_FAO(st.session_state["FAO_data"])

#### Inladen data vanuit session state
Fao_data = st.session_state["FAO_data"]
Fao_pivot = st.session_state["FAO_pivot"]
rampen = st.session_state["Rampen"]

#### Begin TAB
Tab_1, Tab_2, Tab_3 = st.tabs(["Hoofdpagina", "Analyse", "Resultaat"])

#### TAB 1 Hoofdpagina + intro
with Tab_1:
  st.write("Start")

#### TAB 2 Diepere analyse
with Tab_2:
  st.write("Analyse")
  st.write("Productie en yield")
  st.dataframe(Fao_data.head(1000))
  st.divider
  st.write("Pivot van data")
  st.dataframe(Fao_pivot.head(500))
  st.divider()
  st.write("Rampen")
  st.dataframe(rampen.head(1000))
  
#### TAB 3 Resultaten en conclusie
with Tab_3:
  st.write("Resultaten")

  
#### einde script
