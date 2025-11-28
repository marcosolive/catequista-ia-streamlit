import streamlit as st
import os
import requests

# =============================
# IMPORT OPCIONAL DO DOTENV
# =============================
try:
    from dotenv import load_dotenv
    load_dotenv()
except ModuleNotFoundError:
    pass  # Em produção/Cloud, dotenv não é necessário

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

# =============================
# CONFIGURAÇÃO DO GROQ
# =============================
# 1. Tenta pegar do Streamlit Cloud
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
# 2. Tenta pegar do ambiente local
elif os.getenv("GROQ_API_KEY"):
    api_key = os.getenv("GROQ_API_KEY")
# 3. Nenhuma chave encontrada → erro amigável
else:
    st.error(
        "❌ ERRO: A chave GROQ_API_KEY não foi encontrada.\n"
        "→ No Streamlit Cloud: coloque sua chave em 'Secrets'.\n"
        "→ Localmente: defina uma variável de ambiente ou um arquivo .env.\n"
    )
    st.stop()

os.environ["GROQ_API_KEY"] = api_key
chat = ChatGroq(model='llama-3.3-70b-versatile')

# =============================
# PROMPT SYSTEM
# =============================
def prompt_system(documento=""):
    return f"""
Você é uma Catequista Virtual Católico-Romana, especializada em catequese de adultos.
Sua missão é ensinar a doutrina com clareza, fidelidade e caridade, sempre de forma
profunda, objetiva, pastoral e fiel ao Magistério da Igreja.

⚜️ DIRETRIZES PRINCIPAIS
1. Ensine sempre conforme o Catecismo da Igreja Católica (CIC), seu Compêndio,
a Sagrada Escritura, a Tradição e o Magistério autêntico.
2. Quando possível, cite trechos do Catecismo ou referências bíblicas.
3. Evite opiniões pessoais ou interpretações privadas que não estejam em harmonia
com a doutrina católica.
4. Explique de forma clara e catequética, adequada a adultos que buscam formação sólida.
5. Seja serena, paciente, acolhedora, sem moralismo, mantendo rigor doutrinal.
6. Em temas sensíveis (moral, sacramentos, liturgia), responda com precisão e prudência,
sempre conforme a Igreja ensina.

⚜️ ESTILO DE RESPOSTA
• Claro, direto, sem rodeios desnecessários.
• Profundo, mas compreensível.
• Estruturado: introdução, explicação e aplicação prática.
• Quando útil, formule exemplos concretos.
• Se houver dúvidas comuns relacionadas ao tema, antecipe-as e responda.

⚜️ ESCOPO DE ATUAÇÃO
Você responde sobre:
– Mandamentos
– Virtudes e vícios
– Pecado e graça
– Sacramentos
– Liturgia
– Doutrina moral
– Doutrina sobre Cristo, Igreja, Espírito Santo
– Leitura bíblica
– Tradição e Patrística
– Vida espiritual

Quando algo estiver fora da doutrina católica ou for contrário à fé, você responde com fidelidade,
explicando gentilmente o motivo e oferecendo a visão correta da Igreja.

=== Conteúdo enviado pelo usuário ===
{documento}

Use esse conteúdo para responder quando relevante.
Caso o documento não tenha relação com a pergunta, responda normalmente como catequista.
"""

def prompt_meditacoes_sao_josemaria(documento=""):
    return f"""
Você é um diretor espiritual inspirado nos ensinamentos de São Josemaria Escrivá,
fundador do Opus Dei, e escreve **meditações diárias profundas, práticas e calorosas**,
voltadas para pessoas comuns que desejam santificar a vida diária.

⚜️ ESTILO E INTENÇÃO
• Tom espiritual afetuoso, motivador e exigente, como em “Caminho”, “Forja” e “Sulco”.
• Ênfase na santificação do trabalho e da vida ordinária.
• Linguagem direta, curta, concreta e ardente.
• Evite abstrações longas: fale ao coração e à vontade.
• Use frases curtas e fortes, às vezes aforísticas.
• Inclua conselhos práticos para viver a união com Deus “no meio do mundo”.

⚜️ CONTEÚDO DA MEDITAÇÃO
1. Luz inicial do Evangelho do dia (ou do texto enviado).
2. Aplicação prática à vida ordinária.
3. Propósito concreto e possível.
4. Palavras breves de ânimo e correção fraterna.
5. Se adequado, referências a São Josemaria (Caminho, Sulco, Forja), sem citações longas.

⚜️ TONALIDADE
• Firme, mas carinhosa.
• Otimista.
• Cristo no centro.
• Vida interior + trabalho + serviço.

=== Texto base fornecido ===
{documento}

Escreva uma meditação completa com base nisso.
"""

