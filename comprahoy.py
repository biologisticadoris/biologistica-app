import streamlit as st
import google.generativeai as genai
from fpdf import FPDF

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="BioLogística Pro", page_icon="🥗", layout="wide")

# --- LLAVE API MAESTRA (Invisible para el cliente) ---
# En Streamlit Cloud se configura en 'Secrets'. Localmente ponla entre las comillas.
API_KEY_MAESTRA = st.secrets["GOOGLE_API_KEY"] if "GOOGLE_API_KEY" in st.secrets else "TU_LLAVE_AQUI"

# FUNCIÓN PARA EL PDF
def generar_pdf(texto, nombre, proteina, p_ideal, imc, actividad, edad):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(46, 125, 50)
    pdf.cell(0, 10, f"REPORTE DE BIOLOGISTICA: {nombre.upper()}", ln=True, align='C')
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 11)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 7, f"Edad: {edad} anos | Referencia de Peso: {p_ideal} kg | IMC: {imc}", ln=True)
    pdf.cell(0, 7, f"Sugerencia de Proteina: {proteina}g / dia", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", 'I', 8)
    pdf.set_text_color(150, 0, 0)
    pdf.multi_cell(0, 5, txt="AVISO: Este documento es una guia logistica de alimentos. No es una prescripcion medica. Consulte a su profesional de salud.")
    pdf.ln(5)
    pdf.set_font("Arial", size=10)
    pdf.set_text_color(0, 0, 0)
    # Limpiar caracteres especiales para el PDF
    limpio = texto.replace('🚀','').replace('🥗','').replace('✅','').replace('**','').encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 7, txt=limpio)
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFAZ VISUAL ---
st.markdown("<h1 style='text-align: center; color: #2E7D32;'>🥗 BIOLOGÍSTICA DE PRECISIÓN</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Gestión Inteligente de Inventario y Optimización de Alimentos</p>", unsafe_allow_html=True)

# --- ACUERDO DE USO Y PRIVACIDAD ---
st.subheader("⚖️ Acuerdo de Uso y Privacidad")
with st.container(border=True):
    st.info("""
    **Al usar BioLogística, confirmas que comprendes:**
    1. Esta es una herramienta de **organización de inventario**.
    2. Los datos de peso/salud se usan para cálculos matemáticos y **no se almacenan**.
    3. No sustituye el diagnóstico de un médico. Consulta a un profesional antes de cambiar tu dieta.
    """)
    acepto = st.checkbox("He leído y acepto que esto es una guía logística y no una prescripción médica.")

# --- BARRA LATERAL (DATOS) ---
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

# --- CÁLCULOS LOGÍSTICOS ---
talla_m = talla_cm / 100
imc = round(peso / (talla_m**2), 1)
peso_ideal = round((talla_cm - 100) - ((talla_cm - 150) / (2.5 if genero == "Femenino" else 4)), 1)
factores = {"Sedentario": 1.2, "Ligero": 1.4, "Moderado": 1.6, "Intenso": 1.9, "Atleta": 2.2}
f_act = factores[actividad]
if meta == "Ganar Músculo": f_act += 0.2
proteina_diaria = round(peso * f_act, 1)

# --- PANEL DE ESTADO ---
st.subheader("📊 Resumen de Datos")
c1, c2, c3 = st.columns(3)
c1.metric("IMC", imc)
c2.metric("Ref. Peso Ideal", f"{peso_ideal} kg")
c3.metric("Proteína Objetivo", f"{proteina_diaria} g")

st.write("---")
st.subheader("📦 Inventario Real disponible")
inventario = st.text_area("Lista de alimentos que tienes en casa...", placeholder="Ej: 1kg pechuga, 12 huevos, 500g arroz...", height=120)

# --- EJECUCIÓN ---
if st.button("🚀 GENERAR MI PLAN DE BIOLOGÍSTICA", disabled=not acepto):
    if not nombre or not inventario:
        st.error("❌ Por favor completa los campos requeridos.")
    else:
        try:
            client = genai.Client(api_key=API_KEY_MAESTRA)
            
            # PROMPT CON TUS INSTRUCCIONES EXACTAS
            prompt = f"""
            Eres una experta en BioLogística Nutricionaly Gestion de Alimentos. 
            CLIENTE: {nombre}. EDAD: {edad}. PESO: {peso}kg. IMC: {imc}.
            RITMO: {actividad}. META: {meta}. CUIDADO ESPECIAL: {salud}
            PROTEÍNA OBJETIVO: {proteina_diaria}g al día.
            INVENTARIO: {inventario}.

            INSTRUCCIONES DE ORGANIZACIÓN:
            1. Confirma que necesita {proteina_diaria}g de proteína al día por su actividad ({actividad}).
            2. **ESTRATEGIA 100% INVENTARIO**: Diseña el menú de Lunes a Viernes usando lo que hay en el inventario. Combina los alimentos de forma eficiente para cubrir la proteína meta.
               - En cada comida, detalla: [Ingrediente en cantidad] ([Gramos de Proteína])(ej: 150g Pollo = 31g proteína)
               - AL FINAL de cada dia, pon en negrita: **Total Proteína: [Suma Total]g**.
            4. **LOGÍSTICA DE PREPARACIÓN**: Explica brevemente cómo cocinarlo para que sea agradable con los ingredientes que hay.
            5. **PROYECCIÓN SEMANA SIGUIENTE**: 
               - Analiza qué se agotó del inventario de esta semana.
               - Genera y sugiere una lista de compras para la PRÓXIMA SEMANA para reponer stock y mantener la dieta saludable.
            
            Presenta el menú en una tabla Markdown ancha TABLA DE COMIDAS de Lunes a Viernes (Desayuno, Almuerzo, Cena).

            REGLAS:
            - Solo comida natural (nada de polvos).
            - Suma el total de proteína en cada plato: **Total Proteína: [Suma]g**.
            - Da ideas ricas para cocinar y sugiere verduras/frutas específicas que ayuden con: {salud}.
            - No uses lenguaje médico, sé amable y clara.
            - Lista de compras en kilos/unidades.
            """

            with st.spinner("⚖️ Calculando logística de precisión..."):
                response = client.models.generate_content(model="gemini-3.1-flash-lite-preview", contents=prompt)
                plan = response.text
            
            st.markdown(plan)
            
            # Descarga de PDF
            pdf_bytes = generar_pdf(plan, nombre, proteina_diaria, peso_ideal, imc, actividad, edad)
            st.download_button("📥 DESCARGAR REPORTE (PDF)", data=pdf_bytes, file_name=f"BioLogistica_{nombre}.pdf", mime="application/pdf")
            
        except Exception as e:
            st.error(f"Error en el sistema. Asegúrate de que la API Key interna sea válida.")