import pandas as pd
# import duckdb
import plotly.express as px
import streamlit as st
import json

# Conectar ao banco DuckDB
# con = duckdb.connect("crimes.duckdb")

# Ler a tabela 'crimes' para um DataFrame pandas
# df = con.execute("SELECT * FROM crimes").fetchdf()

df = pd.read_csv("sesp_pr_bi.csv", sep=";", encoding="cp1252")

df.columns = df.columns.str.strip().str.lower()

st.markdown("""
<style>

/* Expandir largura máxima do container */
.block-container {
    max-width: 100%;
    padding-left: 1rem;
    padding-right: 1rem;
}

/* Forçar colunas a alinharem pelo topo */
.st-emotion-cache-1r6slb0, .st-emotion-cache-1r6slb0 > div {
    align-items: flex-start;
}

/* Ajustar altura mínima das tabelas */
div[data-testid="stDataFrame"] {
    min-height: 400px;  /* ajuste conforme a altura do gráfico */
}

/* Alinhar tabela com o título do gráfico */
div[data-testid="stDataFrame"] {
    margin-top: 2.5rem; /* ajuste fino para alinhar com o título */
}

/* Fundo da aplicação */
[data-testid="stAppViewContainer"] {
    background-color: #000000; /* preto */
    color: #ffffff;
}

/* Fundo do menu lateral */
[data-testid="stSidebar"] {
    background-color: #111111 !important; /*#FFA500; preto suave */
    color: #ffffff;
    border-radius: 6px;
    padding: 6px;
}

/* Botões dentro da sidebar */
[data-testid="stSidebar"] button {
    background-color: #ff6600 !important;  /* fundo laranja */
    color: white !important;               /* texto branco */
    border-radius: 8px !important;         /* bordas arredondadas */
    border: 1px solid #ff6600 !important;  /* borda igual ao fundo */
}

/* Efeito hover (quando passa o mouse) */
[data-testid="stSidebar"] button:hover {
    background-color: #cc5200 !important;  /* laranja mais escuro */
    border: 1px solid #cc5200 !important;
}

/* Cabeçalho transparente */
[data-testid="stHeader"] {
    background: rgba(0,0,0,0);
}

/* Altera a cor dos textos das st.tabs */
div[data-testid="stTabs"] button {
color: white; /* muda a cor do texto */
}
div[data-testid="stTabs"] button:hover {
color: red; /* cor ao passar o mouse */
}
div[data-testid="stTabs"] button:focus {
color: red; /* cor quando selecionada */
}
/* Altera a cor do texto das opções da st.radio*/
div[data-testid="stRadio"] label {
color: white;
font-weight: bold;
}
            
</style>
""", unsafe_allow_html=True)

st.title("📊 Panorama de Crimes contra a Vida - Paraná")

st.sidebar.header("Filtros de Informações")

# --------------------------------------------------------
# Inicializa estado
# --------------------------------------------------------
if "filtros" not in st.session_state:
    st.session_state.filtros = {}

def aplicar_filtros(df, filtros, ignorar=None):
    df_f = df.copy()
    for col, valores in filtros.items():
        if col == ignorar:
            continue
        if valores:
            df_f = df_f[df_f[col].isin(valores)]
    return df_f

# --------------------------------------------------------
# Lista ordenada dos filtros
# --------------------------------------------------------
filtros_info = [
    ("ano", "Ano"),
    ("mes", "Mês"),
    ("aisp", "Áreas Integr. Seg. Pública - AISP"),
    ("municipio", "Município"),
    ("bairro", "Bairro"),
    ("natureza", "Natureza"),
    ("f_etaria", "Faixa Etária"),
    ("sexo", "Sexo"),
    ("raca_cor", "Raça/Cor"),
    ("orientacao_sexual", "Orientação Sexual"),
]

df_base = df.copy()

for coluna, label in filtros_info:

    # aplica todos os filtros EXCETO o filtro atual
    df_opcoes = aplicar_filtros(df_base, st.session_state.filtros, ignorar=coluna)

    # opções possíveis com o filtro atual excluído (multi select real)
    opcoes = sorted(df_opcoes[coluna].dropna().unique())

    # remove seleções inválidas
    selecao_atual = st.session_state.filtros.get(coluna, [])
    selecao_atual = [v for v in selecao_atual if v in opcoes]

    # --------------------------------------------------------
    # UI
    # --------------------------------------------------------
    with st.sidebar.expander(label, expanded=False):
        nova_selecao = st.multiselect(
            label,
            options=opcoes,
            default=selecao_atual,
            placeholder="Escolha 1 ou +",
            key=f"ms_{coluna}"
        )

    # atualiza filtro e rerun
    if nova_selecao != st.session_state.filtros.get(coluna):
        st.session_state.filtros[coluna] = nova_selecao
        #st.session_state.opcao_mapa = "Quantidade de Crimes"
        st.rerun()

