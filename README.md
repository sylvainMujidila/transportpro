# 🚛 TransportPro — Guide de déploiement

Application de gestion de transport de marchandises — Streamlit

---

## 📁 Structure du projet

```
transportpro/
├── app.py            ← Application principale
├── requirements.txt  ← Dépendances Python
└── README.md         ← Ce fichier
```

---

## 🚀 Déploiement GRATUIT sur Streamlit Cloud (recommandé)

### Étape 1 — Créer un compte GitHub (si pas encore fait)
→ https://github.com/signup

### Étape 2 — Créer un nouveau dépôt GitHub
1. Aller sur https://github.com/new
2. Nommer le dépôt : `transportpro`
3. Choisir **Public**
4. Cliquer **Create repository**

### Étape 3 — Uploader les fichiers
Dans votre dépôt GitHub, cliquer **Add file → Upload files** et déposer :
- `app.py`
- `requirements.txt`

### Étape 4 — Déployer sur Streamlit Cloud
1. Aller sur https://share.streamlit.io
2. Se connecter avec GitHub
3. Cliquer **New app**
4. Choisir votre dépôt `transportpro`
5. Fichier principal : `app.py`
6. Cliquer **Deploy!**

⏱️ Déploiement en 2-3 minutes.  
🌐 Vous obtenez une URL du type : `https://votrenom-transportpro.streamlit.app`

---

## 💻 Lancer en local (test)

```bash
pip install streamlit pandas
streamlit run app.py
```

L'app s'ouvre dans votre navigateur sur http://localhost:8501

---

## 👥 Partager avec votre équipe

- Envoyer l'URL Streamlit Cloud à vos collègues
- Tout le monde accède à la **même base de données** en temps réel
- Aucune installation nécessaire côté utilisateur

---

## ⚙️ Fonctionnalités

| Module         | Fonctionnalités                                              |
|---------------|--------------------------------------------------------------|
| 📊 Dashboard   | KPIs, graphiques CA, répartition des statuts                |
| 📦 Livraisons  | Créer, modifier, changer le statut, supprimer               |
| 👤 Clients     | CRUD complet                                                 |
| 🧑‍✈️ Chauffeurs  | CRUD + disponibilité visuelle                                |
| 🚗 Véhicules   | CRUD + état de la flotte                                     |

---

## ⚠️ Note base de données

Streamlit Cloud utilise un système de fichiers **éphémère** : la base SQLite
se réinitialise lors des redémarrages. Pour une équipe, il est recommandé
de migrer vers une base persistante gratuite :

**Option gratuite recommandée : Supabase (PostgreSQL)**
→ https://supabase.com (plan gratuit : 500 Mo)

Ou utiliser **PlanetScale** (MySQL) ou **Railway** (PostgreSQL).
