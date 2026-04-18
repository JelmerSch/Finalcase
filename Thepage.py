#### Imports
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

#### pagina indeling
st.set_page_config(layout="centered")

############### cache ######################
###Cache van wereld data
@st.cache_data(show_spinner="Wereld Fao")
def Wereld_FAO(FAO_wereld):
  FAO_Wereld_data = pd.read_csv(FAO_wereld)
  return FAO_Wereld_data

###Cache van wereld pivot data
@st.cache_data(show_spinner="Wereld Fao pivot")
def Wereld_FAO_pivot(FAO_Wereld_data):
  FAO_Wereld_data_pivot = FAO_Wereld_data.pivot_table(
    index=['Area Code (M49)', 'Area', 'Item', 'Year', 'Flag', 'Flag Description'],
    columns='Element',
    values=['Unit', 'Value'],
    aggfunc='first',
  ).reset_index()

  #aanpassen en toevoegen kolommen units en values pivot
  FAO_Wereld_data_pivot.columns = [
    '_'.join(col).strip('_') if col[1] else col[0]
    for col in FAO_Wereld_data_pivot.columns]

  #nieuwe kolom voor totale yield
  FAO_Wereld_data_pivot['Yield Quantities'] = (FAO_Wereld_data_pivot['Value_Area harvested']
                                               * FAO_Wereld_data_pivot['Value_Yield']) / 1000
  FAO_Wereld_data_pivot['Unit_Yield Quantities'] = "t"
  return FAO_Wereld_data_pivot

###cache van Fao landen data
@st.cache_data(show_spinner="Fao data laden")
def load_FAO(FAOSTAT_data):
  FAO_data = pd.read_csv(FAOSTAT_data)
  return FAO_data

###cache van Fao landen pivot data
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

####een clean versie van wereld waarbij missen de waarde zijn opgevuld voor figuren
@st.cache_data(show_spinner="Clean wereld pivot")
def Clean_wereld_pivot(FAO_Wereld_clean):
  Flag_prioriteit = ['A', 'E', 'X']
  Values = ['Value_Area harvested', 'Value_Production', 'Value_Yield', 'Yield Quantities']
  #kolom sorteren op prio
  df = FAO_Wereld_clean.copy()

  #multiIndex kolommen voorkomen
  if isinstance(df.columns, pd.MultiIndex):
    df.columns = ['_'.join(col).strip('_') if col[1] else col[0] for col in df.columns]

  df['flag_rank'] = df['Flag'].map({f: i for i, f in enumerate(Flag_prioriteit)})
  df = df[df['flag_rank'].notna()].sort_values(['Area', 'Item', 'Year', 'flag_rank'])

  #Invullen missende waarde met flag E en X en verwijderen van onnodige rijen
  #voorrang is als volgt A>E>X
  Values = [col for col in Values if col in df.columns]

  results = []
  for (area, item, year), group in df.groupby(['Area', 'Item', 'Year'], sort=False):
    base = group.iloc[0].copy()
    for col in Values:
      if pd.isna(base[col]):
        fallback = group[col].dropna()
        if not fallback.empty:
          base[col] = fallback.iloc[0]
    results.append(base)

  #weghalen flagkolom
  clean_wereld = pd.DataFrame(results).reset_index(drop=True)
  clean_wereld = clean_wereld.drop(columns='flag_rank')
  return clean_wereld

###cache van rampen data
@st.cache_data(show_spinner="Rampen laden")
def load_Disasters(disasters_data):
  Rampen = pd.read_csv(disasters_data, compression='zip')
  return Rampen

###schone versie van rampen met alleen het nodige
@st.cache_data(show_spinner="Rampen opschonen")
def Clean_rampen(rampen_df):
  df = rampen_df.copy()
  df = df[df['Year'] >= 1961]
  df = df[df['Disaster Type'].isin(['Drought', 'Flood'])]
  df = df.reset_index(drop=True)
  return df

#### session status
if "FAO_Wereld_data" not in st.session_state:
    st.session_state["FAO_Wereld_data"] = Wereld_FAO("FAOSTAT_wereld_data_en_4-17-2026.csv")
