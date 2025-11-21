import streamlit as st
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

# =============================
# CONFIGURAÇÃO DO GROQ
# =============================

# Carrega .env local (se existir)
load_dotenv()

# 1. Tenta pegar do Streamlit Cloud (st.secrets)
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]

# 2. Se não achar, tenta pegar local via variável de ambiente
elif os.getenv("GROQ_API_KEY"):
    api_key = os.getenv("GROQ_API_KEY")

# 3. Se ainda não encontrou → erro amigável
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
# PROMPT SYSTEM (mantido igual ao seu)
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


# =============================
# FUNÇÃO DO CHAT
# =============================
def resposta_bot(mensagens, documento=""):
    mensagens_modelo = [('system', prompt_system(documento))]
    mensagens_modelo += mensagens

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

st.title("✝️ Catequista Virtual – Catequese de Adultos")
st.write("Escolha o modo abaixo:")

modo = st.radio("Selecione o modo:", ["Conversa com a Catequista", "Estudo Catequético"])

# ------------------  MODO CONVERSA ------------------
if modo == "Conversa com a Catequista":
    st.subheader("💬 Conversa com a Catequista")

    if "mensagens" not in st.session_state:
        st.session_state.mensagens = []

    pergunta = st.text_input("Digite sua pergunta:")

    if st.button("Enviar"):
        if pergunta.strip():
            st.session_state.mensagens.append(("user", pergunta))
            resposta = resposta_bot(st.session_state.mensagens)
            st.session_state.mensagens.append(("assistant", resposta))

    # Mostrar histórico
    for remetente, texto in st.session_state.mensagens:
        if remetente == "user":
            st.markdown(f"**Você:** {texto}")
        else:
            st.markdown(f"**Catequista:** {texto}")


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

    resposta = st.radio(
        "Escolha a resposta:",
        list(teste["alternativas"].keys())
    )

    if st.button("Verificar resposta"):
        if resposta == teste["correta"]:
            st.success("Resposta correta! Muito bem!")
        else:
            st.error(f"Resposta incorreta. A alternativa correta é: {teste['correta']}")

    if st.button("Próxima aula"):
        st.session_state.aula += 1
        if st.session_state.aula > len(modulo["aulas"]):
            st.success("🎉 Você concluiu o módulo 1!")
            st.session_state.aula = len(modulo["aulas"])

