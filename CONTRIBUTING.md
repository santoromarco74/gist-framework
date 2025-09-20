# Contributing to GIST Framework

Grazie per il tuo interesse nel contribuire al GIST Framework! 🎉

## Come Contribuire

### 🐛 Segnalazione Bug
1. Verifica che il bug non sia già stato segnalato nelle [Issues](https://github.com/your-org/gist-framework/issues)
2. Crea una nuova issue utilizzando il template "Bug Report"
3. Includi dettagli specifici: versione Python, OS, steps per riprodurre

### ✨ Richiesta Feature
1. Apri una issue con il template "Feature Request"
2. Descrivi chiaramente il caso d'uso e il beneficio
3. Discuti la proposta con il team prima di implementare

### 🔧 Pull Request
1. Fork il repository
2. Crea un branch per la tua feature: `git checkout -b feature/amazing-feature`
3. Segui le convenzioni di codice (vedi sotto)
4. Aggiungi test per le nuove funzionalità
5. Esegui i test: `pytest tests/`
6. Commit con messaggi descrittivi
7. Push al branch e apri una Pull Request

## Code Style

### Python
- Segui [PEP 8](https://pep8.org/)
- Usa [Black](https://black.readthedocs.io/) per formattazione: `black .`
- Usa [flake8](https://flake8.pycqa.org/) per linting: `flake8 .`
- Type hints obbligatori per funzioni pubbliche

### Documentazione
- Docstring in formato Google style
- Commenti in italiano per logica di business specifica del settore GDO
- README e documentazione pubblica in italiano

### Test
- Coverage minimo 80%
- Test unitari per tutte le funzioni pubbliche
- Test di integrazione per workflow completi
- Mock per dipendenze esterne

## Setup Ambiente Sviluppo

```bash
# Clone e setup
git clone https://github.com/your-org/gist-framework.git
cd gist-framework

# Virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Installazione dipendenze dev
pip install -r requirements.txt
pip install -e .[dev]

# Pre-commit hooks
pre-commit install

# Verifica setup
pytest tests/ -v
```

## Linee Guida Specifiche

### Algoritmi
- Mantenere compatibilità con dataset di calibrazione esistenti
- Documentare assunzioni e limitazioni
- Includere validazione statistica per nuovi algoritmi

### Digital Twin
- Preservare realismo statistico dei dati generati
- Validare output con test appropriati (Benford's Law, etc.)
- Mantenere performance di generazione

### Template Operativi
- Testare su ambienti di sviluppo prima del commit
- Includere documentazione di configurazione
- Considerare compatibilità cross-platform

## Processo Review

1. **Automated Checks**: CI/CD pipeline deve passare
2. **Code Review**: Almeno 1 approvazione da maintainer
3. **Testing**: Verifica manuale se necessaria
4. **Documentation**: Aggiornamento docs se applicabile

## Rilasci

- Versioning semantico (SemVer)
- Changelog dettagliato
- Testing su ambienti multipli
- Backward compatibility quando possibile

## Contatti

- **Issues**: Usa GitHub Issues per bug e feature request
- **Discussioni**: GitHub Discussions per domande generali
- **Email**: gist-framework@research.org per questioni private

## Riconoscimenti

I contributori sono riconosciuti nel [README.md](README.md) e nel changelog di rilascio.

---

Questo progetto segue il [Covenant Code of Conduct](https://www.contributor-covenant.org/). Partecipando, ti impegni a rispettare questi termini.