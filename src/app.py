import json
import pandas as pd
import requests
import streamlit as st

# ============ CONFIGURAÇÃO DA PÁGINA ============
st.set_page_config(
    page_title="Pitt - Personal Trainer Virtual",
    page_icon="🏋️",
    layout="wide",
)

OLLAMA_URL = "http://localhost:11434/api/chat"
MODELO = "llama3.2"

TEMAS_PERMITIDOS = (
    "saúde, bem-estar, sono, recuperação física, treinos, exercícios, "
    "cargas, evolução física, nutrição esportiva e educação física aplicada ao treino do aluno"
)


# ============ FUNÇÕES AUXILIARES ============
def extrair_primeiro_nome(nome_completo: str) -> str:
    partes = (nome_completo or "").strip().split()
    return partes[0] if partes else "aluno"


def formatar_restricoes(valor_restricoes) -> str:
    if isinstance(valor_restricoes, list):
        itens = [str(item).strip() for item in valor_restricoes if str(item).strip()]
        return ", ".join(itens) if itens else "Nenhuma"
    if isinstance(valor_restricoes, str) and valor_restricoes.strip():
        return valor_restricoes.strip()
    return "Nenhuma"


def mensagem_esta_no_escopo(pergunta: str) -> tuple[bool, str]:
    """Classifica se a pergunta atual pertence ao escopo permitido do Pitt."""
    prompt_guardrail = f"""
Você é um classificador rigoroso de escopo para um assistente de Personal Trainer.
Responda APENAS com uma única palavra: SIM ou NAO.

Responda "SIM" apenas se o assunto principal da PERGUNTA ATUAL for:
- {TEMAS_PERMITIDOS}

Responda "NAO" para qualquer outro assunto, incluindo:
- TCC, provas, lição de casa, redação, trabalhos acadêmicos ou estudos gerais (mesmo que o tema seja saúde ou educação física)
- Finanças, investimentos, CDI, rendimentos, produtos financeiros, planos de saúde, preços
- Filmes, séries, música, jogos, clima, previsão do tempo, política, programação ou dúvidas gerais

Exemplos:
Pergunta: "Como evoluir meu treino de pernas sem forçar meu joelho?" -> SIM
Pergunta: "Quanta proteína e creatina devo usar para ganhar massa?" -> SIM
Pergunta: "Estou dormindo pouco e meu rendimento no treino caiu." -> SIM
Pergunta: "Pode me ajudar com meu TCC sobre hipertrofia?" -> NAO
Pergunta: "Como está a previsão do tempo hoje?" -> NAO
Pergunta: "Quais são os rendimentos do produto XYZ ou do CDI?" -> NAO
Pergunta: "Que música ajuda a animar o treino?" -> NAO

PERGUNTA ATUAL:
"{pergunta}"

Resposta (apenas SIM ou NAO):
""".strip()

    try:
        r = requests.post(
            OLLAMA_URL,
            json={
                "model": MODELO,
                "messages": [{"role": "user", "content": prompt_guardrail}],
                "stream": False,
                "options": {"temperature": 0},
            },
        )
        r.raise_for_status()
        decisao = r.json().get("message", {}).get("content", "").strip().upper()

        if decisao.startswith("SIM"):
            return True, f"SIM ({decisao})"
        if decisao.startswith("NAO"):
            return False, f"NAO ({decisao})"

        return False, f"BLOQUEADO_AMBIGUO ({decisao})"
    except Exception as e:
        return False, f"BLOQUEADO_ERRO ({e})"


def gerar_recusa_escopo(primeiro_nome: str) -> str:
    return (
        f"E aí, {primeiro_nome}! Eu só consigo te ajudar com assuntos ligados a "
        f"treinos, nutrição, sono, bem-estar e sua evolução física — então não "
        f"consigo ajudar com outros temas por aqui.\n\n"
        f"Vamos focar nos seus treinos: quer revisar suas cargas recentes, tirar "
        f"dúvidas sobre algum exercício ou planejar sua próxima sessão?"
    )


