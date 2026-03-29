"""
TransportPro — Application Streamlit
Gestion d'entreprise de transport de marchandises
"""

import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, date
import os

# ─────────────────────────────────────────────
#  CONFIG PAGE
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="TransportPro",
    page_icon="🚛",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  CSS CUSTOM
# ─────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Exo+2:wght@300;400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Exo 2', sans-serif;
}

/* Fond général */
.stApp {
    background: #0b1622;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #0f1f30 !important;
    border-right: 1px solid #1e3148;
}
section[data-testid="stSidebar"] * {
    color: #b0c4d8 !important;
}

/* Titre sidebar */
.sidebar-title {
    font-family: 'Share Tech Mono', monospace;
    color: #F5A623 !important;
    font-size: 1.4rem;
    letter-spacing: 2px;
    padding: 1rem 0 0.5rem 0;
    border-bottom: 1px solid #1e3148;
    margin-bottom: 1rem;
}

/* KPI Cards */
.kpi-card {
    background: linear-gradient(135deg, #132337 0%, #0f1f30 100%);
    border: 1px solid #1e3148;
    border-radius: 12px;
    padding: 1.4rem 1rem;
    text-align: center;
    margin-bottom: 0.5rem;
    transition: transform 0.2s;
}
.kpi-card:hover { transform: translateY(-2px); }
.kpi-icon  { font-size: 2rem; margin-bottom: 0.3rem; }
.kpi-value { font-family: 'Share Tech Mono', monospace; font-size: 1.9rem; font-weight: 700; }
.kpi-label { font-size: 0.78rem; color: #7f8c8d; letter-spacing: 1px; text-transform: uppercase; margin-top: 0.2rem; }

/* Section heading */
.section-title {
    font-family: 'Share Tech Mono', monospace;
    color: #F5A623;
    font-size: 1.1rem;
    letter-spacing: 2px;
    border-left: 3px solid #F5A623;
    padding-left: 12px;
    margin: 1.5rem 0 1rem 0;
}

/* Badge statut */
.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.5px;
}
.badge-disponible { background:#1a4a2e; color:#2ecc71; }
.badge-mission    { background:#4a3a00; color:#f39c12; }
.badge-transit    { background:#0d2f4a; color:#1a9bd7; }
.badge-livre      { background:#1a4a2e; color:#27ae60; }
.badge-attente    { background:#2d2d2d; color:#95a5a6; }
.badge-annule     { background:#4a1010; color:#e74c3c; }

/* Boutons */
.stButton > button {
    background: #F5A623 !important;
    color: #0b1622 !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 0.4rem 1.2rem !important;
    letter-spacing: 1px;
    transition: opacity 0.2s !important;
}
.stButton > button:hover { opacity: 0.85 !important; }

/* Inputs */
.stTextInput input, .stNumberInput input, .stSelectbox select, .stDateInput input {
    background: #132337 !important;
    color: #eaf0f6 !important;
    border: 1px solid #1e3148 !important;
    border-radius: 6px !important;
}

/* Dataframe */
.stDataFrame { border-radius: 8px; overflow: hidden; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: #0f1f30;
    border-radius: 8px;
    gap: 4px;
    padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #7f8c8d;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.85rem;
    letter-spacing: 1px;
    border-radius: 6px;
    padding: 0.5rem 1.2rem;
}
.stTabs [aria-selected="true"] {
    background: #132337 !important;
    color: #F5A623 !important;
}

/* Divider */
hr { border-color: #1e3148 !important; }

/* Form card */
.form-card {
    background: #0f1f30;
    border: 1px solid #1e3148;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}

/* Success / error messages */
.stSuccess { background: #1a4a2e !important; }
.stError   { background: #4a1010 !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  BASE DE DONNÉES
# ─────────────────────────────────────────────

DB_FILE = "transport.db"

def get_conn():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL, adresse TEXT, telephone TEXT, email TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS chauffeurs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL, prenom TEXT NOT NULL, permis TEXT,
        telephone TEXT, statut TEXT DEFAULT 'Disponible',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS vehicules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        immatriculation TEXT NOT NULL UNIQUE, marque TEXT, modele TEXT,
        capacite_kg REAL, date_entretien TEXT NOT NULL, statut TEXT DEFAULT 'Disponible',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS livraisons (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        reference TEXT NOT NULL UNIQUE,
        client_id INTEGER REFERENCES clients(id),
        chauffeur_id INTEGER REFERENCES chauffeurs(id),
        vehicule_id INTEGER REFERENCES vehicules(id),
        origine TEXT, destination TEXT, poids_kg REAL, prix_ht REAL,
        statut TEXT DEFAULT 'En attente',
        date_depart TEXT, date_livraison TEXT, notes TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS depenses_vehicules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vehicule_id INTEGER REFERENCES vehicules(id),
        type_depense TEXT NOT NULL,
        montant REAL NOT NULL,
        date_depense TEXT NOT NULL,
        kilometrage REAL,
        fournisseur TEXT,
        description TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS paiements_chauffeurs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chauffeur_id INTEGER REFERENCES chauffeurs(id),
        type_paiement TEXT NOT NULL,
        montant REAL NOT NULL,
        date_paiement TEXT NOT NULL,
        periode TEXT,
        livraison_id INTEGER REFERENCES livraisons(id),
        statut TEXT DEFAULT 'Payé',
        notes TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)
    # Demo data
    c.execute("SELECT COUNT(*) FROM clients")
    if c.fetchone()[0] == 0:
        c.executemany("INSERT INTO clients (nom,adresse,telephone,email) VALUES (?,?,?,?)", [
            ("Acier Pro SAS",        "12 rue de la Forge, Lyon",     "04 72 11 22 33", "contact@acierpro.fr"),
            ("BioFresh Distribution","8 allée des Champs, Bordeaux", "05 56 44 55 66", "bio@biofresh.fr"),
            ("Électro Import",       "45 bd Voltaire, Paris",        "01 44 88 99 00", "import@electro.fr"),
        ])
        c.executemany("INSERT INTO chauffeurs (nom,prenom,permis,telephone,statut) VALUES (?,?,?,?,?)", [
            ("Dupont","Marc",   "B+CE",    "06 12 34 56 78","Disponible","2024-01-17"),
            ("Martin","Sophie", "B+C",     "06 98 76 54 32","Disponible","2024-01-17"),
            ("Leroy", "Julien", "B+CE+C1", "07 11 22 33 44","En mission","2024-01-17"),
        ])
        c.executemany("INSERT INTO vehicules (immatriculation,marque,modele,capacite_kg,statut) VALUES (?,?,?,?,?)", [
            ("AB-123-CD","Renault", "T460",  12000,"Disponible"),
            ("EF-456-GH","Mercedes","Actros",25000,"Disponible"),
            ("IJ-789-KL","Volvo",   "FH16",  30000,"En mission"),
        ])
        c.executemany("""INSERT INTO livraisons
            (reference,client_id,chauffeur_id,vehicule_id,origine,destination,
             poids_kg,prix_ht,statut,date_depart,date_livraison,notes)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""", [
            ("LIV-2024-001",1,1,1,"Lyon",    "Marseille","5000", "1200","Livré",     "2024-01-10","2024-01-11",""),
            ("LIV-2024-002",2,3,3,"Bordeaux","Paris",    "18000","3500","En transit","2024-01-15","2024-01-17","Fragile"),
            ("LIV-2024-003",3,2,2,"Paris",   "Lille",    "8000", "1800","En attente","2024-01-20","2024-01-21",""),
        ])
        c.executemany("""INSERT INTO depenses_vehicules
            (vehicule_id,type_depense,montant,date_depense,kilometrage,fournisseur,description)
            VALUES (?,?,?,?,?,?,?)""", [
            (1,"Carburant",   180.0, "2024-01-10", 152000, "Total",         "Plein gasoil Lyon"),
            (1,"Entretien",   320.0, "2024-01-05", 150000, "Renault Trucks","Vidange + filtres"),
            (2,"Carburant",   410.0, "2024-01-15", 280000, "BP",            "Plein autoroute"),
            (3,"Réparation",  1200.0,"2024-01-08", 310000, "Volvo Service", "Remplacement plaquettes"),
            (2,"Pneumatiques",880.0, "2024-01-12", 279000, "Euromaster",    "2 pneus avant"),
        ])
        c.executemany("""INSERT INTO paiements_chauffeurs
            (chauffeur_id,type_paiement,montant,date_paiement,periode,statut,notes)
            VALUES (?,?,?,?,?,?,?)""", [
            (1,"Salaire mensuel", 2800.0,"2024-01-31","Janvier 2024","Payé",   ""),
            (2,"Salaire mensuel", 2600.0,"2024-01-31","Janvier 2024","Payé",   ""),
            (3,"Salaire mensuel", 2900.0,"2024-01-31","Janvier 2024","Payé",   ""),
            (1,"Prime mission",    350.0,"2024-01-11","LIV-2024-001","Payé",   "Prime livraison express"),
            (3,"Avance",           500.0,"2024-01-20","Janvier 2024","Payé",   "Avance sur salaire"),
        ])
    conn.commit()
    conn.close()

def query(sql, params=()):
    conn = get_conn()
    df = pd.read_sql_query(sql, conn, params=params)
    conn.close()
    return df

def execute(sql, params=()):
    conn = get_conn()
    conn.execute(sql, params)
    conn.commit()
    conn.close()

# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────

STATUS_COLORS = {
    "Disponible": "badge-disponible",
    "En mission": "badge-mission",
    "En transit": "badge-transit",
    "Livré":      "badge-livre",
    "En attente": "badge-attente",
    "Annulé":     "badge-annule",
    "En maintenance": "badge-annule",
    "Absent":     "badge-annule",
}

def badge(statut):
    cls = STATUS_COLORS.get(statut, "badge-attente")
    return f'<span class="badge {cls}">{statut}</span>'

def kpi_card(icon, value, label, color):
    return f"""
    <div class="kpi-card">
        <div class="kpi-icon">{icon}</div>
        <div class="kpi-value" style="color:{color}">{value}</div>
        <div class="kpi-label">{label}</div>
    </div>"""

def section(title):
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)

def unique_ref():
    return f"LIV-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

# ─────────────────────────────────────────────
#  INIT DB — appelé ici, avant toute requête SQL
# ─────────────────────────────────────────────

init_db()

# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────

with st.sidebar:
    st.markdown('<div class="sidebar-title">🚛 Kabeya Trans</div>', unsafe_allow_html=True)
    st.markdown("**Système de gestion**  \nTransport de marchandises", unsafe_allow_html=True)
    st.divider()
    page = st.radio("Navigation", [
        "📊  Tableau de bord",
        "📦  Livraisons",
        "👤  Clients",
        "🧑‍✈️  Chauffeurs",
        "🚗  Véhicules",
        "🔧  Dépenses Véhicule",
        "💰  Paiements Chauffeur",
    ], label_visibility="collapsed")
    st.divider()
    st.caption(f"🗓 {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    st.caption(f"💾 `{os.path.abspath(DB_FILE)}`")

# ─────────────────────────────────────────────
#  PAGE : TABLEAU DE BORD
# ─────────────────────────────────────────────

if "Tableau" in page:
    st.markdown("# 📊 Tableau de bord")
    st.divider()

    conn = get_conn(); c = conn.cursor()
    total_liv  = c.execute("SELECT COUNT(*) FROM livraisons").fetchone()[0]
    livrees    = c.execute("SELECT COUNT(*) FROM livraisons WHERE statut='Livré'").fetchone()[0]
    en_transit = c.execute("SELECT COUNT(*) FROM livraisons WHERE statut='En transit'").fetchone()[0]
    en_attente = c.execute("SELECT COUNT(*) FROM livraisons WHERE statut='En attente'").fetchone()[0]
    nb_clients = c.execute("SELECT COUNT(*) FROM clients").fetchone()[0]
    nb_vehic   = c.execute("SELECT COUNT(*) FROM vehicules").fetchone()[0]
    nb_chauff  = c.execute("SELECT COUNT(*) FROM chauffeurs").fetchone()[0]
    ca         = c.execute("SELECT COALESCE(SUM(prix_ht),0) FROM livraisons WHERE statut='Livré'").fetchone()[0]
    total_dep  = c.execute("SELECT COALESCE(SUM(montant),0) FROM depenses_vehicules").fetchone()[0]
    total_paie = c.execute("SELECT COALESCE(SUM(montant),0) FROM paiements_chauffeurs WHERE statut='Payé'").fetchone()[0]
    conn.close()

    benefice = ca - total_dep - total_paie

    # KPIs row 1
    cols = st.columns(4)
    kpis = [
        ("📦", total_liv,  "Livraisons totales", "#1a9bd7"),
        ("✅", livrees,    "Livrées",             "#27ae60"),
        ("🔄", en_transit, "En transit",          "#f39c12"),
        ("⏳", en_attente, "En attente",          "#95a5a6"),
    ]
    for col, (icon, val, label, color) in zip(cols, kpis):
        with col:
            st.markdown(kpi_card(icon, val, label, color), unsafe_allow_html=True)

    cols2 = st.columns(4)
    kpis2 = [
        ("💶", f"{ca:,.0f} $",        "CA HT livré",         "#27ae60"),
        ("🔧", f"{total_dep:,.0f} $",  "Dépenses véhicules",  "#e74c3c"),
        ("💰", f"{total_paie:,.0f} $", "Paiements chauffeurs","#f39c12"),
        ("📈", f"{benefice:,.0f} $",   "Bénéfice net estimé", "#27ae60" if benefice >= 0 else "#e74c3c"),
    ]
    for col, (icon, val, label, color) in zip(cols2, kpis2):
        with col:
            st.markdown(kpi_card(icon, val, label, color), unsafe_allow_html=True)

    st.divider()

    # Graphiques
    col_a, col_b = st.columns(2)

    with col_a:
        section("Répartition des statuts livraisons")
        df_stat = query("SELECT statut, COUNT(*) as nb FROM livraisons GROUP BY statut")
        if not df_stat.empty:
            st.bar_chart(df_stat.set_index("statut")["nb"])

    with col_b:
        section("Dépenses par type (véhicules)")
        df_dep_type = query("SELECT type_depense, SUM(montant) as total FROM depenses_vehicules GROUP BY type_depense ORDER BY total DESC")
        if not df_dep_type.empty:
            st.bar_chart(df_dep_type.set_index("type_depense")["total"])

    col_c, col_d = st.columns(2)
    with col_c:
        section("Chiffre d'affaires par client")
        df_ca = query("""
            SELECT c.nom, COALESCE(SUM(l.prix_ht),0) as ca
            FROM clients c LEFT JOIN livraisons l ON l.client_id=c.id AND l.statut='Livré'
            GROUP BY c.nom ORDER BY ca DESC
        """)
        if not df_ca.empty:
            st.bar_chart(df_ca.set_index("nom")["ca"])

    with col_d:
        section("Paiements par chauffeur")
        df_pay = query("""
            SELECT ch.nom||' '||ch.prenom as chauffeur, SUM(p.montant) as total
            FROM paiements_chauffeurs p
            JOIN chauffeurs ch ON ch.id=p.chauffeur_id
            GROUP BY ch.id ORDER BY total DESC
        """)
        if not df_pay.empty:
            st.bar_chart(df_pay.set_index("chauffeur")["total"])

    section("Dernières livraisons")
    df_liv = query("""
        SELECT l.reference as "Réf.", c.nom as "Client",
               l.origine as "Origine", l.destination as "Destination",
               l.poids_kg as "Poids (kg)", l.prix_ht as "Prix HT €",
               l.statut as "Statut", l.date_depart as "Départ"
        FROM livraisons l LEFT JOIN clients c ON c.id=l.client_id
        ORDER BY l.created_at DESC LIMIT 10
    """)
    st.dataframe(df_liv, use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────
#  PAGE : LIVRAISONS
# ─────────────────────────────────────────────

elif "Livraisons" in page:
    st.markdown("# 📦 Gestion des Livraisons")
    st.divider()

    tab_list, tab_new, tab_edit, tab_status = st.tabs([
        "📋 Liste", "➕ Nouvelle livraison", "✏️ Modifier", "🔄 Changer statut"
    ])

    # Listes FK
    clients_df    = query("SELECT id, nom FROM clients ORDER BY nom")
    chauffeurs_df = query("SELECT id, nom || ' ' || prenom AS nom FROM chauffeurs WHERE statut=? ORDER BY nom", params=("Disponible",))
    vehicules_df  = query("SELECT id, immatriculation FROM vehicules  WHERE statut=? ORDER BY immatriculation", params=("Disponible",))

    clients_map    = dict(zip(clients_df["nom"],    clients_df["id"]))
    chauffeurs_map = dict(zip(chauffeurs_df["nom"], chauffeurs_df["id"]))
    vehicules_map  = dict(zip(vehicules_df["immatriculation"], vehicules_df["id"]))

    with tab_list:
        df = query("""
            SELECT l.reference as "Référence",
                   COALESCE(c.nom,'—') as "Client",
                   COALESCE(ch.nom||' '||ch.prenom,'—') as "Chauffeur",
                   COALESCE(v.immatriculation,'—') as "Véhicule",
                   l.origine as "Origine", l.destination as "Destination",
                   l.poids_kg as "Poids (kg)", l.prix_ht as "Prix HT €",
                   l.statut as "Statut", l.date_depart as "Départ", l.date_livraison as "Livraison"
            FROM livraisons l
            LEFT JOIN clients    c  ON c.id  = l.client_id
            LEFT JOIN chauffeurs ch ON ch.id = l.chauffeur_id
            LEFT JOIN vehicules  v  ON v.id  = l.vehicule_id
            ORDER BY l.created_at DESC
        """)

        # Filtres
        fc1, fc2 = st.columns(2)
        with fc1:
            filtre_statut = st.selectbox("Filtrer par statut", ["Tous","En attente","En transit","Livré","Annulé"])
        with fc2:
            filtre_client = st.selectbox("Filtrer par client", ["Tous"] + list(clients_map.keys()))

        if filtre_statut != "Tous":
            df = df[df["Statut"] == filtre_statut]
        if filtre_client != "Tous":
            df = df[df["Client"] == filtre_client]

        st.dataframe(df, use_container_width=True, hide_index=True)
        st.caption(f"{len(df)} livraison(s) affichée(s)")

    with tab_new:
        section("Créer une nouvelle livraison")
        with st.form("form_new_liv"):
            c1, c2 = st.columns(2)
            with c1:
                ref      = st.text_input("Référence", value=unique_ref())
                client   = st.selectbox("Client",    list(clients_map.keys()))
                chauff   = st.selectbox("Chauffeur", list(chauffeurs_map.keys()))
                vehicule = st.selectbox("Véhicule",  list(vehicules_map.keys()))
                statut   = st.selectbox("Statut",    ["En attente","En transit","Livré","Annulé"])
            with c2:
                origine     = st.text_input("Ville d'origine")
                destination = st.text_input("Ville de destination")
                poids       = st.number_input("Poids (kg)", min_value=0.0, step=100.0)
                prix        = st.number_input("Prix HT ($)", min_value=0.0, step=10.0)
                d_depart    = st.date_input("Date de départ",    value=date.today())
                d_livraison = st.date_input("Date de livraison", value=date.today())
            notes = st.text_area("Notes")
            submitted = st.form_submit_button("💾 Enregistrer la livraison")
            if submitted:
                try:
                    execute("""INSERT INTO livraisons
                        (reference,client_id,chauffeur_id,vehicule_id,origine,destination,
                         poids_kg,prix_ht,statut,date_depart,date_livraison,notes)
                        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                        (ref, clients_map[client], chauffeurs_map[chauff],
                         vehicules_map[vehicule], origine, destination,
                         poids, prix, statut,
                         d_depart.isoformat(), d_livraison.isoformat(), notes))
                    st.success(f"✅ Livraison **{ref}** créée avec succès !")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erreur : {e}")

    with tab_edit:
        section("Modifier une livraison existante")
        livs_df = query("SELECT reference FROM livraisons ORDER BY created_at DESC")
        if livs_df.empty:
            st.info("Aucune livraison disponible.")
        else:
            ref_sel = st.selectbox("Sélectionner la référence", livs_df["reference"].tolist())
            row = query("SELECT * FROM livraisons WHERE reference=?", params=(ref_sel,))
            if not row.empty:
                r = row.iloc[0]
                with st.form("form_edit_liv"):
                    c1, c2 = st.columns(2)

                    def idx(lst, val):
                        try: return list(lst).index(val)
                        except: return 0

                    # Retrouver noms depuis ids
                    def get_name(df, id_col, id_val, name_col):
                        res = df[df["id"] == id_val]
                        return res[name_col].iloc[0] if not res.empty else None

                    cl_name = get_name(clients_df,    "id", r["client_id"],    "nom") or list(clients_map.keys())[0]
                    ch_name = get_name(chauffeurs_df, "id", r["chauffeur_id"], "nom") or list(chauffeurs_map.keys())[0]
                    vh_name = get_name(vehicules_df,  "id", r["vehicule_id"],  "immatriculation") or list(vehicules_map.keys())[0]

                    with c1:
                        client   = st.selectbox("Client",    list(clients_map.keys()),    index=idx(clients_map.keys(), cl_name))
                        chauff   = st.selectbox("Chauffeur", list(chauffeurs_map.keys()), index=idx(chauffeurs_map.keys(), ch_name))
                        vehicule = st.selectbox("Véhicule",  list(vehicules_map.keys()),  index=idx(vehicules_map.keys(), vh_name))
                        statuts  = ["En attente","En transit","Livré","Annulé"]
                        statut   = st.selectbox("Statut", statuts, index=idx(statuts, r["statut"]))
                    with c2:
                        origine     = st.text_input("Origine",     value=r["origine"] or "")
                        destination = st.text_input("Destination", value=r["destination"] or "")
                        poids       = st.number_input("Poids (kg)",    value=float(r["poids_kg"] or 0), step=100.0)
                        prix        = st.number_input("Prix HT ($)",   value=float(r["prix_ht"] or 0), step=10.0)
                        try:
                            d_dep = date.fromisoformat(r["date_depart"]) if r["date_depart"] else date.today()
                            d_liv = date.fromisoformat(r["date_livraison"]) if r["date_livraison"] else date.today()
                        except:
                            d_dep = d_liv = date.today()
                        d_depart    = st.date_input("Date de départ",    value=d_dep)
                        d_livraison = st.date_input("Date de livraison", value=d_liv)
                    notes = st.text_area("Notes", value=r["notes"] or "")
                    if st.form_submit_button("💾 Mettre à jour"):
                        execute("""UPDATE livraisons SET client_id=?,chauffeur_id=?,vehicule_id=?,
                            origine=?,destination=?,poids_kg=?,prix_ht=?,statut=?,
                            date_depart=?,date_livraison=?,notes=? WHERE reference=?""",
                            (clients_map[client], chauffeurs_map[chauff], vehicules_map[vehicule],
                             origine, destination, poids, prix, statut,
                             d_depart.isoformat(), d_livraison.isoformat(), notes, ref_sel))
                        st.success("✅ Livraison mise à jour !")
                        st.rerun()

                if st.button("🗑️ Supprimer cette livraison", type="secondary"):
                    execute("DELETE FROM livraisons WHERE reference=?", (ref_sel,))
                    st.success("Livraison supprimée.")
                    st.rerun()

    with tab_status:
        section("Mise à jour rapide du statut")
        livs_df2 = query("""
            SELECT l.reference, COALESCE(c.nom,'—') as client, l.statut
            FROM livraisons l LEFT JOIN clients c ON c.id=l.client_id
            ORDER BY l.created_at DESC
        """)
        if livs_df2.empty:
            st.info("Aucune livraison.")
        else:
            ref_s = st.selectbox("Livraison", livs_df2["reference"].tolist())
            cur_stat = livs_df2[livs_df2["reference"] == ref_s]["statut"].iloc[0]
            st.markdown(f"Statut actuel : {badge(cur_stat)}", unsafe_allow_html=True)
            new_stat = st.radio("Nouveau statut", ["En attente","En transit","Livré","Annulé"],
                                index=["En attente","En transit","Livré","Annulé"].index(cur_stat)
                                if cur_stat in ["En attente","En transit","Livré","Annulé"] else 0)
            if st.button("🔄 Appliquer le changement"):
                execute("UPDATE livraisons SET statut=? WHERE reference=?", (new_stat, ref_s))
                st.success(f"Statut mis à jour → **{new_stat}**")
                st.rerun()

# ─────────────────────────────────────────────
#  PAGE : CLIENTS
# ─────────────────────────────────────────────

elif "Clients" in page:
    st.markdown("# 👤 Gestion des Clients")
    st.divider()

    tab_list, tab_new, tab_edit = st.tabs(["📋 Liste", "➕ Nouveau client", "✏️ Modifier / Supprimer"])

    with tab_list:
        df = query("SELECT id as ID, nom as Nom, adresse as Adresse, telephone as Téléphone, email as Email FROM clients ORDER BY nom")
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.caption(f"{len(df)} client(s)")

    with tab_new:
        section("Ajouter un client")
        with st.form("form_new_client"):
            nom       = st.text_input("Nom / Raison sociale *")
            adresse   = st.text_input("Adresse")
            telephone = st.text_input("Téléphone")
            email     = st.text_input("Email")
            if st.form_submit_button("💾 Ajouter"):
                if not nom:
                    st.error("Le nom est obligatoire.")
                else:
                    execute("INSERT INTO clients (nom,adresse,telephone,email) VALUES (?,?,?,?)",
                            (nom, adresse, telephone, email))
                    st.success(f"✅ Client **{nom}** ajouté !")
                    st.rerun()

    with tab_edit:
        section("Modifier ou supprimer un client")
        clients_df = query("SELECT id, nom FROM clients ORDER BY nom")
        if clients_df.empty:
            st.info("Aucun client.")
        else:
            sel = st.selectbox("Sélectionner", clients_df["nom"].tolist())
            row = query("SELECT * FROM clients WHERE nom=?", params=(sel,))
            if not row.empty:
                r = row.iloc[0]
                with st.form("form_edit_client"):
                    nom       = st.text_input("Nom",       value=r["nom"])
                    adresse   = st.text_input("Adresse",   value=r["adresse"] or "")
                    telephone = st.text_input("Téléphone", value=r["telephone"] or "")
                    email     = st.text_input("Email",     value=r["email"] or "")
                    if st.form_submit_button("💾 Mettre à jour"):
                        execute("UPDATE clients SET nom=?,adresse=?,telephone=?,email=? WHERE id=?",
                                (nom, adresse, telephone, email, r["id"]))
                        st.success("✅ Client mis à jour !")
                        st.rerun()
                if st.button("🗑️ Supprimer ce client"):
                    execute("DELETE FROM clients WHERE id=?", (r["id"],))
                    st.success("Client supprimé.")
                    st.rerun()

# ─────────────────────────────────────────────
#  PAGE : CHAUFFEURS
# ─────────────────────────────────────────────

elif "Chauffeurs" in page:
    st.markdown("# 🧑‍✈️ Gestion des Chauffeurs")
    st.divider()

    tab_list, tab_new, tab_edit = st.tabs(["📋 Liste", "➕ Nouveau chauffeur", "✏️ Modifier / Supprimer"])

    with tab_list:
        df = query("""SELECT id as ID, nom as Nom, prenom as Prénom, permis as Permis,
                             telephone as Téléphone, statut as Statut
                      FROM chauffeurs ORDER BY nom""")
        st.dataframe(df, use_container_width=True, hide_index=True)

        # Disponibilités visuelles
        st.divider()
        section("Disponibilité en temps réel")
        disp = query("SELECT nom||' '||prenom as nom, statut FROM chauffeurs ORDER BY nom")
        cols = st.columns(len(disp))
        for col, (_, row) in zip(cols, disp.iterrows()):
            with col:
                st.markdown(f"**{row['nom']}**<br>{badge(row['statut'])}", unsafe_allow_html=True)

    with tab_new:
        section("Ajouter un chauffeur")
        with st.form("form_new_chauffeur"):
            c1, c2 = st.columns(2)
            with c1:
                nom    = st.text_input("Nom *")
                prenom = st.text_input("Prénom *")
                permis = st.text_input("Catégorie permis")
            with c2:
                telephone = st.text_input("Téléphone")
                statut    = st.selectbox("Statut", ["Disponible","En mission","Absent"])
            if st.form_submit_button("💾 Ajouter"):
                if not nom or not prenom:
                    st.error("Nom et prénom obligatoires.")
                else:
                    execute("INSERT INTO chauffeurs (nom,prenom,permis,telephone,statut) VALUES (?,?,?,?,?)",
                            (nom, prenom, permis, telephone, statut))
                    st.success(f"✅ Chauffeur **{nom} {prenom}** ajouté !")
                    st.rerun()

    with tab_edit:
        section("Modifier ou supprimer un chauffeur")
    
        # Charger la liste des chauffeurs
        df_ch = query("SELECT id, nom, prenom FROM chauffeurs ORDER BY nom")
    
        if df_ch.empty:
            st.info("Aucun chauffeur.")
        else:
            # Création d'un label unique pour éviter les doublons
            df_ch["label"] = df_ch.apply(
                lambda r: f"{r['nom']} {r['prenom']}  (ID={r['id']})",
                axis=1
            )
    
            # Sélection du chauffeur
            sel = st.selectbox("Sélectionner un chauffeur :", df_ch["label"].tolist())
    
            # Extraire l'ID du chauffeur à partir du label
            cid = int(sel.split("ID=")[1].replace(")", ""))
    
            # Vérification et récupération des données complètes
            row = query("SELECT * FROM chauffeurs WHERE id=?", params=(cid,))
    
            if row.empty:
                st.error("❌ Chauffeur introuvable dans la base.")
            else:
                r = row.iloc[0]
    
                # ----- FORMULAIRE DE MISE À JOUR -----
                with st.form("form_edit_chauffeur"):
                    c1, c2 = st.columns(2)
    
                    with c1:
                        nom    = st.text_input("Nom",    value=r["nom"])
                        prenom = st.text_input("Prénom", value=r["prenom"])
                        permis = st.text_input("Permis", value=r.get("permis", "") or "")
    
                    with c2:
                        telephone = st.text_input("Téléphone", value=r.get("telephone", "") or "")
                        statuts   = ["Disponible", "En mission", "Absent"]
    
                        statut = st.selectbox(
                            "Statut",
                            statuts,
                            index=statuts.index(r["statut"]) if r["statut"] in statuts else 0
                        )
    
                    # --------- BOUTON MAJ ---------
                    if st.form_submit_button("💾 Mettre à jour le chauffeur"):
                        execute("""
                            UPDATE chauffeurs 
                            SET nom=?, prenom=?, permis=?, telephone=?, statut=? 
                            WHERE id=?
                        """, (nom, prenom, permis, telephone, statut, cid))
    
                        st.success("✅ Chauffeur mis à jour !")
                        st.rerun()
    
                # --------- BOUTON SUPPRESSION ---------
                if st.button("🗑️ Supprimer ce chauffeur"):
                    execute("DELETE FROM chauffeurs WHERE id=?", (cid,))
                    st.success("🚮 Chauffeur supprimé.")
                    st.rerun()

# ─────────────────────────────────────────────
#  PAGE : VÉHICULES
# ─────────────────────────────────────────────

elif "Véhicules" in page:
    st.markdown("# 🚗 Flotte de Véhicules")
    st.divider()

    tab_list, tab_new, tab_edit = st.tabs(["📋 Flotte", "➕ Nouveau véhicule", "✏️ Modifier / Supprimer"])

    with tab_list:
        df = query("""SELECT id as ID, immatriculation as Immatriculation,
                             marque as Marque, modele as Modèle,
                             capacite_kg as "Capacité (kg)", date_entretien as "Date Entretien", statut as Statut
                      FROM vehicules ORDER BY immatriculation""")
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.divider()
        section("Statut de la flotte")
        veh = query("SELECT immatriculation, marque, modele, statut FROM vehicules ORDER BY statut")
        cols = st.columns(min(len(veh), 4))
        for i, (_, row) in enumerate(veh.iterrows()):
            with cols[i % len(cols)]:
                st.markdown(
                    f"**{row['immatriculation']}**<br>{row['marque']} {row['modele']}<br>{badge(row['statut'])}",
                    unsafe_allow_html=True)
                st.write("")

    with tab_new:
        section("Ajouter un véhicule")
        with st.form("form_new_veh"):
            c1, c2 = st.columns(2)
            with c1:
                immat  = st.text_input("Immatriculation *")
                marque = st.text_input("Marque")
                modele = st.text_input("Modèle")
            with c2:
                capacite = st.number_input("Capacité (kg)", min_value=0.0, step=500.0)
                dtentretien = st.text_input("date_entretien")
                statut   = st.selectbox("Statut", ["Disponible","En mission","En maintenance"])
            if st.form_submit_button("💾 Ajouter"):
                if not immat:
                    st.error("L'immatriculation est obligatoire.")
                else:
                    try:
                        execute("INSERT INTO vehicules (immatriculation,marque,modele,capacite_kg,dtentretien,statut) VALUES (?,?,?,?,?)",
                                (immat, marque, modele, capacite,date_entretien ,statut))
                        st.success(f"✅ Véhicule **{immat}** ajouté !")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erreur : {e}")

    with tab_edit:
        section("Modifier ou supprimer un véhicule")
    
        # Charger la liste des véhicules
        veh_df = query("SELECT id, immatriculation FROM vehicules ORDER BY immatriculation")
    
        if veh_df.empty:
            st.info("Aucun véhicule.")
        else:
            # Generer un label unique pour chaque véhicule
            veh_df["label"] = veh_df.apply(
                lambda r: f"{r['immatriculation']} (ID={r['id']})",
                axis=1
            )
    
            # Selection du véhicule
            sel = st.selectbox("Sélectionner un véhicule :", veh_df["label"].tolist())
    
            # Extraction de l'ID à partir du label
            vid = int(sel.split("ID=")[1].replace(")", ""))
    
            # Récupération des données complètes du véhicule
            row = query("SELECT * FROM vehicules WHERE id=?", params=(vid,))
    
            if row.empty:
                st.error("❌ Véhicule introuvable dans la base.")
            else:
                r = row.iloc[0]
    
                # -------- FORMULAIRE DE MISE À JOUR --------
                with st.form("form_edit_veh"):
                    c1, c2 = st.columns(2)
    
                    with c1:
                        immat  = st.text_input("Immatriculation", value=r["immatriculation"])
                        marque = st.text_input("Marque", value=r.get("marque", "") or "")
                        modele = st.text_input("Modèle", value=r.get("modele", "") or "")
    
                    with c2:
                        capacite = st.number_input(
                            "Capacité (kg)",
                            value=float(r.get("capacite_kg", 0) or 0),
                            step=500.0
                        )
    
                        statuts = ["Disponible", "En mission", "En maintenance"]
                        statut = st.selectbox(
                            "Statut",
                            statuts,
                            index=statuts.index(r["statut"]) if r["statut"] in statuts else 0
                        )
    
                    # ------- BOUTON MISE À JOUR -------
                    if st.form_submit_button("💾 Mettre à jour le véhicule"):
                        execute("""
                            UPDATE vehicules
                            SET immatriculation=?, marque=?, modele=?, capacite_kg=?, statut=?
                            WHERE id=?
                        """, (immat, marque, modele, capacite, statut, vid))
    
                        st.success("✅ Véhicule mis à jour !")
                        st.rerun()
    
                # ------- SUPPRESSION -------
                if st.button("🗑️ Supprimer ce véhicule"):
                    execute("DELETE FROM vehicules WHERE id=?", (vid,))
                    st.success("🚮 Véhicule supprimé.")
                    st.rerun()
# ─────────────────────────────────────────────
#  PAGE : DÉPENSES VÉHICULES
# ─────────────────────────────────────────────

elif "Dépenses" in page:
    st.markdown("# 🔧 Dépenses Véhicules")
    st.divider()

    # KPIs résumé
    conn = get_conn(); c = conn.cursor()
    total_dep    = c.execute("SELECT COALESCE(SUM(montant),0) FROM depenses_vehicules").fetchone()[0]
    dep_carbu    = c.execute("SELECT COALESCE(SUM(montant),0) FROM depenses_vehicules WHERE type_depense='Carburant'").fetchone()[0]
    dep_entret   = c.execute("SELECT COALESCE(SUM(montant),0) FROM depenses_vehicules WHERE type_depense='Entretien'").fetchone()[0]
    dep_rep      = c.execute("SELECT COALESCE(SUM(montant),0) FROM depenses_vehicules WHERE type_depense='Réparation'").fetchone()[0]
    conn.close()

    k1, k2, k3, k4 = st.columns(4)
    with k1: st.markdown(kpi_card("💶", f"{total_dep:,.0f} €", "Total dépenses", "#e74c3c"), unsafe_allow_html=True)
    with k2: st.markdown(kpi_card("⛽", f"{dep_carbu:,.0f} €", "Carburant",      "#f39c12"), unsafe_allow_html=True)
    with k3: st.markdown(kpi_card("🔩", f"{dep_entret:,.0f} €","Entretien",      "#1a9bd7"), unsafe_allow_html=True)
    with k4: st.markdown(kpi_card("🛠️", f"{dep_rep:,.0f} €",   "Réparations",    "#e74c3c"), unsafe_allow_html=True)

    st.divider()

    tab_list, tab_new, tab_edit = st.tabs(["📋 Historique", "➕ Nouvelle dépense", "✏️ Modifier / Supprimer"])

    veh_df2 = query("SELECT id, immatriculation FROM vehicules ORDER BY immatriculation")
    veh_map2 = dict(zip(veh_df2["immatriculation"], veh_df2["id"]))

    TYPES_DEP = ["Carburant", "Entretien", "Réparation", "Pneumatiques", "Lavage", "Péage", "Assurance", "Autre"]

    with tab_list:
        # Filtres
        f1, f2 = st.columns(2)
        with f1:
            filtre_veh = st.selectbox("Filtrer par véhicule", ["Tous"] + list(veh_map2.keys()))
        with f2:
            filtre_type = st.selectbox("Filtrer par type", ["Tous"] + TYPES_DEP)

        sql = """
            SELECT d.id, v.immatriculation as "Véhicule", d.type_depense as "Type",
                   d.montant as "Montant (€)", d.date_depense as "Date",
                   d.kilometrage as "Km", d.fournisseur as "Fournisseur",
                   d.description as "Description"
            FROM depenses_vehicules d
            LEFT JOIN vehicules v ON v.id = d.vehicule_id
            WHERE 1=1
        """
        params = []
        if filtre_veh != "Tous":
            sql += " AND v.immatriculation=?"
            params.append(filtre_veh)
        if filtre_type != "Tous":
            sql += " AND d.type_depense=?"
            params.append(filtre_type)
        sql += " ORDER BY d.date_depense DESC"

        df_dep = query(sql, params=tuple(params))
        st.dataframe(df_dep.drop(columns=["id"]), use_container_width=True, hide_index=True)

        total_filtre = df_dep["Montant (€)"].sum() if not df_dep.empty else 0
        st.caption(f"**Total affiché : {total_filtre:,.2f} €** — {len(df_dep)} enregistrement(s)")

        st.divider()
        section("Dépenses par véhicule")
        df_par_veh = query("""
            SELECT v.immatriculation, d.type_depense, SUM(d.montant) as total
            FROM depenses_vehicules d JOIN vehicules v ON v.id=d.vehicule_id
            GROUP BY v.immatriculation, d.type_depense ORDER BY v.immatriculation
        """)
        if not df_par_veh.empty:
            pivot = df_par_veh.pivot_table(index="immatriculation", columns="type_depense",
                                            values="total", fill_value=0)
            st.bar_chart(pivot)

    with tab_new:
        section("Enregistrer une dépense")
        with st.form("form_new_dep"):
            c1, c2 = st.columns(2)
            with c1:
                veh_sel    = st.selectbox("Véhicule *", list(veh_map2.keys()))
                type_dep   = st.selectbox("Type de dépense *", TYPES_DEP)
                montant    = st.number_input("Montant (€) *", min_value=0.0, step=1.0)
                date_dep   = st.date_input("Date *", value=date.today())
            with c2:
                kilometrage  = st.number_input("Kilométrage", min_value=0.0, step=100.0)
                fournisseur  = st.text_input("Fournisseur / Garage")
                description  = st.text_area("Description / Notes")
            if st.form_submit_button("💾 Enregistrer la dépense"):
                if montant <= 0:
                    st.error("Le montant doit être supérieur à 0.")
                else:
                    execute("""INSERT INTO depenses_vehicules
                        (vehicule_id,type_depense,montant,date_depense,kilometrage,fournisseur,description)
                        VALUES (?,?,?,?,?,?,?)""",
                        (veh_map2[veh_sel], type_dep, montant,
                         date_dep.isoformat(), kilometrage or None,
                         fournisseur, description))
                    st.success(f"✅ Dépense de **{montant:.2f} €** ({type_dep}) enregistrée !")
                    st.rerun()

    with tab_edit:
        section("Modifier ou supprimer une dépense")
        df_all_dep = query("""
            SELECT d.id, v.immatriculation||' — '||d.type_depense||' — '||d.date_depense||' ('||d.montant||'€)' as label
            FROM depenses_vehicules d LEFT JOIN vehicules v ON v.id=d.vehicule_id
            ORDER BY d.date_depense DESC
        """)
        if df_all_dep.empty:
            st.info("Aucune dépense enregistrée.")
        else:
            sel_label = st.selectbox("Sélectionner", df_all_dep["label"].tolist())
            dep_id    = df_all_dep[df_all_dep["label"] == sel_label]["id"].iloc[0]
            row       = query("SELECT * FROM depenses_vehicules WHERE id=?", params=(dep_id,))
            if not row.empty:
                r = row.iloc[0]
                with st.form("form_edit_dep"):
                    c1, c2 = st.columns(2)
                    veh_names = list(veh_map2.keys())
                    cur_veh   = query("SELECT immatriculation FROM vehicules WHERE id=?", params=(r["vehicule_id"],))
                    cur_veh_n = cur_veh["immatriculation"].iloc[0] if not cur_veh.empty else veh_names[0]
                    with c1:
                        veh_sel   = st.selectbox("Véhicule", veh_names,
                                                  index=veh_names.index(cur_veh_n) if cur_veh_n in veh_names else 0)
                        type_dep  = st.selectbox("Type", TYPES_DEP,
                                                  index=TYPES_DEP.index(r["type_depense"]) if r["type_depense"] in TYPES_DEP else 0)
                        montant   = st.number_input("Montant (€)", value=float(r["montant"]), step=1.0)
                        try:    date_dep = st.date_input("Date", value=date.fromisoformat(r["date_depense"]))
                        except: date_dep = st.date_input("Date", value=date.today())
                    with c2:
                        kilometrage = st.number_input("Kilométrage", value=float(r["kilometrage"] or 0), step=100.0)
                        fournisseur = st.text_input("Fournisseur", value=r["fournisseur"] or "")
                        description = st.text_area("Description",  value=r["description"] or "")
                    if st.form_submit_button("💾 Mettre à jour"):
                        execute("""UPDATE depenses_vehicules SET vehicule_id=?,type_depense=?,montant=?,
                            date_depense=?,kilometrage=?,fournisseur=?,description=? WHERE id=?""",
                            (veh_map2[veh_sel], type_dep, montant, date_dep.isoformat(),
                             kilometrage or None, fournisseur, description, dep_id))
                        st.success("✅ Dépense mise à jour !")
                        st.rerun()
                if st.button("🗑️ Supprimer cette dépense"):
                    execute("DELETE FROM depenses_vehicules WHERE id=?", (dep_id,))
                    st.success("Dépense supprimée.")
                    st.rerun()

# ─────────────────────────────────────────────
#  PAGE : PAIEMENTS CHAUFFEURS
# ─────────────────────────────────────────────

elif "Paiements" in page:
    st.markdown("# 💰 Paiements Chauffeurs")
    st.divider()

    # KPIs
    conn = get_conn(); c = conn.cursor()
    total_pay   = c.execute("SELECT COALESCE(SUM(montant),0) FROM paiements_chauffeurs").fetchone()[0]
    pay_salaire = c.execute("SELECT COALESCE(SUM(montant),0) FROM paiements_chauffeurs WHERE type_paiement='Salaire mensuel'").fetchone()[0]
    pay_prime   = c.execute("SELECT COALESCE(SUM(montant),0) FROM paiements_chauffeurs WHERE type_paiement='Prime mission'").fetchone()[0]
    en_attente_p= c.execute("SELECT COALESCE(SUM(montant),0) FROM paiements_chauffeurs WHERE statut='En attente'").fetchone()[0]
    conn.close()

    k1, k2, k3, k4 = st.columns(4)
    with k1: st.markdown(kpi_card("💶", f"{total_pay:,.0f} €",   "Total versé",      "#f39c12"), unsafe_allow_html=True)
    with k2: st.markdown(kpi_card("🧾", f"{pay_salaire:,.0f} €", "Salaires",          "#1a9bd7"), unsafe_allow_html=True)
    with k3: st.markdown(kpi_card("⭐", f"{pay_prime:,.0f} €",   "Primes & bonus",    "#27ae60"), unsafe_allow_html=True)
    with k4: st.markdown(kpi_card("⏳", f"{en_attente_p:,.0f} €","En attente paiement","#e74c3c"), unsafe_allow_html=True)

    st.divider()

    tab_list, tab_new, tab_edit, tab_recap = st.tabs([
        "📋 Historique", "➕ Nouveau paiement", "✏️ Modifier / Supprimer", "📊 Récapitulatif"
    ])

    chauff_df2 = query("SELECT id, nom||' '||prenom as nom FROM chauffeurs ORDER BY nom")
    chauff_map2 = dict(zip(chauff_df2["nom"], chauff_df2["id"]))

    TYPES_PAY = ["Salaire mensuel", "Prime mission", "Avance", "Remboursement frais",
                 "Heures supplémentaires", "Indemnité", "Autre"]

    with tab_list:
        f1, f2, f3 = st.columns(3)
        with f1: filtre_ch   = st.selectbox("Chauffeur",    ["Tous"] + list(chauff_map2.keys()))
        with f2: filtre_tp   = st.selectbox("Type",         ["Tous"] + TYPES_PAY)
        with f3: filtre_stat = st.selectbox("Statut paiement", ["Tous", "Payé", "En attente", "Annulé"])

        sql = """
            SELECT p.id, ch.nom||' '||ch.prenom as "Chauffeur",
                   p.type_paiement as "Type", p.montant as "Montant (€)",
                   p.date_paiement as "Date", p.periode as "Période",
                   p.statut as "Statut", p.notes as "Notes"
            FROM paiements_chauffeurs p
            LEFT JOIN chauffeurs ch ON ch.id = p.chauffeur_id
            WHERE 1=1
        """
        params = []
        if filtre_ch != "Tous":
            sql += " AND ch.nom||' '||ch.prenom=?"
            params.append(filtre_ch)
        if filtre_tp != "Tous":
            sql += " AND p.type_paiement=?"
            params.append(filtre_tp)
        if filtre_stat != "Tous":
            sql += " AND p.statut=?"
            params.append(filtre_stat)
        sql += " ORDER BY p.date_paiement DESC"

        df_pay_list = query(sql, params=tuple(params))
        st.dataframe(df_pay_list.drop(columns=["id"]), use_container_width=True, hide_index=True)
        total_filtre = df_pay_list["Montant (€)"].sum() if not df_pay_list.empty else 0
        st.caption(f"**Total affiché : {total_filtre:,.2f} €** — {len(df_pay_list)} enregistrement(s)")

    with tab_new:
        section("Enregistrer un paiement")
        with st.form("form_new_pay"):
            c1, c2 = st.columns(2)
            livs_list = query("SELECT id, reference FROM livraisons ORDER BY created_at DESC")
            livs_options = ["— Aucune —"] + livs_list["reference"].tolist()
            with c1:
                chauff_sel   = st.selectbox("Chauffeur *", list(chauff_map2.keys()))
                type_pay     = st.selectbox("Type de paiement *", TYPES_PAY)
                montant_p    = st.number_input("Montant (€) *", min_value=0.0, step=10.0)
                date_pay     = st.date_input("Date de paiement *", value=date.today())
            with c2:
                periode      = st.text_input("Période (ex: Janvier 2024)")
                liv_ref      = st.selectbox("Livraison associée (optionnel)", livs_options)
                statut_p     = st.selectbox("Statut", ["Payé", "En attente", "Annulé"])
                notes_p      = st.text_area("Notes")
            if st.form_submit_button("💾 Enregistrer le paiement"):
                if montant_p <= 0:
                    st.error("Le montant doit être supérieur à 0.")
                else:
                    liv_id = None
                    if liv_ref != "— Aucune —" and not livs_list.empty:
                        lv = livs_list[livs_list["reference"] == liv_ref]
                        liv_id = int(lv["id"].iloc[0]) if not lv.empty else None
                    execute("""INSERT INTO paiements_chauffeurs
                        (chauffeur_id,type_paiement,montant,date_paiement,periode,livraison_id,statut,notes)
                        VALUES (?,?,?,?,?,?,?,?)""",
                        (chauff_map2[chauff_sel], type_pay, montant_p,
                         date_pay.isoformat(), periode, liv_id, statut_p, notes_p))
                    st.success(f"✅ Paiement de **{montant_p:.2f} €** enregistré pour **{chauff_sel}** !")
                    st.rerun()
                    
    with tab_edit:
        section("Modifier ou supprimer un paiement")
    
        # Charger la liste complète des paiements
        df_all_pay = query("""
            SELECT 
                p.id,
                ch.nom || ' ' || ch.prenom || ' — ' || p.type_paiement || 
                ' — ' || p.date_paiement || ' (' || p.montant || '€)' AS label
            FROM paiements_chauffeurs p
            LEFT JOIN chauffeurs ch ON ch.id = p.chauffeur_id
            ORDER BY p.date_paiement DESC
        """)
    
        if df_all_pay.empty:
            st.info("Aucun paiement enregistré.")
        else:
    
            # Création d’un label unique
            df_all_pay["label"] = df_all_pay.apply(
                lambda r: f"{r['label']}  (ID={r['id']})",
                axis=1
            )
    
            # Sélection dans liste déroulante
            sel_label_p = st.selectbox("Sélectionner un paiement :", df_all_pay["label"].tolist())
    
            # Extraction de l’ID
            pay_id = int(sel_label_p.split("ID=")[1].replace(")", ""))
    
            # Charger les infos complètes du paiement
            row_p = query("SELECT * FROM paiements_chauffeurs WHERE id=?", params=(pay_id,))
    
            if row_p.empty:
                st.error("❌ Paiement introuvable.")
            else:
                r = row_p.iloc[0]
    
                # Récupérer le chauffeur actuel
                ch_names = list(chauff_map2.keys())
    
                cur_ch = query(
                    "SELECT nom || ' ' || prenom AS nom FROM chauffeurs WHERE id=?",
                    params=(r["chauffeur_id"],)
                )
                cur_ch_n = cur_ch["nom"].iloc[0] if not cur_ch.empty else ch_names[0]
    
                # ---------------- FORMULAIRE ----------------
                with st.form("form_edit_pay"):
                    c1, c2 = st.columns(2)
    
                    with c1:
                        chauff_sel = st.selectbox(
                            "Chauffeur",
                            ch_names,
                            index=ch_names.index(cur_ch_n) if cur_ch_n in ch_names else 0
                        )
    
                        type_pay = st.selectbox(
                            "Type",
                            TYPES_PAY,
                            index=TYPES_PAY.index(r["type_paiement"]) if r["type_paiement"] in TYPES_PAY else 0
                        )
    
                        montant_p = st.number_input(
                            "Montant (€)",
                            value=float(r["montant"]),
                            step=10.0
                        )
    
                        try:
                            date_pay = st.date_input(
                                "Date",
                                value=date.fromisoformat(r["date_paiement"])
                            )
                        except:
                            date_pay = st.date_input("Date", value=date.today())
    
                    with c2:
                        periode = st.text_input("Période", value=r.get("periode", "") or "")
    
                        statuts_p = ["Payé", "En attente", "Annulé"]
                        statut_p = st.selectbox(
                            "Statut",
                            statuts_p,
                            index=statuts_p.index(r["statut"]) if r["statut"] in statuts_p else 0
                        )
    
                        notes_p = st.text_area("Notes", value=r.get("notes", "") or "")
    
                    # -------- MISE À JOUR --------
                    if st.form_submit_button("💾 Mettre à jour"):
                        execute("""
                            UPDATE paiements_chauffeurs 
                            SET chauffeur_id=?, type_paiement=?, montant=?, 
                                date_paiement=?, periode=?, statut=?, notes=?
                            WHERE id=?
                        """, (
                            chauff_map2[chauff_sel], type_pay, montant_p,
                            date_pay.isoformat(), periode, statut_p, notes_p, pay_id
                        ))
    
                        st.success("✅ Paiement mis à jour !")
                        st.rerun()
    
                # -------- SUPPRESSION --------
                if st.button("🗑️ Supprimer ce paiement"):
                    execute("DELETE FROM paiements_chauffeurs WHERE id=?", (pay_id,))
                    st.success("🚮 Paiement supprimé.")
                    st.rerun()
    with tab_recap:
        section("Récapitulatif par chauffeur")
        df_recap = query("""
            SELECT ch.nom||' '||ch.prenom as "Chauffeur",
                   SUM(CASE WHEN p.type_paiement='Salaire mensuel'      THEN p.montant ELSE 0 END) as "Salaires (€)",
                   SUM(CASE WHEN p.type_paiement='Prime mission'        THEN p.montant ELSE 0 END) as "Primes (€)",
                   SUM(CASE WHEN p.type_paiement='Avance'               THEN p.montant ELSE 0 END) as "Avances (€)",
                   SUM(CASE WHEN p.type_paiement='Heures supplémentaires' THEN p.montant ELSE 0 END) as "Heures supp. (€)",
                   SUM(CASE WHEN p.type_paiement='Remboursement frais'  THEN p.montant ELSE 0 END) as "Remboursements (€)",
                   SUM(p.montant) as "TOTAL ($)"
            FROM paiements_chauffeurs p
            JOIN chauffeurs ch ON ch.id=p.chauffeur_id
            WHERE p.statut='Payé'
            GROUP BY ch.id ORDER BY "TOTAL ($)" DESC
        """)
        st.dataframe(df_recap, use_container_width=True, hide_index=True)

        st.divider()
        section("Évolution des paiements dans le temps")
        df_evol = query("""
            SELECT strftime('%Y-%m', date_paiement) as mois,
                   SUM(montant) as total
            FROM paiements_chauffeurs WHERE statut='Payé'
            GROUP BY mois ORDER BY mois
        """)
        if not df_evol.empty:
            st.line_chart(df_evol.set_index("mois")["total"])


