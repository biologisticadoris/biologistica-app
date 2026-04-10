import streamlit as st
from groq import Groq
from fpdf import FPDF

st.set_page_config(page_title="BioLogística Pro", page_icon="🥗", layout="wide")

API_KEY_MAESTRA = st.secrets["GROQ_API_KEY"] if "GROQ_API_KEY" in st.secrets else "TU_LLAVE_AQUI"

def generar_pdf(texto, nombre, proteina, p_ideal, imc, actividad, edad):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(15, 15, 15)
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(46, 125, 50)
    pdf.cell(0, 10, f"REPORTE BIOLOGISTICA: {nombre.upper()}", ln=True, align='C')
    pdf.ln(3)
    pdf.set_font("Arial", 'B', 10)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 7, f"Edad: {edad} anos | Peso ref: {p_ideal}kg | IMC: {imc} | Proteina: {proteina}g/dia", ln=True)
    pdf.ln(3)
    pdf.set_font("Arial", 'I', 8)
    pdf.set_text_color(150, 0, 0)
    pdf.multi_cell(0, 5, "AVISO: Guia logistica de alimentos. No es prescripcion medica.")
    pdf.ln(4)
    pdf.set_font("Arial", size=9)
    pdf.set_text_color(0, 0, 0)
    limpio = texto
    for c in ['🚀','🥗','✅','⚖️','📦','📊','**','###','##','#','|','-']:
        limpio = limpio.replace(c, '')
    limpio = limpio.encode('latin-1', 'ignore').decode('latin-1')
    for linea in limpio.split('\n'):
        linea = linea.strip()
        if linea:
            pdf.multi_cell(0, 6, txt=linea)
            pdf.ln(1)
    return pdf.output(dest='S').encode('latin-1')

st.markdown("<h1 style='text-align: center; color: #2E7D32;'>🥗 BIOLOGÍSTICA DE PRECISIÓN</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Gestión Inteligente de Inventario y Optimización de Alimentos</p>", unsafe_allow_html=True)

st.subheader("⚖️ Acuerdo de Uso y Privacidad")
with st.container(border=True):
    st.info("""
    **Al usar BioLogística, confirmas que comprendes:**
    1. Esta es una herramienta de **organización de inventario**.
    2. Los datos de peso/salud se usan para cálculos matemáticos y **no se almacenan**.
    3. No sustituye el diagnóstico de un médico. Consulta a un profesional antes de cambiar tu dieta.
    """)
    acepto = st.checkbox("He leído y acepto que esto es una guía logística y no una prescripción médica.")

with st.sidebar:
    st.markdown('<div style="font-size: 80px; text-align: center;">🥗</div>', unsafe_allow_html=True)
    st.header("👤 Datos del Cliente")
    nombre = st.text_input("Nombre:")
    col_a, col_b = st.columns(2)
    with col_a:
        edad = st.number_input("Edad:", 1, 120, 40)
        peso = st.number_input("Peso (kg):", 30.0, 200.0, 65.0)
    with col_b:
        talla_cm = st.number_input("Altura (cm):", 100.0, 250.0, 160.0)
        genero = st.radio("Género:", ["Femenino", "Masculino"])
    actividad = st.select_slider("Ritmo de vida:", options=["Sedentario", "Ligero", "Moderado", "Intenso", "Atleta"], value="Moderado")
    meta = st.radio("Objetivo:", ["Mantener", "Ganar Músculo", "Perder Grasa"])
    salud = st.multiselect("Cuidado especial en:", ["Diabetes", "Colesterol", "Hígado Graso", "Presión Alta"], default=["Hígado Graso"])

talla_m = talla_cm / 100
imc = round(peso / (talla_m**2), 1)
peso_ideal = round((talla_cm - 100) - ((talla_cm - 150) / (2.5 if genero == "Femenino" else 4)), 1)
factores = {"Sedentario": 1.2, "Ligero": 1.4, "Moderado": 1.6, "Intenso": 1.9, "Atleta": 2.2}
f_act = factores[actividad]
if meta == "Ganar Músculo": f_act += 0.2
proteina_diaria = round(peso * f_act, 1)

st.subheader("📊 Resumen de Datos")
c1, c2, c3 = st.columns(3)
c1.metric("IMC", imc)
c2.metric("Ref. Peso Ideal", f"{peso_ideal} kg")
c3.metric("Proteína Objetivo", f"{proteina_diaria} g")

st.write("---")
st.subheader("📦 Inventario Real disponible")
inventario = st.text_area("Lista de alimentos que tienes en casa...", placeholder="Ej: 1kg pechuga, 12 huevos, 500g arroz...", height=120)

if st.button("🚀 GENERAR MI PLAN DE BIOLOGÍSTICA", disabled=not acepto):
    if not nombre or not inventario:
        st.error("❌ Por favor completa los campos requeridos.")
    else:
        try:
            client = Groq(api_key=API_KEY_MAESTRA)

            prompt = f"""
Eres una experta en BioLogística nutricional y Gestión de Alimentos.
CLIENTE: {nombre}. EDAD: {edad}. PESO: {peso}kg. IMC: {imc}.
RITMO: {actividad}. META: {meta}. CUIDADO ESPECIAL: {salud}
PROTEÍNA OBJETIVO: {proteina_diaria}g al día.
INVENTARIO DISPONIBLE: {inventario}.

INSTRUCCIONES:
1. Confirma la proteína necesaria explicando brevemente por qué.
2. Diseña menú de Lunes a Viernes usando el inventario disponible.
   - En cada comida indica el alimento, cantidad y proteína entre paréntesis.
   - Ejemplo: 150g Pechuga de pollo (31g proteína)
   - Al final de cada día suma EXACTAMENTE los gramos de proteína de cada comida.
   - REGLA IMPORTANTE: El Total Proteína diario = suma exacta de desayuno + almuerzo + cena. No inventes el total, calcula matemáticamente.
3. Explica brevemente cómo preparar los alimentos de forma saludable.
4. Lista de compras para la semana siguiente basada SOLO en las cantidades reales usadas en el menú. Si el menú usa 4 huevos en total, pide 4 huevos, no 60. Sé proporcional y lógica.

REGLAS:
- Solo comida natural, nada de polvos ni suplementos.
- Sugiere alimentos específicos que ayuden con: {salud}.
- Lista de compras en cantidades reales usadas en el menú.
- Sé amable y clara, sin lenguaje médico.
"""

            with st.spinner("⚖️ Calculando logística de precisión..."):
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=2000
                )
                plan = response.choices[0].message.content

            st.markdown(plan)

            pdf_bytes = generar_pdf(plan, nombre, proteina_diaria, peso_ideal, imc, actividad, edad)
            st.download_button("📥 DESCARGAR REPORTE (PDF)", data=pdf_bytes, file_name=f"BioLogistica_{nombre}.pdf", mime="application/pdf")

        except Exception as e:
            st.error(f"Error en el sistema: {e}")