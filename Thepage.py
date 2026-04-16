#### Imports
import streamlit as st
import pandas as pd
import numpy as np


#### cache
@st.cache_data(show_spinner="Fao productie laden")
def load_fao_productie(fao_data_production_indices_data):
  Fao_productie = pd.read_csv("fao_data_production_indices_data.csv.zip", compression='zip')
  return Fao_productie

@st.cache_data(show_spinner="Fao crops laden")
def load_fao_crops(fao_data_crops_data):
  Fao_crops = pd.read_csv("fao_data_crops_data.csv.zip", compression='zip')
  return Fao_crops

@st.cache_data(show_spinner="Rampen laden")
def load_Disasters(disasters_data):
  Rampen = pd.read_csv("1900_2021_DISASTERS.csv.zip", compression='zip')
  return Rampen

#### session status



#### hervormen data


#### pagina indeling
st.set_page_config(layout="centered")

#### Begin TAB
Tab_1, Tab_2, Tab_3 = st.tabs(["Hoofdpagina", "Analyse", "Resultaat"])

#### TAB 1 hoofdpagina + intro
with Tab_1:
  st.write("start")

#### TAB 2 diepere analyse
with Tab_2:
  st.write("analyse")
  st.dataframe(Fao_crops.head(100))
  
#### TAB 3 resultaten en conclusie
with Tab_3:
  st.write("resultaten")

  
#### einde script
