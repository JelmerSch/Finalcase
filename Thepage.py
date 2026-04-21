#### Imports
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

#### pagina indeling
st.set_page_config(layout="wide")

############### cache ######################
###Cache van wereld data
@st.cache_data(show_spinner="Wereld Fao")
def Wereld_FAO(FAO_wereld):
    FAO_Wereld_data = pd.read_csv(FAO_wereld)
    return FAO_Wereld_data

###Cache van wereld pivot data en pivotting dataframe
@st.cache_data(show_spinner="Wereld Fao pivot")
def Wereld_FAO_pivot(FAO_Wereld_data):
    FAO_Wereld_data_pivot = FAO_Wereld_data.pivot_table(
        index=['Area Code (M49)', 'Area', 'Item', 'Year', 'Flag', 'Flag Description'],
        columns='Element', values=['Unit', 'Value'], aggfunc='first').reset_index()

    # aanpassen en toevoegen kolommen units en values pivot
    FAO_Wereld_data_pivot.columns = ['_'.join(col).strip('_') if col[1] else col[0]
        for col in FAO_Wereld_data_pivot.columns]

    # nieuwe kolom voor totale yield
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
        columns='Element', values=['Unit', 'Value'], aggfunc='first').reset_index()

    # aanpassen en toevoegen kolommen units en values pivot
    FAO_pivot.columns = ['_'.join(col).strip('_') if col[1] else col[0]
        for col in FAO_pivot.columns]

    # nieuwe kolom voor totale yield
    FAO_pivot['Yield Quantities'] = (FAO_pivot['Value_Area harvested'] * FAO_pivot['Value_Yield']) / 1000
    FAO_pivot['Unit_Yield Quantities'] = "t"
    return FAO_pivot


####een clean versie van wereld waarbij missen de waarde zijn opgevuld voor figuren
@st.cache_data(show_spinner="Clean wereld pivot")
def Clean_wereld_pivot(FAO_Wereld_clean):
    Flag_prioriteit = ['A', 'E', 'X']
    Values = ['Value_Area harvested', 'Value_Production', 'Value_Yield', 'Yield Quantities']
    # kolom sorteren op prio
    df = FAO_Wereld_clean.copy()

    # multiIndex kolommen voorkomen (probleem door huidige versie pandas)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = ['_'.join(col).strip('_') if col[1] else col[0] for col in df.columns]

    df['flag_rank'] = df['Flag'].map({f: i for i, f in enumerate(Flag_prioriteit)})
    df = df[df['flag_rank'].notna()].sort_values(['Area', 'Item', 'Year', 'flag_rank'])

    # Invullen missende waarde met flag E en X en verwijderen van onnodige rijen
    # voorrang is als volgt A>E>X
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

    # weghalen flagkolom
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

### Foto`s voor uitleg van soorten granen
### in cahce gezet voor voorkomen inladen
@st.cache_data(show_spinner="Foto Flax laden")
def load_foto_Flax(f_url):
    return f_url

@st.cache_data(show_spinner="Foto Rye laden")
def load_foto_Rye(r_url):
    return r_url

@st.cache_data(show_spinner="Foto Wheat laden")
def load_foto_Wheat(w_url):
    return w_url


#### session status voor mogelijk toevogen van slider of dergelijks
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
Fao_data = st.session_state["FAO_data"]
Fao_pivot = st.session_state["FAO_pivot"]
Fao_pivot_clean = st.session_state["FAO_pivot_clean"]
Fao_wereld_data = st.session_state["FAO_Wereld_data"]
Fao_wereld_pivot = st.session_state["FAO_Wereld_data_pivot"]
Fao_wereld_pivot_clean = st.session_state["FAO_Wereld_pivot_clean"]
rampen = st.session_state["Rampen"]
rampen_clean = st.session_state["Rampen_clean"]

