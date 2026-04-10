import streamlit as st
from groq import Groq
from fpdf import FPDF

st.set_page_config(page_title="BioLogística Pro", page_icon="🥗", layout="wide")

# Llave API desde Secrets
API_KEY_MAESTRA = st.secrets["GROQ_API_KEY"] if "GROQ_API_KEY" in st.secrets else "TU_LLAVE_AQUI"

def generar_pdf(texto, nombre, proteina, p_ideal, imc, edad):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(15, 15, 15)
    
    # Encabezado corregido (set_text_color)
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(46, 125, 50)
    pdf.cell(0, 10, f"REPORTE BIOLOGISTICA: {nombre.upper()}", ln=True, align='C')
    pdf.ln(3)
    
    # Datos de Salud
    pdf.set_font("Arial", 'B', 10)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 7, f"Edad: {edad} anos | Peso ref: {p_ideal}kg | IMC: {imc} | Proteina: {proteina}g/dia", ln=True)
    pdf.ln(5)
    
    # Contenido con multi_cell para que NO SE CORTE
    pdf.set_font("Arial", size=10)
    limpio = texto.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 6, txt=limpio, border=1)
    
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFAZ ---
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
    st.header("👤 Datos del Cliente")
    nombre = st.text_input("Nombre:")
    col_a, col_b = st.columns(2)
    with col_a:
        edad = st.number_input("Edad:", 1, 120, 57)
        peso = st.number_input("Peso (kg):", 30.0, 200.0, 65.0)
    with col_b:
        talla_cm = st.number_input("Altura (cm):", 100.0, 250.0, 155.0)
        genero = st.radio("Género:", ["Femenino", "Masculino"])
    
    actividad = st.select_slider("Ritmo de vida:", options=["Sedentario", "Ligero", "Moderado", "Intenso"], value="Sedentario")
    salud = st.multiselect("Cuidado especial:", ["Diabetes", "Colesterol", "Hígado Graso", "Presión Alta"], default=["Hígado Graso", "Colesterol"])

# Cálculos rápidos
talla_m = talla_cm / 100
imc = round(peso / (talla_m**2), 1)
peso_ideal = round((talla_cm - 100) - ((talla_cm - 150) / (2.5 if genero == "Femenino" else 4)), 1)
proteina_diaria = round(peso * 1.2, 1)

st.subheader("📊 Resumen de Datos")
c1, c2, c3 = st.columns(3)
c1.metric("IMC", imc)
c2.metric("Ref. Peso Ideal", f"{peso_ideal} kg")
c3.metric("Proteína Objetivo", f"{proteina_diaria} g")

st.write("---")
st.subheader("📦 Inventario Real disponible")
inventario = st.text_area("Escribe lo que TIENES hoy en casa:", placeholder="Ej: 12 huevos, 2 latas de atún...", height=120)

if st.button("🚀 GENERAR MI PLAN DE BIOLOGÍSTICA", disabled=not acepto):
    if not nombre or not inventario:
        st.error("❌ Por favor completa tu nombre e inventario.")
    else:
        try:
            client = Groq(api_key=API_KEY_MAESTRA)
            
            prompt = f"""
            Eres una experta en BioLogística. Tu misión es organizar el consumo de alimentos de {nombre}.
            INVENTARIO DISPONIBLE: {inventario}
            REQUERIMIENTO: Plan de 5 días con {proteina_diaria}g proteína/día.

            INSTRUCCIONES OBLIGATORIAS:
            1. REGLA DE RESTA: Antes de sugerir comprar algo, mira el INVENTARIO. Si el cliente tiene suficiente de un ingrediente, la LISTA DE COMPRAS debe decir: "Ya tienes suficiente". Solo pide comprar la diferencia faltante.
            2. PORCIONES LOGICAS: No excedas cantidades absurdas (Max 40g queso por comida).
            3. NO INVENTES: Si no hay pollo en el inventario, NO pongas pollo en el menú.
            4. FORMATO: Menú diario y LISTA DE COMPRAS REAL (restando inventario).
            """

            with st.spinner("⚖️ Calculando logística y descontando inventario..."):
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.4
                )
                plan = response.choices[0].message.content
                st.markdown(plan)
                
                pdf_bytes = generar_pdf(plan, nombre, proteina_diaria, peso_ideal, imc, edad)
                st.download_button("📥 DESCARGAR REPORTE PDF", data=pdf_bytes, file_name=f"BioLogistica_{nombre}.pdf", mime="application/pdf")

        except Exception as e:
            st.error(f"Error en el sistema: {e}")