#### Imports
import streamlit as st
import pandas as pd
import numpy as np

#### pagina indeling
st.set_page_config(layout="centered")

#### cache
@st.cache_data(show_spinner="Wereld Fao")
def Wereld_FAO(FAO_wereld):
  FAO_Wereld_data = pd.read_csv(FAO_wereld)
  return FAO_Wereld_data

@st.cache_data(show_spinner="Wereld Fao pivot")
def Wereld_FAO_pivot(FAO_Wereld_data):
  FAO_Wereld_data_pivot = FAO_Wereld_data.pivot_tabel(
    index=['Area Code (M49)', 'Area', 'Item', 'Year', 'Flag', 'Flag Description'],
    columns='Element',
    values=['Unit', 'Value'],
    aggfunc='first',
  ).reset_index()

  #aanpassen en toevoegen kolommen units en values pivot
  FAO_pivot.columns = [
    '_'.join(col).strip('_') if col[1] else col[0]
    for col in FAO_pivot.columns]

  #nieuwe kolom voor totale yield
  FAO_pivot['Yield Quantities'] = (FAO_pivot['Value_Area harvested'] * FAO_pivot['Value_Yield']) / 1000
  FAO_pivot['Unit_Yield Quantities'] = "t"
  return FAO_Wereld_data_pivot

@st.cache_data(show_spinner="Rampen laden")
def load_Disasters(disasters_data):
  Rampen = pd.read_csv(disasters_data, compression='zip')
  return Rampen

@st.cache_data(show_spinner="Fao data laden")
def load_FAO(FAOSTAT_data):
  FAO_data = pd.read_csv(FAOSTAT_data)
  return FAO_data

@st.cache_data(show_spinner="Pivotten Fao")
def pivot_FAO(FAO_data):
  FAO_pivot = FAO_data.pivot_table(
    index=['Area Code (M49)', 'Area', 'Item', 'Year', 'Flag', 'Flag Description'],
    columns='Element',
    values=['Unit', 'Value'],
    aggfunc='first',
  ).reset_index()

  #aanpassen en toevoegen kolommen units en values pivot
  FAO_pivot.columns = [
    '_'.join(col).strip('_') if col[1] else col[0]
    for col in FAO_pivot.columns]

  #nieuwe kolom voor totale yield
  FAO_pivot['Yield Quantities'] = (FAO_pivot['Value_Area harvested'] * FAO_pivot['Value_Yield']) / 1000
  FAO_pivot['Unit_Yield Quantities'] = "t"
  return FAO_pivot

#### session status
if "FAO_Wereld_data" not in st.session_state:
    st.session_state["FAO_Wereld_data"] = load_FAO("FAOSTAT_wereld_data_en_4-17-2026.csv")
if "FAO_Wereld_data_pivot" not in st.session_state:
    st.session_state["FAO_Wereld_data_pivot"] = pivot_FAO(st.session_state["FAO_Wereld_data"])
if "Rampen" not in st.session_state:
    st.session_state["Rampen"] = load_Disasters("1900_2021_DISASTERS.xlsx - emdat data.csv.zip")
if "FAO_data" not in st.session_state:
    st.session_state["FAO_data"] = load_FAO("FAOSTAT_data_en_4-17-2026.csv")
if "FAO_pivot" not in st.session_state:
    st.session_state["FAO_pivot"] = pivot_FAO(st.session_state["FAO_data"])

#### Inladen data vanuit session state
Fao_data = st.session_state["FAO_data"]
Fao_pivot = st.session_state["FAO_pivot"]
Fao_wereld_data = st.session_state["FAO_Wereld_data"]
Fao_wereld_pivot = st.session_state["FAO_Wereld_data_pivot"]
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
  st.divider()
  st.write("Pivot van data")
  st.dataframe(Fao_pivot.head(500))
  st.divider()
  st.write("Productie en yield")
  st.dataframe(Fao_wereld_data.head(1000))
  st.divider()
  st.write("Pivot van data")
  st.dataframe(Fao_wereld_pivot.head(500))
  st.divider()
  st.write("Rampen")
  st.dataframe(rampen.head(1000))
  
#### TAB 3 Resultaten en conclusie
with Tab_3:
  st.write("Resultaten")

  
#### Einde script