if "FAO_Wereld_data_pivot" not in st.session_state:
    st.session_state["FAO_Wereld_data_pivot"] = Wereld_FAO_pivot(st.session_state["FAO_Wereld_data"])
if "FAO_Wereld_pivot_clean" not in st.session_state:
  st.session_state["FAO_Wereld_pivot_clean"] = Clean_wereld_pivot(st.session_state["FAO_Wereld_data_pivot"])
if "FAO_data" not in st.session_state:
    st.session_state["FAO_data"] = load_FAO("FAOSTAT_data_en_4-17-2026.csv")
if "FAO_pivot" not in st.session_state:
    st.session_state["FAO_pivot"] = pivot_FAO(st.session_state["FAO_data"])
if "FAO_pivot_clean" not in st.session_state:
  st.session_state["FAO_pivot_clean"] = Clean_wereld_pivot(st.session_state["FAO_pivot"])
if "Rampen" not in st.session_state:
    st.session_state["Rampen"] = load_Disasters("1900_2021_DISASTERS.xlsx - emdat data.csv.zip")
if "Rampen_clean" not in st.session_state:
  st.session_state["Rampen_clean"] = Clean_rampen(st.session_state["Rampen"])

#### Inladen data vanuit session state
Fao_data                = st.session_state["FAO_data"]
Fao_pivot               = st.session_state["FAO_pivot"]
Fao_pivot_clean         = st.session_state["FAO_pivot_clean"]
Fao_wereld_data         = st.session_state["FAO_Wereld_data"]
Fao_wereld_pivot        = st.session_state["FAO_Wereld_data_pivot"]
Fao_wereld_pivot_clean  = st.session_state["FAO_Wereld_pivot_clean"]
rampen                  = st.session_state["Rampen"]
rampen_clean            = st.session_state["Rampen_clean"]

### voor figuren
Granen_soorten = ['Rye', 'Flax, raw or retted', 'Wheat']
Continenten = ['Europe', 'Oceania', 'Africa', 'Americas', 'Asia']

### debugging
st.sidebar.markdown("---")
if st.sidebar.button("🔄 Cache wissen & herladen"):
    st.cache_data.clear()
    st.rerun()

#### Begin TAB
Tab_1, Tab_2, Tab_3 = st.tabs(["Hoofdpagina", "Analyse", "Resultaat"])

#### TAB 1 Hoofdpagina + intro
with Tab_1:
  st.write("Start")
  ### debugging
  if st.sidebar.button("🔄 Cache wissen & herladen"):
    st.cache_data.clear()
    st.rerun()

