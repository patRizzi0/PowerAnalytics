# ⚡ PowerAnalytics

## Panoramica

**PowerAnalytics** è un'applicazione web per simulare e analizzare i consumi energetici domestici, con dati reali da Eurostat per 29 paesi europei.

L'idea è semplice ma efficace: aiutare le persone a capire **come le loro abitudini quotidiane influenzano i costi energetici**, fornendo proiezioni realistiche basate su:
- Superficie dell'abitazione
- Numero di persone
- Stagione e tipo di abitazione
- Prezzi kWh reali da Eurostat

Oltre alle simulazioni personali, puoi **confrontare i prezzi tra due paesi europei** e visualizzare l'andamento storico dei costi.

---

## 🎯 Caratteristiche principali

- **Simulatore consumi**: calcola il consumo annuo stimato basato su parametri personali
- **29 paesi europei**: supporto completo da Italia a Norvegia
- **Dati Eurostat**: prezzi kWh sempre aggiornati dall'API ufficiale
- **Confronto paesi**: confronta prezzi e storico tra due paesi con grafici interattivi
- **Calcolo elettrodomestici**: stima il consumo di specifici dispositivi
- **Insight personalizzati**: analisi automatica dei consumi con raccomandazioni
- **Interfaccia intuitiva**: form guidati con validazione in tempo reale

---

## 🛠️ Stack tecnologico

| Layer | Tecnologia |
|-------|-----------|
| **Backend** | Flask 3.1.3, Python 3.10+ |
| **Database** | PostgreSQL + SQLAlchemy 2.0 |
| **Frontend** | HTML5, CSS3, JavaScript (Chart.js) |
| **Testing** | pytest, unittest.mock |
| **Deployment** | Railway (con gunicorn) |

### Dipendenze principali
```
Flask==3.1.3
Flask-SQLAlchemy==3.1.1
SQLAlchemy==2.0.49
psycopg2-binary==2.9.12
requests==2.33.1
pytest==9.0.3
gunicorn
```

---

## 🚀 Quick start

### 1. **Setup locale**

#### Prerequisiti
- Python 3.10+
- PostgreSQL 12+
- Git

#### Installazione
```bash
# Clone il repository
git clone https://github.com/patRizzi0/PowerAnalytics.git
cd PowerAnalytics

# Crea environment virtuale
python -m venv venv

# Attiva il venv
# Su Windows:
venv\Scripts\activate
# Su macOS/Linux:
source venv/bin/activate

# Installa dipendenze
pip install -r requirements.txt
```

#### Configurazione database

1. **Crea un database PostgreSQL**:
```sql
createdb power_analytics
```

2. **Configura le variabili d'ambiente** (copia `.env.example`):
```bash
cp .env.example .env
```

3. **Modifica `.env`** con le tue credenziali:
```env
DATABASE_URL=postgresql://username:password@localhost:5432/power_analytics
FLASK_ENV=development
FLASK_DEBUG=1
LOG_LEVEL=DEBUG
PORT=5000
```

4. **Inizializza lo schema** (opzionale, se usi alembic):
```bash
# Se hai migrations Alembic:
alembic upgrade head

# Oppure esegui direttamente:
psql -U username -d power_analytics -f schema.sql
```

5. **Popola i dati** (dispositivi e categorie):
```bash
python insert_data.py
```

### 2. **Avvia l'app in locale**

```bash
python app.py
```

Accedi a: **http://localhost:5000/home**

---

## 📁 Struttura del progetto

