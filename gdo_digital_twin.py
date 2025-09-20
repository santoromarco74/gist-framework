#!/usr/bin/env python3
"""
GDO Digital Twin Framework
==========================

Framework per la generazione di dataset sintetici realistici
nel settore della Grande Distribuzione Organizzata (GDO).

Author: GIST Framework Research
License: MIT
Version: 1.0
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TransactionGenerator:
    """
    Genera transazioni giornaliere con pattern realistici
    calibrati su dati ISTAT 2023
    """

    def __init__(self, config: Dict = None):
        self.config = config or self._default_config()

    def _default_config(self) -> Dict:
        """Configurazione default basata su dati ISTAT"""
        return {
            'store_profiles': {
                'micro': {
                    'avg_daily_transactions': 450,
                    'avg_transaction_value': 18.50,
                    'variance': 0.15
                },
                'piccola': {
                    'avg_daily_transactions': 1200,
                    'avg_transaction_value': 22.30,
                    'variance': 0.18
                },
                'media': {
                    'avg_daily_transactions': 2800,
                    'avg_transaction_value': 28.75,
                    'variance': 0.20
                },
                'grande': {
                    'avg_daily_transactions': 5500,
                    'avg_transaction_value': 35.20,
                    'variance': 0.22
                },
                'enterprise': {
                    'avg_daily_transactions': 12000,
                    'avg_transaction_value': 42.10,
                    'variance': 0.25
                }
            }
        }

    def generate_daily_pattern(self, store_id: str, date: datetime,
                             store_type: str = 'media') -> pd.DataFrame:
        """
        Genera transazioni giornaliere con pattern realistico

        Args:
            store_id: Identificativo del punto vendita
            date: Data per cui generare le transazioni
            store_type: Tipologia di store (micro, piccola, media, grande, enterprise)

        Returns:
            DataFrame con transazioni generate
        """
        profile = self.config['store_profiles'][store_type]
        base_trans = profile['avg_daily_transactions']

        # Fattori moltiplicativi
        day_factor = self._get_day_factor(date.weekday())
        season_factor = self._get_seasonal_factor(date.month)

        # Numero transazioni con variazione stocastica
        n_transactions = int(
            base_trans * day_factor * season_factor *
            np.random.normal(1.0, profile['variance'])
        )

        transactions = []
        for i in range(n_transactions):
            # Distribuzione oraria bimodale (11-13 e 17-20)
            hour = self._generate_bimodal_hour()
            minute = np.random.randint(0, 60)

            transaction = {
                'store_id': store_id,
                'timestamp': date.replace(hour=hour, minute=minute),
                'amount': self._generate_amount_lognormal(
                    profile['avg_transaction_value']
                ),
                'payment_method': self._select_payment_method(),
                'items_count': max(1, np.random.poisson(4.5)),
                'customer_type': self._select_customer_type()
            }
            transactions.append(transaction)

        return pd.DataFrame(transactions)

    def _get_day_factor(self, weekday: int) -> float:
        """Fattore moltiplicativo per giorno della settimana"""
        factors = {
            0: 1.0,    # Lunedì
            1: 0.85,   # Martedì
            2: 0.90,   # Mercoledì
            3: 0.95,   # Giovedì
            4: 1.15,   # Venerdì
            5: 1.35,   # Sabato
            6: 0.75    # Domenica
        }
        return factors.get(weekday, 1.0)

    def _get_seasonal_factor(self, month: int) -> float:
        """Fattore stagionale per mese"""
        factors = {
            1: 0.85, 2: 0.80, 3: 0.95, 4: 1.05,
            5: 1.10, 6: 1.15, 7: 1.20, 8: 1.10,
            9: 1.05, 10: 1.10, 11: 1.25, 12: 1.35
        }
        return factors.get(month, 1.0)

    def _generate_bimodal_hour(self) -> int:
        """Distribuzione bimodale picchi 11-13 e 17-20"""
        if np.random.random() < 0.45:
            # Picco mattutino
            return max(8, min(13, int(np.random.normal(11.5, 1.5))))
        else:
            # Picco serale
            return max(16, min(21, int(np.random.normal(18.5, 1.5))))

    def _generate_amount_lognormal(self, mean_amount: float) -> float:
        """Genera importo con distribuzione log-normale"""
        sigma = 0.6
        mu = np.log(mean_amount) - 0.5 * sigma**2
        amount = np.random.lognormal(mu, sigma)
        return round(max(1.0, amount), 2)

    def _select_payment_method(self) -> str:
        """Seleziona metodo di pagamento secondo distribuzione italiana"""
        methods = ['cash', 'card', 'digital_wallet', 'contactless']
        probabilities = [0.31, 0.45, 0.14, 0.10]
        return np.random.choice(methods, p=probabilities)

    def _select_customer_type(self) -> str:
        """Seleziona tipologia cliente"""
        types = ['regular', 'premium', 'occasional', 'business']
        probabilities = [0.60, 0.15, 0.20, 0.05]
        return np.random.choice(types, p=probabilities)


class SecurityEventGenerator:
    """
    Genera eventi di sicurezza seguendo distribuzione ENISA
    """

    def __init__(self):
        # Distribuzione threat landscape da ENISA 2023
        self.threat_distribution = {
            'malware': 0.28,
            'phishing': 0.22,
            'dos_ddos': 0.15,
            'data_breach': 0.12,
            'insider_threat': 0.08,
            'supply_chain': 0.06,
            'physical_attack': 0.05,
            'other': 0.04
        }

        self.config = {
            'daily_security_events': 8.5,  # Media eventi per punto vendita
            'false_positive_rate': 0.87    # Tasso FP da ENISA
        }

    def generate_security_events(self, n_hours: int, store_id: str) -> pd.DataFrame:
        """
        Genera eventi di sicurezza seguendo processo di Poisson

        Args:
            n_hours: Numero di ore da simulare
            store_id: Identificativo punto vendita

        Returns:
            DataFrame con eventi generati
        """
        events = []
        base_rate = self.config['daily_security_events'] / 24

        for hour in range(n_hours):
            # Poisson non omogeneo con rate variabile
            if hour in [2, 3, 4]:  # Ore notturne
                rate = base_rate * 0.3
            elif hour in [9, 10, 14, 15]:  # Ore di punta
                rate = base_rate * 1.5
            else:
                rate = base_rate

            n_events = np.random.poisson(rate)

            for _ in range(n_events):
                # Genera evento secondo distribuzione ENISA
                threat_type = np.random.choice(
                    list(self.threat_distribution.keys()),
                    p=list(self.threat_distribution.values())
                )

                event = self._create_security_event(threat_type, hour, store_id)

                # Determina se true positive o false positive
                if np.random.random() > self.config['false_positive_rate']:
                    event['is_incident'] = True
                    event['severity'] = self._escalate_severity(event['severity'])
                else:
                    event['is_incident'] = False

                events.append(event)

        return pd.DataFrame(events)

    def _create_security_event(self, threat_type: str, hour: int,
                             store_id: str) -> Dict:
        """Crea evento di sicurezza specifico"""
        severity_map = {
            'malware': 'high',
            'phishing': 'medium',
            'dos_ddos': 'high',
            'data_breach': 'critical',
            'insider_threat': 'medium',
            'supply_chain': 'high',
            'physical_attack': 'medium',
            'other': 'low'
        }

        return {
            'store_id': store_id,
            'timestamp': datetime.now().replace(hour=hour),
            'threat_type': threat_type,
            'severity': severity_map.get(threat_type, 'low'),
            'source_ip': self._generate_ip(),
            'affected_system': self._select_affected_system(),
            'is_incident': False  # Verrà determinato dal chiamante
        }

    def _escalate_severity(self, base_severity: str) -> str:
        """Escalation della severità per incidenti reali"""
        escalation = {
            'low': 'medium',
            'medium': 'high',
            'high': 'critical',
            'critical': 'critical'
        }
        return escalation.get(base_severity, base_severity)

    def _generate_ip(self) -> str:
        """Genera IP address casuale"""
        return f"{np.random.randint(1,255)}.{np.random.randint(1,255)}.{np.random.randint(1,255)}.{np.random.randint(1,255)}"

    def _select_affected_system(self) -> str:
        """Seleziona sistema affetto"""
        systems = ['pos', 'server', 'network', 'database', 'iot_device']
        probabilities = [0.35, 0.25, 0.20, 0.15, 0.05]
        return np.random.choice(systems, p=probabilities)


class GDODigitalTwin:
    """
    Framework principale Digital Twin per GDO
    """

    def __init__(self, config_file: str = None):
        self.transaction_gen = TransactionGenerator()
        self.security_gen = SecurityEventGenerator()

        if config_file:
            with open(config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = self._default_config()

    def _default_config(self) -> Dict:
        """Configurazione default"""
        return {
            'archetipi': {
                'micro': {'count': 87, 'pv_range': (1, 10)},
                'piccola': {'count': 73, 'pv_range': (10, 50)},
                'media': {'count': 42, 'pv_range': (50, 150)},
                'grande': {'count': 25, 'pv_range': (150, 500)},
                'enterprise': {'count': 7, 'pv_range': (500, 2000)}
            }
        }

    def generate_demo_dataset(self, n_stores: int = 10, n_days: int = 30,
                            validate: bool = True, save: bool = False) -> Dict:
        """
        Genera dataset dimostrativo

        Args:
            n_stores: Numero di punti vendita da simulare
            n_days: Numero di giorni da simulare
            validate: Se True, esegue validazione statistica
            save: Se True, salva i dati su file

        Returns:
            Dictionary con dataset generati
        """
        logger.info(f"Generando dataset per {n_stores} store, {n_days} giorni")

        transactions = []
        security_events = []

        start_date = datetime.now() - timedelta(days=n_days)

        for store_idx in range(n_stores):
            store_id = f"store_{store_idx:03d}"
            store_type = self._assign_store_type(store_idx, n_stores)

            for day in range(n_days):
                current_date = start_date + timedelta(days=day)

                # Genera transazioni giornaliere
                daily_trans = self.transaction_gen.generate_daily_pattern(
                    store_id, current_date, store_type
                )
                transactions.append(daily_trans)

                # Genera eventi sicurezza
                daily_events = self.security_gen.generate_security_events(
                    24, store_id
                )
                security_events.append(daily_events)

        # Concatena tutti i dati
        all_transactions = pd.concat(transactions, ignore_index=True)
        all_security_events = pd.concat(security_events, ignore_index=True)

        dataset = {
            'transactions': all_transactions,
            'security_events': all_security_events,
            'generation_timestamp': datetime.now().isoformat(),
            'config': {
                'n_stores': n_stores,
                'n_days': n_days,
                'total_transactions': len(all_transactions),
                'total_security_events': len(all_security_events)
            }
        }

        if validate:
            validation_results = self._validate_dataset(dataset)
            dataset['validation'] = validation_results
            logger.info(f"Validazione: {validation_results['overall_pass_rate']:.1%} test superati")

        if save:
            self._save_dataset(dataset)

        return dataset

    def _assign_store_type(self, store_idx: int, total_stores: int) -> str:
        """Assegna tipologia store secondo distribuzione archetipi"""
        # Distribuzione proporzionale
        ratio = store_idx / total_stores
        if ratio < 0.37:  # 87/234
            return 'micro'
        elif ratio < 0.68:  # 73/234
            return 'piccola'
        elif ratio < 0.86:  # 42/234
            return 'media'
        elif ratio < 0.97:  # 25/234
            return 'grande'
        else:
            return 'enterprise'

    def _validate_dataset(self, dataset: Dict) -> Dict:
        """Validazione statistica del dataset"""
        from scipy import stats

        transactions = dataset['transactions']
        results = {}

        # Test Benford's Law sugli importi
        first_digits = transactions['amount'].apply(
            lambda x: int(str(x).replace('.','').lstrip('0')[0]) if x > 0 else 1
        )

        benford_expected = [np.log10(1 + 1/d) for d in range(1, 10)]
        benford_observed = [
            (first_digits == d).sum() / len(first_digits) for d in range(1, 10)
        ]

        chi2, p_benford = stats.chisquare(benford_observed, benford_expected)
        results['benford_law'] = {'chi2': chi2, 'p_value': p_benford, 'pass': p_benford > 0.05}

        # Test distribuzione oraria (deve essere non-uniforme)
        hourly_dist = transactions['timestamp'].dt.hour.value_counts().sort_index()
        chi2_hour, p_hour = stats.chisquare(hourly_dist.values)
        results['hourly_distribution'] = {'chi2': chi2_hour, 'p_value': p_hour, 'pass': p_hour < 0.05}

        # Completezza dati
        missing_rate = transactions.isnull().sum().sum() / (len(transactions) * len(transactions.columns))
        results['data_completeness'] = {'missing_rate': missing_rate, 'pass': missing_rate < 0.01}

        # Calcola pass rate complessivo
        passed = sum(1 for test in results.values() if test['pass'])
        total = len(results)
        results['overall_pass_rate'] = passed / total

        return results

    def _save_dataset(self, dataset: Dict, prefix: str = "gdo_dataset") -> str:
        """Salva dataset su file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Salva transazioni
        trans_file = f"{prefix}_transactions_{timestamp}.csv"
        dataset['transactions'].to_csv(trans_file, index=False)

        # Salva eventi sicurezza
        events_file = f"{prefix}_security_{timestamp}.csv"
        dataset['security_events'].to_csv(events_file, index=False)

        # Salva metadata
        meta_file = f"{prefix}_metadata_{timestamp}.json"
        metadata = {k: v for k, v in dataset.items()
                   if k not in ['transactions', 'security_events']}

        with open(meta_file, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)

        logger.info(f"Dataset salvato: {trans_file}, {events_file}, {meta_file}")
        return meta_file


if __name__ == "__main__":
    # Esempio di utilizzo
    twin = GDODigitalTwin()

    # Genera dataset demo
    dataset = twin.generate_demo_dataset(
        n_stores=5,
        n_days=7,
        validate=True,
        save=True
    )

    print(f"Dataset generato:")
    print(f"- Transazioni: {len(dataset['transactions']):,}")
    print(f"- Eventi sicurezza: {len(dataset['security_events']):,}")
    print(f"- Validazione: {dataset['validation']['overall_pass_rate']:.1%} test superati")