# --------------------------------------------------------
# Botão limpar filtros
# --------------------------------------------------------
if st.sidebar.button("Limpar filtros"):
    st.session_state.filtros = {}
    st.rerun()

df_filtrado = aplicar_filtros(df_base, st.session_state.filtros)

#-----------------------------------------------------------------------------------------------------------
# Cria abas
aba1, aba2, aba3, aba4 = st.tabs([
    "Histórico por Período",
    "Histórico por Região",
    "Histórico por Perfil Social",
    "Histórico por Tipo de Crime"
])

with aba1:
    st.subheader("📈 Mortes - Histórico por Período")
    #st.write("👉 Incluir novos gráficos")

    #-----------------------------------------------------------------------------------------------------------
    # Gráfico - Quantidade de Crimes por Ano
    # Agrupar os dados por ano
    df_ano = df_filtrado.groupby("ano", as_index=False)["natureza"].count().reset_index()

    # Gráfico em colunas
    fig_ano = px.bar(
        df_ano,
        x="ano",
        y="natureza",
        title="Evolução dos Crimes por Ano",
        labels={"ano": "Ano", "natureza": "Quantidade de Crimes"},
        color="natureza",
        #color_continuous_scale="Blues",  # escala de azul (mais escuro = maior)
        #text="natureza"  # mostra o total em cima das colunas
    )
    # Ajustes visuais
    #fig.update_traces(texttemplate="%{text}", textposition="outside")
    fig_ano.update_layout(
        xaxis_title="Ano",
        yaxis_title="Quantidade de Crimes",
        showlegend=False,
        plot_bgcolor="black",             # fundo da área do gráfico
        paper_bgcolor="black",            # fundo externo
        font=dict(color="white"),         # texto branco
        title=dict(x=0, font=dict(color="white")),
        # Ajuste dos eixos para remover linhas de grade
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
        #coloraxis_showscale=False
    )
    st.plotly_chart(fig_ano, use_container_width=True)

    #-----------------------------------------------------------------------------------------------------------
    # Gráfico - Quantidade de Crimes por Mês
    # Agrupar os dados por mês

    mes_map = {1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun", 7: "Jul", 8: "Ago", 9: "Set", 10: "Out", 11: "Nov", 12: "Dez"}
    df_mes = df_filtrado.groupby("mes", as_index=False)["natureza"].count().reset_index()

    # Gráfico em colunas
    fig_mes = px.bar(
        df_mes,
        x="mes",
        y="natureza",
        title="Evolução dos Crimes por Mês",
        labels={"mes": "Mês", "natureza": "Quantidade de Crimes"},
        color="natureza",
        #color_continuous_scale="Blues",  # escala de azul (mais escuro = maior)
        #text="natureza"  # mostra o total em cima das colunas
    )
    # Forçar todos os ticks do eixo X
    fig_mes.update_xaxes(
    tickmode="array",
    tickvals=list(mes_map.keys()),
    ticktext=list(mes_map.values())
    )
    # Ajustes visuais
    #fig.update_traces(texttemplate="%{text}", textposition="outside")
    fig_mes.update_layout(
        xaxis_title="Mês",
        yaxis_title="Quantidade de Crimes",
        showlegend=False,
        plot_bgcolor="black",             # fundo da área do gráfico
        paper_bgcolor="black",            # fundo externo
        font=dict(color="white"),         # texto branco
        title=dict(x=0, font=dict(color="white")),
        # Ajuste dos eixos para remover linhas de grade
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
         #coloraxis_showscale=False
    )
    st.plotly_chart(fig_mes, use_container_width=True)

    #-----------------------------------------------------------------------------------------------------------
    # Gráfico - Quantidade de Crimes por Dia
    # Agrupar os dados por mês

    dia_map = {i: str(i) for i in range(1, 32)}
    df_dia = df_filtrado.groupby("dia", as_index=False)["natureza"].count().reset_index()

    # Gráfico em colunas
    fig_dia = px.bar(
        df_dia,
        x="dia",
        y="natureza",
        title="Evolução dos Crimes por Dia",
        labels={"dia": "Dias", "natureza": "Quantidade de Crimes"},
        color="natureza",
        #color_continuous_scale="Blues",  # escala de azul (mais escuro = maior)
        #text="natureza"  # mostra o total em cima das colunas
    )
    #Forçar todos os ticks do eixo X
    fig_dia.update_xaxes(
    tickmode="array",
    tickvals=list(dia_map.keys()),
    ticktext=list(dia_map.values())
    )
    # Ajustes visuais
    #fig.update_traces(texttemplate="%{text}", textposition="outside")
    fig_dia.update_layout(
        xaxis_title="Dias",
        yaxis_title="Quantidade de Crimes",
        showlegend=False,
        plot_bgcolor="black",             # fundo da área do gráfico
        paper_bgcolor="black",            # fundo externo
        font=dict(color="white"),         # texto branco
        title=dict(x=0, font=dict(color="white")),
        # Ajuste dos eixos para remover linhas de grade
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
        #coloraxis_showscale=False
    )
    st.plotly_chart(fig_dia, use_container_width=True)

    #-----------------------------------------------------------------------------------------------------------
    # Gráfico - Totalização de Crimes por dia da semana
    df_dia_sem = df_filtrado.groupby("dia_semana")["natureza"].count().reset_index()

    dias_semana_map = {1: "Segunda-feira", 2: "Terça-feira", 3: "Quarta-feira", 4: "Quinta-feira", 5: "Sexta-feira", 6: "Sábado", 7: "Domingo"}

    totais = df_dia_sem.groupby("dia_semana")["natureza"].sum().to_dict()
    df_dia_sem["total_legenda"] = df_dia_sem["dia_semana"].map(lambda d: totais.get(d, 0))

    fig_dia_sem = px.bar(
        df_dia_sem,
        x="dia_semana",
        y="natureza",
        title="Quantidade de Crimes por Dia da Semana",
        labels={"natureza": "Quantidade de Crimes", "dia_semana": "Dia da Semana", "total_legenda": "Crimes"},
        color="total_legenda",
        #color_continuous_scale="Blues"  # escala de azul (mais escuro = maior)
    )

    fig_dia_sem.update_xaxes(
        tickvals=list(dias_semana_map.keys()),   # valores originais (1 a 7)
        ticktext=list(dias_semana_map.values())  # nomes que vão aparecer
    )
    fig_dia_sem.update_layout(
        showlegend=False,
        plot_bgcolor="black",             # fundo da área do gráfico
        paper_bgcolor="black",            # fundo externo
        font=dict(color="white"),         # texto branco
        title=dict(x=0, font=dict(color="white")),
        # Ajuste dos eixos para remover linhas de grade
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
    )
    st.plotly_chart(fig_dia_sem, use_container_width=True)

    #col1, col2 = st.columns([1.7, 1])  # gráfico ocupa mais largura, tabela menos
    #with col1:
    #    st.plotly_chart(fig, use_container_width=True)
    #with col2:
        # Número de linhas da tabela
    #    num_linhas = len(df_group)

        # Definir altura proporcional (ex.: 35px por linha + espaço para cabeçalho)
    #    altura = min(600, max(283, num_linhas * 35))  
        
    #    df_group_display = df_group.copy()
    #    df_group_display["dia_semana"] = df_group_display["dia_semana"].map(dias_semana_map)

    #    df_group_display.index.name = "Rank"
        
    #    st.dataframe(df_group_display.drop(columns=["total_legenda"]), use_container_width=True, height=altura)

    #-----------------------------------------------------------------------------------------------------------
    # Gráfico - Quantidade de Crimes por Hora
    # Agrupar os dados por mês
    hora_map = {i: str(i) for i in range(0, 24)}
    df_hora = df_filtrado.groupby("hora", as_index=False)["natureza"].count().reset_index()

    # Gráfico em colunas
    fig_hora = px.bar(
        df_hora,
        x="hora",
        y="natureza",
        title="Evolução dos Crimes por Hora",
        labels={"hora": "Horas", "natureza": "Quantidade de Crimes"},
        color="natureza",
        #color_continuous_scale="Blues",  # escala de azul (mais escuro = maior)
        #text="natureza"  # mostra o total em cima das colunas
    )
    #Forçar todos os ticks do eixo X
    fig_hora.update_xaxes(
    tickmode="array",
    tickvals=list(hora_map.keys()),
    ticktext=list(hora_map.values())
    )
    # Ajustes visuais
    #fig.update_traces(texttemplate="%{text}", textposition="outside")
    fig_hora.update_layout(
        xaxis_title="Horas",
        yaxis_title="Quantidade de Crimes",
        showlegend=False,
        plot_bgcolor="black",             # fundo da área do gráfico
        paper_bgcolor="black",            # fundo externo
        font=dict(color="white"),         # texto branco
        title=dict(x=0, font=dict(color="white")),
        # Ajuste dos eixos para remover linhas de grade
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
        #coloraxis_showscale=False
    )
    st.plotly_chart(fig_hora, use_container_width=True)

with aba2:
    st.subheader("📈 Mortes - Histórico por Região")

    # Dataframes - Contagem por município (Absoluta e Taxa por 100.000 Habitantes)
    df_mun_absol = df_filtrado.groupby("municipio", as_index=False)["natureza"].count()
    df_mun_taxa = df_filtrado.groupby(["municipio", "populacao"], as_index=False)["natureza"].count()
    df_mun_taxa["taxa_crimes"] = round((df_mun_taxa["natureza"] / df_mun_taxa["populacao"]) * 100000,2)

    #-----------------------------------------------------------------------------------------------------------
    # Gráfico - Mapa com contagem absoluta de crimes por município e Taxa por 100.000 Habitantes)
    with open("geojs-41-mun-normalizado.json", "r", encoding="utf-8") as f:
        geojson_data = json.load(f)

    # Recuperar coordenadas do GeoJSON
    coords = []
    for feature in geojson_data["features"]:
        props = feature["properties"]
        nome = props.get("name_normalizado")

        # só municípios filtrados
        if nome in df_mun_absol["municipio"].values:
            geom = feature["geometry"]

            # pegar coordenadas do primeiro polígono
            if geom["type"] == "Polygon":
                poly = geom["coordinates"][0]
            elif geom["type"] == "MultiPolygon":
                poly = geom["coordinates"][0][0]
            else:
                continue

            lons = [p[0] for p in poly]
            lats = [p[1] for p in poly]

            coords.extend(list(zip(lats, lons)))

    # Calcular centro e zoom dinamicamente
    import numpy as np

    if len(coords) > 0:
        lats = np.array([c[0] for c in coords])
        lons = np.array([c[1] for c in coords])

        lat_center = lats.mean()
        lon_center = lons.mean()

        lat_range = lats.max() - lats.min()
        lon_range = lons.max() - lons.min()
        range_max = max(lat_range, lon_range)

        # cálculo do zoom adaptativo
        if range_max < 0.1:
            zoom = 10.5
        elif range_max < 0.3:
            zoom = 10
        elif range_max < 0.7:
            zoom = 9
        elif range_max < 1.5:
            zoom = 8
        elif range_max < 3:
            zoom = 7
        else:
            zoom = 6.5
    else:
        # valores padrão para o estado inteiro
        lat_center = -25.4
        lon_center = -49.3
        zoom = 6.5

    # Criar mapa coroplético - contagem absoluta
    fig_mapa_absol = px.choropleth_mapbox(
        df_mun_absol,
        geojson=geojson_data,
        locations="municipio",
        featureidkey="properties.name_normalizado",
        color="natureza",
        color_continuous_scale="Blues",
        title="Municípios com maior incidência de crimes",
        mapbox_style="carto-darkmatter",
        zoom=zoom,
        center={"lat": lat_center, "lon": lon_center},
        opacity=1.0, #0.6,
    )
    fig_mapa_absol.update_layout(
        height=700,
        plot_bgcolor="black",
        paper_bgcolor="black",
        font=dict(color="white"),
        title=dict(x=0, font=dict(color="white")),
        margin=dict(l=0, r=0, t=40, b=0),
        coloraxis_colorbar=dict(title="Quantidade de Crimes")   # 👉 novo título da legenda
    )

    # Criar mapa coroplético - Taxa por 100.000 Habitantes
    fig_mapa_taxa = px.choropleth_mapbox(
        df_mun_taxa,
        geojson=geojson_data,
        locations="municipio",
        featureidkey="properties.name_normalizado",
        color="taxa_crimes",                 # 👉 agora usamos a taxa
        color_continuous_scale="Reds",       # escala em vermelho para destacar intensidade
        title="Taxa de Crimes por 100.000 habitantes",
        mapbox_style="carto-darkmatter",
        zoom=zoom,
        center={"lat": lat_center, "lon": lon_center},
        opacity=1.0,
    )
    fig_mapa_taxa.update_layout(
        height=700,
        plot_bgcolor="black",
        paper_bgcolor="black",
        font=dict(color="white"),
        title=dict(x=0, font=dict(color="white")),
        margin=dict(l=0, r=0, t=40, b=0),
        coloraxis_colorbar=dict(title="Taxa por 100.000 hab.")
    )
    # seleciona gráfico absoluto ou taxa
    if "opcao_mapa" not in st.session_state:
        st.session_state.opcao_mapa = "Quantidade de Crimes"
    
    opcao_mapa = st.radio(
        "Selecione o tipo de mapa:",
        ["Quantidade de Crimes", "Taxa por 100.000 habitantes"],
        key="opcao_mapa"
    )
    if st.session_state.opcao_mapa == "Quantidade de Crimes":
        st.plotly_chart(fig_mapa_absol, use_container_width=True)
    else:
        st.plotly_chart(fig_mapa_taxa, use_container_width=True)

    #-----------------------------------------------------------------------------------------------------------
    # Gráfico - 10 municípios com a maior incidência de crimes (Quantidade)
    # df_munic_qtd_maior = df_filtrado.groupby("municipio")["natureza"].count().reset_index()
    # df_munic_qtd_maior = df_munic_qtd_maior.sort_values("natureza", ascending=False).head(10)
    top10_mun_absol = df_mun_absol.nlargest(10, "natureza")

    fig_munic_qtd_maior = px.bar(
        top10_mun_absol,
        x="natureza",
        y="municipio",
        orientation="h",
        title="10 Municípios com a maior incidência de crimes",
        labels={"natureza": "Quantidade de Crimes", "municipio": "Municípios"},
        color="natureza",
        #color_continuous_scale="Blues"  # escala de azul (mais escuro = maior)
    )
    fig_munic_qtd_maior.update_layout(
        yaxis=dict(categoryorder="total ascending", showgrid=False),
        xaxis=dict(showgrid=False),
        showlegend=False,
        plot_bgcolor="black",             # fundo da área do gráfico
        paper_bgcolor="black",            # fundo externo
        font=dict(color="white"),         # texto branco
        title=dict(x=0, font=dict(color="white")),
    )
    st.plotly_chart(fig_munic_qtd_maior, use_container_width=True)

    #-----------------------------------------------------------------------------------------------------------
    # Gráfico - 10 municípios com maior taxa de crimes por 100.000 habitantes
    top10_mun_taxa = df_mun_taxa.nlargest(10, "taxa_crimes")
    
    # Criar gráfico de barras horizontais
    fig_municipio = px.bar(top10_mun_taxa,
                        x="taxa_crimes",
                        y="municipio",
                        orientation="h",
                        title="10 Municípios com Maior Taxa de Crimes por 100.000 Habitantes",
                        labels={"taxa_crimes": "Crimes por Total de Habitantes", "municipio": "Município"},
                        color="taxa_crimes")

    # Mostrar maior taxa no topo
    fig_municipio.update_layout(
        yaxis=dict(categoryorder="total ascending", showgrid=False),
        xaxis=dict(showgrid=False),
        showlegend=False,
        plot_bgcolor="black",             # fundo da área do gráfico
        paper_bgcolor="black",            # fundo externo
        font=dict(color="white"),         # texto branco
        title=dict(x=0, font=dict(color="white")),
    )
    st.plotly_chart(fig_municipio, use_container_width=True)
    # Opcional: mostrar tabela com valores exatos
    # st.dataframe(top10_mun_taxa[["municipio", "total_crimes", "populacao", "taxa_crimes"]])

    #-----------------------------------------------------------------------------------------------------------
    # Gráfico - 10 municípios com a menor quantidade de crimes
    bottom10_mun_absol = df_mun_absol.nsmallest(10, "natureza")

    fig_munic_qtd_menor = px.bar(
        bottom10_mun_absol,
        x="natureza",
        y="municipio",
        orientation="h",
        title="10 Municípios com a menor incidência de crimes",
        labels={"natureza": "Quantidade de Crimes", "municipio": "Municípios"},
        color="natureza",
        #color_continuous_scale="Blues"  # escala de azul (mais escuro = maior)
    )
    fig_munic_qtd_menor.update_layout(
        yaxis=dict(categoryorder="total descending", showgrid=False),
        xaxis=dict(showgrid=False),
        showlegend=False,
        plot_bgcolor="black",             # fundo da área do gráfico
        paper_bgcolor="black",            # fundo externo
        font=dict(color="white"),         # texto branco
        title=dict(x=0, font=dict(color="white")),
  )
    st.plotly_chart(fig_munic_qtd_menor, use_container_width=True)
   
    #-----------------------------------------------------------------------------------------------------------
    # Gráfico - 10 municípios com menor taxa de crimes por 100.000 habitantes
    bottom10_mun_taxa = df_mun_taxa.nsmallest(10, "taxa_crimes")

    fig_municipio_menor = px.bar(bottom10_mun_taxa,
                                x="taxa_crimes",
                                y="municipio",
                                orientation="h",
                                title="10 Municípios com Menor Taxa de Crimes por 100.000 Habitante",
                                labels={"taxa_crimes": "Crimes por Total de Habitantes", "municipio": "Município"},
                                color="taxa_crimes")

    # Mostrar menor taxa no topo
    fig_municipio_menor.update_layout(
        yaxis=dict(categoryorder="total descending", showgrid=False),
        xaxis=dict(showgrid=False),
        showlegend=False,
        plot_bgcolor="black",             # fundo da área do gráfico
        paper_bgcolor="black",            # fundo externo
        font=dict(color="white"),         # texto branco
        title=dict(x=0, font=dict(color="white")),
   )
    st.plotly_chart(fig_municipio_menor, use_container_width=True)

    #-----------------------------------------------------------------------------------------------------------
    # Gráfico - 10 municípios mais populosos e suas taxas de crimes por 100.000 habitantes
    top10_mun_pop_taxa = df_mun_taxa.nlargest(10, "populacao")

    # Criar gráfico de barras horizontais
    fig_populosos = px.bar(top10_mun_pop_taxa,
                        x="taxa_crimes",
                        y="municipio",
                        orientation="h",
                        title="10 Municípios Mais Populosos e suas Taxas de Crimes",
                        labels={"taxa_crimes": "Taxa de Crimes por 100.000 Habitantes", "municipio": "Município"},
                        color="taxa_crimes")

    # Mostrar maior taxa no topo
    fig_populosos.update_layout(
        yaxis=dict(categoryorder="total ascending", showgrid=False),
        xaxis=dict(showgrid=False),
        showlegend=False,
        plot_bgcolor="black",             # fundo da área do gráfico
        paper_bgcolor="black",            # fundo externo
        font=dict(color="white"),         # texto branco
        title=dict(x=0, font=dict(color="white")),
    )
    st.plotly_chart(fig_populosos, use_container_width=True)

#-----------------------------------------------------------------------------------------------------------
    # Gráfico - 10 municípios menos populosos e menores taxas de crimes
    bottom_mun_pop_taxa = df_mun_taxa.nsmallest(10, "populacao")

    # Criar gráfico de barras horizontais
    fig_populosos = px.bar(bottom_mun_pop_taxa,
                        x="taxa_crimes",
                        y="municipio",
                        orientation="h",
                        title="10 Municípios Menos Populosos e suas Taxas de Crimes",
                        labels={"taxa_crimes": "Taxa de Crimes por 100.000 Habitantes", "municipio": "Município"},
                        color="taxa_crimes")

    # Mostrar maior taxa no topo
    fig_populosos.update_layout(
        yaxis=dict(categoryorder="total descending", showgrid=False),
        xaxis=dict(showgrid=False),
        showlegend=False,
        plot_bgcolor="black",             # fundo da área do gráfico
        paper_bgcolor="black",            # fundo externo
        font=dict(color="white"),         # texto branco
        title=dict(x=0, font=dict(color="white")),    
    )
    st.plotly_chart(fig_populosos, use_container_width=True)



    #df_group_populosos_ren = df_group_populosos.rename(columns={
    #    "municipio": "Municípios",
    #    "total_crimes": "Crimes",
    #    "populacao": "População",
    #    "taxa_crimes": "Taxa de Crimes"
    #})
    
    #col1, col2 = st.columns([1.7, 1])  # gráfico ocupa mais largura, tabela menos
    #with col1:
    #    st.plotly_chart(fig_populosos, use_container_width=True)
    #with col2:
        # st.markdown("Top 10 Municípios Mais Populosos e Taxa de Crimes")
    #    st.dataframe(df_group_populosos_ren, use_container_width=True, height=380)

    #-----------------------------------------------------------------------------------------------------------
    # Gráfico 2 - Top 10 bairros com maior incidência
    df_group_bairro = df_filtrado.groupby("bairro")["natureza"].count().reset_index()
    df_group_bairro = df_group_bairro.sort_values("natureza", ascending=False).head(10)

    fig_bairro = px.bar(
    df_group_bairro,
    x="natureza",
    y="bairro",
    orientation="h",   # barras horizontais
    title="10 Bairros com Maior Incidência de Crimes",
    labels={"natureza": "Quantidade de Crimes", "bairro": "Bairro"},
    color="natureza",
    #color_continuous_scale="Blues",
)

    # Inverter ordem para mostrar o maior no topo
    fig_bairro.update_layout(
        yaxis=dict(categoryorder="total ascending", showgrid=False),  # ordem + remove grade
        xaxis=dict(showgrid=False),                                   # remove grade eixo X
        showlegend=False,
        plot_bgcolor="black",             # fundo da área do gráfico
        paper_bgcolor="black",            # fundo externo
        font=dict(color="white"),         # texto branco
        title=dict(x=0, font=dict(color="white"))
    )
    st.plotly_chart(fig_bairro, use_container_width=True)

    # Gráfico - Top 10 bairros com meno incidência
    df_group_bairro_ = df_filtrado.groupby("bairro")["natureza"].count().reset_index()
    df_group_bairro_ = df_group_bairro_.sort_values("natureza", ascending=False).tail(10)

    fig_bairro_ = px.bar(df_group_bairro_, 
                        x="natureza", 
                        y="bairro",
                        orientation="h",   # barras horizontais
                        title="10 Bairros com Menor Incidência de Crimes",
                        labels={"natureza": "Quantidade de Crimes", "bairro": "Bairro"},
                        color="natureza")
    # Inverter ordem para mostrar o maior no topo
    fig_bairro_.update_layout(
            yaxis=dict(categoryorder="total descending", showgrid=False),
            xaxis=dict(showgrid=False),
            showlegend=False,
            plot_bgcolor="black",             # fundo da área do gráfico
            paper_bgcolor="black",            # fundo externo
            font=dict(color="white"),         # texto branco
            title=dict(x=0, font=dict(color="white")),
    )
    st.plotly_chart(fig_bairro_, use_container_width=True)

with aba3:
    st.subheader("📈 Mortes - Histórico por Perfil Social")
    st.write("👉 Incluir novos gráficos")
    
    #-----------------------------------------------------------------------------------------------------------
    # Gráfico - Crimes por Sexo/Gênero
    df_sexo = df_filtrado.groupby("sexo")["natureza"].count().reset_index()

    cores = ["#ffffff", "#cce5ff", "#66b2ff", "#0050a0"]

    fig_sexo = px.pie(
        df_sexo,
        names="sexo",          # categorias (sexo/gênero)
        values="natureza",     # quantidade de crimes
        title="Distribuição por Sexo/Gênero",
        color="sexo",
        color_discrete_sequence=cores,
        hole=0.4                 # se quiser formato donut, use hole=0.4
    )
    fig_sexo.update_layout(
    title={
        "text": "Distribuição por Sexo/Gênero",
        "x": 0.5,              # centraliza horizontalmente
        "xanchor": "center",   # ancora no centro
        "yanchor": "top",      # ancora no topo
        "font": {"color": "white"}
    },
    showlegend=False,
    plot_bgcolor="black",      # fundo da área do gráfico
    paper_bgcolor="black",     # fundo externo
    font=dict(color="white"),  # texto branco (geral)
    xaxis=dict(showgrid=False),
    yaxis=dict(showgrid=False),
    )

    # Mostrar percentuais no gráfico
    fig_sexo.update_traces(textinfo="percent+label",showlegend=False )
    
    #-----------------------------------------------------------------------------------------------------------
    # Gráfico - Crimes por Raça/Cor
    df_raca = df_filtrado.groupby("raca_cor")["natureza"].count().reset_index()

    fig_raca = px.pie(
        df_raca,
        names="raca_cor",      # categorias (raça/cor)
        values="natureza",     # quantidade de crimes
        title="Distribuição por Raça/Cor",
        color_discrete_sequence=cores,
        hole=0.4                 # se quiser formato donut, use hole=0.4
    )
    fig_raca.update_layout(
    title={
        "text": "Distribuição por Raça/Cor",
        "x": 0.5,              # 👉 centraliza horizontalmente
        "xanchor": "center",   # ancora no centro
        "yanchor": "top",      # ancora no topo
        "font": {"color": "white"}
    },
    showlegend=False,
    plot_bgcolor="black",             # fundo da área do gráfico
    paper_bgcolor="black",            # fundo externo
    font=dict(color="white"),         # texto branco
    # Ajuste dos eixos para remover linhas de grade
    xaxis=dict(showgrid=False),
    yaxis=dict(showgrid=False),
    )
    # Mostrar percentuais no gráfico
    fig_raca.update_traces(textinfo="percent+label",showlegend=False )

    #-----------------------------------------------------------------------------------------------------------
    # Gráfico - Crimes por Orientação Sexual
    df_orientacao = df_filtrado.groupby("orientacao_sexual")["natureza"].count().reset_index()

    fig_orientacao = px.pie(
        df_orientacao,
        names="orientacao_sexual",      # categorias (raça/cor)
        values="natureza",     # quantidade de crimes
        title="Distribuição por Orientação Sexual",
        color_discrete_sequence=cores,
        hole=0.4                 # se quiser formato donut, use hole=0.4
    )
    fig_orientacao.update_layout(
    title={
        "text": "Distribuição por Orientação Sexual",
        "x": 0.5,              # 👉 centraliza horizontalmente
        "xanchor": "center",   # ancora no centro
        "yanchor": "top",       # ancora no topo
        "font": {"color": "white"}
        },
    showlegend=False,
    plot_bgcolor="black",             # fundo da área do gráfico
    paper_bgcolor="black",            # fundo externo
    font=dict(color="white"),         # texto branco
    # Ajuste dos eixos para remover linhas de grade
    xaxis=dict(showgrid=False),
    yaxis=dict(showgrid=False),
    )
    # Mostrar percentuais no gráfico
    fig_orientacao.update_traces(textinfo="percent+label",showlegend=False )


    col1, col2, col3 = st.columns([1, 1, 1])  # gráfico ocupa mais largura, tabela menos
    with col1:
        st.plotly_chart(fig_sexo, use_container_width=True)
    
    with col2:
        st.plotly_chart(fig_raca, use_container_width=True)

    with col3:
        st.plotly_chart(fig_orientacao, use_container_width=True)


    #-----------------------------------------------------------------------------------------------------------
    # Gráfico - Quantidade de Crimes por Faixa Etária
    df_etaria = df_filtrado.groupby("f_etaria", as_index=False)["natureza"].count().reset_index()

    # Gráfico em colunas
    fig_etaria = px.bar(
        df_etaria,
        x="f_etaria",
        y="natureza",
        title="Evolução dos Crimes por Faixa Etária",
        labels={"hora": "Horas", "natureza": "Quantidade de Crimes"},
        color="natureza",
        #color_continuous_scale="Blues",  # escala de azul (mais escuro = maior)
        #text="natureza"  # mostra o total em cima das colunas
    )
    # Ajustes visuais
    #fig.update_traces(texttemplate="%{text}", textposition="outside")
    fig_etaria.update_layout(
        xaxis_title="Faixa Etária",
        yaxis_title="Quantidade de Crimes",
        showlegend=False,
        plot_bgcolor="black",             # fundo da área do gráfico
        paper_bgcolor="black",            # fundo externo
        font=dict(color="white"),         # texto branco
        title=dict(x=0, font=dict(color="white")),
        # Ajuste dos eixos para remover linhas de grade
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
        #coloraxis_showscale=False
    )
    st.plotly_chart(fig_etaria, use_container_width=True)

    #-----------------------------------------------------------------------------------------------------------
    # Gráfico - Quantidade de Crimes por Idade
    df_idade = df_filtrado.groupby("idade", as_index=False)["natureza"].count().reset_index()

    ordem_idades = ["< 01 ano"] + sorted([i for i in df_idade["idade"].unique() if i != "< 01 ano"]) + ["Não Informado"]

    # Gráfico em colunas
    fig_idade = px.bar(
        df_idade,
        x="idade",
        y="natureza",
        title="Evolução dos Crimes por Idade",
        labels={"idade": "Idade", "natureza": "Quantidade de Crimes"},
        color="natureza",
        category_orders={"idade": ordem_idades},  # 👉 força a ordem
        #color_continuous_scale="Blues",  # escala de azul (mais escuro = maior)
        #text="natureza"  # mostra o total em cima das colunas
    )
    # Ajustes visuais
    #fig.update_traces(texttemplate="%{text}", textposition="outside")
    fig_idade.update_layout(
        xaxis_title="Idades",
        yaxis_title="Quantidade de Crimes",
        showlegend=False,
        plot_bgcolor="black",             # fundo da área do gráfico
        paper_bgcolor="black",            # fundo externo
        font=dict(color="white"),         # texto branco
        title=dict(x=0, font=dict(color="white")),
        # Ajuste dos eixos para remover linhas de grade
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False)
    )
    st.plotly_chart(fig_idade, use_container_width=True)