```
PowerAnalytics/
├── app.py                          # Punto di ingresso Flask + routing
├── connection.py                   # Configurazione SQLAlchemy
├── requirements.txt                # Dipendenze Python
├── Procfile                        # Configurazione Railway
│
├── models/                         # SQLAlchemy ORM models
│   ├── device_model.py            # Modello elettrodomestico
│   ├── category_model.py          # Modello categoria dispositivo
│   └── Rule.py                    # Modello regola (non usato al momento)
│
├── service/                        # Logica di business (CLEAN ARCHITECTURE)
│   ├── consumi_service.py         # Calcolo consumo abitazione
│   ├── multiplier_consumi_service.py  # Moltiplicatore per persone
│   ├── validators.py              # Validazione input form
│   ├── countries.py               # Lista paesi supportati + mapping
│   ├── eurostat_service.py        # Fetch dati da Eurostat API
│   ├── converts_paese_eurostat.py # Transform dati paese → formato interno
│   ├── converts.py                # Utility conversioni dati
│   ├── build_dict_rule.py         # Builder regole (legacy)
│   │
│   ├── calculators/               # Calcolatori specifici
│   │   ├── fetch_paese.py         # Fetch dati completi un paese
│   │   ├── media_nazionale.py     # Media nazionale consumo
│   │   ├── variation_years.py     # Variazione storica anni
│   │   ├── key_precedent.py       # Logica precedente (legacy)
│   │   └── build_description.py   # Builder descrizione insight
│   │
│   └── insights/                  # Generazione insight personalizzati
│       └── insight_generator.py   # Logica insight per consumo/costo
│
├── data/                           # Coefficienti configurabili
│   ├── coeff_stagione.json        # Moltiplicatori stagionali
│   └── coeff_appartamento.json    # Moltiplicatori per tipo abitazione
│
├── templates/                      # Jinja2 templates HTML
│   ├── layout/
│   │   └── base.html              # Layout base + navigation
│   ├── pages/
│   │   ├── home.html              # Home page
│   │   ├── consumi.html           # Form calcolo consumi
│   │   ├── calcolo_consumi.html   # Risultati consumi
│   │   ├── calcolo_elettrodomestico.html  # Form dispositivi
│   │   ├── eurostat.html          # Info Eurostat
│   │   ├── filtro.html            # Visualizzazione dati Eurostat
│   │   ├── confronto.html         # Confronto due paesi
│   │   ├── francia_prova.html     # Test Francia (dev)
│   │   └── error.html             # Pagina errore generica
│   └── partials/
│       ├── header.html            # Header comune
│       └── footer.html            # Footer comune
│
├── static/                         # Asset frontend
│   ├── css/
│   │   └── style.css              # Stili principali
│   ├── js/
│   │   ├── grafico.js             # Chart.js singola linea
│   │   ├── grafico_due_linee.js   # Chart.js doppia linea
│   │   └── script_consumi.js      # Logica form interattivo
│   └── img/                        # Immagini (tipi abitazione)
│
├── tests/                          # Test suite pytest
│   ├── test_validators.py         # Test validazione input
│   ├── test_consumi_service.py    # Test calcolo consumi
│   ├── test_multiplier_consumi_service.py  # Test moltiplicatori
│   └── test_converts_paese_eurostat.py    # Test transform dati
│
├── migrations/                     # Alembic migrations (opzionale)
│   └── versions/                  # Migration scripts
│
├── .env.example                    # Template variabili ambiente
├── .gitignore                      # Esclusioni Git
├── schema.sql                      # Schema DB iniziale
├── insert_data.py                  # Script popolamento DB
└── check_tables.py                 # Debug schema tables
```

---

## 🔧 API Eurostat

L'app usa l'API ufficiale Eurostat per recuperare i prezzi kWh reali.

### Endpoint usato
```
https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/{dataset}
```

### Dataset principale
**`nrg_pc_204`** — Prezzo dell'energia per uso domestico (kWh)

Parametri:
- `geo`: Codice paese (es. `IT`, `FR`, `DE`)
- `currency`: `EUR` (fisso)
- `unit`: `KWH` (fisso)
- `tax`: `I_TAX` (con tasse incluse)
- `nrg_cons`: Banda di consumo (es. `KWH2500-4999`)

### Implementazione
```python
# service/eurostat_service.py
EurostatService.prendi_dati_grezzi(paese_code)  # Fetch dati grezzi
converts_paese_eurostat(paese)  # Transform → formato interno
```

### Cache
I dati sono cachati in memory con LRU thread-safe per evitare troppe richieste all'API.

---

