import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

# Configuração da página do Streamlit
st.set_page_config(page_title="Análise de Acidentes de Trânsito", layout="wide")

# 1. TÍTULO E INTRODUÇÃO [cite: 102, 103]
st.title("📊 Análise de Acidentes de Trânsito no Brasil (2015-2024)") [cite: 11]
st.markdown("""
Esta aplicação analítica visa investigar a evolução temporal, os fatores de risco e as regiões mais críticas 
de acidentes rodoviários em território nacional[cite: 13].
""")

# Carga dos dados com cache para otimização
@st.cache_data
def carregar_dados():
    df = pd.read_csv("dados/simulacao_acidentes_transito_brasil.csv")
    df['data'] = pd.to_datetime(df['data'])
    return df

df = carregar_dados()

# 2. BARRA LATERAL - FILTROS OBRIGATÓRIOS [cite: 76, 105]
st.sidebar.header("Filtros de Pesquisa")

anos_disponiveis = sorted(df['ano'].unique())
ano_selecionado = st.sidebar.multiselect("Selecione o(s) Ano(s)", anos_disponiveis, default=anos_disponiveis) [cite: 78]

regioes_disponiveis = sorted(df['regiao'].unique())
regiao_selecionada = st.sidebar.multiselect("Selecione a Região", regioes_disponiveis, default=regioes_disponiveis) [cite: 80]

estados_filtrados = sorted(df[df['regiao'].isin(regiao_selecionada)]['uf'].unique()) if regiao_selecionada else sorted(df['uf'].unique())
estado_selecionado = st.sidebar.multiselect("Selecione o Estado (UF)", estados_filtrados, default=estados_filtrados) [cite: 81]

tipos_disponiveis = sorted(df['tipo_acidente'].unique())
tipo_selecionado = st.sidebar.multiselect("Tipo de Acidente", tipos_disponiveis, default=tipos_disponiveis) [cite: 82]

gravidade_disponivel = sorted(df['nivel_gravidade'].unique())
gravidade_selecionada = st.sidebar.multiselect("Nível de Gravidade", gravidade_disponivel, default=gravidade_disponivel) [cite: 84]

# Filtragem dinâmica do DataFrame principal
df_filtrado = df[
    (df['ano'].isin(ano_selecionado)) &
    (df['regiao'].isin(regiao_selecionada)) &
    (df['uf'].isin(estado_selecionado)) &
    (df['tipo_acidente'].isin(tipo_selecionado)) &
    (df['nivel_gravidade'].isin(gravidade_selecionada))
]

# 3. CARD DE INDICADORES (KPIs OBRIGATÓRIOS) [cite: 53, 60, 104]
st.header("📌 Indicadores Chave (KPIs)") [cite: 53, 60]
kpi1, kpi2, kpi3 = st.columns(3)

with kpi1:
    st.metric("Total de Acidentes", f"{df_filtrado['acidentes'].sum():,}") [cite: 62]
with kpi2:
    st.metric("Total de Feridos", f"{df_filtrado['feridos'].sum():,}") [cite: 62]
with kpi3:
    st.metric("Total de Óbitos", f"{df_filtrado['obitos'].sum():,}") [cite: 62]

kpi4, kpi5, kpi6 = st.columns(3)
with kpi4:
    estado_critico = df_filtrado.groupby('uf')['acidentes'].sum().idxmax() if not df_filtrado.empty else "N/A"
    st.metric("Estado Mais Crítico", estado_critico) [cite: 62]
with kpi5:
    periodo_perigoso = df_filtrado.groupby('periodo_dia')['acidentes'].sum().idxmax() if not df_filtrado.empty else "N/A"
    st.metric("Período Mais Perigoso", periodo_perigoso) [cite: 62]
with kpi6:
    tipo_frequente = df_filtrado.groupby('tipo_acidente')['acidentes'].sum().idxmax() if not df_filtrado.empty else "N/A"
    st.metric("Tipo de Acidente Comum", tipo_frequente) [cite: 62]

st.markdown("---")

# 4. GRÁFICOS E VISUALIZAÇÕES OBRIGATÓRIAS [cite: 73, 106]
st.header("📈 Gráficos Analíticos")

col_esq, col_dir = st.columns(2)

with col_esq:
    # Linha Temporal [cite: 75]
    st.subheader("Evolução Temporal dos Acidentes") [cite: 65, 75]
    df_temporal = df_filtrado.groupby('ano')['acidentes'].sum().reset_index()
    fig_linha = px.line(df_temporal, x='ano', y='acidentes', markers=True, title="Acidentes por Ano")
    st.plotly_chart(fig_linha, use_container_width=True)

    # Barras por Tipo de Acidente [cite: 75]
    st.subheader("Frequência por Tipo de Acidente") [cite: 57, 75]
    df_tipo = df_filtrado.groupby('tipo_acidente')['acidentes'].sum().reset_index().sort_values(by='acidentes', ascending=True)
    fig_tipo = px.bar(df_tipo, x='acidentes', y='tipo_acidente', orientation='h', title="Acidentes por Tipo")
    st.plotly_chart(fig_tipo, use_container_width=True)

with col_dir:
    # Barras por Estado [cite: 75]
    st.subheader("Comparação por Estado (UF)") [cite: 56, 66, 75]
    df_uf = df_filtrado.groupby('uf')['acidentes'].sum().reset_index().sort_values(by='acidentes', ascending=False)
    fig_uf = px.bar(df_uf, x='uf', y='acidentes', title="Acidentes por Unidade da Federação")
    st.plotly_chart(fig_uf, use_container_width=True)

    # Gráfico de Pizza por Clima [cite: 75]
    st.subheader("Distribuição por Condição Climática") [cite: 70, 75]
    df_clima = df_filtrado.groupby('condicao_climatica')['acidentes'].sum().reset_index()
    fig_pizza = px.pie(df_clima, values='acidentes', names='condicao_climatica', title="Impacto do Clima")
    st.plotly_chart(fig_pizza, use_container_width=True)

# Heatmap por Período/Horário (Utilizando Seaborn/Matplotlib incorporado) [cite: 75]
st.subheader("🔍 Densidade de Acidentes por Período do Dia") [cite: 69, 75]
if not df_filtrado.empty:
    pivot_table = df_filtrado.pivot_table(index='periodo_dia', columns='regiao', values='acidentes', aggfunc='sum', fill_value=0)
    fig_heat, ax = plt.subplots(figsize=(10, 4))
    sns.heatmap(pivot_table, annot=True, fmt="d", cmap="YlOrRd", ax=ax)
    st.pyplot(fig_heat)

# Tabela Dinâmica Detalhada [cite: 75]
st.subheader("📋 Tabela Dinâmica e Exploração de Dados") [cite: 75]
st.dataframe(df_filtrado[['ano', 'regiao', 'uf', 'municipio', 'tipo_acidente', 'acidentes', 'feridos', 'obitos']], use_container_width=True)

st.markdown("---")

# 5. INTERPRETAÇÃO E CONCLUSÃO EXECUTIVA [cite: 58, 59, 107, 108]
st.header("📝 Conclusão Executiva e Análise Estratégica") [cite: 59, 108]
st.markdown("""
A partir do painel analítico estruturado, observam-se padrões consistentes sobre os fatores de risco rodoviários[cite: 132, 133]. 
O mapeamento das regiões e estados mais críticos viabiliza a alocação preditiva de recursos de salvamento e fiscalização ostensiva pelas autoridades competentes[cite: 5, 6, 134].
Recomenda-se a intensificação de campanhas preventivas nos períodos identificados como de maior severidade e frequência histórica[cite: 7, 8, 133].
""")