#col1, col2 = st.columns([1.7, 1])  # gráfico ocupa mais largura, tabela menos
    #with col1:
    #    st.plotly_chart(fig, use_container_width=True)
    #with col2:
        # Número de linhas da tabela
    #    num_linhas = len(df_group)

        # Definir altura proporcional (ex.: 35px por linha + espaço para cabeçalho)
    #    altura = min(600, max(283, num_linhas * 35))  
        
    #    df_group_display = df_group.copy()
    #    df_group_display["dia_semana"] = df_group_display["dia_semana"].map(dias_semana_map)

    #    df_group_display.index.name = "Rank"
        
    #    st.dataframe(df_group_display.drop(columns=["total_legenda"]), use_container_width=True, height=altura)





with aba4:
    st.subheader("📈 Mortes - Histórico por Tipo de Crime")
    st.write("👉 Incluir novos gráficos")

    # Gráfico - Quantidade de Crimes por Tipo de Crime
    df_tipo_crime = df_filtrado.groupby("natureza", as_index=False)["id_vitima"].count().reset_index()

    #ordem_idades = ["< 01 ano"] + sorted([i for i in df_idade["idade"].unique() if i != "< 01 ano"]) + ["Não Informado"]

    # Gráfico em colunas
    fig_tipo_crime = px.bar(
        df_tipo_crime,
        x="id_vitima",
        y="natureza",
        orientation="h",
        title="Evolução dos Crimes por Tipo de Crime",
        labels={"natureza": "Tipo de Crime", "id_vitima": "Quantidade de Crimes"},
        color="id_vitima",
        #category_orders={"idade": ordem_idades}  # 👉 força a ordem
        #color_continuous_scale="Blues",  # escala de azul (mais escuro = maior)
        #text="natureza"  # mostra o total em cima das colunas
    )
    # Ajustes visuais
    #fig.update_traces(texttemplate="%{text}", textposition="outside")
    fig_tipo_crime.update_layout(
        xaxis_title="Tipo de Crime",
        yaxis_title="Quantidade de Crimes",
        showlegend=False,
        plot_bgcolor="black",             # fundo da área do gráfico
        paper_bgcolor="black",            # fundo externo
        font=dict(color="white"),         # texto branco
        title=dict(x=0.5, font=dict(color="white")),
        # Ajuste dos eixos para remover linhas de grade
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
        #coloraxis_showscale=False
    )
    st.plotly_chart(fig_tipo_crime, use_container_width=True)


# Fechar conexão com o banco de dados
# con.close()





