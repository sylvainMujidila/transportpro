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
        capacite_kg REAL, statut TEXT DEFAULT 'Disponible',
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
            ("Dupont","Marc",   "B+CE",    "06 12 34 56 78","Disponible"),
            ("Martin","Sophie", "B+C",     "06 98 76 54 32","Disponible"),
            ("Leroy", "Julien", "B+CE+C1", "07 11 22 33 44","En mission"),
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
    st.markdown('<div class="sidebar-title">🚛 TRANSPORTPRO</div>', unsafe_allow_html=True)
    st.markdown("**Système de gestion**  \nTransport de marchandises", unsafe_allow_html=True)
    st.divider()
    page = st.radio("Navigation", [
        "📊  Tableau de bord",
        "📦  Livraisons",
        "👤  Clients",
        "🧑‍✈️  Chauffeurs",
        "🚗  Véhicules",
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
    conn.close()

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
        ("👤", nb_clients, "Clients",   "#F5A623"),
        ("🧑‍✈️", nb_chauff, "Chauffeurs", "#1a9bd7"),
        ("🚗", nb_vehic,   "Véhicules", "#1a9bd7"),
        ("💶", f"{ca:,.0f} €", "CA HT livré", "#27ae60"),
    ]
    for col, (icon, val, label, color) in zip(cols2, kpis2):
        with col:
            st.markdown(kpi_card(icon, val, label, color), unsafe_allow_html=True)

    st.divider()

    # Graphiques
    col_a, col_b = st.columns(2)

    with col_a:
        section("Répartition des statuts")
        df_stat = query("SELECT statut, COUNT(*) as nb FROM livraisons GROUP BY statut")
        if not df_stat.empty:
            st.bar_chart(df_stat.set_index("statut")["nb"])

    with col_b:
        section("Chiffre d'affaires par client")
        df_ca = query("""
            SELECT c.nom, COALESCE(SUM(l.prix_ht),0) as ca
            FROM clients c LEFT JOIN livraisons l ON l.client_id=c.id AND l.statut='Livré'
            GROUP BY c.nom ORDER BY ca DESC
        """)
        if not df_ca.empty:
            st.bar_chart(df_ca.set_index("nom")["ca"])

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
    chauffeurs_df = query("SELECT id, nom||' '||prenom as nom FROM chauffeurs ORDER BY nom")
    vehicules_df  = query("SELECT id, immatriculation FROM vehicules ORDER BY immatriculation")

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
                prix        = st.number_input("Prix HT (€)", min_value=0.0, step=10.0)
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
                        prix        = st.number_input("Prix HT (€)",   value=float(r["prix_ht"] or 0), step=10.0)
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
        df_ch = query("SELECT id, nom||' '||prenom as nom FROM chauffeurs ORDER BY nom")
        if df_ch.empty:
            st.info("Aucun chauffeur.")
        else:
            sel = st.selectbox("Sélectionner", df_ch["nom"].tolist())
            cid = df_ch[df_ch["nom"] == sel]["id"].iloc[0]
            row = query("SELECT * FROM chauffeurs WHERE id=?", params=(cid,))
            if not row.empty:
                r = row.iloc[0]
                with st.form("form_edit_chauffeur"):
                    c1, c2 = st.columns(2)
                    with c1:
                        nom    = st.text_input("Nom",    value=r["nom"])
                        prenom = st.text_input("Prénom", value=r["prenom"])
                        permis = st.text_input("Permis", value=r["permis"] or "")
                    with c2:
                        telephone = st.text_input("Téléphone", value=r["telephone"] or "")
                        statuts   = ["Disponible","En mission","Absent"]
                        statut    = st.selectbox("Statut", statuts,
                                                  index=statuts.index(r["statut"]) if r["statut"] in statuts else 0)
                    if st.form_submit_button("💾 Mettre à jour"):
                        execute("UPDATE chauffeurs SET nom=?,prenom=?,permis=?,telephone=?,statut=? WHERE id=?",
                                (nom, prenom, permis, telephone, statut, cid))
                        st.success("✅ Chauffeur mis à jour !")
                        st.rerun()
                if st.button("🗑️ Supprimer ce chauffeur"):
                    execute("DELETE FROM chauffeurs WHERE id=?", (cid,))
                    st.success("Chauffeur supprimé.")
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
                             capacite_kg as "Capacité (kg)", statut as Statut
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
                statut   = st.selectbox("Statut", ["Disponible","En mission","En maintenance"])
            if st.form_submit_button("💾 Ajouter"):
                if not immat:
                    st.error("L'immatriculation est obligatoire.")
                else:
                    try:
                        execute("INSERT INTO vehicules (immatriculation,marque,modele,capacite_kg,statut) VALUES (?,?,?,?,?)",
                                (immat, marque, modele, capacite, statut))
                        st.success(f"✅ Véhicule **{immat}** ajouté !")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erreur : {e}")

    with tab_edit:
        section("Modifier ou supprimer un véhicule")
        veh_df = query("SELECT id, immatriculation FROM vehicules ORDER BY immatriculation")
        if veh_df.empty:
            st.info("Aucun véhicule.")
        else:
            sel = st.selectbox("Sélectionner", veh_df["immatriculation"].tolist())
            vid = veh_df[veh_df["immatriculation"] == sel]["id"].iloc[0]
            row = query("SELECT * FROM vehicules WHERE id=?", params=(vid,))
            if not row.empty:
                r = row.iloc[0]
                with st.form("form_edit_veh"):
                    c1, c2 = st.columns(2)
                    with c1:
                        immat  = st.text_input("Immatriculation", value=r["immatriculation"])
                        marque = st.text_input("Marque",          value=r["marque"] or "")
                        modele = st.text_input("Modèle",          value=r["modele"] or "")
                    with c2:
                        capacite = st.number_input("Capacité (kg)", value=float(r["capacite_kg"] or 0), step=500.0)
                        statuts  = ["Disponible","En mission","En maintenance"]
                        statut   = st.selectbox("Statut", statuts,
                                                 index=statuts.index(r["statut"]) if r["statut"] in statuts else 0)
                    if st.form_submit_button("💾 Mettre à jour"):
                        execute("UPDATE vehicules SET immatriculation=?,marque=?,modele=?,capacite_kg=?,statut=? WHERE id=?",
                                (immat, marque, modele, capacite, statut, vid))
                        st.success("✅ Véhicule mis à jour !")
                        st.rerun()
                if st.button("🗑️ Supprimer ce véhicule"):
                    execute("DELETE FROM vehicules WHERE id=?", (vid,))
                    st.success("Véhicule supprimé.")
                    st.rerun()


