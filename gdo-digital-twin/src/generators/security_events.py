"""
Generatore eventi di sicurezza calibrato su threat landscape reale
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import uuid
import random  # FIX: aggiunto import
import hashlib  # FIX: aggiunto import
from typing import Dict, List

class SecurityEventGenerator:
    """Simula eventi di sicurezza realistici per ambiente GDO"""
    
    def __init__(self, config: Dict):
        self.config = config['security_baseline']
        np.random.seed(42)
        
        # Severity levels CVSS-based
        self.severity_levels = {
            'critical': {'range': (9.0, 10.0), 'prob': 0.02},
            'high': {'range': (7.0, 8.9), 'prob': 0.08},
            'medium': {'range': (4.0, 6.9), 'prob': 0.25},
            'low': {'range': (0.1, 3.9), 'prob': 0.35},
            'info': {'range': (0.0, 0.0), 'prob': 0.30}
        }
    
    def generate_security_events(
        self,
        n_hours: int = 24,
        store_id: int = 1,
        include_incidents: bool = True
    ) -> pd.DataFrame:
        """
        Genera eventi di sicurezza per periodo specificato
        
        Args:
            n_hours: Numero di ore da simulare  
            store_id: ID del punto vendita
            include_incidents: Se includere incidenti reali (non solo FP)
        
        Returns:
            DataFrame con eventi di sicurezza
        """
        
        events = []
        base_rate = self.config['daily_security_events'] / 24
        
        for hour in range(n_hours):
            # Eventi nell'ora (distribuzione Poisson)
            n_events = np.random.poisson(base_rate)
            
            for _ in range(n_events):
                event = self._generate_single_event(hour, store_id)
                
                # Determina se è un vero incidente o false positive
                if include_incidents and np.random.random() > self.config['false_positive_rate']:
                    event['is_incident'] = True
                    event['requires_action'] = True
                    # Aumenta severity per incidenti reali
                    if event['severity'] in ['low', 'info']:
                        event['severity'] = 'medium'
                else:
                    event['is_incident'] = False
                    event['requires_action'] = False
                
                events.append(event)
        
        df = pd.DataFrame(events)
        
        # Aggiungi correlazioni realistiche
        df = self._add_correlations(df)
        
        return df
    
    def _generate_single_event(self, hour: int, store_id: int) -> Dict:
        """Genera singolo evento di sicurezza"""
        
        # Seleziona tipo di threat
        threat_types = list(self.config['threat_distribution'].keys())
        threat_probs = list(self.config['threat_distribution'].values())
        threat_type = np.random.choice(threat_types, p=threat_probs)
        
        # Genera severity
        severity = self._generate_severity()
        
        # Timestamp con minuti/secondi random
        timestamp = datetime.now() - timedelta(hours=hour)
        timestamp += timedelta(
            minutes=np.random.randint(0, 60),
            seconds=np.random.randint(0, 60)
        )
        
        event = {
            'event_id': str(uuid.uuid4()),
            'timestamp': timestamp,
            'store_id': f'ST{store_id:03d}',
            'threat_type': threat_type,
            'severity': severity,
            'severity_score': self._get_severity_score(severity),
            'source_ip': self._generate_ip(),
            'destination_ip': f'10.{store_id}.{np.random.randint(1,255)}.{np.random.randint(1,255)}',
            'source_port': np.random.randint(1024, 65535),
            'destination_port': self._get_common_port(threat_type),
            'protocol': np.random.choice(['TCP', 'UDP', 'ICMP'], p=[0.7, 0.2, 0.1]),
            'detection_method': np.random.choice(['IDS', 'Firewall', 'SIEM', 'EDR'], p=[0.3, 0.3, 0.25, 0.15]),
            'confidence_score': np.random.beta(8, 2),  # Skewed verso alta confidence
            'bytes_transferred': int(np.random.lognormal(10, 2)),
            'packets_count': np.random.poisson(50)
        }
        
        # Aggiungi dettagli specifici per threat type
        event.update(self._get_threat_details(threat_type))
        
        return event
    
    def _generate_severity(self) -> str:
        """Genera severity level realistico"""
        severities = list(self.severity_levels.keys())
        probs = [self.severity_levels[s]['prob'] for s in severities]
        return np.random.choice(severities, p=probs)
    
    def _get_severity_score(self, severity: str) -> float:
        """Converte severity in score numerico CVSS"""
        range_min, range_max = self.severity_levels[severity]['range']
        if range_min == range_max:
            return 0.0
        return round(np.random.uniform(range_min, range_max), 1)
    
    def _generate_ip(self) -> str:
        """Genera IP sorgente realistico"""
        # 70% IP privati (insider/lateral), 30% pubblici (esterni)
        if np.random.random() < 0.7:
            return f"192.168.{np.random.randint(1,255)}.{np.random.randint(1,255)}"
        else:
            # IP pubblici comuni per attacchi
            malicious_ranges = [
                "185.220",  # TOR exit nodes
                "45.142",   # Hosting providers
                "89.248",   # Scanner networks
                "194.165"   # Compromised servers
            ]
            prefix = np.random.choice(malicious_ranges)
            return f"{prefix}.{np.random.randint(1,255)}.{np.random.randint(1,255)}"
    
    def _get_common_port(self, threat_type: str) -> int:
        """Ritorna porta comune per tipo di minaccia"""
        port_map = {
            'malware': [445, 3389, 22, 23],  # SMB, RDP, SSH, Telnet
            'phishing': [80, 443, 25, 587],  # HTTP, HTTPS, SMTP
            'dos': [80, 443, 53, 3306],      # Web, DNS, MySQL
            'insider': [445, 1433, 3306, 5432],  # File shares, DBs
            'misconfiguration': [22, 3389, 8080, 8443],  # Admin ports
            'other': [np.random.randint(1, 65535)]  # Usa np.random invece di random
        }
        return np.random.choice(port_map.get(threat_type, [443]))
    
    def _get_threat_details(self, threat_type: str) -> Dict:
        """Dettagli specifici per tipo di threat"""
        details = {
            'malware': {
                'malware_family': np.random.choice(['Emotet', 'TrickBot', 'Ryuk', 'Cobalt Strike']),
                'file_hash': hashlib.md5(str(uuid.uuid4()).encode()).hexdigest(),
                'process_name': np.random.choice(['svchost.exe', 'chrome.exe', 'update.exe'])
            },
            'phishing': {
                'sender_email': f"noreply@{np.random.choice(['amaz0n', 'paypaI', 'microsoft-support'])}.com",
                'subject_keywords': np.random.choice(['urgent', 'verify account', 'suspended']),
                'url_reputation': np.random.uniform(0, 30)
            },
            'dos': {
                'attack_type': np.random.choice(['SYN Flood', 'UDP Flood', 'HTTP Flood']),
                'requests_per_second': np.random.randint(1000, 50000),
                'source_country': np.random.choice(['CN', 'RU', 'US', 'NL'])
            },
            'insider': {
                'user_id': f"USR{np.random.randint(1000, 9999)}",
                'access_time': np.random.choice(['after_hours', 'weekend', 'normal']),
                'data_exfiltration_mb': np.random.lognormal(2, 1.5) if np.random.random() < 0.3 else 0
            },
            'misconfiguration': {
                'config_type': np.random.choice(['open_port', 'weak_password', 'missing_patch']),
                'cve_id': f"CVE-2024-{np.random.randint(10000, 99999)}" if np.random.random() < 0.4 else None,
                'exposure_level': np.random.choice(['internal', 'external'])
            }
        }
        return details.get(threat_type, {})
    
    def _add_correlations(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aggiunge correlazioni realistiche tra eventi"""
        
        if len(df) < 2:
            return df
        
        # Attacchi tendono a raggrupparsi temporalmente
        df['cluster_id'] = 0
        cluster_id = 1
        last_incident_time = None
        
        for idx, row in df.iterrows():
            if row['is_incident']:
                if last_incident_time and (row['timestamp'] - last_incident_time).seconds < 3600:
                    # Stesso cluster se entro 1 ora
                    df.at[idx, 'cluster_id'] = cluster_id
                else:
                    cluster_id += 1
                    df.at[idx, 'cluster_id'] = cluster_id
                last_incident_time = row['timestamp']
        
        # Kill chain stages per incident clusters
        kill_chain_stages = ['reconnaissance', 'weaponization', 'delivery', 
                           'exploitation', 'installation', 'command_control', 'actions']
        
        for cluster in df['cluster_id'].unique():
            if cluster > 0:
                cluster_events = df[df['cluster_id'] == cluster].index
                n_stages = min(len(cluster_events), len(kill_chain_stages))
                stages = np.random.choice(kill_chain_stages, n_stages, replace=False)
                
                for i, idx in enumerate(cluster_events[:n_stages]):
                    df.at[idx, 'kill_chain_stage'] = stages[i]
        
        return df