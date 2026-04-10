import streamlit as st
from groq import Groq
from fpdf import FPDF

st.set_page_config(page_title="BioLogística Pro", page_icon="🥗", layout="wide")

# Llave API
API_KEY_MAESTRA = st.secrets["GROQ_API_KEY"] if "GROQ_API_KEY" in st.secrets else "TU_LLAVE_AQUI"

def generar_pdf(texto, nombre, proteina, p_ideal, imc, edad, objetivo):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(15, 15, 15)
    
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(46, 125, 50)
    pdf.cell(0, 10, f"REPORTE BIOLOGISTICA: {nombre.upper()}", ln=True, align='C')
    pdf.ln(3)
    
    pdf.set_font("Arial", 'B', 10)
    pdf.set_text_color(0, 0, 0)
    resumen = f"Edad: {edad} | Objetivo: {objetivo} | Peso ref: {p_ideal}kg | IMC: {imc} | Proteina: {proteina}g/dia"
    pdf.cell(0, 7, resumen.encode('latin-1', 'ignore').decode('latin-1'), ln=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", size=10)
    limpio = texto.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 6, txt=limpio, border=1)
    
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFAZ ---
st.markdown("<h1 style='text-align: center; color: #2E7D32;'>🥗 BIOLOGÍSTICA DE PRECISIÓN</h1>", unsafe_allow_html=True)

st.subheader("⚖️ Acuerdo de Uso y Privacidad")
with st.container(border=True):
    st.info("""
    **Al usar BioLogística, confirmas que comprendes:**
    1. Esta es una herramienta de **organización de inventario**.
    2. Los datos de peso/salud se usan para cálculos matemáticos y **no se almacenan**.
    3. No sustituye el diagnóstico de un médico.
    """)
    acepto = st.checkbox("He leído y acepto que esto es una guía logística.")

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
    
    # --- AQUÍ VOLVIERON LOS OBJETIVOS ---
    objetivo = st.radio("Objetivo:", ["Mantener", "Ganar Músculo", "Perder Grasa"])
    actividad = st.select_slider("Ritmo de vida:", options=["Sedentario", "Ligero", "Moderado", "Intenso"], value="Sedentario")
    salud = st.multiselect("Cuidado especial:", ["Diabetes", "Colesterol", "Hígado Graso", "Presión Alta"], default=["Hígado Graso", "Colesterol"])

# Cálculos rápidos
talla_m = talla_cm / 100
imc = round(peso / (talla_m**2), 1)
peso_ideal = round((talla_cm - 100) - ((talla_cm - 150) / (2.5 if genero == "Femenino" else 4)), 1)

# Ajuste de proteína según objetivo
factor_prot = 1.2
if objetivo == "Ganar Músculo": factor_prot = 1.8
elif objetivo == "Perder Grasa": factor_prot = 1.5
proteina_diaria = round(peso * factor_prot, 1)

st.subheader("📊 Resumen de Datos")
c1, c2, c3 = st.columns(3)
c1.metric("IMC", imc)
c2.metric("Ref. Peso Ideal", f"{p_ideal} kg") # Usamos p_ideal calculado
c3.metric("Proteína Objetivo", f"{proteina_diaria} g")

st.write("---")
st.subheader("📦 Inventario Real disponible")
inventario = st.text_area("Escribe lo que TIENES hoy en casa:", height=100)

if st.button("🚀 GENERAR MI PLAN", disabled=not acepto):
    if not nombre or not inventario:
        st.error("❌ Completa nombre e inventario.")
    else:
        try:
            client = Groq(api_key=API_KEY_MAESTRA)
            
            # PROMPT MATEMÁTICO Y CON OBJETIVO
            prompt = f"""
            Eres un Auditor de Logística Nutricional. 
            CLIENTE: {nombre} | OBJETIVO: {objetivo} | PROTEÍNA: {proteina_diaria}g/día.
            INVENTARIO REAL: {inventario}

            INSTRUCCIONES:
            1. Menú de 5 días usando SOLO lo que hay en INVENTARIO.
            2. REGLA DE ORO: Si no hay pollo en el inventario, NO pongas pollo. 
            3. LISTA DE COMPRAS: Resta (Necesidad para 5 días) - (Inventario). 
               - Si no hay suficiente proteína para el objetivo de '{objetivo}', pide comprar lo necesario en la lista.
            4. Se amable pero muy preciso con las cantidades.
            """

            with st.spinner("⚖️ Calculando logística..."):
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.0 # Cero imaginación, pura matemática
                )
                plan = response.choices[0].message.content
                st.markdown(plan)
                
                pdf_bytes = generar_pdf(plan, nombre, proteina_diaria, peso_ideal, imc, edad, objetivo)
                st.download_button("📥 DESCARGAR PDF", data=pdf_bytes, file_name=f"Plan_{nombre}.pdf")

        except Exception as e:
            st.error(f"Error: {e}")