# 📋 ISTRUZIONI PER INTEGRARE IL REPOSITORY NELLA TESI

## ✅ File Creati e Pronti all'Uso

### 1. **Nota Repository** (Sezione dedicata)
**File**: `capitoli/nota_repository.tex`
- Pagina completa con descrizione repository
- QR code per accesso rapido
- Istruzioni installazione

### 2. **Box Informativi per Capitoli**
**File**: `capitoli/riferimenti_capitoli.tex`
- Box colorati da inserire nei capitoli rilevanti
- Collegamenti specifici agli algoritmi

### 3. **Riferimenti Bibliografici**
**File**: `bibliografia/repository_references.bib`
- 7 riferimenti software/dataset pronti
- Formato BibTeX standard

### 4. **QR Code**
**File generato**: `figure/qr_code_repository.png`
- QR code funzionante per accesso diretto
- Pronto per inclusione LaTeX

---

## 🔧 MODIFICHE DA FARE IN `main.tex`

### OPZIONE A: Inserire Nota Repository dopo Prefazione

```latex
% Dopo \input{prefazione.tex}
\input{capitoli/nota_repository.tex}
\newpage
```

### OPZIONE B: Inserire Nota Repository prima delle Appendici

```latex
% Prima delle appendici
\chapter*{Materiale Supplementare}
\addcontentsline{toc}{chapter}{Materiale Supplementare}
\input{capitoli/nota_repository.tex}

% Poi le appendici
\appendix
\input{capitoli/app_metodologia.tex}
\input{capitoli/app_scoring.tex}
```

---

## 📝 INSERIMENTO NEI CAPITOLI

### Capitolo 2 - Threat Landscape
Dopo la sezione ASSA-GDO (circa riga 450), aggiungi:

```latex
% Box implementazione ASSA-GDO
\begin{tcolorbox}[colback=blue!5!white,colframe=blue!75!black,title=Implementazione Disponibile]
L'algoritmo ASSA-GDO descritto in questa sezione è disponibile come implementazione Python nel repository ufficiale:
\begin{itemize}
    \item File: \texttt{assa\_gdo\_calculator.py}
    \item Documentazione: \url{https://github.com/gist-framework/gdo-security#assa-gdo}
    \item Esempio: \texttt{python assa\_gdo\_calculator.py --org-factor 1.2}
\end{itemize}
\end{tcolorbox}
```

### Capitolo 3 - Digital Twin
Dopo la descrizione del framework Digital Twin, aggiungi:

```latex
% Box Digital Twin Framework
\begin{tcolorbox}[colback=green!5!white,colframe=green!75!black,title=Digital Twin Framework]
Il framework Digital Twin completo per la generazione di dataset sintetici è disponibile nel repository:
\begin{itemize}
    \item File: \texttt{gdo\_digital\_twin.py}
    \item Genera dataset realistici calibrati su dati ISTAT 2023
    \item Validazione automatica con test statistici
\end{itemize}
\end{tcolorbox}
```

### Capitolo 5 - GIST Score
Dopo la presentazione del GIST Score, aggiungi:

```latex
% Box GIST Calculator
\begin{tcolorbox}[colback=red!5!white,colframe=red!75!black,title=GIST Calculator - Implementazione Completa]
Il calcolatore GIST Score è disponibile come tool standalone:

\textbf{Installazione:}
\begin{lstlisting}[language=bash, basicstyle=\footnotesize\ttfamily]
pip install gist-framework
\end{lstlisting}

\textbf{Uso:}
\begin{lstlisting}[language=python, basicstyle=\footnotesize\ttfamily]
from gist_calculator import GISTCalculator
calc = GISTCalculator("Nome Organizzazione")
result = calc.calculate_score(scores)
\end{lstlisting}
\end{tcolorbox}
```

---

## 📚 AGGIORNAMENTO BIBLIOGRAFIA

Nel file della bibliografia principale, aggiungi:

```latex
% Alla fine del file .bib esistente
\input{bibliografia/repository_references.bib}
```

O copia il contenuto di `repository_references.bib` nel file bibliografia esistente.

---

## 🎨 QR CODE NELLA TESI

Il QR code è già referenziato in `nota_repository.tex`:

```latex
\includegraphics[width=3cm]{figure/qr_code_repository.png}
```

Assicurati che il file sia in `figure/qr_code_repository.png` ✅ (già generato!)

---

## 🔄 AGGIORNAMENTO APPENDICI

In `main.tex`, sostituisci le vecchie appendici:

```latex
% RIMUOVI:
%\input{capitoli/appA.tex}
%\input{capitoli/appB.tex}
%\input{capitoli/appC.tex}
%\input{capitoli/appD.tex}
%\input{capitoli/appE.tex}

% AGGIUNGI:
\appendix
\input{capitoli/app_metodologia.tex}
\input{capitoli/app_scoring.tex}
```

---

## ✅ CHECKLIST FINALE INTEGRAZIONE

- [ ] Inserita `nota_repository.tex` in posizione scelta
- [ ] Aggiunti box informativi nei capitoli 2, 3, 5
- [ ] Bibliografia aggiornata con riferimenti repository
- [ ] QR code presente in `figure/`
- [ ] Appendici vecchie rimosse
- [ ] Appendici nuove incluse
- [ ] Compilazione LaTeX senza errori

---

## 🚀 TEST COMPILAZIONE

```bash
# Compilazione completa
compila.bat

# Verifica:
# 1. QR code visibile e scannerizzabile
# 2. Box informativi nei capitoli corretti
# 3. Collegamenti URL funzionanti nel PDF
# 4. Bibliografia con riferimenti software
```

---

## 💡 SUGGERIMENTI AGGIUNTIVI

### Menzione nelle Conclusioni
Aggiungi nel capitolo conclusioni:

```latex
\section{Disponibilità del Codice}
Tutto il codice sorgente, i dataset di validazione e la documentazione tecnica
sono disponibili pubblicamente su GitHub per garantire la riproducibilità dei
risultati e facilitare l'adozione del framework nel settore:

\begin{center}
\Large
\textbf{\url{https://github.com/gist-framework/gdo-security}}
\end{center}
```

### Abstract/Sommario
Aggiungi una riga nell'abstract:

```latex
Il framework è disponibile come software open source all'indirizzo
\url{https://github.com/gist-framework/gdo-security}.
```

---

## 📧 SUPPORTO

Se hai problemi con l'integrazione:
1. Verifica che tutti i file siano nelle directory corrette
2. Controlla i log di compilazione LaTeX per errori
3. Assicurati che il package `tcolorbox` sia installato per i box colorati
4. Il QR code richiede il package `graphicx`

**Repository pronto per pubblicazione su GitHub!** 🎉