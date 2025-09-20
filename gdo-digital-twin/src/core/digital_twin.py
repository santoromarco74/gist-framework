"""
Orchestratore principale del Digital Twin GDO
"""

import os
import json
import pandas as pd
from datetime import datetime
from typing import Dict, Optional

from ..generators.transactions import TransactionGenerator
from ..generators.security_events import SecurityEventGenerator
from ..validators.statistical_tests import StatisticalValidator
from .config import GDOConfig

class GDODigitalTwin:
    """
    Digital Twin completo per ambiente GDO
    Integra tutti i generatori e validatori
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Inizializza Digital Twin
        
        Args:
            config_path: Path al file di configurazione JSON
        """
        self.config = GDOConfig()
        
        if config_path and os.path.exists(config_path):
            self.config.load_config(config_path)
        
        # Inizializza generatori
        self.transaction_gen = TransactionGenerator(self.config.params)
        self.security_gen = SecurityEventGenerator(self.config.params)
        
        # Validatore
        self.validator = StatisticalValidator()
        
        # Storage paths
        self.output_dir = 'outputs'
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Metadata
        self.metadata = {
            'version': '1.0.0',
            'created_at': datetime.now().isoformat(),
            'config_hash': hash(json.dumps(self.config.params, sort_keys=True))
        }
    
    def generate_demo_dataset(
        self,
        n_stores: int = 5,
        n_days: int = 7,
        validate: bool = True,
        save: bool = True
    ) -> Dict[str, pd.DataFrame]:
        """
        Genera dataset dimostrativo completo
        
        Args:
            n_stores: Numero di punti vendita
            n_days: Giorni da simulare
            validate: Se eseguire validazione statistica
            save: Se salvare su disco
        
        Returns:
            Dizionario con tutti i dataframe generati
        """
        
        print(f"\n{'='*60}")
        print(f"GENERAZIONE DIGITAL TWIN GDO")
        print(f"{'='*60}")
        print(f"Parametri:")
        print(f"  - Punti vendita: {n_stores}")
        print(f"  - Periodo: {n_days} giorni")
        print(f"  - Validazione: {'Sì' if validate else 'No'}")
        print(f"  - Salvataggio: {'Sì' if save else 'No'}")
        print(f"{'='*60}\n")
        
        datasets = {}
        
        # 1. Genera transazioni
        print("1. Generazione transazioni POS...")
        transactions = self.transaction_gen.generate_batch(
            n_stores=n_stores,
            n_days=n_days
        )
        datasets['transactions'] = transactions
        
        # 2. Genera eventi sicurezza
        print("\n2. Generazione eventi di sicurezza...")
        security_events_list = []
        for store_id in range(n_stores):
            events = self.security_gen.generate_security_events(
                n_hours=n_days * 24,
                store_id=store_id
            )
            security_events_list.append(events)
        
        security_events = pd.concat(security_events_list, ignore_index=True)
        datasets['security_events'] = security_events
        
        print(f"✓ Generati {len(security_events):,} eventi di sicurezza")
        
        # 3. Validazione (se richiesta)
        if validate:
            print("\n3. Validazione statistica...")
            
            validation_results = {}
            for name, df in datasets.items():
                validation_results[name] = self.validator.validate_dataset(
                    df, 
                    dataset_type=name.split('_')[0]
                )
            
            self.metadata['validation'] = validation_results
        
        # 4. Salvataggio (se richiesto)
        if save:
            print("\n4. Salvataggio dataset...")
            self._save_datasets(datasets)
        
        # 5. Report finale
        self._print_summary(datasets)
        
        return datasets
    
    def _save_datasets(self, datasets: Dict[str, pd.DataFrame]):
        """Salva dataset su disco"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        for name, df in datasets.items():
            # CSV per compatibilità
            csv_path = os.path.join(self.output_dir, f'{name}_{timestamp}.csv')
            df.to_csv(csv_path, index=False)
            print(f"  ✓ Salvato {name} → {csv_path}")
            
            # Parquet per efficienza
            parquet_path = os.path.join(self.output_dir, f'{name}_{timestamp}.parquet')
            df.to_parquet(parquet_path, index=False)
        
        # Salva metadata
        metadata_path = os.path.join(self.output_dir, f'metadata_{timestamp}.json')
        with open(metadata_path, 'w') as f:
            # Converti oggetti non serializzabili
            metadata_serializable = json.loads(
                json.dumps(self.metadata, default=str)
            )
            json.dump(metadata_serializable, f, indent=2)
        
        # Salva configurazione usata
        config_path = os.path.join(self.output_dir, f'config_{timestamp}.json')
        self.config.save_config(config_path)
    
    def _print_summary(self, datasets: Dict[str, pd.DataFrame]):
        """Stampa summary finale"""
        
        print(f"\n{'='*60}")
        print(f"SUMMARY DIGITAL TWIN GENERATO")
        print(f"{'='*60}")
        
        total_size = 0
        total_records = 0
        
        for name, df in datasets.items():
            size_mb = df.memory_usage(deep=True).sum() / 1024**2
            total_size += size_mb
            total_records += len(df)
            
            print(f"\n{name.upper()}:")
            print(f"  Records: {len(df):,}")
            print(f"  Colonne: {len(df.columns)}")
            print(f"  Dimensione: {size_mb:.1f} MB")
            
            if 'timestamp' in df.columns:
                print(f"  Periodo: {df['timestamp'].min()} → {df['timestamp'].max()}")
        
        print(f"\n{'='*40}")
        print(f"TOTALE:")
        print(f"  Records totali: {total_records:,}")
        print(f"  Dimensione totale: {total_size:.1f} MB")
        print(f"  Fattore di scala per 270GB: {270*1024/total_size:.1f}x")
        
        # Riferimenti bibliografici
        print(f"\n{'='*40}")
        print("FONTI PARAMETRI:")
        for source, ref in self.config.get_references().items():
            print(f"  • {source}: {ref}")
        
        print(f"{'='*60}\n")