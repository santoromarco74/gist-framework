# GIST Framework - Implementation Repository

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen.svg)](./docs/)

**GIST Framework** (Governance, Infrastructure, Security, Trust) per la valutazione della maturità digitale nel settore della Grande Distribuzione Organizzata (GDO).

> 🎓 **Nota**: Questo repository contiene le implementazioni tecniche derivate dalla tesi di laurea "Framework per la Valutazione della Maturità Digitale in Ambienti Cloud Ibridi: Analisi del Settore GDO". La metodologia completa è disponibile nella tesi accademica.

## 📋 Indice

- [Caratteristiche](#-caratteristiche)
- [Installazione](#-installazione)
- [Uso Rapido](#-uso-rapido)
- [Componenti](#-componenti)
- [Documentazione](#-documentazione)
- [Contribuire](#-contribuire)
- [Licenza](#-licenza)

## 🚀 Caratteristiche

### Core Framework
- **GIST Calculator**: Calcolo automatizzato del GIST Score per valutazione maturità digitale
- **ASSA-GDO Algorithm**: Quantificazione della superficie di attacco specifica per GDO
- **Digital Twin Framework**: Generazione dataset sintetici realistici per il settore retail

### Strumenti Operativi
- **Checklist Migrazione Cloud**: Valutazione readiness per migrazione cloud
- **Runbook Sicurezza**: Automazione risposta incidenti (ransomware, data breach)
- **Dashboard Grafana**: Visualizzazione real-time postura di sicurezza

### Algoritmi Avanzati
- **Modello SIR**: Simulazione propagazione malware in reti GDO
- **Risk Scoring XGBoost**: Sistema adattivo di scoring del rischio
- **Monte Carlo Analysis**: Analisi probabilistica scenari di rischio

## 🛠 Installazione

### Prerequisiti
- Python 3.8 o superiore
- pip (package manager)
- Git

### Installazione Base
```bash
# Clone del repository
git clone https://github.com/your-org/gist-framework.git
cd gist-framework

# Installazione dipendenze
pip install -r requirements.txt

# Test installazione
python gist_calculator.py --demo
```

### Installazione con Docker
```bash
# Build immagine
docker build -t gist-framework .

# Esecuzione container
docker run -it --name gist-framework gist-framework
```

## ⚡ Uso Rapido

### Calcolo GIST Score
```python
from gist_calculator import GISTCalculator

# Inizializza calcolatore
calc = GISTCalculator("Mia Organizzazione")

# Definisci punteggi componenti (0-100)
scores = {
    'physical': 65,
    'architectural': 72,
    'security': 68,
    'compliance': 75
}

# Calcola GIST Score
result = calc.calculate_score(scores)
print(f"GIST Score: {result['score']:.2f}")
print(f"Livello Maturità: {result['maturity_level']}")
```

### Generazione Dataset con Digital Twin
```python
from gdo_digital_twin import GDODigitalTwin

# Inizializza Digital Twin
twin = GDODigitalTwin()

# Genera dataset dimostrativo
dataset = twin.generate_demo_dataset(
    n_stores=10,    # 10 punti vendita
    n_days=30,      # 30 giorni di dati
    validate=True   # Validazione statistica
)

print(f"Transazioni generate: {len(dataset['transactions']):,}")
print(f"Eventi sicurezza: {len(dataset['security_events']):,}")
```

### Calcolo ASSA Score
```python
from assa_gdo_calculator import ASSA_GDO, create_sample_infrastructure

# Crea infrastruttura di esempio
infrastructure = create_sample_infrastructure()

# Calcola ASSA Score
assa = ASSA_GDO(infrastructure, org_factor=1.2)
total_score, components = assa.calculate_assa()

print(f"ASSA Score Totale: {total_score:.2f}")

# Genera raccomandazioni
mitigations = assa.recommend_mitigations(budget=50000)
print(f"ROI Mitigazioni: {mitigations['overall_roi']:.1f}")
```

## 📦 Componenti

### 1. Core Algorithms

| File | Descrizione | Uso |
|------|-------------|-----|
| `gist_calculator.py` | Calcolatore GIST Score principale | Valutazione maturità digitale |
| `assa_gdo_calculator.py` | Algoritmo superficie di attacco | Risk assessment infrastrutturale |
| `gdo_digital_twin.py` | Framework Digital Twin | Generazione dati sintetici |

### 2. Operational Templates

| File | Descrizione | Uso |
|------|-------------|-----|
| `templates/cloud_migration_checklist.json` | Checklist migrazione cloud | Assessment pre-migrazione |
| `templates/ransomware_response_runbook.sh` | Runbook risposta ransomware | Automazione incident response |
| `templates/grafana_dashboard_gist.json` | Dashboard Grafana | Monitoring postura sicurezza |

### 3. Advanced Analytics

| Componente | Descrizione | Caso d'uso |
|------------|-------------|-----------|
| SIR Model | Simulazione propagazione malware | Analisi impatto epidemiologico |
| XGBoost Risk Scorer | ML per risk scoring | Predizione incidenti sicurezza |
| Monte Carlo Engine | Analisi probabilistica | Valutazione scenari multipli |

## 📖 Documentazione

### Riferimenti Principali
- **[Metodologia GIST](docs/methodology.md)**: Fondamenti teorici del framework
- **[API Reference](docs/api.md)**: Documentazione completa delle API
- **[Esempi Pratici](examples/)**: Casi d'uso e tutorial
- **[Deployment Guide](docs/deployment.md)**: Guida installazione produzione

### Archetipi Organizzativi
Il framework è calibrato su 5 archetipi del settore GDO italiano:

| Archetipo | Range PV | Organizzazioni | Caratteristiche |
|-----------|----------|----------------|----------------|
| **Micro** | 1-10 | 87 | Risorse limitate, soluzioni basic |
| **Piccola** | 10-50 | 73 | Crescita rapida, scalabilità |
| **Media** | 50-150 | 42 | Integrazione sistemi, complessità |
| **Grande** | 150-500 | 25 | Processi strutturati, governance |
| **Enterprise** | 500-2000 | 7 | Trasformazione digitale completa |

### Validazione Scientifica
- **234 organizzazioni** analizzate nel settore GDO italiano
- **R² = 0.783** nella validazione incrociata k-fold
- **88.9% pass rate** nei test di validazione statistica
- **23 esperti** coinvolti nel processo Delphi per calibrazione pesi

## 🔧 Configurazione Avanzata

### Personalizzazione Pesi GIST
```python
# Modifica pesi componenti (default: Physical=18%, Architectural=32%, Security=28%, Compliance=22%)
calc = GISTCalculator()
calc.WEIGHTS = {
    'physical': 0.20,
    'architectural': 0.30,
    'security': 0.30,
    'compliance': 0.20
}
```

### Configurazione Digital Twin
```json
{
  "archetipi": {
    "custom": {
      "count": 10,
      "pv_range": [1, 20],
      "avg_daily_transactions": 800,
      "avg_transaction_value": 25.50
    }
  }
}
```

## 🧪 Testing e Validazione

```bash
# Esecuzione test suite completa
python -m pytest tests/ -v

# Validazione dataset generati
python tests/validate_digital_twin.py

# Benchmark performance algoritmi
python tests/benchmark_algorithms.py
```

## 📊 Metriche e KPI

Il framework genera automaticamente:
- **Disponibilità stimata**: 99.0% - 99.95% basata su GIST Score
- **MTTR stimato**: Calcolato da componente Security
- **Incidents/anno**: Predizione basata su threat landscape
- **ROI investimenti**: Analisi costo-beneficio mitigazioni

## 🤝 Contribuire

Accogliamo contributi dalla comunità! Consulta [CONTRIBUTING.md](CONTRIBUTING.md) per:
- Guidelines contribuzione
- Code style e standards
- Processo review
- Roadmap sviluppo

### Sviluppo
```bash
# Setup ambiente sviluppo
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate
pip install -r requirements-dev.txt

# Pre-commit hooks
pre-commit install
```

## 📈 Roadmap

### v2.0 (Q2 2025)
- [ ] Integrazione AI/ML avanzata per predizione automatica
- [ ] Support multi-tenant per MSP
- [ ] API REST completa
- [ ] Dashboard web nativa

### v2.1 (Q3 2025)
- [ ] Integrazione SIEM/SOAR principali
- [ ] Estensione ad altri settori retail
- [ ] Mobile app per assessment
- [ ] Blockchain per audit trail

## 🏢 Uso in Produzione

Il framework è utilizzato da:
- **Organizzazioni GDO**: Assessment interno maturità digitale
- **System Integrator**: Valutazione clienti e progettazione soluzioni
- **Consulenti di Sicurezza**: Risk assessment e gap analysis
- **Ricercatori**: Benchmark e analisi comparative

## 📄 Licenza

Questo progetto è rilasciato sotto [Licenza MIT](LICENSE).

## 🙏 Riconoscimenti

- **Settore GDO Italiano**: Collaborazione e dati per calibrazione
- **Community Accademica**: Validazione metodologia
- **ENISA**: Threat landscape data per calibrazione sicurezza
- **ISTAT**: Dati statistici settore retail

## 📞 Supporto

- **Issues**: [GitHub Issues](https://github.com/your-org/gist-framework/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/gist-framework/discussions)
- **Email**: gist-framework@your-org.com
- **Documentation**: [docs.gist-framework.org](https://docs.gist-framework.org)

---

<div align="center">
  <strong>GIST Framework</strong> - Developed with ❤️ for the Italian retail sector<br>
  © 2025 - Released under MIT License
</div>