def prompt_homilias_bento_xvi(documento=""):
    return f"""
Você é um teólogo-pregador com o estilo e a espiritualidade de Bento XVI:
profundo, cristalino, centrado em Cristo, teologicamente preciso e liturgicamente sensível.

⚜️ ESTILO E REFERÊNCIA
• Clareza intelectual + profundidade espiritual.
• Linguagem elegante, simples, mas elevada.
• Cristologia no centro: Cristo como chave da interpretação.
• Hermenêutica da continuidade — fidelidade ao Magistério.
• Unidade entre razão e fé.
• Recorrência a temas típicos de Bento XVI:
  – Verdade
  – Beleza litúrgica
  – Amizade com Cristo
  – A fé como encontro pessoal
  – Conversão do coração
  – Sentido teológico da liturgia

⚜️ ESTRUTURA DA HOMILIA
1. Introdução iluminando o Evangelho do dia.
2. Explicação teológica clara e profunda.
3. Aplicação espiritual e existencial.
4. Chamado à conversão e à esperança.
5. Conclusão com olhar mariano.

⚜️ TOM
• Contemplativo.
• Cristocêntrico.
• Esperançoso.
• Sólido na doutrina.

=== Evangelho do dia ou texto base ===
{documento}

Escreva uma homilia completa nesse estilo.
"""


# =============================
# FUNÇÃO DO CHAT
# =============================
def obter_evangelho_do_dia():
    try:
        url = "https://liturgia.up.railway.app/evangelho"
        r = requests.get(url, timeout=10)
        data = r.json()

        evangelho = f"{data['referencia']}\n\n{data['texto']}"
        return evangelho

    except Exception as e:
        return f"Não foi possível obter o Evangelho automaticamente. Erro: {e}"

def resposta_bot(mensagens, documento=""):

    # Escolher o prompt conforme o agente selecionado
    agente = st.session_state.agente

    if agente == "Catequista":
        system_prompt = prompt_system(documento)

    elif agente == "Homilias – Bento XVI":
        system_prompt = prompt_homilias_bento_xvi(documento)

    elif agente == "Meditações – São Josemaria":
        system_prompt = prompt_meditacoes_sao_josemaria(documento)

    # Montar mensagens para o modelo
    mensagens_modelo = [('system', system_prompt)]
    mensagens_modelo += mensagens

    # Gerar resposta
    template = ChatPromptTemplate.from_messages(mensagens_modelo)
    chain = template | chat
    return chain.invoke({}).content


# ======================================================================
# CONTEÚDO DO CURSO COM TESTES
# ======================================================================
modulos = {
    1: {
        "titulo": "O Dom da Fé",
        "aulas": [
            {
                "titulo": "O que é a fé?",
                "conteudo": """
A fé é, segundo o Catecismo (CIC 142–150), a resposta do ser humano ao Deus que se revela.
Ela é:
• Um dom gratuito de Deus;
• A adesão pessoal ao Deus verdadeiro;
• A aceitação da verdade revelada por Ele.

A fé é o início da vida eterna.
                """,
                "teste": {
                    "pergunta": "Qual definição expressa melhor o que é a fé?",
                    "alternativas": {
                        "A": "Apenas um sentimento religioso.",
                        "B": "Um dom de Deus e adesão à Sua verdade.",
                        "C": "Uma tradição cultural."
                    },
                    "correta": "B"
                }
            },
            {
                "titulo": "Como a fé cresce?",
                "conteudo": """
A fé cresce pela:
• oração constante (CIC 162),
• vida sacramental,
• meditação da Palavra de Deus,
• caridade vivida no cotidiano.

A fé é como uma chama: precisa ser alimentada.
                """,
                "teste": {
                    "pergunta": "Como a fé cresce principalmente?",
                    "alternativas": {
                        "A": "Vendo milagres.",
                        "B": "Com oração, sacramentos e caridade.",
                        "C": "Pelo esforço humano isolado."
                    },
                    "correta": "B"
                }
            }
        ]
    }
}

# ======================================================================
# INTERFACE STREAMLIT
# ======================================================================
st.set_page_config(page_title="Catequista Virtual", layout="centered")

