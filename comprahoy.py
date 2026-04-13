import streamlit as st
from groq import Groq
from fpdf import FPDF

st.set_page_config(page_title="BioLogística Pro", page_icon="🥗", layout="wide")

# Llave API
API_KEY_MAESTRA = st.secrets["GROQ_API_KEY"] if "GROQ_API_KEY" in st.secrets else "TU_LLAVE_AQUI"

def generar_pdf(texto, nombre, proteina, peso_ideal, imc, edad, objetivo, actividad):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(15, 15, 15)
    
    # Encabezado
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(46, 125, 50)
    pdf.cell(0, 10, f"PLAN MAESTRO DE BIOLOGISTICA: {nombre.upper()}", ln=True, align='C')
    pdf.ln(5)
    
    # Ficha del cliente
    pdf.set_font("Arial", 'B', 10)
    pdf.set_text_color(0, 0, 0)
    pdf.set_fill_color(230, 240, 230)
    resumen = f"Edad: {edad} | Actividad: {actividad} | IMC: {imc} | Meta: {proteina_diaria}g prot/dia"
    pdf.cell(0, 10, resumen.encode('latin-1', 'ignore').decode('latin-1'), ln=True, fill=True, border=1, align='C')
    pdf.ln(10)
    
    # Cuerpo del reporte
    pdf.set_font("Arial", size=10)
    limpio = texto.replace('|', ' ').replace('*', '').encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 6, txt=limpio)
    
    return bytes(pdf.output())

# --- INTERFAZ PRINCIPAL ---
st.markdown("<h1 style='text-align: center; color: #2E7D32;'>🥗 BIOLOGÍSTICA DE PRECISIÓN</h1>", unsafe_allow_html=True)

# --- BLOQUE DE SEGURIDAD ---
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
    st.header("👤 Perfil del cliente")
    nombre = st.text_input("Nombre:", value="Doris")
    col1, col2 = st.columns(2)
    with col1:
        edad = st.number_input("Edad:", 1, 120, 57)
        peso = st.number_input("Peso (kg):", 30.0, 200.0, 65.0)
    with col2:
        talla_cm = st.number_input("Altura (cm):", 100.0, 250.0, 155.0)
        genero = st.radio("Género:", ["Femenino", "Masculino"])
    
    # --- AQUÍ ESTÁ LO QUE FALTABA: ACTIVIDAD FÍSICA ---
    actividad = st.select_slider(
        "Ritmo de vida / Actividad:",
        options=["Sedentario", "Ligero", "Moderado", "Intenso"],
        value="Sedentario"
    )
    
    objetivo = st.radio("Objetivo:", ["Mantener", "Ganar Músculo", "Perder Grasa"])
    salud = st.multiselect("Cuidado especial:", ["Suave para el higado", "Bajo en grasas", "Bajo en azucar", "Bajo en sodio"], default=["Suave para el higado", "Bajo en grasas"])

# Cálculos de Nutrición Ajustados
talla_m = talla_cm / 100
imc = round(peso / (talla_m**2), 1)
peso_ideal = round((talla_cm - 100) - ((talla_cm - 150) / (2.5 if genero == "Femenino" else 4)), 1)

# Factor de proteína ajustado por actividad y objetivo
base_prot = {"Mantener": 1.2, "Ganar Músculo": 1.6, "Perder Grasa": 1.4}
extra_actividad = {"Sedentario": 0.0, "Ligero": 0.1, "Moderado": 0.2, "Intenso": 0.3}
factor_final = base_prot[objetivo] + extra_actividad[actividad]
proteina_diaria = round(peso * factor_final, 1)

st.write("---")
st.subheader("📦 Inventario de Despensa")
inventario = st.text_area("Escribe detalladamente qué tienes (Ej: 3 huevos, 100g de queso...)", height=100)

