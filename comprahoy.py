import streamlit as st
from groq import Groq
from fpdf import FPDF

st.set_page_config(page_title="BioLogística Pro", page_icon="🥗", layout="wide")

# Llave API
API_KEY_MAESTRA = st.secrets["GROQ_API_KEY"] if "GROQ_API_KEY" in st.secrets else "TU_LLAVE_AQUI"

def generar_pdf(texto, nombre, proteina, peso_ideal, imc, edad, objetivo):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(15, 15, 15)
    
    # Encabezado
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(46, 125, 50)
    pdf.cell(0, 10, f"PLAN MAESTRO DE BIOLOGISTICA: {nombre.upper()}", ln=True, align='C')
    pdf.ln(5)
    
    # Ficha del Paciente
    pdf.set_font("Arial", 'B', 10)
    pdf.set_text_color(0, 0, 0)
    pdf.set_fill_color(230, 240, 230)
    resumen = f"Edad: {edad} | IMC: {imc} | Peso Ref: {peso_ideal}kg | Meta: {proteina}g prot/dia"
    pdf.cell(0, 10, resumen.encode('latin-1', 'ignore').decode('latin-1'), ln=True, fill=True, border=1, align='C')
    pdf.ln(10)
    
    # Cuerpo del reporte
    pdf.set_font("Arial", size=10)
    # Limpiamos caracteres que ensucian el PDF
    limpio = texto.replace('|', ' ').replace('*', '').encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 6, txt=limpio)
    
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFAZ PRINCIPAL ---
st.markdown("<h1 style='text-align: center; color: #2E7D32;'>🥗 BIOLOGÍSTICA DE PRECISIÓN</h1>", unsafe_allow_html=True)

# --- BLOQUE DE SEGURIDAD (OBLIGATORIO) ---
st.subheader("⚖️ Acuerdo de Responsabilidad y Privacidad")
with st.container(border=True):
     **Al usar BioLogística, confirmas que comprendes:**
    1. Esta es una herramienta de **organización de inventario**.
    2. Los datos de peso/salud se usan para cálculos matemáticos y **no se almacenan**.
    3. No sustituye el diagnóstico de un médico. Consulta a un profesional antes de cambiar tu dieta.
    """)
    acepto = st.checkbox("He leído y acepto que esto es una guía logística y no una prescripción médica.")

with st.sidebar:
    st.header("👤 Perfil del cliente")
    nombre = st.text_input("Nombre:", value="Doris")
    col1, col2 = st.columns(2)
    with col1:
        edad = st.number_input("Edad:", 1, 120, 57)
        peso = st.number_input("Peso (kg):", 30.0, 200.0, 65.0)
    with col2:
        talla_cm = st.number_input("Altura (cm):", 100.0, 250.0, 155.0)
        genero = st.radio("Género:", ["Femenino", "Masculino"])
    
    objetivo = st.radio("Objetivo:", ["Mantener", "Ganar Músculo", "Perder Grasa"])
    salud = st.multiselect("Condiciones médicas:", ["Hígado Graso", "Colesterol", "Diabetes", "Hipertensión"], default=["Hígado Graso", "Colesterol"])

# Cálculos de Nutrición
talla_m = talla_cm / 100
imc = round(peso / (talla_m**2), 1)
peso_ideal = round((talla_cm - 100) - ((talla_cm - 150) / (2.5 if genero == "Femenino" else 4)), 1)
factores = {"Mantener": 1.2, "Ganar Músculo": 1.7, "Perder Grasa": 1.5}
proteina_diaria = round(peso * factores[objetivo], 1)

st.write("---")
st.subheader("📦 Inventario de Despensa")
inventario = st.text_area("Escribe detalladamente qué tienes (Ej: 3 huevos, 100g de queso, nada de carne...)", height=100)

# BOTÓN CONECTADO AL CHECKBOX DE SEGURIDAD
if st.button("🚀 GENERAR PLAN NUTRICIONAL Y COMPRAS", disabled=not acepto_seguridad):
    if not inventario:
        st.error("❌ Por favor, ingresa tu inventario para poder calcular las compras.")
    else:
        try:
            client = Groq(api_key=API_KEY_MAESTRA)
            
            prompt = f"""
            Actúa como Nutricionista  y Experta en Logística de Suministros.
            CLIENTE: {nombre}, {edad} años, con {salud}.
            META: {proteina_diaria}g proteína diaria para {objetivo}.
            INVENTARIO ACTUAL: {inventario}.

            TAREAS ESTRICTAS:
            1. TABLA DE MENÚ (Lunes a Viernes): 
               - Crea un menú saludable. Si un ingrediente necesario NO está en el inventario, deja el espacio vacío y pon "(Falta compra)".
               
            2. LISTA DE COMPRAS PROFESIONAL (PARA 7 DÍAS):
               - Calcula las cantidades totales de los alimentos necesarias de acuerdo a los requerimientos del cliente, restando el inventario.
               - Formato de Supermercado: Kilos (kg) para carnes/verduras, Litros (L) para lácteos/aceites.
               - Ejemplo: "Comprar 1.2 kg de Pechuga de Pollo", "2 kg de Manzanas", "1 L de Aceite de Oliva".
            
            3. FORMATO: Texto claro y profesional. No uses barritas '|' que dañen el PDF.
            """

            with st.spinner("⚖️ Aplicando criterios médicos y calculando kilos de compra..."):
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.0
                )
                plan = response.choices[0].message.content
                st.markdown(plan)
                
                pdf_bytes = generar_pdf(plan, nombre, proteina_diaria, peso_ideal, imc, edad, objetivo)
                st.download_button("📥 DESCARGAR REPORTE PDF PROFESIONAL", data=pdf_bytes, file_name=f"Plan_Nutricional_{nombre}.pdf")
        except Exception as e:
            st.error(f"Error técnico: {e}")