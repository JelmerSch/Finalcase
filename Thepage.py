#### Imports
import streamlit as st
import pandas as pd
import numpy as np



Fao_crops_data = pd.read_csv("fao_data_crops_data.csv.zip", compression='zip')

#### cache


#### session status



#### hervormen data


####pagina indeling
st.set_page_config(layout="centered")

#### Begin TAB
Tab_1, Tab_2, Tab_3 = st.tabs(["Hoofdpagina", "Analyse", "Resultaat"])

#### TAB 1 hoofdpagina + intro
with Tab_1:
  st.write("start")

#### TAB 2 diepere analyse
with Tab_2:
  st.write("analyse")

#### TAB 3 resultaten en conclusie
with Tab_3:
  st.write("resultaten")

  
#### einde script
