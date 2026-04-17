#### Imports
import streamlit as st
import pandas as pd
import numpy as np


#### pagina indeling
st.set_page_config(layout="centered")

#### cache
@st.cache_data(show_spinner="Fao productie laden")
def load_fao_productie(fao_data_production_indices_data):
  Fao_productie = pd.read_csv(fao_data_production_indices_data, compression='zip')
  return Fao_productie

@st.cache_data(show_spinner="Fao crops laden")
def load_fao_crops(fao_data_crops_data):
  Fao_crops = pd.read_csv(fao_data_crops_data, compression='zip')
  return Fao_crops

@st.cache_data(show_spinner="Rampen laden")
def load_Disasters(disasters_data):
  Rampen = pd.read_csv(disasters_data, compression='zip')
  return Rampen

#### session status
if "Fao_productie" not in st.session_state:
    st.session_state["Fao_productie"] = load_fao_productie("fao_data_production_indices_data.csv.zip")

if "Fao_crops" not in st.session_state:
    st.session_state["Fao_crops"] = load_fao_crops("fao_data_crops_data.csv.zip")

if "Rampen" not in st.session_state:
    st.session_state["Rampen"] = load_Disasters("1900_2021_DISASTERS.xlsx - emdat data.csv.zip")

#### Inladen data vanuit session state
Fao_productie = st.session_state["Fao_productie"]
Fao_crops = st.session_state["Fao_crops"]
rampen = st.session_state["Rampen"]

#### Begin TAB
Tab_1, Tab_2, Tab_3 = st.tabs(["Hoofdpagina", "Analyse", "Resultaat"])

#### TAB 1 hoofdpagina + intro
with Tab_1:
  st.write("Start")

#### TAB 2 diepere analyse
with Tab_2:
  st.write("Analyse")
  st.write("Productie")
  st.dataframe(Fao_productie.head(500))
  st.divider()
  st.write("Crops")
  st.dataframe(Fao_crops.head(500))
  st.divider()
  st.write("Rampen")
  st.dataframe(rampen.head(500))
  
#### TAB 3 resultaten en conclusie
with Tab_3:
  st.write("Resultaten")

  
#### einde script