#laden url van foto's
f_url = load_foto_Flax("https://raw.githubusercontent.com/JelmerSch/Finalcase/main/Flax(blond)2.jpg")
r_url = load_foto_Rye("https://raw.githubusercontent.com/JelmerSch/Finalcase/main/Rye.jpg")
w_url = load_foto_Wheat("https://raw.githubusercontent.com/JelmerSch/Finalcase/main/Wheat2.jpg")

### voor figuren en dergelijks
Granen_soorten = ['Rye', 'Flax, raw or retted', 'Wheat']
Continenten = ['Europe', 'Oceania', 'Africa', 'Americas', 'Asia']

#### Begin TAB
Tab_1, Tab_2, Tab_3, Tab_4 = st.tabs(["Hoofdpagina", "Granen Analyse", "Rampen Analyse", "Resultaat en Conclusie"])

#### TAB 1 Hoofdpagina + intro
with Tab_1:
    ### scherm op delen in 3 en selcteren van de middelste
    cen = st.columns([1, 2, 1])[1]
    with cen:
        ###tekst van de hoofdpagina
        st.title("Hallo en welkom")

        st.write("""In deze streamlit omgeving wordt er een analyse gedaan voor de case van graan productie in de wereld 
        en de invloed van natuurlijke rampen op deze productie. Specifiek wordt er gekeken naar drie soorten 
        graan namelijk wheat, rye en flax. Respectievelijk is dit in Nederlands tarwe, rogge en lijnzaad (vlas) 
        meer over deze drie soorten graan zomenteen. Om de case minder omslagtig te maken zijn deze drie granen 
        gekozen en zijn de soorten natuurlijke rampen beperkt naar "Floods" en "Droughts" oftewel overstromingen 
        en droogte.""")

        st.write("**De onderzoeksvraag is als volgt:** Wat is de invloed van overstromingen en droogtes op "
                 "de productie van tarwe, rogge en lijnzaad (vlas)?")

        st.header("Methode van de Analyse")
        st.write("""Eerst zal er gekeken worden de productie van tarwe, rogge en lijnzaad (vlas) over de wereld. De data 
        die gebruikt zal worden is van de FAO (Voedsel- en Landbouworganisatie van de Verenigede Naties). De 
        data aangeboden van de FAO bevat info van allerlei landen in de wereld. Er zijn in deze datasets drie 
        verschillende waardes te vinden op jaar basis sinds 1961 namelijk Productie in tonnen(t), hoeveelheid 
        land waarop is geoogst in hectare(ha) en de yield in tonnen per hectare(t/ha). Hierbij wordt aangegeven 
        of dit officiële cijfers, geschatte waardes of waardes die door externe zijn gegeven. Deze gegevens 
        worden voorbereid voordat ze verwerkt worden in figuren om een beeld te krijgen van de verdeling van 
        de productie van de granen in de wereld.""")

        st.write("""Na het analyseren van de productie van de granen wordt er gekeken naar de 2 soorten rampen. Deze 
        dataset komt van kaggle en bevat allerlei info over rampen vanaf 1900. Deze dataset wordt voorbereid 
        om te gebruiken door het te limiteren naar 1961 en naar de twee type rampen "Floods" en "Droughts". 
        Er zal niet gekeken worden naar de groottes van deze rampen tenzij het blijkt uit latere cijfers dat 
        maar één of twee rampen echt invloed hadden op productie van graan.""")

        st.write("""Als laatst worden de cijfers van de twee rampen en de productie van graan samen verwerkt in een figuur. 
        Om een antwoordt te krijgen op de onderzoeksvraag en te concluderen of overstromingen en droogtes 
        invloed hebben op productie van graan.""")

        st.header("De 3 Soorten graan")
        st.subheader("Flax (Vlas of Lijnzaad")
        st.write("""Lijnzaad is het zaad van (olie)vlas. Lijnzaad heeft twee grote gebruiksdoelen. 
        Het wordt gebruikt als grondstof voor lijnzaadolie dat met behulp van een oliemolen uit het 
        zaad wordt geperst. Het restproduct van dit proces noemt men lijnkoek. Lijnkoeken worden 
        gebruikt als veevoer. Het wordt ook gebruikt als ingrediënt in brood, muesli of andere 
        keukentoepassingen.""")
        st.image(f_url)

        st.subheader("Rye (Rogge)")
        st.write("""Rogge wordt vooral geteeld om er roggebrood van te maken. Ook ontbijtkoek 
        wordt van rogge gemaakt. In Ierland en de Verenigde Staten wordt rogge gebruikt als 
        natuurlijke grondstof voor whisky. Rogge wordt voornamelijk op de zand- en dalgronden 
        verbouwd.""")
        st.image(r_url)

        st.subheader("Wheat (Tarwe)")
        st.write("""Tarwe (Triticum) is een geslacht van granen waar de mensheid zich mee voedt, 
        naast rijst en maïs. Tarwe is een van de oudste gedomesticeerde planten. De domesticatie 
        vond waarschijnlijk ongeveer 10.000 jaar geleden plaats in het Midden-Oosten en Afrika 
        van Syrië tot Kasjmir en naar het zuiden tot in Ethiopië.""")
        st.image(w_url)