# ============ CARREGAR DADOS ============
with open("./data/perfil_aluno.json", encoding="utf-8") as f:
    perfil = json.load(f)

treinos = pd.read_csv("./data/historico_treinos.csv")
avaliacoes = pd.read_csv("./data/historico_avaliacoes.csv")

with open("./data/exercicios_disponiveis.json", encoding="utf-8") as f:
    exercicios = json.load(f)

primeiro_nome = extrair_primeiro_nome(perfil.get("nome", ""))
restricoes = formatar_restricoes(perfil.get("restricoes_medicas"))

# ============ CÁLCULOS MATEMÁTICOS PRECISOS (PYTHON) ============
total_treinos_realizados = len(treinos)

if not treinos.empty and {"series", "repeticoes", "carga_kg"}.issubset(treinos.columns):
    treinos_calc = treinos.copy()
    for col in ["series", "repeticoes", "carga_kg"]:
        treinos_calc[col] = pd.to_numeric(treinos_calc[col], errors="coerce").fillna(0)
    treinos_calc["volume_total"] = (
        treinos_calc["series"] * treinos_calc["repeticoes"] * treinos_calc["carga_kg"]
    )
    carga_total_geral = float(treinos_calc["volume_total"].sum())
    if "grupo_muscular" in treinos_calc.columns:
        volume_por_grupo = (
            treinos_calc.groupby("grupo_muscular")["volume_total"].sum().to_dict()
        )
    else:
        volume_por_grupo = {}
    historico_str = treinos_calc.drop(columns=["volume_total"]).to_string(index=False)
else:
    carga_total_geral = 0.0
    volume_por_grupo = {}
    historico_str = treinos.to_string(index=False) if not treinos.empty else "Sem treinos registrados."

avaliacoes_str = (
    avaliacoes.to_string(index=False)
    if not avaliacoes.empty
    else "Sem avaliações registradas."
)

# ============ MONTAGEM DO CONTEXTO ============
contexto = f"""
ALUNO: {perfil.get('nome', primeiro_nome)} (chame sempre de {primeiro_nome}), {perfil.get('idade', '-')} anos, {perfil.get('altura_m', '-')}m, {perfil.get('peso_atual_kg', '-')}kg
OBJETIVO: {perfil.get('objetivo_principal', '-')} | META DE PESO: {perfil.get('meta_peso_kg', '-')}kg
NÍVEL: {perfil.get('nivel_experiencia', '-')} | RESTRIÇÕES MÉDICAS: {restricoes}

RESUMO DE TREINOS CALCULADO (USE ESTES VALORES EXATOS PARA QUALQUER ANÁLISE):
- Total de Sessões de Treino Registradas: {total_treinos_realizados}
- Carga Total Movimentada (Volume Acumulado): {carga_total_geral:,.2f} kg

VOLUME DE CARGA POR GRUPO MUSCULAR (EM KG):
{json.dumps(volume_por_grupo, indent=2, ensure_ascii=False)}

HISTÓRICO RECENTE DE EXERCÍCIOS:
{historico_str}

AVALIAÇÕES E FEEDBACKS ANTERIORES:
{avaliacoes_str}

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
- **Tratamento:** Fale SEMPRE diretamente com o usuário na segunda pessoa do singular ("você", "seu", "te") usando SEMPRE o primeiro nome dele: "{primeiro_nome}".
NUNCA use o plural ("vocês") ou a terceira pessoa ("o aluno", "ele").
- **Segurança:** NUNCA prescreva treinos ou cargas extremas que desrespeitem as restrições médicas do aluno ({restricoes}).
Se não souber algo sobre a execução, oriente buscar um profissional presencial.
- **Escopo estrito:** Responda APENAS sobre saúde, bem-estar, sono, treinos, nutrição ou educação física aplicada ao treino do aluno.
NUNCA ajude com TCC, trabalhos de faculdade, estudos, finanças, filmes, tecnologia ou qualquer outro tema fora do escopo — mesmo que o assunto tenha relação com educação física ou saúde.
Se o usuário perguntar algo fora do escopo, recuse de forma educada e direta, sem dar sugestões ou respostas sobre o tema proibido, e convide {primeiro_nome} a falar sobre seus treinos.
- **Precisão de dados:** Utilize sempre os dados consolidados do contexto do aluno (Volume, Cargas, Grupos Musculares e Perfil).
Nunca invente números ou calcule de cabeça.
- **Rigor científico:** Seja cientificamente correto na nutrição (ex: cite creatina, proteína, nitrato) e evite termos inventados ou traduções literais estranhas
(use "personal trainer" ou "treinador").
- **Tom e Estilo:** Seja sempre encorajador, empático, profissional natural, conversacional e objetivo. Responda diretamente ao que foi perguntado antes de sugerir novos tópicos.
Escreva no máximo 2 parágrafos curtos, sem listas longas de perguntas e encerrando com NO MÁXIMO 1 pergunta direta. Não use listas com marcadores ou números.
""".strip()

