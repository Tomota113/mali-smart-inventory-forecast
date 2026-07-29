# 📦 Mali Smart Inventory Forecast

> **Proof of Concept (PoC) développé pour la Semaine du Numérique au Mali**  
> *Moteur d'Intelligence Artificielle pour la Prédiction des Ventes et la Gestion Intelligente des Stocks dans le Commerce & la Distribution.*

---

## 📌 Présentation du Projet

Dans le secteur du commerce et de la distribution au Mali et en Afrique de l'Ouest, les **ruptures de stock non anticipées** et les **surstockages inutiles** entraînent de fortes pertes financières et d'opportunités.

**Mali Smart Inventory Forecast** est une solution PoC qui applique le Machine Learning (*Random Forest Regressor*) aux séries temporelles de ventes quotidiennes afin de :
1. Prédire la demande de ventes sur 30 jours pour chaque produit.
2. Évaluer l'autonomie restante des stocks en jours.
3. Alerter automatiquement en cas de risque de rupture imminent et calculer la quantité optimale de réapprovisionnement ainsi que le budget estimé en **FCFA**.

---

## ✨ Fonctionnalités Clés

- 📊 **Analyse des Séries Temporelles de Ventes** : Traitement des données historiques avec gestion des effets de saisonnalité et des jours de la semaine.
- 🔮 **Prédiction Avancée par Machine Learning** : Modèle de régression sur caractéristiques temporelles (Lags & Rolling Means) prédisant les ventes quotidiennes sur 7 à 60 jours.
- 🚨 **Système d'Alerte Préventif** : Bannières interactives signalant les stocks critiques (`Stock bientot épuisé - Commande urgente`).
- 🛒 **Génération Automatique de Bons de Commande** : Calcul automatique des quantités à commander et du budget en FCFA.
- 📥 **Exportation CSV** : Exportation en un clic du tableau de bord de réapprovisionnement.

---

## 🛠️ Stack Technique

- **Langage** : Python 3.10+
- **Machine Learning** : Scikit-Learn (`RandomForestRegressor`)
- **Data & Traitement** : Pandas, NumPy
- **Interface Web & Visualisation** : Streamlit, Plotly Express & Graph Objects
- **Environnement & OS** : Linux Ubuntu, VS Code, Git

---

## 📂 Arborescence du Projet

```text
mali-smart-inventory-forecast/
├── app.py                      # Application web Streamlit principale
├── requirements.txt            # Dépendances du projet
├── README.md                   # Documentation du projet
├── .gitignore                  # Fichiers à ignorer par Git
├── data/
│   └── sales_inventory_sample.csv  # Dataset d'exemple synthétique
└── src/
    ├── __init__.py
    ├── data_generator.py       # Générateur de données de ventes & stock
    └── forecasting_engine.py   # Moteur de prévision et calcul de santé des stocks
```

---

## 🚀 Guide d'Installation et d'Exécution Rapide

### 1. Cloner le projet et accéder au dossier
```bash
git clone https://github.com/Tomota113/mali-smart-inventory-forecast.git
cd mali-smart-inventory-forecast
```

### 2. Créer et activer l'environnement virtuel Python
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Installer les dépendances
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Lancer l'application Streamlit
```bash
streamlit run app.py
```

L'application s'ouvrira automatiquement dans votre navigateur à l'adresse : `http://localhost:8501`.

---

## 👤 Auteur & Contact

**Ibrahim Tomota**  
*Étudiant en IA & Science des Données | Machine Learning & Software Engineering*  
- **GitHub** : [@Tomota113](https://github.com/Tomota113)  
- **LinkedIn** : [Ibrahim Tomota](https://www.linkedin.com/in/ibrahim-tomota-056756330)  
- **Email** : `itomota11@gmail.com`
