#!/usr/bin/env python3
"""
Script principale per generazione Digital Twin GDO
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.digital_twin import GDODigitalTwin

def main():
    """Genera dataset dimostrativo Digital Twin"""
    
    # Inizializza Digital Twin
    twin = GDODigitalTwin()
    
    # Genera dataset dimostrativo
    # Per la tesi: 5 store, 30 giorni = ~500MB realistici
    datasets = twin.generate_demo_dataset(
        n_stores=5,
        n_days=30,
        validate=True,
        save=True
    )
    
    print("\n✨ DIGITAL TWIN COMPLETATO!")
    print("I dataset sono disponibili nella cartella 'outputs/'")
    print("\nProssimi passi:")
    print("1. Analizza i risultati della validazione")
    print("2. Crea visualizzazioni in Jupyter Notebook")
    print("3. Documenta nella tesi come 'Framework Digital Twin'")
    print("4. Carica su GitHub per riproducibilità")

if __name__ == "__main__":
    main()