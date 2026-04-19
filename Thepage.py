#### Imports
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import folium
from folium.plugins import LayerControl
import branca.colormap as cm
from streamlit_folium import st_folium

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

#### Folium kaart voor analyse
@st.cache_data(show_spinner="Folium kaart bouwen")
def build_folium_map(fao_pivot_clean, rampen_clean):
    """Bouw een Folium kaart met lagen voor Rye, Flax, Wheat, Overstromingen en Droogtes."""

    # --- Productie data per graansoort voorbereiden ---
    graan_data = {}
    for graan in ['Rye', 'Flax, raw or retted', 'Wheat']:
        df = (fao_pivot_clean[fao_pivot_clean['Item'] == graan]
              .groupby(['Area'], as_index=False)['Value_Production'].mean())
        df.columns = ['Area', 'Gem_Productie']
        graan_data[graan] = df

    # --- Rampen data voorbereiden ---
    df_flood = (rampen_clean[rampen_clean['Disaster Type'] == 'Flood']
                .groupby(['Country', 'ISO'], as_index=False).size()
                .rename(columns={'size': 'Aantal'}))
    df_drought = (rampen_clean[rampen_clean['Disaster Type'] == 'Drought']
                  .groupby(['Country', 'ISO'], as_index=False).size()
                  .rename(columns={'size': 'Aantal'}))

    # --- GeoJSON URL voor landen grenzen ---
    geojson_url = "https://raw.githubusercontent.com/python-visualization/folium/master/examples/data/world-countries.json"

    # --- Kaart aanmaken ---
    m = folium.Map(location=[20, 0], zoom_start=2, tiles="CartoDB positron")

    # --- Kleurenschalen voor granen ---
    graan_kleuren = {
        'Rye':              ['#ffffcc', '#ffeda0', '#fed976', '#feb24c', '#fd8d3c', '#fc4e2a', '#e31a1c', '#b10026'],
        'Flax, raw or retted': ['#f7fcf5', '#e5f5e0', '#c7e9c0', '#a1d99b', '#74c476', '#41ab5d', '#238b45', '#005a32'],
        'Wheat':            ['#fff5eb', '#fee6ce', '#fdd0a2', '#fdae6b', '#fd8d3c', '#f16913', '#d94801', '#7f2704'],
    }

    for graan, df_g in graan_data.items():
        if df_g.empty:
            continue

        max_val = df_g['Gem_Productie'].max()
        min_val = df_g['Gem_Productie'].min()
        if max_val == min_val:
            max_val = min_val + 1

        colormap = cm.LinearColormap(
            colors=graan_kleuren[graan],
            vmin=min_val,
            vmax=max_val,
            caption=f'Gem. Productie {graan} (t)'
        )

        productie_dict = dict(zip(df_g['Area'], df_g['Gem_Productie']))

        def style_graan(feature, pd=productie_dict, cmap=colormap):
            naam = feature['properties'].get('name', '')
            val = pd.get(naam, None)
            if val is None or pd.isna(val):
                return {'fillColor': '#d3d3d3', 'color': '#555', 'weight': 0.5,
                        'fillOpacity': 0.4}
            return {'fillColor': cmap(val), 'color': '#555', 'weight': 0.5,
                    'fillOpacity': 0.75}

        layer = folium.GeoJson(
            geojson_url,
            name=f'Productie: {graan}',
            style_function=style_graan,
            tooltip=folium.GeoJsonTooltip(
                fields=['name'],
                aliases=['Land:'],
                localize=True
            ),
            show=graan == 'Wheat'  # Wheat standaard zichtbaar
        )
        layer.add_to(m)
        colormap.add_to(m)

    # --- Overstromingen laag ---
    if not df_flood.empty:
        max_flood = df_flood['Aantal'].max()
        min_flood = df_flood['Aantal'].min()
        if max_flood == min_flood:
            max_flood = min_flood + 1

        colormap_flood = cm.LinearColormap(
            colors=['#deebf7', '#9ecae1', '#4292c6', '#08519c', '#08306b'],
            vmin=min_flood,
            vmax=max_flood,
            caption='Aantal Overstromingen'
        )

        flood_dict = dict(zip(df_flood['Country'], df_flood['Aantal']))

        def style_flood(feature, fd=flood_dict, cmap=colormap_flood):
            naam = feature['properties'].get('name', '')
            val = fd.get(naam, None)
            if val is None:
                return {'fillColor': '#d3d3d3', 'color': '#555', 'weight': 0.5,
                        'fillOpacity': 0.3}
            return {'fillColor': cmap(val), 'color': '#336699', 'weight': 0.7,
                    'fillOpacity': 0.75}

        flood_layer = folium.GeoJson(
            geojson_url,
            name='Overstromingen',
            style_function=style_flood,
            tooltip=folium.GeoJsonTooltip(
                fields=['name'],
                aliases=['Land:'],
                localize=True
            ),
            show=False
        )
        flood_layer.add_to(m)
        colormap_flood.add_to(m)

    # --- Droogtes laag ---
    if not df_drought.empty:
        max_drought = df_drought['Aantal'].max()
        min_drought = df_drought['Aantal'].min()
        if max_drought == min_drought:
            max_drought = min_drought + 1

        colormap_drought = cm.LinearColormap(
            colors=['#fff7bc', '#fee391', '#fec44f', '#fe9929', '#d95f0e', '#993404'],
            vmin=min_drought,
            vmax=max_drought,
            caption='Aantal Droogtes'
        )

        drought_dict = dict(zip(df_drought['Country'], df_drought['Aantal']))

        def style_drought(feature, dd=drought_dict, cmap=colormap_drought):
            naam = feature['properties'].get('name', '')
            val = dd.get(naam, None)
            if val is None:
                return {'fillColor': '#d3d3d3', 'color': '#555', 'weight': 0.5,
                        'fillOpacity': 0.3}
            return {'fillColor': cmap(val), 'color': '#8B4513', 'weight': 0.7,
                    'fillOpacity': 0.75}

        drought_layer = folium.GeoJson(
            geojson_url,
            name='Droogtes',
            style_function=style_drought,
            tooltip=folium.GeoJsonTooltip(
                fields=['name'],
                aliases=['Land:'],
                localize=True
            ),
            show=False
        )
        drought_layer.add_to(m)
        colormap_drought.add_to(m)

    # --- Layer Control toevoegen ---
    LayerControl(collapsed=False).add_to(m)

    return m