# ============ BARRA LATERAL (SIDEBAR) ============
with st.sidebar:
    st.title("👤 Painel do Aluno")
    st.write(f"**Nome:** {perfil.get('nome', primeiro_nome)}")
    st.write(f"**Idade:** {perfil.get('idade', '-')} anos")
    st.write(f"**Altura:** {perfil.get('altura_m', '-')} m")
    st.markdown("---")

    st.subheader("📊 Métricas Atuais")
    st.metric(
        "Peso Atual",
        f"{perfil.get('peso_atual_kg', '-')} kg",
        f"Meta: {perfil.get('meta_peso_kg', '-')} kg",
    )
    st.metric("Treinos Registrados", f"{total_treinos_realizados} sessões")
    st.metric("Carga Acumulada", f"{carga_total_geral:,.0f} kg")

    st.markdown("---")
    st.write(f"**Objetivo:** {perfil.get('objetivo_principal', '-')}")

   

    if st.button("🗑️ Limpar Conversa"):
        st.session_state.messages = []
        #st.session_state.pop("ultimo_filtro", None)
        st.rerun()

# ============ INTERFACE PRINCIPAL (CHAT) ============
st.title("🏋️ Sou Pitt, seu Personal Trainer Virtual!")
st.markdown(f"Fala, {primeiro_nome}! Converse comigo sobre seus treinos, cargas e dúvidas!")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if pergunta := st.chat_input("Pergunte sobre seus treinos, cargas ou evolução..."):
    st.session_state.messages.append({"role": "user", "content": pergunta})
    with st.chat_message("user"):
        st.markdown(pergunta)

    with st.spinner("Analisando seu treino..."):
        no_escopo, diagnostico = mensagem_esta_no_escopo(pergunta)
        st.session_state.ultimo_filtro = diagnostico

        if not no_escopo:
            resposta = gerar_recusa_escopo(primeiro_nome)
        else:
            historico_recente = st.session_state.messages[-6:]
            mensagens_para_ia = [{"role": "system", "content": SYSTEM_PROMPT}]
            for m in historico_recente:
                mensagens_para_ia.append({"role": m["role"], "content": m["content"]})

            try:
                r = requests.post(
                    OLLAMA_URL,
                    json={
                        "model": MODELO,
                        "messages": mensagens_para_ia,
                        "stream": False,
                        "options": {
                            "temperature": 0.35,
                            "repeat_penalty": 1.2,
                            "num_predict": 260,
                        },
                    },
                )
                r.raise_for_status()
                resposta = r.json()["message"]["content"].strip()
            except Exception as e:
                resposta = (
                    f"Desculpe, {primeiro_nome}, ocorreu um erro ao conectar "
                    f"com o Ollama: {e}"
                )

    st.session_state.messages.append({"role": "assistant", "content": resposta})
    with st.chat_message("assistant"):
        st.markdown(resposta)