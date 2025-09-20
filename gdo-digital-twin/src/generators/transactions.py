"""
Generatore di transazioni POS realistiche
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import hashlib

class TransactionGenerator:
    """Genera transazioni POS sintetiche ma realistiche"""
    
    def __init__(self, config: Dict):
        self.config = config
        np.random.seed(42)  # Riproducibilità
        
    def generate_daily_transactions(
        self, 
        store_id: int, 
        date: datetime, 
        store_type: str = 'medium'
    ) -> pd.DataFrame:
        """
        Genera transazioni per un singolo giorno
        
        Args:
            store_id: ID del punto vendita
            date: Data di riferimento
            store_type: Tipologia store (small/medium/large)
        
        Returns:
            DataFrame con transazioni del giorno
        """
        
        profile = self.config['store_profiles'][store_type]
        base_transactions = profile['avg_daily_transactions']
        
        # Variazione per giorno della settimana
        day_name = date.strftime('%A').lower()
        if day_name in ['saturday', 'sunday']:
            day_factor = 1.3
        elif day_name == 'friday':
            day_factor = 1.2
        else:
            day_factor = 0.95
        
        # Variazione stagionale
        month = date.strftime('%B').lower()
        season_factor = self.config['temporal_patterns']['seasonal_factors'].get(month, 1.0)
        
        # Numero totale di transazioni con variazione stocastica
        n_transactions = int(
            base_transactions * day_factor * season_factor * 
            np.random.normal(1.0, 0.1)
        )
        
        transactions = []
        
        for i in range(n_transactions):
            # Distribuzione oraria realistica
            hour = self._generate_hour_distribution()
            minute = np.random.randint(0, 60)
            second = np.random.randint(0, 60)
            
            timestamp = datetime(
                date.year, date.month, date.day,
                hour, minute, second
            )
            
            # Genera dettagli transazione
            transaction = {
                'transaction_id': self._generate_transaction_id(store_id, timestamp, i),
                'store_id': f'ST{store_id:03d}',
                'timestamp': timestamp,
                'amount': self._generate_amount(profile['avg_transaction_value']),
                'payment_method': self._select_payment_method(),
                'items_count': np.random.poisson(4.5) + 1,  # Media 5.5 articoli
                'pos_terminal': f'POS{np.random.randint(1, 11):02d}',
                'cashier_id': f'CSH{np.random.randint(1, profile["employees"]+1):03d}',
                'customer_type': np.random.choice(['regular', 'member', 'new'], p=[0.6, 0.3, 0.1]),
                'discount_applied': np.random.random() < 0.15,  # 15% con sconto
                'processing_time_ms': int(np.random.gamma(2, 500))  # Tempo elaborazione
            }
            
            transactions.append(transaction)
        
        df = pd.DataFrame(transactions)
        
        # Aggiungi metriche derivate
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['is_peak_hour'] = df['hour'].isin(self.config['temporal_patterns']['peak_hours'])
        
        return df
    
    def _generate_hour_distribution(self) -> int:
        """Genera ora con distribuzione bimodale (picchi mattina/sera)"""
        # Mistura di due gaussiane per i picchi
        if np.random.random() < 0.45:
            # Picco mattutino (10-13)
            hour = int(np.random.normal(11.5, 1.5))
        else:
            # Picco serale (17-20)
            hour = int(np.random.normal(18.5, 1.5))
        
        # Assicura range valido 8-21 (orario negozio)
        return np.clip(hour, 8, 21)
    
    def _generate_amount(self, avg_value: float) -> float:
        """Genera importo transazione con distribuzione log-normale"""
        # Log-normale per simulare molte transazioni piccole e poche grandi
        amount = np.random.lognormal(np.log(avg_value), 0.6)
        return round(amount, 2)
    
    def _select_payment_method(self) -> str:
        """Seleziona metodo di pagamento secondo distribuzione configurata"""
        methods = list(self.config['payment_methods'].keys())
        probs = list(self.config['payment_methods'].values())
        return np.random.choice(methods, p=probs)
    
    def _generate_transaction_id(self, store_id: int, timestamp: datetime, seq: int) -> str:
        """Genera ID transazione univoco e verificabile"""
        data = f"{store_id}{timestamp.isoformat()}{seq}"
        return hashlib.sha256(data.encode()).hexdigest()[:16].upper()
    
    def generate_batch(
        self, 
        n_stores: int = 5, 
        n_days: int = 30,
        store_types: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Genera batch di transazioni per multiple stores e giorni
        
        Args:
            n_stores: Numero di punti vendita
            n_days: Numero di giorni da simulare
            store_types: Lista tipologie store (se None, random)
        
        Returns:
            DataFrame completo con tutte le transazioni
        """
        
        if store_types is None:
            # Mix realistico: più piccoli, meno grandi
            store_types = np.random.choice(
                ['small', 'medium', 'large'],
                size=n_stores,
                p=[0.5, 0.35, 0.15]
            )
        
        all_transactions = []
        
        for store_id in range(n_stores):
            store_type = store_types[store_id] if store_id < len(store_types) else 'medium'
            
            for day_offset in range(n_days):
                date = datetime.now() - timedelta(days=day_offset)
                daily_trans = self.generate_daily_transactions(
                    store_id, 
                    date, 
                    store_type
                )
                all_transactions.append(daily_trans)
        
        result = pd.concat(all_transactions, ignore_index=True)
        result = result.sort_values('timestamp')
        
        print(f"✓ Generate {len(result):,} transazioni per {n_stores} store in {n_days} giorni")
        print(f"  Dimensione dataset: {result.memory_usage(deep=True).sum() / 1024**2:.1f} MB")
        
        return result