### voor figuren
Granen_soorten = ['Rye', 'Flax, raw or retted', 'Wheat']
Continenten = ['Europe', 'Oceania', 'Africa', 'Americas', 'Asia']

#### Begin TAB
Tab_1, Tab_2, Tab_3 = st.tabs(["Hoofdpagina", "Analyse", "Resultaat"])

#### TAB 1 Hoofdpagina + intro
with Tab_1:
  st.write("Start")

#### TAB 2 Diepere analyse
with Tab_2:
  st.write("Analyse")
  # --- Folium kaart: Productie per land + Rampen ---
  st.subheader("Gemiddelde productie per land & rampen")
  st.caption("Gebruik het laagmenu rechts op de kaart om te wisselen tussen graansoorten, overstromingen en droogtes.")

  folium_kaart = build_folium_map(Fao_pivot_clean, rampen_clean)
  st_folium(folium_kaart, use_container_width=True, height=500)

  st.divider()
  ##line chart hier
  st.subheader("Wereld productie van 3 soorten graan")
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
  st.divider()

  ## Pie Charts
  st.subheader("Verdeling van productie van 3 soorten graan")
  pie1, pie2, pie3 = st.columns(3)
  for col, graan in zip([pie1, pie2, pie3], Granen_soorten):
     avg = (Fao_wereld_pivot_clean[(Fao_wereld_pivot_clean['Area'].isin(Continenten))&
         (Fao_wereld_pivot_clean['Item'] == graan)].groupby('Area')['Value_Production'].mean()
          .reindex(Continenten).fillna(0))
     fig_pie = go.Figure(go.Pie(labels=avg.index.tolist(), values=avg.values.tolist(), hole=0.3))
     fig_pie.update_layout(title=graan, showlegend=True)
     with col:
       st.plotly_chart(fig_pie, use_container_width=True)

  ##Tijdlijn van type rampen en jaar
  st.subheader("Verdeling overstromingen en droogtes in de wereld")
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