if st.button("🚀 GENERAR PLAN DE COMIDAS SEMANAL Y COMPRAS", disabled=not acepto):
    if not inventario:
        st.error("❌ Por favor, ingresa tu inventario.")
    else:
        try:
            client = Groq(api_key=API_KEY_MAESTRA)
            
            prompt = f"""
            Actúa como Nutricionista Experta en  gastronomia peruana y logistica.
            CLIENTE: {nombre}, {edad} años, {genero}.
            NIVEL DE ACTIVIDAD: {actividad}.
            PREFERENCIAS ALIMENTARIAS DEL CLIENTE: {salud}.
            Adapta el menú respetando el inventario y las preferencias de {nombre}:
- Bajo en azúcar: evita dulces, harinas blancas, 
  frutas muy dulces. Prioriza alimentos de bajo 
  índice glucémico.
- Bajo en grasas: limita quesos curados a 20-30g 
  como condimento, evita fritos y grasas saturadas.
- Suave para el hígado: prioriza proteínas magras, 
  verduras frescas, evita alcohol y ultraprocesados.
- Bajo en sodio: evita sal en exceso, embutidos 
  y enlatados.
            META: {proteina_diaria}g proteína diaria para {objetivo}.
            INVENTARIO ACTUAL: {inventario}.
REGLAS DE COCINA PERSONALIZADAS:
- En la preparacion de la comida USA exclusivamente los alimentos del inventario disponible.
- El menú es para UNA persona durante 5 días.
- Los snacks deben ser apetecibles:  Nunca verduras crudas solas como snack.
-- Calcula las porciones según el perfil de {nombre}: 
  {peso}kg, {edad} años, actividad {actividad}, 
  objetivo {objetivo}.
-- La lista de compras debe reflejar lo que se necesita la semana siguiente restando el inventario.
            TAREAS:
            1. HACER EL CALCULO DE PROTEINAS que necesita el cliente por dia y distribuirlo en cada comida, poniendo la cantidad de proteina en cada comida y en cada dia
            2. TABLA DE MENÚ SEMANAL: Basada en el inventario, sus "prefencias alimentarias" y actividad {actividad}. usar el inventario estrictamente. poner comidas variadas cada dia
            -poner la cantidad del alimento crudo  a usar y la cantidad de gramos de proteina en cada comida, calculo matematico exacto y el total de proteinas de cada plato.
            3. LISTA DE COMPRAS PERSONALIZADA para la semana siguiente:
    -Hacer la lista de compras personalizada de los alimentos que  necesita el cliente para la semana siguiente restando el inventario y poniendo el saldo para comprar, calculo matematico exacto. sugerir nuevos alimentos en la lista cada semana, Adaptada a las prefencias alimentarias: {salud}
   - Considera que {nombre} tiene {edad} años, pesa {peso}kg  y su objetivo es {objetivo}
   - Organiza por categorías: Proteínas, Verduras, Frutas, 
     Lácteos, sugerir alimentos naturales, pero nunca polvos de proteina ni otros quimicos
   - Indica cantidad exacta de cada alimento en kg, litros o unidades, nunca en paquetes o cabezas
   - Sugiere alternativas económicas cuando sea posible
   - IMPORTANTE: las comidas deben ser de recetas de comidad peruana
        4. FORMATO: Sin barritas '|'. Texto limpio y profesional.
        5. si el inventario es insuficente para el requerimiento del cliente calculo hasta el dia que alcanza y sugerir la compra inmediata de alimentos
            """

            with st.spinner("⚖️ Calculando según actividad física y salud..."):
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.0
                )
                plan = response.choices[0].message.content
                st.markdown(plan)
                
                pdf_bytes = generar_pdf(plan, nombre, proteina_diaria, peso_ideal, imc, edad, objetivo, actividad)
                st.download_button("📥 DESCARGAR REPORTE PDF", data=pdf_bytes, file_name=f"Plan_{nombre}.pdf")
        except Exception as e:
            st.error(f"Error técnico: {e}")