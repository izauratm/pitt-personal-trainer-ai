import json
import pandas as pd
import requests
import streamlit as st

# ============ CONFIGURAÇÃO DA PÁGINA ============
st.set_page_config(
    page_title="Pitt - Personal Trainer Virtual",
    page_icon="🏋️",
    layout="wide"
)

OLLAMA_URL = "http://localhost:11434/api/chat"
MODELO = "llama3.2"

# ============ CARREGAR DADOS ============
perfil = json.load(open('./data/perfil_aluno.json'))
treinos = pd.read_csv('./data/historico_treinos.csv')
avaliacoes = pd.read_csv('./data/historico_avaliacoes.csv')
exercicios = json.load(open('./data/exercicios_disponiveis.json'))

# ============ CÁLCULOS MATEMÁTICOS PRECISOS (PYTHON) ============
total_treinos_realizados = len(treinos)
treinos['volume_total'] = treinos['series'] * treinos['repeticoes'] * treinos['carga_kg']
carga_total_geral = treinos['volume_total'].sum()

volume_por_grupo = (
    treinos.groupby('grupo_muscular')['volume_total']
    .sum()
    .to_dict()
)

# ============ MONTAGEM DO CONTEXTO ============
contexto = f"""
ALUNO: {perfil['nome']}, {perfil['idade']} anos, {perfil['altura_m']}m, {perfil['peso_atual_kg']}kg
OBJETIVO: {perfil['objetivo_principal']} | META DE PESO: {perfil['meta_peso_kg']}kg
NÍVEL: {perfil['nivel_experiencia']} | RESTRIÇÕES MÉDICAS: {', '.join(perfil['restricoes_medicas'])}

RESUMO DE TREINOS CALCULADO (USE ESTES VALORES EXATOS PARA QUALQUER ANÁLISE):
- Total de Sessões de Treino Registradas: {total_treinos_realizados}
- Carga Total Movimentada (Volume Acumulado): {carga_total_geral:,.2f} kg

VOLUME DE CARGA POR GRUPO MUSCULAR (EM KG):
{json.dumps(volume_por_grupo, indent=2, ensure_ascii=False)}

HISTÓRICO RECENTE DE EXERCÍCIOS:
{treinos.drop(columns=['volume_total']).to_string(index=False)}

AVALIAÇÕES E FEEDBACKS ANTERIORES:
{avaliacoes.to_string(index=False)}

EXERCÍCIOS DISPONÍVEIS NA BIBLIOTECA:
{json.dumps(exercicios, indent=2, ensure_ascii=False)}
"""

# ============ SYSTEM PROMPT ============
SYSTEM_PROMPT = f"""Você é o Pitt, um personal trainer motivador, focado em segurança, técnica correta e ciência do esporte.

OBJETIVO:
Ajudar o aluno a entender sua evolução física, sugerir progressões de treino inteligentes com base nos dados e manter a motivação.

CONTEXTO DO ALUNO:
{contexto}

DIRETRIZES DE COMPORTAMENTO:
- **Tratamento:** Fale SEMPRE diretamente com o usuário na segunda pessoa do singular usando o primeiro nome dele. 
NUNCA use o plural ("vocês") ou a terceira pessoa.
- **Segurança:** NUNCA prescreva treinos ou cargas extremas que desrespeitem as restrições médicas do aluno (ex: cuidado com o joelho). 
Se não souber algo sobre a execução, oriente buscar um profissional presencial.
- **Escopo restrito:** Responda apenas sobre saúde, bem-estar, sono, treinos, nutrição ou educação física. Se o usuário perguntar sobre outros temas (filme, finanças, tempo, etc.), 
recuse educadamente e redirecione o papo para os treinos.
- **Precisão de dados:** Utilize sempre os dados consolidados do contexto do aluno (Volume, Cargas, Grupos Musculares e Perfil). 
Nunca invente números ou calcule de cabeça.
- **Rigor científico:** Seja cientificamente correto na nutrição (ex: cite creatina, proteína, nitrato) e evite termos inventados ou traduções literais estranhas 
(use "personal trainer" ou "treinador").
- **Tom e Estilo:** Seja sempre encorajador, empático, profissional natural, conversacional e objetivo. Responda diretamente ao que foi perguntado antes de sugerir novos tópicos. 
Evite respostas longas ou robóticas, com no máximo 2 paragrafos, explicando como se fosse para um amigo.
 """

# ============ BARRA LATERAL (SIDEBAR) ============
with st.sidebar:
    st.title("👤 Painel do Aluno")
    st.write(f"**Nome:** {perfil['nome']}")
    st.write(f"**Idade:** {perfil['idade']} anos")
    st.write(f"**Altura:** {perfil['altura_m']} m")
    st.markdown("---")
    
    st.subheader("📊 Métricas Atuais")
    st.metric("Peso Atual", f"{perfil['peso_atual_kg']} kg", f"Meta: {perfil['meta_peso_kg']} kg")
    st.metric("Treinos Registrados", f"{total_treinos_realizados} sessões")
    st.metric("Carga Acumulada", f"{carga_total_geral:,.0f} kg")
    
    st.markdown("---")
    st.write(f"**Objetivo:** {perfil['objetivo_principal']}")
    
    # Botão opcional para limpar o histórico do chat
    if st.button("🗑️ Limpar Conversa"):
        st.session_state.messages = []
        st.rerun()

# ============ INTERFACE PRINCIPAL (CHAT) ============
st.title("🏋️ Sou Pitt, seu Personal Trainer Virtual!")
st.markdown("Converse com o Pitt sobre seus treinos e tire suas dúvidas!")

# Inicializa o histórico de mensagens no estado da sessão
if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibe as mensagens anteriores na tela
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Captura nova entrada do usuário
if pergunta := st.chat_input("Pergunte sobre seus treinos, cargas ou evolução..."):
    st.session_state.messages.append({"role": "user", "content": pergunta})
    with st.chat_message("user"):
        st.markdown(pergunta)

    # Prepara mensagens para enviar ao Ollama
    mensagens_para_ia = [{"role": "system", "content": SYSTEM_PROMPT}]
    for m in st.session_state.messages:
        mensagens_para_ia.append({"role": m["role"], "content": m["content"]})

    with st.spinner("Analisando seu treino..."):
        try:
            r = requests.post(
                OLLAMA_URL,
                json={
                    "model": MODELO,
                    "messages": mensagens_para_ia,
                    "stream": False
                }
            )
            resposta = r.json()["message"]["content"]
        except Exception as e:
            resposta = f"Desculpe, ocorreu um erro ao conectar com o Ollama: {e}"

    st.session_state.messages.append({"role": "assistant", "content": resposta})
    with st.chat_message("assistant"):
        st.markdown(resposta)

# rodar com : streamlit run .\src\app.py        