#### TAB 2 granen analyse
with Tab_2:
    ana1 = st.columns([0.5, 2, 0.5])[1]
    with ana1:
        with st.container(border=True):
            ###tekst in container
            st.title("Gemiddelde productie graan per land")
            st.write("""Hieronder is een wereld kaart waarin de gemiddelde productie van de verschillende soorten graan in 
            tonnen te zien is. Dit is op een kleurenschaal gezet om een duidelijk verschil te zien tussen de 
            landen. De landen die wit zijn hebben geen data beschikbaar wat betekend dat het graan soort daar 
            niet wordt geproduceerd.""")

            ##select box maken
            graan_kaart = st.selectbox("Selecteer graansoort", Granen_soorten, key="graan_kraat")

            #slider voor tijd
            jaar_min_kaart = int(Fao_pivot_clean['Year'].min())
            jaar_max_kaart = int(Fao_pivot_clean['Year'].max())
            jaar_slider_kaart = st.slider("Bepaal het jaarbereik", min_value=jaar_min_kaart, max_value=jaar_max_kaart,
                                          value=(jaar_min_kaart, jaar_max_kaart), key="jaar_slider")

            # voorwerk van kaart maken.
            df_kaart = (Fao_pivot_clean[(Fao_pivot_clean['Item'] == graan_kaart) &
                        (Fao_pivot_clean['Year'] >= jaar_slider_kaart[0]) &
                        (Fao_pivot_clean['Year'] <= jaar_slider_kaart[1])]
                        .groupby(['Area', 'Area Code (M49)'], as_index=False)['Value_Production'].mean())
            df_kaart.columns = ['Area', 'Area_Code', 'Gem_Productie']

            ### alle waarde naar num zetten voor verijderen foute waarde
            df_kaart['Area_Code'] = pd.to_numeric(df_kaart['Area_Code'], errors='coerce')

            ### verwijderen van NaN waardes
            df_kaart = df_kaart.dropna(subset=['Area_Code'])

            ### verwijder de decimalen door integers te maken,
            ###omzetten daarna naar strings en zorg dat elek string 3 cijfers langs is
            df_kaart['Area_Code'] = df_kaart['Area_Code'].astype(int).astype(str).str.zfill(3)

            #kaart in kwestie
            fig_kaart = px.choropleth(df_kaart, locations='Area', locationmode='country names',
                                    color='Gem_Productie', hover_name='Area',
                                    color_continuous_scale='YlOrRd',
                                    labels={'Gem_Productie': 'Gem Productie (t)'},
                                    title=f'Gemiddelde Productie - {graan_kaart}')
            fig_kaart.update_layout(coloraxis_colorbar=dict(title='Gem Productie (t)',
                                                            thickness=15, len=0.75), geo=dict(showframe=False,
                                                            showcoastlines=True),margin=dict(l=0, r=0, t=40, b=0))
            st.plotly_chart(fig_kaart, use_container_width=True)
            ###tekst in container na figuur
            st.subheader("Rye")
            st.write("""Zoals te zien is wordt er veel rye geproduceerd in Europa voornamelijk in Duitsland, Polen en Rusland. 
            Er wordt vrijwel niks geproduceerd in Africa en nauwelijks iets in Oceanië, Azië en Noord- of Zuid Amerika.""")

            st.subheader("Flax")
            st.write("""Zoals te zien is op de kaart is de productie van flax in Europa het grootst en de grootste producenten 
            zijn Rusland en Frankrijk. Er zijn weinig landen buiten Europa die het überhaupt produceren. China is 
            het enige land buiten Europa die het in significante hoeveelheid produceert.""")

            st.subheader("Wheat")
            st.write("""Zoals te zien is op de kaart wordt wheat overal in de wereld geproduceerd. De grootste producenten 
            van wheat zijn China, India, US en Rusland. Er is duidelijk te zien dat de verdeling van de productie 
            van wheat veel meer verdeeld is in de wereld en dat het geproduceerd wordt op elk continent.""")

        ##line chart hier
        with st.container(border=True):
            ###tekst in container voor figuur
            st.header("Wereld productie van 3 soorten graan")
            st.write("""Hieronder is de wereld productie te zien van de verschillende soorten graan en hoe groot het gebied 
            is waarop het geoogst is. Om de twee waardes tegelijk te zien zijn twee y-assen gebruikt en in 
            verschillende kleuren gezet om een duidelijk contrast tussen de twee te hebben.""")

            ### voorbereiden van data figuur
            graan_lijn = st.selectbox("Selecteer graansoort", Granen_soorten, key="graan_lijn")
            df_graan = Fao_wereld_pivot_clean[(Fao_wereld_pivot_clean['Area'] == 'World') &
                                            (Fao_wereld_pivot_clean['Item'] == graan_lijn)].sort_values('Year')
            ### figuur maken
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            fig.add_trace(go.Scatter(x=df_graan['Year'], y=df_graan['Value_Area harvested'],
                                    name='Area harvested (ha)', line=dict(color='blue'),
                                    mode='lines', ), secondary_y=False)
            fig.add_trace(go.Scatter(x=df_graan['Year'], y=df_graan['Value_Production'],
                                    name='Production (t)', line=dict(color='red'),
                                    mode='lines', ), secondary_y=True)
            fig.update_layout(title=f'Wereld productie - {graan_lijn}', xaxis_title='Year',
                            legend=dict(orientation='h', yanchor='bottom', y=1.02,
                                        xanchor='right', x=1))
            fig.update_yaxes(title_text='Area harvested (ha)', secondary_y=False,
                            title_font=dict(color='blue'), tickfont=dict(color='blue'), rangemode='tozero')
            fig.update_yaxes(title_text='Production (t)', secondary_y=True,
                            title_font=dict(color='red'), tickfont=dict(color='red'), rangemode='tozero')
            st.plotly_chart(fig, use_container_width=True)

        ## Pie Charts
        with st.container(border=True):
            ###tekst in container voor figuur
            st.header("Verdeling van productie van 3 soorten graan")
            st.write("""Hieronder kan je zien de verdeling van de productie van de 3 soorten graan per continent. 
            Dit geeft een duidelijk beeld welk type graan waar voornamelijk wordt geproduceerd in de wereld.""")

            pie1, pie2, pie3 = st.columns(3)
            for col, graan in zip([pie1, pie2, pie3], Granen_soorten):
                avg = (Fao_wereld_pivot_clean[(Fao_wereld_pivot_clean['Area'].isin(Continenten)) &
                                            (Fao_wereld_pivot_clean['Item'] == graan)].groupby('Area')
                                            ['Value_Production'].mean().reindex(Continenten).fillna(0))
                fig_pie = go.Figure(go.Pie(labels=avg.index.tolist(), values=avg.values.tolist(), hole=0.3))
                fig_pie.update_layout(title=graan, showlegend=True)
                with col:
                    st.plotly_chart(fig_pie, use_container_width=True)