#### TAB 2 Diepere analyse
with Tab_2:
  st.write("Analyse")
  st.write(Fao_pivot_clean.columns.tolist())

  with st.container(border=True):
    st.write("Gemiddelde productie per land")
    graan_kaart = st.selectbox("Selecteer graansoort", Granen_soorten, key="graan_kraat")
    df_kaart = (Fao_pivot_clean[Fao_pivot_clean['Item'] == graan_kaart]
      .groupby(['Area', 'Area Code (M49)'], as_index=False)['Value_Production'].mean())
    df_kaart.columns = ['Area', 'Area_Code', 'Gem_Productie']
    df_kaart['Area_Code'] = pd.to_numeric(df_kaart['Area_Code'], errors='coerce')
    df_kaart = df_kaart.dropna(subset=['Area_Code'])
    df_kaart['Area_Code'] = df_kaart['Area_Code'].astype(int).astype(str).str.zfill(3)

    fig_kaart = px.choropleth(df_kaart, locations='Area', locationmode='country names',
                              color='Gem_Productie', hover_name='Area',
                              color_continuous_scale='YlOrRd',
                              labels={'Gem_Productie': 'Gem Productie (t)'},
                              title=f'Gemiddelde Productie - {graan_kaart}')
    fig_kaart.update_layout(coloraxis_colorbar=dict(title='Gem Productie (t)',
                            thickness=15, len=0.75), geo=dict(showframe=False,
                            showcoastlines=True), margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(fig_kaart, use_container_width=True)

  ##line chart hier
  with st.container(border=True):
   st.write("Wereld productie van 3 soorten graan")
   graan_lijn = st.selectbox("Selecteer graansoort", Granen_soorten, key="graan_lijn")
   df_graan = Fao_wereld_pivot_clean[(Fao_wereld_pivot_clean['Area'] == 'World') &
                                     (Fao_wereld_pivot_clean['Item'] == graan_lijn)].sort_values('Year')
   fig = make_subplots(specs=[[{"secondary_y": True}]])
   fig.add_trace(go.Scatter(x=df_graan['Year'], y=df_graan['Value_Area harvested'],
                               name='Area harvested (ha)', line=dict(color='blue'),
                               mode='lines',), secondary_y=False)
   fig.add_trace(go.Scatter(x=df_graan['Year'], y=df_graan['Value_Production'],
                            name='Production (t)', line=dict(color='red'),
                            mode='lines', ), secondary_y=True)
   fig.update_layout(title=f'Wereld productie - {graan_lijn}', xaxis_title='Year',
                     legend=dict(orientation='h', yanchor='bottom', y=1.02,
                     xanchor='right', x=1))
   fig.update_yaxes(title_text='Area harvested (ha)', secondary_y=False,
                    title_font=dict(color='blue'), tickfont=dict(color='blue'))
   fig.update_yaxes(title_text='Production (t)', secondary_y=True,
                    title_font=dict(color='red'), tickfont=dict(color='red'))
   st.plotly_chart(fig, use_container_width=True)

  ## Pie Charts
  with st.container(border=True):
    st.write("Verdeling van productie van 3 soorten graan")
    pie1, pie2, pie3 = st.columns(3)
    for col, graan in zip([pie1, pie2, pie3], Granen_soorten):
      avg = (Fao_wereld_pivot_clean[(Fao_wereld_pivot_clean['Area'].isin(Continenten))&
          (Fao_wereld_pivot_clean['Item'] == graan)].groupby('Area')['Value_Production'].mean()
           .reindex(Continenten).fillna(0))
      fig_pie = go.Figure(go.Pie(labels=avg.index.tolist(), values=avg.values.tolist(), hole=0.3))
      fig_pie.update_layout(title=graan, showlegend=True)
      with col:
        st.plotly_chart(fig_pie, use_container_width=True)

  ##rampen op een kaart
  with st.container(border=True):
    st.write("Overstromingen en droogtes per land")
    df_ramp_totaal = (rampen_clean.groupby(['Country', 'ISO'], as_index=False)['Disaster Type']
                      .count().rename(columns={'Disaster Type': 'Aantal'}))
    fig_ramp = px.choropleth(df_ramp_totaal, locations='ISO', locationmode='ISO-3',
                             color='Aantal', hover_name='Country', color_continuous_scale='Blues',
                             labels={'Aantal': 'Aantal rampen'},
                             title='Overstromingen en Droogtes in de wereld')
    fig_ramp.update_layout(coloraxis_colorbar=dict(title='Aantal rampen', thickness=15, len=0.75),
                           geo=dict(showframe=False, showcoastlines=True),
                           margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(fig_ramp, use_container_width=True)

    ##Tijdlijn van type rampen en jaar
    df_tijd = (rampen_clean.groupby(['Year', 'Disaster Type']).size().reset_index(name='Aantal'))
    fig_tijd = px.bar(df_tijd, x='Year', y='Aantal', color='Disaster Type', barmode='group',
                      color_discrete_map={'Drought': 'orange', 'Flood': 'steelblue'},
                      labels={'Year': 'Jaar', 'Aantal': 'Aantal rampen', 'Disaster Type': 'Type'},
                      title='Verdeling overstromingen en droogtes in de wereld')
    st.plotly_chart(fig_tijd, use_container_width=True)

#### TAB 3 Resultaten en conclusie
with Tab_3:
  st.write("Resultaten")

  
#### Einde script