# ===================== CSS =====================
st.markdown("""
<style>
/* ============================
   TEMA PADRÃO (LIGHT MODE)
   ============================ */
body {
    background-color: #f6f3ef !important;
    color: #2b2b2b !important;
}

.msg {
    padding: 10px 15px;
    margin: 8px 0;
    max-width: 85%;
    border-radius: 10px;
    font-size: 16px;
    line-height: 1.5;
}

/* Mensagem do usuário */
.msg.user {
    margin-left: auto;
    background-color: #d9e8ff !important;
    border: 1px solid #aac8ff !important;
    text-align: right;
    color: #000 !important;
}

/* Mensagem do bot */
.msg.bot {
    margin-right: auto;
    background-color: #fffaf2 !important;
    border: 1px solid #f0d9b5 !important;
    text-align: left;
    color: #000 !important;
}

/* Botões */
button[kind=secondary] {
    background-color: #4a7bd6 !important;
    color: white !important;
    border-radius: 6px !important;
}

/* Inputs (light) */
input[type=text],
textarea {
    border-radius: 6px !important;
    border: 1px solid #bbb !important;
    background-color: #ffffff !important;
    color: #000 !important;
}

/* =======================================
   DARK MODE — aplicado automaticamente
   ======================================= */
@media (prefers-color-scheme: dark) {
    body {
        background-color: #121212 !important;
        color: #e8e8e8 !important;
    }

    /* Mensagens */
    .msg.user {
        background-color: #1e3a5f !important;
        border: 1px solid #355983 !important;
        color: #e3eeff !important;
    }

    .msg.bot {
        background-color: #2a2420 !important;
        border: 1px solid #4f3e2d !important;
        color: #f2e6d8 !important;
    }

    /* Inputs */
    input[type=text],
    textarea {
        background-color: #1e1e1e !important;
        border: 1px solid #555 !important;
        color: #f0f0f0 !important;
    }

    /* Botões */
    button[kind=secondary] {
        background-color: #3f6ac9 !important;
        color: #fff !important;
        border-radius: 6px !important;
    }

    /* Radio buttons e textos gerais */
    .stRadio label {
        color: #e8e8e8 !important;
    }

    .stMarkdown,
    p, h1, h2, h3, h4, h5 {
        color: #e8e8e8 !important;
    }
}
</style>
""", unsafe_allow_html=True)

st.title("✝️ Catequista Virtual – Catequese de Adultos")
st.write("Escolha o modo abaixo:")

modo = st.radio("Selecione o modo:", ["Conversa com a Catequista", "Estudo Catequético"])
if "agente" not in st.session_state:
    st.session_state.agente = "Catequista"

st.subheader("Escolha o agente:")
agente = st.radio(
    "Selecione o perfil do agente:",
    [
        "Catequista",
        "Homilias – Bento XVI",
        "Meditações – São Josemaria"
    ]
)

st.session_state.agente = agente


# ------------------  MODO CONVERSA ------------------
if modo == "Conversa com a Catequista":
    st.subheader("💬 Conversa com a Catequista")
    if st.session_state.agente in ["Homilias – Bento XVI", "Meditações – São Josemaria"]:
        if st.button("📖 Usar Evangelho do Dia"):
            evangelho = obter_evangelho_do_dia()
            st.session_state.pergunta = evangelho


    if "mensagens" not in st.session_state:
        st.session_state.mensagens = []

    # Função enviar mensagem
    def enviar_msg():
        texto = st.session_state.pergunta.strip()
        if not texto:
            return
        st.session_state.mensagens.append(("user", texto))
        st.session_state.pergunta = ""
        with st.spinner("✍️ Formulando resposta..."):
            resposta = resposta_bot(st.session_state.mensagens)
        st.session_state.mensagens.append(("assistant", resposta))
        #st.rerun()

    # Histórico
    for sender, text in st.session_state.mensagens:
        if sender == "user":
            st.markdown(f"<div class='msg user'>{text}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='msg bot'>{text}</div>", unsafe_allow_html=True)

    st.markdown("---")

    # Caixa de texto + botão
    col1, col2 = st.columns([4, 1])
    with col1:
        #st.text_input("Digite sua pergunta:", key="pergunta")
        st.text_area("Digite sua pergunta:", key="pergunta", height=80)
    with col2:
        st.button("Enviar", on_click=enviar_msg)

# ------------------  MODO ESTUDO ------------------
if modo == "Estudo Catequético":
    st.subheader("📘 Curso Catequético – Módulo 1")

    if "modulo" not in st.session_state:
        st.session_state.modulo = 1
        st.session_state.aula = 1

    modulo = modulos[st.session_state.modulo]
    aula = modulo["aulas"][st.session_state.aula - 1]

    st.markdown(f"### Aula {st.session_state.aula}: {aula['titulo']}")
    st.markdown(aula["conteudo"])

    st.markdown("---")
    st.markdown("### 📝 Teste rápido")
    teste = aula["teste"]

    st.write(teste["pergunta"])

    opcoes_formatadas = [f"{letra}) {texto}" for letra, texto in teste["alternativas"].items()]
    resposta_usuario = st.radio("Escolha a resposta:", opcoes_formatadas)

    if st.button("Verificar resposta"):
        letra_escolhida = resposta_usuario[0]
        if letra_escolhida == teste["correta"]:
            st.success("Resposta correta! Muito bem!")
        else:
            st.error(f"Resposta incorreta. A alternativa correta é: {teste['correta']}")

    if st.button("Próxima aula"):
        st.session_state.aula += 1
        if st.session_state.aula > len(modulo["aulas"]):
            st.success("🎉 Você concluiu o módulo 1!")
            st.session_state.aula = len(modulo["aulas"])

