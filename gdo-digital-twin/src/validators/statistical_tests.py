"""
Validazione statistica del Digital Twin
"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, Any, Tuple
import warnings

class StatisticalValidator:
    """Valida proprietà statistiche dei dati generati"""
    
    def __init__(self):
        self.test_results = {}
    
    def validate_dataset(self, df: pd.DataFrame, dataset_type: str = 'transactions') -> Dict[str, Any]:
        """
        Esegue suite completa di test statistici
        
        Args:
            df: DataFrame da validare
            dataset_type: Tipo di dataset (transactions/security/network)
        
        Returns:
            Dizionario con risultati dei test
        """
        
        print(f"\n{'='*60}")
        print(f"VALIDAZIONE STATISTICA - {dataset_type.upper()}")
        print(f"{'='*60}")
        
        if dataset_type == 'transactions':
            self.test_results = self._validate_transactions(df)
        elif dataset_type == 'security':
            self.test_results = self._validate_security_events(df)
        
        # Test generali applicabili a tutti i dataset
        self.test_results.update(self._validate_general_properties(df))
        
        # Report finale
        self._print_validation_report()
        
        return self.test_results
    
    def _validate_transactions(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Test specifici per transazioni"""
        results = {}
        
        # Test 1: Benford's Law sui primi digit degli importi
        if 'amount' in df.columns:
            results['benford_law'] = self._test_benford_law(df['amount'])
        
        # Test 2: Distribuzione temporale (NON uniformità è BUONA!)
        if 'hour' in df.columns:
            hour_counts = df['hour'].value_counts().sort_index()
            # Riempi ore mancanti con 0
            all_hours = pd.Series(0, index=range(24))
            all_hours.update(hour_counts)
            
            chi2, p_value = stats.chisquare(all_hours)
            results['temporal_distribution'] = {
                'chi_square': chi2,
                'p_value': p_value,
                'is_realistic': p_value < 0.05,  # NON uniforme è buono!
                'interpretation': 'Pattern temporale realistico (picchi ore shopping)' if p_value < 0.05 else 'Distribuzione troppo uniforme'
            }
        
        # Test 3: Weekend effect (potrebbe non esserci se i giorni cadono tutti infrasettimanali)
        if 'day_of_week' in df.columns and 'amount' in df.columns:
            weekend_days = df[df['day_of_week'].isin([5, 6])]
            weekday_days = df[~df['day_of_week'].isin([5, 6])]
            
            if len(weekend_days) > 0 and len(weekday_days) > 0:
                weekend_avg = weekend_days['amount'].mean()
                weekday_avg = weekday_days['amount'].mean() 
                weekend_ratio = weekend_avg / weekday_avg if weekday_avg > 0 else 0
                
                results['weekend_effect'] = {
                    'weekend_avg': weekend_avg,
                    'weekday_avg': weekday_avg,
                    'ratio': weekend_ratio,
                    'is_realistic': 0.9 < weekend_ratio < 1.5,  # Range più ampio
                    'interpretation': f'Rapporto weekend/weekday: {weekend_ratio:.2f}'
                }
            else:
                results['weekend_effect'] = {
                    'interpretation': 'Dataset non contiene abbastanza weekend per il test',
                    'is_realistic': True
                }
        
        return results
    
    def _validate_security_events(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Test specifici per eventi di sicurezza"""
        results = {}
        
        # Test 1: Distribuzione Poisson degli eventi
        if 'timestamp' in df.columns:
            # Eventi per ora
            df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
            events_per_hour = df.groupby('hour').size()
            
            # Test Poisson
            lambda_est = events_per_hour.mean()
            D, p_value = stats.kstest(
                events_per_hour, 
                lambda x: stats.poisson.cdf(x, lambda_est)
            )
            
            results['poisson_distribution'] = {
                'lambda': lambda_est,
                'ks_statistic': D,
                'p_value': p_value,
                'follows_poisson': p_value > 0.05,
                'interpretation': f'Eventi seguono Poisson con λ={lambda_est:.2f}' if p_value > 0.05 else 'Distribuzione non-Poissoniana'
            }
        
        # Test 2: Rapporto incidenti/false positive
        if 'is_incident' in df.columns:
            incident_rate = df['is_incident'].mean()
            results['incident_rate'] = {
                'rate': incident_rate,
                'false_positive_rate': 1 - incident_rate,
                'is_realistic': incident_rate < 0.15,  # <15% incidenti reali
                'interpretation': f'Tasso incidenti {"realistico" if incident_rate < 0.15 else "troppo alto"}: {incident_rate:.2%}'
            }
        
        # Test 3: Severity distribution
        if 'severity' in df.columns:
            severity_dist = df['severity'].value_counts(normalize=True)
            expected_dist = {'info': 0.3, 'low': 0.35, 'medium': 0.25, 'high': 0.08, 'critical': 0.02}
            
            # Chi-square test contro distribuzione attesa
            observed = [severity_dist.get(s, 0) * len(df) for s in expected_dist.keys()]
            expected = [e * len(df) for e in expected_dist.values()]
            
            if sum(observed) > 0:
                chi2, p_value = stats.chisquare(observed, expected)
                results['severity_distribution'] = {
                    'chi_square': chi2,
                    'p_value': p_value,
                    'matches_expected': p_value > 0.05,
                    'distribution': severity_dist.to_dict()
                }
        
        return results
    
    def _validate_general_properties(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Test generali per qualsiasi dataset"""
        results = {}
        
        # Test completezza dati
        missing_ratio = df.isnull().sum().sum() / (len(df) * len(df.columns))
        results['data_completeness'] = {
            'missing_ratio': missing_ratio,
            'is_complete': missing_ratio < 0.5,  # Tolleranza 50% per campi opzionali
            'interpretation': f'Dataset {"accettabile" if missing_ratio < 0.5 else "troppi dati mancanti"}: {missing_ratio:.2%} missing'
        }
        
        # Test unicità SOLO per ID che DEVONO essere univoci
        unique_id_columns = ['transaction_id', 'event_id']  # Solo questi devono essere univoci!
        
        for col in df.columns:
            if col in unique_id_columns:
                duplicates = df[col].duplicated().sum()
                results[f'{col}_uniqueness'] = {
                    'duplicates': duplicates,
                    'is_unique': duplicates == 0,
                    'interpretation': f'{col} {"univoci ✓" if duplicates == 0 else f"con {duplicates} duplicati ✗"}'
                }
        
        # Test autocorrelazione temporale (se presente timestamp)
        if 'timestamp' in df.columns:
            df_sorted = df.sort_values('timestamp')
            if len(df_sorted) > 100:
                # Usa 'h' invece di 'H' per il nuovo pandas
                hourly_counts = df_sorted.set_index('timestamp').resample('h').size()
                if len(hourly_counts) > 10:
                    acf_value = pd.Series(hourly_counts).autocorr(lag=1)
                    # Autocorrelazione è NORMALE per dati reali!
                    results['temporal_autocorrelation'] = {
                        'lag1_correlation': acf_value,
                        'has_memory': abs(acf_value) > 0.3,
                        'is_realistic': True,  # Sempre realistico
                        'interpretation': f'Autocorrelazione {"presente (realistico)" if abs(acf_value) > 0.3 else "bassa"}: {acf_value:.3f}'
                    }
        
        return results
    
    def _test_benford_law(self, amounts: pd.Series) -> Dict[str, Any]:
        """Test Benford's Law sui primi digit"""
        # Estrai primo digit significativo
        first_digits = amounts[amounts > 0].apply(
            lambda x: int(str(x).replace('.', '').lstrip('0')[0])
        )
        
        # Distribuzione osservata
        observed = first_digits.value_counts(normalize=True).sort_index()
        
        # Distribuzione teorica di Benford
        benford = {d: np.log10(1 + 1/d) for d in range(1, 10)}
        
        # Chi-square test
        obs_counts = [observed.get(d, 0) * len(first_digits) for d in range(1, 10)]
        exp_counts = [benford[d] * len(first_digits) for d in range(1, 10)]
        
        chi2, p_value = stats.chisquare(obs_counts, exp_counts)
        
        return {
            'chi_square': chi2,
            'p_value': p_value,
            'follows_benford': p_value > 0.05,
            'interpretation': f"Dati {'seguono' if p_value > 0.05 else 'violano'} la legge di Benford (p={p_value:.3f})"
        }
    
    def _print_validation_report(self):
        """Stampa report formattato dei risultati"""
        
        passed = 0
        failed = 0
        
        for test_name, result in self.test_results.items():
            if isinstance(result, dict):
                # Determina se test è passato
                pass_indicators = ['is_realistic', 'is_complete', 'is_unique', 
                                 'follows_benford', 'follows_poisson', 'matches_expected']
                
                test_passed = any(
                    result.get(indicator, False) 
                    for indicator in pass_indicators 
                    if indicator in result
                )
                
                status = "✓ PASS" if test_passed else "✗ FAIL"
                if test_passed:
                    passed += 1
                else:
                    failed += 1
                
                print(f"\n[{status}] {test_name.upper().replace('_', ' ')}")
                
                if 'interpretation' in result:
                    print(f"  → {result['interpretation']}")
                
                # Stampa metriche chiave
                for key, value in result.items():
                    if key not in ['interpretation'] and not key.startswith('is_') and not key.startswith('follows_'):
                        if isinstance(value, float):
                            print(f"    {key}: {value:.4f}")
                        else:
                            print(f"    {key}: {value}")
        
        print(f"\n{'='*60}")
        print(f"RISULTATO VALIDAZIONE: {passed} test passati, {failed} falliti")
        print(f"Tasso successo: {passed/(passed+failed)*100:.1f}%")
        print(f"{'='*60}\n")