import streamlit as st
import google.generativeai as genai

# ==========================================
# 1. DATABASE COMPONENTI (Logica Rigida)
# ==========================================
db = {
    "cpu": [
        {"name": "Intel Core i5-13600K", "socket": "LGA1700", "price": 310, "tdp": 125},
        {"name": "Intel Core i7-14700K", "socket": "LGA1700", "price": 420, "tdp": 253}
    ],
    "motherboard": [
        {"name": "ASUS Prime B760M-A D4 (White)", "socket": "LGA1700", "format": "mATX", "price": 140},
        {"name": "MSI MAG B760M MORTAR WIFI", "socket": "LGA1700", "format": "mATX", "price": 180},
        {"name": "ASUS ROG STRIX Z790-A GAMING WIFI", "socket": "LGA1700", "format": "ATX", "price": 350}
    ],
    "case": [
        {"name": "Lian Li O11 Dynamic Mini Snow (White)", "formats_supported": ["mATX", "ITX"], "max_radiator": 280, "max_gpu": 395, "price": 130},
        {"name": "NZXT H6 Flow White (Panoramic)", "formats_supported": ["ATX", "mATX", "ITX"], "max_radiator": 360, "max_gpu": 365, "price": 120}
    ],
    "gpu": [
        {"name": "NVIDIA RTX 4070 Super", "length": 260, "price": 650, "tdp": 220},
        {"name": "NVIDIA RTX 4080 Super", "length": 342, "price": 1100, "tdp": 320}
    ],
    "cooler": [
        {"name": "NZXT Kraken Elite 280 RGB White", "socket": "LGA1700", "radiator_size": 280, "price": 260},
        {"name": "Corsair iCUE H150i ELITE CAPELLIX XT 360mm", "socket": "LGA1700", "radiator_size": 360, "price": 240}
    ],
    "psu": [
        {"name": "Corsair RM750e 750W", "wattage": 750, "price": 110},
        {"name": "Corsair RM850x 850W White", "wattage": 850, "price": 150}
    ]
}

# ==========================================
# 2. INTERFACCIA E LOGICA DI FILTRAGGIO
# ==========================================
st.set_page_config(page_title="Custom PC Builder", layout="wide")
st.title("🛠️ PC Builder Ottimizzato - Vincoli Garantiti")

# Sidebar per il Budget
st.sidebar.header("Impostazioni Iniziali")
budget_max = st.sidebar.slider("Budget Massimo (€)", 1000, 3000, 1800, step=50)

st.subheader("1. Scegli i Componenti Principali")

# Scelta CPU
cpu_names = [c["name"] for c in db["cpu"]]
scelta_cpu_nome = st.selectbox("Processore (CPU)", cpu_names)
cpu_selezionata = next(c for c in db["cpu"] if c["name"] == scelta_cpu_nome)

# Filtro Motherboard in base al Socket della CPU
mb_compatibili = [m for m in db["motherboard"] if m["socket"] == cpu_selezionata["socket"]]
mb_names = [m["name"] for m in mb_compatibili]
scelta_mb_nome = st.selectbox("Scheda Madre (Filtrata per Socket)", mb_names)
mb_selezionata = next(m for m in mb_compatibili if m["name"] == scelta_mb_nome)

# Scelta Case
case_names = [c["name"] for c in db["case"]]
scelta_case_nome = st.selectbox("Case", case_names)
case_selezionato = next(c for c in db["case"] if c["name"] == scelta_case_nome)

# Controllo Compatibilità Formato (Case vs Motherboard)
if mb_selezionata["format"] not in case_selezionato["formats_supported"]:
    st.error(f"⚠️ Attenzione! La scheda madre {mb_selezionata['format']} non entra nel case selezionato.")

# Filtro GPU in base allo spazio nel Case
gpu_compatibili = [g for g in db["gpu"] if g["length"] <= case_selezionato["max_gpu"]]
gpu_names = [g["name"] for g in gpu_compatibili]
scelta_gpu_nome = st.selectbox("Scheda Video (GPU) (Filtrata per spazio Case)", gpu_names)
gpu_selezionata = next(g for g in gpu_compatibili if g["name"] == scelta_gpu_nome)

# Filtro Dissipatore (AIO) in base al Socket e spazio Radiatore del Case
cooler_compatibili = [k for k in db["cooler"] if k["socket"] == cpu_selezionata["socket"] and k["radiator_size"] <= case_selezionato["max_radiator"]]
cooler_names = [k["name"] for k in cooler_compatibili]
if not cooler_names:
    st.warning("Nessun dissipatore compatibile con questo case in archivio.")
    cooler_selezionato = {"name": "Nessuno", "price": 0}
else:
    scelta_cooler_nome = st.selectbox("Raffreddamento a Liquido (AIO)", cooler_names)
    cooler_selezionato = next(k for k in cooler_compatibili if k["name"] == scelta_cooler_nome)

# Calcolo Wattaggio e Scelta Alimentatore
watt_stimati = cpu_selezionata["tdp"] + gpu_selezionata["tdp"] + 100 # Margine extra
psu_compatibili = [p for p in db["psu"] if p["wattage"] >= watt_stimati * 1.2] # Margine di sicurezza 20%
psu_names = [p["name"] for p in psu_compatibili]
scelta_psu_nome = st.selectbox("Alimentatore (PSU) (Filtrato per Wattaggio sicuro)", psu_names)
psu_selezionato = next(p for p in psu_compatibili if p["name"] == scelta_psu_nome)

# ==========================================
# 3. CALCOLO BUDGET
# ==========================================
totale = cpu_selezionata["price"] + mb_selezionata["price"] + case_selezionato["price"] + gpu_selezionata["price"] + cooler_selezionato["price"] + psu_selezionato["price"]

st.write("---")
st.subheader("Riepilogo Costi")
if totale <= budget_max:
    st.success(f"✅ Totale: {totale}€ (Entro il budget di {budget_max}€)")
else:
    st.error(f"❌ Totale: {totale}€ (Hai superato il budget di {totale - budget_max}€)")

# ==========================================
# 4. INTEGRAZIONE IA PER LA GUIDA AL MONTAGGIO
# ==========================================
st.write("---")
st.subheader("2. Genera la Guida di Montaggio con l'IA")

# Qui va inserita la tua chiave API di Google Gemini (gratuita)
API_KEY = "INSERISCI_QUI_LA_TUA_CHIAVE_API" 

if st.button("Genera Tutorial Passo-Passo"):
    if API_KEY == "INSERISCI_QUI_LA_TUA_CHIAVE_API":
        st.warning("Inserisci la tua API Key di Gemini nel codice riga 114 per attivare questa funzione.")
    else:
        with st.spinner('L\'IA sta scrivendo la guida personalizzata...'):
            genai.configure(api_key=API_KEY)
            model = genai.GenerativeModel('gemini-pro')
            
            prompt_ia = f"""
            Sei un esperto assemblatore di PC. Scrivi una guida passo-passo molto pratica e sicura per montare esattamente questi componenti:
            - CPU: {cpu_selezionata['name']}
            - Scheda Madre: {mb_selezionata['name']}
            - Case: {case_selezionato['name']}
            - Dissipatore: {cooler_selezionato['name']}
            
            Struttura la risposta in 5 passaggi numerati. Evidenzia dove va messa la pasta termica e dove collegare la pompa dell'AIO sulla scheda madre. 
            Il tono deve essere professionale ma incoraggiante.
            """
            
            response = model.generate_content(prompt_ia)
            st.markdown(response.text)