#### TAB 3 rampen analyse
with Tab_3:
    ana2 = st.columns([0.5, 2, 0.5])[1]
    with ana2:
        with st.container(border=True):
            ###tekst in container voor figuur
            st.title("Overstromingen en droogtes per land")
            st.write(""""Hieronder is een kaart te zien van de hoeveelheid overstromingen en droogtes in de wereld. 
            Er is een optie om de rampen apart te zien of tegelijktijdig. Er is een duidelijk verschil te zien 
            tussen de twee soorten rampen en waar ze plaats vinden. In China gebeuren de meeste rampen in totaal 
            en individueel.""")

            ##selectbox voor de een kaart
            ramp_keuze = st.selectbox("Selecteer het type kaart met rampen", key="ramp_keuze",
                                    options=["Floods and Droughts","Floods", "Droughts"])

            ###slider voor de kaart
            jaar_min_ramp = int(rampen_clean['Year'].min())
            jaar_max_ramp = int(rampen_clean['Year'].max())
            jaar_slider_ramp = st.slider("Selecteer jaarbereik", min_value=jaar_min_ramp, max_value=jaar_max_ramp,
                                        value=(jaar_min_ramp, jaar_max_ramp), key="slider_ramp")

            #Kleuren schalen voor rampen op kaart
            Kleur_ramp = {"Floods and Droughts":    {"filter": ["Flood", "Drought"],
                                                    "schaal": "Purples",
                                                    "label": "Aantal rampen",
                                                    "titel": "Overstromingen en Droogtes in de wereld"},
                        "Floods": {"filter":        ["Flood"],
                                    "schaal":       "Blues",
                                    "label":        "Aantal overstromingen",
                                    "titel":        "Overstromingen in de wereld"},
                        "Droughts": {"filter":      ["Drought"],
                                    "schaal":       [[0.0, "#ffffb2"], [0.2, "#fecc5c"], [0.4, "#fd8d3c"],
                                                    [0.6, "#f03b20"], [0.8, "#bd0026"], [1.0, "#67000d"]],
                                    "label":        "Aantal droogtes",
                                    "titel":        "Droogtes in de wereld",}}
            Kleur = Kleur_ramp[ramp_keuze]
            df_ramp_gefilterd = rampen_clean[(rampen_clean['Disaster Type'].isin(Kleur["filter"])) &
                                             (rampen_clean['Year'] >= jaar_slider_ramp[0]) &
                                             (rampen_clean['Year'] <= jaar_slider_ramp[1])]
            df_ramp_totaal = (df_ramp_gefilterd.groupby(['Country', 'ISO'], as_index=False)['Disaster Type']
                            .count().rename(columns={'Disaster Type': 'Aantal'}))
            fig_ramp = px.choropleth(df_ramp_totaal, locations='ISO', locationmode='ISO-3',
                                    color='Aantal', hover_name='Country', color_continuous_scale=Kleur['schaal'],
                                    labels={'Aantal': Kleur['label']},
                                    title=Kleur['titel'])
            fig_ramp.update_layout(coloraxis_colorbar=dict(title=Kleur['label'], thickness=15, len=0.75),
                                geo=dict(showframe=False, showcoastlines=True),
                                margin=dict(l=0, r=0, t=40, b=0))
            st.plotly_chart(fig_ramp, use_container_width=True)

        with st.container(border=True):
            ### tekst voor het figuur
            st.header("Verdeling overstromingen en droogtes in de wereld")
            st.write("""Hieronder is te zien het aantal overstromingen en droogtes in de wereld vanaf 1961. 
            Er is een duidelijk toenamen in de hoeveelheid overstromingen, maar een gematigde toename voor 
            het aantal droogtes in de wereld. Beide worden beïnvloed door het feit dat hedendaags rampen 
            beter worden bijgehouden.""")

            ##Tijdlijn van type rampen en jaar
            df_tijd = (rampen_clean.groupby(['Year', 'Disaster Type']).size().reset_index(name='Aantal'))
            fig_tijd = px.bar(df_tijd, x='Year', y='Aantal', color='Disaster Type', barmode='group',
                            color_discrete_map={'Drought': 'orange', 'Flood': 'steelblue'},
                            labels={'Year': 'Jaar', 'Aantal': 'Aantal rampen', 'Disaster Type': 'Type'},
                            title='Verdeling overstromingen en droogtes in de wereld')
            st.plotly_chart(fig_tijd, use_container_width=True)

