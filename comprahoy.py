import streamlit as st
from groq import Groq
from fpdf import FPDF

st.set_page_config(page_title="BioLogística Pro", page_icon="🥗", layout="wide")

API_KEY_MAESTRA = st.secrets["GROQ_API_KEY"] if "GROQ_API_KEY" in st.secrets else "TU_LLAVE_AQUI"

def generar_pdf(texto, nombre, proteina, peso_ideal, imc, edad, objetivo):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(15, 15, 15)
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(46, 125, 50)
    pdf.cell(0, 10, f"REPORTE BIOLOGISTICA: {nombre.upper()}", ln=True, align='C')
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 10)
    pdf.set_text_color(0, 0, 0)
    resumen = f"Edad: {edad} | Objetivo: {objetivo} | Peso ref: {peso_ideal}kg | IMC: {imc} | Meta: {proteina}g prot/dia"
    pdf.cell(0, 8, resumen.encode('latin-1', 'ignore').decode('latin-1'), ln=True, border=1)
    pdf.ln(5)
    
    pdf.set_font("Arial", size=10)
    # Limpieza de caracteres extraños para el PDF
    limpio = texto.replace('|', '').replace('-', '').replace('*', '').encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 6, txt=limpio)
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFAZ ---
st.markdown("<h1 style='text-align: center; color: #2E7D32;'>🥗 BIOLOGÍSTICA DE PRECISIÓN</h1>", unsafe_allow_html=True)

# --- BOTÓN DE SEGURIDAD Y AVISO ---
st.subheader("⚖️ Acuerdo de Uso y Privacidad")
with st.container(border=True):
    st.info("""
    **Al usar BioLogística, confirmas que comprendes:**
    1. Esta es una herramienta de **organización de inventario**.
    2. Los datos de peso/salud se usan para cálculos matemáticos y **no se almacenan**.
    3. No sustituye el diagnóstico de un médico. Consulta a un profesional antes de cambiar tu dieta.
    """)
    # Este es el botón de seguridad que bloquea el resto de la app
    acepto = st.checkbox("He leído y acepto que esto es una guía logística y no una prescripción médica.")

with st.sidebar:
    st.header("👤 Datos del Cliente")
    nombre = st.text_input("Nombre:")
    col_a, col_b = st.columns(2)
    with col_a:
        edad = st.number_input("Edad:", 1, 120, 57)
        peso = st.number_input("Peso (kg):", 30.0, 200.0, 65.0)
    with col_b:
        talla_cm = st.number_input("Altura (cm):", 100.0, 250.0, 155.0)
        genero = st.radio("Género:", ["Femenino", "Masculino"])
    
    objetivo = st.radio("Objetivo:", ["Mantener", "Ganar Músculo", "Perder Grasa"])
    actividad = st.select_slider("Ritmo de vida:", options=["Sedentario", "Ligero", "Moderado", "Intenso"], value="Sedentario")
    salud = st.multiselect("Condiciones de salud:", ["Diabetes", "Colesterol", "Hígado Graso", "Presión Alta"], default=["Hígado Graso", "Colesterol"])

# Cálculos
talla_m = talla_cm / 100
imc = round(peso / (talla_m**2), 1)
peso_ideal = round((talla_cm - 100) - ((talla_cm - 150) / (2.5 if genero == "Femenino" else 4)), 1)
factor_prot = {"Mantener": 1.2, "Ganar Músculo": 1.7, "Perder Grasa": 1.5}[objetivo]
proteina_diaria = round(peso * factor_prot, 1)

st.subheader("📊 Resumen de Diagnóstico")
c1, c2, c3 = st.columns(3)
c1.metric("IMC", imc)
c2.metric("Ref. Peso Ideal", f"{peso_ideal} kg")
c3.metric("Proteína Meta", f"{proteina_diaria} g")

st.write("---")
st.subheader("📦 Inventario Real disponible")
inventario = st.text_area("Lista de lo que tienes hoy (Ej: 2 huevos, 100g lenteja...):", height=100)

# El botón solo se activa si "acepto" es True
if st.button("🚀 GENERAR PLAN NUTRICIONAL", disabled=not acepto):
    if not nombre or not inventario:
        st.error("❌ Por favor completa nombre e inventario.")
    else:
        try:
            client = Groq(api_key=API_KEY_MAESTRA)
            
            prompt = f"""
            Actúa como Nutricionista Clínica experta en BioLogística. 
            CLIENTE: {nombre} | CONDICIONES: {salud} | OBJETIVO: {objetivo} | META: {proteina_diaria}g proteína/día.
            INVENTARIO: {inventario}.

            REGLAS NUTRICIONALES Y LOGÍSTICAS:
            1. SALUD: Por {salud}, prohíbe el exceso de grasas. Máximo 20g de queso al día. Prioriza fibras y proteínas magras.
            2. INVENTARIO: No menciones alimentos que no están en la lista de inventario. Si falta proteína, NO la inventes en el menú, pídela en la lista de compras.
            3. MATEMÁTICA: Lista de Compras = (Necesidad para 5 días) - (Inventario).
            4. FORMATO: Texto limpio en párrafos. No uses tablas '|' ni símbolos extraños.
            """

            with st.spinner("⚖️ Procesando con criterio clínico..."):
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.0 
                )
                plan = response.choices[0].message.content
                st.markdown(plan)
                
                pdf_bytes = generar_pdf(plan, nombre, proteina_diaria, peso_ideal, imc, edad, objetivo)
                st.download_button("📥 DESCARGAR REPORTE PDF", data=pdf_bytes, file_name=f"BioLogistica_{nombre}.pdf")
        except Exception as e:
            st.error(f"Error: {e}")