## 📊 Paesi supportati

L'app supporta **29 paesi europei**:

| Codice | Paese | Codice | Paese |
|--------|-------|--------|-------|
| AT | Austria | LT | Lituania |
| BE | Belgio | LU | Lussemburgo |
| BG | Bulgaria | MT | Malta |
| CY | Cipro | NL | Paesi Bassi |
| CZ | Repubblica Ceca | NO | Norvegia |
| DE | Germania | PL | Polonia |
| DK | Danimarca | PT | Portogallo |
| EE | Estonia | RO | Romania |
| ES | Spagna | SE | Svezia |
| FI | Finlandia | SI | Slovenia |
| FR | Francia | SK | Slovacchia |
| GR | Grecia | HR | Croazia |
| HU | Ungheria | IE | Irlanda |
| IT | Italia | | |

I paesi sono definiti in `service/countries.py` e facilmente estendibili.

---

## 📈 Calcolo consumi

### Formula
```
Consumo [kWh] = Superficie × 24 × Coeff_Tipo × Coeff_Stagione × Moltiplicatore_Persone

Costo [€] = Consumo × Prezzo_kWh
```

### Coefficienti

**Stagionali** (`data/coeff_stagione.json`):
- Inverno: 1.2 (picco riscaldamento)
- Primavera/Autunno: 1.0 (baseline)
- Estate: 0.8 (meno riscaldamento)

**Tipo abitazione** (`data/coeff_appartamento.json`):
- Studio: 0.85
- Appartamento piccolo: 0.92
- Appartamento medio: 1.00 (baseline)
- Appartamento grande: 1.10
- Colocation: 0.75
- Casa indipendente: 1.40

**Moltiplicatore persone**:
Ogni persona aggiunge consumo non lineare (è in `multiplier_consumi_service.py`).

---

## 🧪 Testing

### Eseguire i test
```bash
pytest tests/
```

### Cobertura dei test

Test disponibili:
- ✅ `test_validators.py` — Validazione input form
- ✅ `test_consumi_service.py` — Calcolo consumo (includes mocking Eurostat)
- ✅ `test_multiplier_consumi_service.py` — Moltiplicatori persone
- ✅ `test_converts_paese_eurostat.py` — Transform dati paese

### Aggiungere coverage report
```bash
pip install coverage

coverage run -m pytest tests/
coverage report
coverage html  # Genera report HTML in htmlcov/
```

### Logica di test
- Mock di `EurostatService` per evitare dipendenze esterne
- Test di edge case (input invalido, file mancanti, paesi non supportati)
- Verifiche di output atteso

---

## 🚢 Deployment su Railway

### Prerequisiti
- Account Railway
- GitHub repository collegato

### Procedura

1. **Crea progetto Railway**:
   - Connect il tuo GitHub repo
   - Railway auto-detect la presence di `requirements.txt` e `Procfile`

2. **Configura variabili ambiente**:
   ```env
   DATABASE_URL=postgresql://user:pass@host:5432/power_analytics
   FLASK_ENV=production
   FLASK_DEBUG=0
   LOG_LEVEL=INFO
   PORT=5000
   ```

3. **Deploy automatico**:
   - Ogni push a `main` trigga un deploy automatico
   - Railway esegue `gunicorn app:app` (da Procfile)

4. **URL dell'app**:
   ```
   https://poweranalytics-production.up.railway.app/home
   ```

### Note importanti
- Usa `FLASK_DEBUG=0` in production
- PostgreSQL deve essere provision su Railway o esterno
- Backup regolari del database sono consigliati

---

## 🔐 Variabili d'ambiente

Vedi `.env.example` per il template. Variabili richieste:

```env
DATABASE_URL          # PostgreSQL connection string (REQUIRED)
FLASK_ENV            # development | production
FLASK_DEBUG          # 0 o 1 (NUNCA 1 in production!)
LOG_LEVEL            # DEBUG | INFO | WARNING | ERROR
PORT                 # Porta (default 5000)
```

---

## 🎯 Validazione input

L'app ha **validazione a due livelli**:

### 1. Frontend (JavaScript)
- Form HTML5 `required` attributes
- Validazione tipo radio buttons

### 2. Backend (Python)
**`service/validators.py`**:
- `n_persone > 0`
- `m_quadri >= 20`

**`service/consumi_service.py`** (logica di business):
- Tipo abitazione presente in `coeff_appartamento.json`
- Stagione presente in `coeff_stagione.json`
- Prezzo kWh valido e convertibile a float
- Valori numerici per persone e metri quadri

---

## 🛣️ Route principali

| Route | Metodo | Descrizione |
|-------|--------|------------|
| `/home` | GET | Home page |
| `/consumi` | GET | Form simulazione consumi |
| `/calcolo_consumi` | POST | Calcolo e risultati consumi |
| `/confronto` | GET/POST | Confronto prezzi due paesi |
| `/eurostat` | GET | Info e dati Eurostat |
| `/filtro` | GET | Visualizzazione dati Eurostat filtrati |
| `/calcolo_elettrodomestico` | GET/POST | Calcolo consumi dispositivi |
| `/device/<id>` | GET | API JSON dettagli dispositivo |

---

## 🐛 Error handling

L'app ha error handling robusto:

```python
# app.py - Tutti gli errori sono catturati e mostrati all'utente

@app.errorhandler(404)          # Route non trovate
@app.errorhandler(HTTPException) # Errori HTTP generici
@app.errorhandler(Exception)    # Eccezioni inattese
```

Ogni errore mostra una pagina user-friendly (`templates/pages/error.html`) senza esporre dettagli tecnici.

---

## 🏗️ Architettura

### Pattern: Clean Architecture

```
Route (Controller)
    ↓
Validator (Input validation)
    ↓
Service Layer (Business logic)
    │
    ├─ Eurostat Service (Fetch dati)
    ├─ Consumi Service (Calcoli)
    ├─ Insight Generator (Analisi)
    │
    ↓
Repository (Database queries)
    ↓
Response (Template rendering)
```

**Vantaggi**:
- Service layer completamente testabile
- Database queries isolate in models/
- Logica di business indipendente da Flask
- Facile aggiungere nuove features

---

## 📝 Development notes

### Aggiungere un nuovo paese

1. Aggiungi a `service/countries.py`:
```python
SUPPORTED_COUNTRIES = {
    ...
    "NE": {"it": "Nuovo Paese", "en": "New Country"},
}
```

2. Test che `EurostatService` abbia dati per il paese
3. Test il calcolo con dati reali Eurostat

### Aggiungere un nuovo coefficiente

1. Modifica il JSON in `data/`:
```json
{
  "nuovo_valore": 1.05
}
```

2. Aggiungi validazione in `consumi_service.py`
3. Scrivi test in `tests/`

### Debugging

Usa le route di debug disponibili in development mode:

```python
# Richiede FLASK_ENV=development
GET /debug/test_eurostat
```

---

## 🚀 Roadmap future

- [ ] Support lingue (multi-language)
- [ ] Storico consumo personale (user accounts)
- [ ] Export PDF report
- [ ] Mobile app (Flutter/React Native)
- [ ] API pubblica per third-party
- [ ] Machine learning per predizioni consumi
- [ ] Integrazione smart meters reali
- [ ] Ottimizzazione consumi con AI

---

## 📄 Licenza

MIT License — Vedi LICENSE file.

---

## 👤 Autore

**Patrick** (@patRizzi0)  
Progetti: PowerAnalytics, Reservation_App  
GitHub: https://github.com/patRizzi0

---

## 📧 Contatti e supporto

Per bug report, feature request o domande:
- Apri un [Issue su GitHub](https://github.com/patRizzi0/PowerAnalytics/issues)
- Scrivi una mail (se disponibile)

---

## ⭐ Ringraziamenti

- **Eurostat** per i dati pubblici API
- **Flask community** per la documentazione
- **pytest** per il framework di testing

---

**Ultimo aggiornamento**: Maggio 2026  
**Versione**: 1.0.0