#### TAB 4 Resultaten en conclusie
with Tab_4:
    cen2 = st.columns([0.5, 2, 0.5])[1]
    with cen2:
        with st.container(border=True):
            st.title("Invloed van rampen op graanproductie")
            st.write("""Hieronder is de productie van de 3 soorten graan te zien samen met het aantal 
            overstromingen en droogtes per jaar. Selecteer een graansoort en ramptype om de relatie 
            tussen de twee te bekijken. Er is ook de optie om de productie per continent te bekijken""")

            ### selectie boxen
            col_sel1, col_sel2, col_sel3 = st.columns(3)
            with col_sel1:
                graan_res = st.selectbox("Selecteer graansoort", Granen_soorten, key="graan_res")
            with col_sel2:
                ramp_res = st.selectbox("Selecteer ramptype", ["Flood", "Drought"], key="ramp_res")
            with col_sel3:
                gebied_opties = ['World'] + Continenten
                gebied_res = st.selectbox("Selecteer gebied", gebied_opties, key="gebied_res")

            ### info voorbereiden lijn diagramen
            df_prod = (Fao_wereld_pivot_clean[(Fao_wereld_pivot_clean['Area'] == gebied_res) &
                      (Fao_wereld_pivot_clean['Item'] == graan_res)].sort_values('Year')
                      [['Year', 'Value_Production', 'Value_Area harvested']])

            df_ramp_jaar = (rampen_clean[rampen_clean['Disaster Type'] == ramp_res]
                            .groupby('Year').size().reset_index(name='Aantal_rampen'))

            df_samen = pd.merge(df_prod, df_ramp_jaar, on='Year', how='left').fillna(0)

            #### 1ste lijn diagram met wereld en contineten
            fig_line = go.Figure()

            fig_line.add_trace(go.Scatter(x=df_samen['Year'], y=df_samen['Value_Production'],
                                name='Productie (t)', line=dict(color='green'), mode='lines', yaxis='y1'))

            fig_line.add_trace(go.Scatter(x=df_samen['Year'], y=df_samen['Value_Area harvested'],
                                name='Area harvested (ha)', line=dict(color='purple'), mode='lines',
                                yaxis='y3'))

            fig_line.add_trace(go.Bar(x=df_samen['Year'], y=df_samen['Aantal_rampen'],
                                name=f'Aantal {ramp_res}s', marker_color='rgba(255, 100, 100, 0.4)',
                                yaxis='y2'))

            fig_line.update_layout(title=f'Productie {graan_res} ({gebied_res}) vs aantal {ramp_res}s per jaar',
                yaxis=dict(title='Productie (t)', title_font=dict(color='green'),
                           tickfont=dict(color='green'), side='left'),
                yaxis2=dict(title=f'Aantal {ramp_res}s', title_font=dict(color='red'),
                            tickfont=dict(color='red'), side='right', overlaying='y'),
                yaxis3=dict(title='Area harvested (ha)', title_font=dict(color='purple'),
                            tickfont=dict(color='purple'), side='left', overlaying='y',
                            anchor='free', position=0.0, showgrid=False),
                xaxis=dict(title='Jaar', domain=[0.12, 1.0]),
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1))
            st.plotly_chart(fig_line, use_container_width=True)

        # 2de lijn diagram met landen
        with st.container(border=True):
            st.header("Invloed van rampen op graanproductie per land")
            st.write("""Hieronder is dezelfde analyse te zien maar dan voor een specifiek land. 
            Selecteer een land, graansoort en ramptype om de relatie te bekijken.""")

            # data landen ophalen
            beschikbare_landen = sorted(Fao_pivot_clean['Area'].unique().tolist())

            col_land1, col_land2, col_land3 = st.columns(3)
            with col_land1:
                land_res = st.selectbox("Selecteer land", beschikbare_landen, key="land_res",
                                        index=beschikbare_landen.index('China')
                                        if 'China' in beschikbare_landen else 0)
            with col_land2:
                graan_land = st.selectbox("Selecteer graansoort", Granen_soorten, key="graan_land")
            with col_land3:
                ramp_land = st.selectbox("Selecteer ramptype", ["Flood", "Drought"], key="ramp_land")

            # info voorbereiden lijn diagramen
            df_prod_land = (Fao_pivot_clean[(Fao_pivot_clean['Area'] == land_res) &
                           (Fao_pivot_clean['Item'] == graan_land)].sort_values('Year')
                           [['Year', 'Value_Production', 'Value_Area harvested']])

            # Rampen filteren op land
            land_iso = rampen_clean[rampen_clean['Country'] == land_res]['ISO'].unique()
            if len(land_iso) > 0:
                df_ramp_land = (rampen_clean[(rampen_clean['ISO'].isin(land_iso)) &
                               (rampen_clean['Disaster Type'] == ramp_land)]
                               .groupby('Year').size().reset_index(name='Aantal_rampen'))
            else:
                df_ramp_land = pd.DataFrame(columns=['Year', 'Aantal_rampen'])

            df_samen_land = pd.merge(df_prod_land, df_ramp_land, on='Year', how='left').fillna(0)

            ### traces maken voor figuur met fallback voor geen data
            if df_samen_land.empty:
                st.warning(f"Geen data beschikbaar voor {land_res} met {graan_land}.")
            else:
                fig_land = go.Figure()

                fig_land.add_trace(go.Scatter(x=df_samen_land['Year'], y=df_samen_land['Value_Production'],
                                              name='Productie (t)', line=dict(color='green'), mode='lines',
                                              yaxis='y1'))

                fig_land.add_trace(go.Scatter(x=df_samen_land['Year'], y=df_samen_land['Value_Area harvested'],
                                              name='Area harvested (ha)', line=dict(color='purple'), mode='lines',
                                              yaxis='y3'))

                fig_land.add_trace(go.Bar(x=df_samen_land['Year'], y=df_samen_land['Aantal_rampen'],
                                              name=f'Aantal {ramp_land}s', marker_color='rgba(255, 100, 100, 0.4)',
                                              yaxis='y2'))

                fig_land.update_layout(title=f'Productie {graan_land} in {land_res} vs aantal {ramp_land}s per jaar',
                                       legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
                                       yaxis=dict(title='Productie (t)', title_font=dict(color='green'),
                                       tickfont=dict(color='green'), side='left'),
                                       yaxis2=dict(title=f'Aantal {ramp_land}s', title_font=dict(color='red'),
                                       tickfont=dict(color='red'), side='right', overlaying='y'),
                                       yaxis3=dict(title='Area harvested (ha)', title_font=dict(color='purple'),
                                       tickfont=dict(color='purple'), side='left', overlaying='y',
                                       anchor='free', position=0.0, showgrid=False),
                                       xaxis=dict(title='Jaar', domain=[0.12, 1.0]))
                st.plotly_chart(fig_land, use_container_width=True)

                #### Conclusie
                st.subheader("Uiteindelijke conclusie")
                st.write("""Als de onderzoeksvraag wordt beantwoord op wereld productie van de soorten graan
                dan valt het moeilijk te zeggen of het echt invloed heeft om het niet duidelijk zichtbare invloed
                heeft. Maar als het landelijk wordt bepaald kan er een beter argument gemaakt worden. Het blijft
                moeilijk om een duidelijke invloed te concluderen zonder allerlei andere soorten factoren op de 
                productie van de verschillende soorten granen mee te nemen in de analyse. Een vervolg onderzoek is
                nodig dat andere factoren meerekent om een conclusie te trekken.""")


#### Einde script
