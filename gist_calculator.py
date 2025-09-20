#!/usr/bin/env python3
"""
GIST Score Calculator
=====================

Calcolatore del GIST Score per valutazione della maturità digitale
nel settore della Grande Distribuzione Organizzata (GDO).

Implementa le formule standard e critica con validazione completa.

Author: GIST Framework Research
License: MIT
Version: 1.0
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Literal
from datetime import datetime
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GISTCalculator:
    """
    Calcolatore del GIST Score per organizzazioni GDO.
    Implementa sia formula standard che critica con validazione completa.
    """

    # Costanti di classe calibrate empiricamente
    WEIGHTS = {
        'physical': 0.18,
        'architectural': 0.32,
        'security': 0.28,
        'compliance': 0.22
    }

    GAMMA = 0.95  # Esponente per rendimenti decrescenti

    MATURITY_LEVELS = [
        (0, 25, "Iniziale", "Infrastruttura legacy, sicurezza reattiva"),
        (25, 50, "In Sviluppo", "Modernizzazione parziale, sicurezza proattiva"),
        (50, 75, "Avanzato", "Architettura moderna, sicurezza integrata"),
        (75, 100, "Ottimizzato", "Trasformazione completa, sicurezza adattiva")
    ]

    # Archetipi per calcolo aggregato (calibrati su 234 organizzazioni)
    ARCHETIPI_WEIGHTS = {
        'micro': 87/234,
        'piccola': 73/234,
        'media': 42/234,
        'grande': 25/234,
        'enterprise': 7/234
    }

    def __init__(self, organization_name: str = ""):
        """
        Inizializza il calcolatore GIST.

        Args:
            organization_name: Nome dell'organizzazione (opzionale)
        """
        self.organization = organization_name
        self.history = []

    def calculate_score(self,
                       scores: Dict[str, float],
                       method: Literal['sum', 'prod'] = 'sum',
                       save_history: bool = True) -> Dict:
        """
        Calcola il GIST Score con metodo specificato.

        Args:
            scores: Dizionario con punteggi delle componenti (0-100)
            method: 'sum' per sommatoria, 'prod' per produttoria
            save_history: Se True, salva il calcolo nella storia

        Returns:
            Dizionario con risultati completi del calcolo

        Raises:
            ValueError: Se input non validi
        """
        # Validazione input
        self._validate_inputs(scores)

        # Calcolo score basato sul metodo
        if method == 'sum':
            gist_score = self._calculate_sum(scores)
        elif method == 'prod':
            gist_score = self._calculate_prod(scores)
        else:
            raise ValueError(f"Metodo non supportato: {method}")

        # Determina livello di maturità
        maturity = self._get_maturity_level(gist_score)

        # Genera analisi dei gap
        gaps = self._analyze_gaps(scores)

        # Genera raccomandazioni
        recommendations = self._generate_recommendations(scores, gist_score)

        # Calcola metriche derivate
        derived_metrics = self._calculate_derived_metrics(scores, gist_score)

        # Prepara risultato
        result = {
            'timestamp': datetime.now().isoformat(),
            'organization': self.organization,
            'score': round(gist_score, 2),
            'method': method,
            'maturity_level': maturity['level'],
            'maturity_description': maturity['description'],
            'components': {k: round(v, 2) for k, v in scores.items()},
            'component_weights': self.WEIGHTS,
            'gaps': gaps,
            'recommendations': recommendations,
            'derived_metrics': derived_metrics
        }

        # Salva nella storia se richiesto
        if save_history:
            self.history.append(result)

        return result

    def calcola_aggregato(self, risultati_archetipi: Dict[str, float]) -> float:
        """
        Calcola GIST aggregato per le 234 organizzazioni dai 5 archetipi

        Args:
            risultati_archetipi: Dict con chiavi archetipi e valori GIST

        Returns:
            GIST Score aggregato ponderato
        """
        gist_aggregato = sum(
            self.ARCHETIPI_WEIGHTS[arch] * risultati_archetipi[arch]
            for arch in self.ARCHETIPI_WEIGHTS.keys()
            if arch in risultati_archetipi
        )

        return round(gist_aggregato, 2)

    def _calculate_sum(self, scores: Dict[str, float]) -> float:
        """Calcola GIST Score con formula sommatoria."""
        return sum(
            self.WEIGHTS[k] * (scores[k] ** self.GAMMA)
            for k in scores.keys()
        )

    def _calculate_prod(self, scores: Dict[str, float]) -> float:
        """Calcola GIST Score con formula produttoria."""
        # Media geometrica pesata
        product = np.prod([
            scores[k] ** self.WEIGHTS[k]
            for k in scores.keys()
        ])

        # Normalizzazione su scala 0-100
        max_possible = 100 ** sum(self.WEIGHTS.values())
        return (product / max_possible) * 100

    def _validate_inputs(self, scores: Dict[str, float]):
        """
        Valida completezza e correttezza degli input.

        Raises:
            ValueError: Se validazione fallisce
        """
        required = set(self.WEIGHTS.keys())
        provided = set(scores.keys())

        # Verifica completezza
        if required != provided:
            missing = required - provided
            extra = provided - required
            msg = []
            if missing:
                msg.append(f"Componenti mancanti: {missing}")
            if extra:
                msg.append(f"Componenti non riconosciute: {extra}")
            raise ValueError(". ".join(msg))

        # Verifica range e tipi
        for component, value in scores.items():
            if not isinstance(value, (int, float)):
                raise ValueError(
                    f"Punteggio {component} deve essere numerico, ricevuto {type(value)}"
                )
            if not 0 <= value <= 100:
                raise ValueError(
                    f"Punteggio {component}={value} fuori range [0,100]"
                )

    def _get_maturity_level(self, score: float) -> Dict[str, str]:
        """Determina livello di maturità basato sullo score."""
        for min_score, max_score, level, description in self.MATURITY_LEVELS:
            if min_score <= score < max_score:
                return {'level': level, 'description': description}
        return {'level': 'Ottimizzato', 'description': self.MATURITY_LEVELS[-1][3]}

    def _analyze_gaps(self, scores: Dict[str, float]) -> Dict:
        """Analizza gap rispetto ai target ottimali."""
        # Target basati su best practice del settore
        targets = {
            'physical': 85,
            'architectural': 88,
            'security': 82,
            'compliance': 86
        }

        gaps = {}
        for component, current in scores.items():
            target = targets[component]
            gap = target - current
            gaps[component] = {
                'current': round(current, 2),
                'target': target,
                'gap': round(gap, 2),
                'gap_percentage': round((gap / target) * 100, 1) if gap > 0 else 0
            }

        return gaps

    def _generate_recommendations(self,
                                 scores: Dict[str, float],
                                 total_score: float) -> List[Dict]:
        """
        Genera raccomandazioni prioritizzate basate sui punteggi.

        Returns:
            Lista di raccomandazioni con priorità e impatto stimato
        """
        recommendations = []

        # Identifica componenti critiche (sotto soglia)
        critical_threshold = 50
        medium_threshold = 70

        for component, score in scores.items():
            if score < medium_threshold:
                if score < critical_threshold:
                    priority = "CRITICA"
                else:
                    priority = "ALTA"

                rec = {
                    'priority': priority,
                    'component': component,
                    'current_score': round(score, 2),
                    'recommendation': self._get_specific_recommendation(component, score),
                    'estimated_impact': self._estimate_impact(component, score),
                    'effort_required': self._estimate_effort(component, score)
                }
                recommendations.append(rec)

        # Ordina per priorità e impatto
        priority_order = {"CRITICA": 3, "ALTA": 2, "MEDIA": 1}
        recommendations.sort(
            key=lambda x: (priority_order.get(x['priority'], 0), x['estimated_impact']),
            reverse=True
        )

        return recommendations

    def _get_specific_recommendation(self, component: str, score: float) -> str:
        """Genera raccomandazione specifica per componente."""
        recommendations_map = {
            'physical': {
                'low': "Urgente: Upgrade infrastruttura fisica - UPS, cooling, connettività fiber",
                'medium': "Migliorare ridondanza e capacità - dual power, N+1 cooling",
                'high': "Ottimizzare efficienza energetica - PUE target < 1.5"
            },
            'architectural': {
                'low': "Avviare migrazione cloud - hybrid cloud pilot per servizi non critici",
                'medium': "Espandere adozione cloud - multi-cloud strategy, containerization",
                'high': "Implementare cloud-native completo - serverless, edge computing"
            },
            'security': {
                'low': "Implementare controlli base - firewall NG, EDR, patch management",
                'medium': "Evolvere verso Zero Trust - microsegmentazione, SIEM/SOAR",
                'high': "Security operations avanzate - threat hunting, deception technology"
            },
            'compliance': {
                'low': "Stabilire framework compliance - policy, procedure, training base",
                'medium': "Automatizzare compliance - GRC platform, continuous monitoring",
                'high': "Compliance-as-code - policy automation, real-time attestation"
            }
        }

        level = 'low' if score < 40 else 'medium' if score < 70 else 'high'
        return recommendations_map.get(component, {}).get(level, "Miglioramento generale richiesto")

    def _estimate_impact(self, component: str, current_score: float) -> float:
        """
        Stima l'impatto potenziale del miglioramento di una componente.

        Returns:
            Impatto stimato sul GIST Score totale (0-100)
        """
        # Calcola delta potenziale (target - current)
        targets = {'physical': 85, 'architectural': 88, 'security': 82, 'compliance': 86}
        target = targets.get(component, 85)
        delta = max(0, target - current_score)

        # Peso della componente
        weight = self.WEIGHTS[component]

        # Stima impatto considerando non-linearità
        impact = weight * (delta ** self.GAMMA)

        return min(round(impact, 1), 100)

    def _estimate_effort(self, component: str, current_score: float) -> str:
        """Stima lo sforzo richiesto per il miglioramento"""
        if current_score < 30:
            return "ALTO"
        elif current_score < 60:
            return "MEDIO"
        else:
            return "BASSO"

    def _calculate_derived_metrics(self,
                                  scores: Dict[str, float],
                                  gist_score: float) -> Dict:
        """
        Calcola metriche derivate dal GIST Score.

        Returns:
            Dizionario con metriche operative stimate
        """
        # Formule empiriche calibrate su dati di settore
        availability = 99.0 + (gist_score / 100) * 0.95  # 99.0% - 99.95%

        # ASSA Score inversamente correlato
        assa_score = 1000 * np.exp(-gist_score / 40)

        # MTTR in ore
        mttr_hours = 24 * np.exp(-gist_score / 30)

        # Compliance coverage
        compliance_coverage = 50 + (scores['compliance'] / 100) * 50

        # Security incidents annuali attesi
        incidents_per_year = 100 * np.exp(-scores['security'] / 25)

        # Cost efficiency index
        cost_efficiency = gist_score / 100 * 0.8 + 0.2

        return {
            'estimated_availability': round(availability, 3),
            'estimated_assa_score': round(assa_score, 0),
            'estimated_mttr_hours': round(mttr_hours, 1),
            'compliance_coverage_percent': round(compliance_coverage, 1),
            'expected_incidents_per_year': round(incidents_per_year, 1),
            'cost_efficiency_index': round(cost_efficiency, 3)
        }

    def compare_scenarios(self,
                         scenarios: Dict[str, Dict[str, float]]) -> pd.DataFrame:
        """
        Confronta multipli scenari e genera report comparativo.

        Args:
            scenarios: Dizionario nome_scenario -> scores

        Returns:
            DataFrame con confronto dettagliato
        """
        results = []

        for name, scores in scenarios.items():
            result = self.calculate_score(scores, save_history=False)
            results.append({
                'Scenario': name,
                'GIST Score': result['score'],
                'Maturity': result['maturity_level'],
                'Physical': result['components']['physical'],
                'Architectural': result['components']['architectural'],
                'Security': result['components']['security'],
                'Compliance': result['components']['compliance'],
                'Availability': result['derived_metrics']['estimated_availability'],
                'ASSA': result['derived_metrics']['estimated_assa_score'],
                'MTTR (h)': result['derived_metrics']['estimated_mttr_hours']
            })

        df = pd.DataFrame(results)
        df = df.sort_values('GIST Score', ascending=False)

        return df

    def export_report(self, result: Dict, filename: str = None) -> str:
        """
        Esporta report dettagliato in formato JSON.

        Args:
            result: Risultato del calcolo GIST
            filename: Nome file output (opzionale)

        Returns:
            Path del file salvato
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            org_name = self.organization.replace(" ", "_") if self.organization else "org"
            filename = f"gist_report_{org_name}_{timestamp}.json"

        with open(filename, 'w') as f:
            json.dump(result, f, indent=2, default=str)

        logger.info(f"Report salvato: {filename}")
        return filename

    def get_history_summary(self) -> pd.DataFrame:
        """Ritorna summary della storia dei calcoli"""
        if not self.history:
            return pd.DataFrame()

        summary_data = []
        for entry in self.history:
            summary_data.append({
                'Timestamp': entry['timestamp'],
                'Score': entry['score'],
                'Method': entry['method'],
                'Maturity': entry['maturity_level'],
                'Physical': entry['components']['physical'],
                'Architectural': entry['components']['architectural'],
                'Security': entry['components']['security'],
                'Compliance': entry['components']['compliance']
            })

        return pd.DataFrame(summary_data)


def run_demo():
    """Esempio di utilizzo del GIST Calculator."""

    print("=" * 60)
    print("DEMO GIST CALCULATOR")
    print("=" * 60)

    # Inizializza calcolatore
    calc = GISTCalculator("Demo Organization")

    # Definisci scenari di esempio
    scenarios = {
        "Baseline (AS-IS)": {
            'physical': 42,
            'architectural': 38,
            'security': 45,
            'compliance': 52
        },
        "Quick Wins (6 mesi)": {
            'physical': 55,
            'architectural': 45,
            'security': 58,
            'compliance': 65
        },
        "Trasformazione (18 mesi)": {
            'physical': 68,
            'architectural': 72,
            'security': 70,
            'compliance': 75
        },
        "Target (36 mesi)": {
            'physical': 85,
            'architectural': 88,
            'security': 82,
            'compliance': 86
        }
    }

    # Calcola e confronta scenari
    for scenario_name, scores in scenarios.items():
        print(f"\n### {scenario_name} ###")

        # Calcola con entrambi i metodi
        result_sum = calc.calculate_score(scores, method='sum')
        result_prod = calc.calculate_score(scores, method='prod')

        print(f"GIST Score (standard): {result_sum['score']:.2f}")
        print(f"GIST Score (critico):  {result_prod['score']:.2f}")
        print(f"Livello Maturità: {result_sum['maturity_level']}")

        # Mostra metriche derivate
        metrics = result_sum['derived_metrics']
        print(f"Disponibilità stimata: {metrics['estimated_availability']:.3f}%")
        print(f"ASSA Score stimato: {metrics['estimated_assa_score']:.0f}")
        print(f"MTTR stimato: {metrics['estimated_mttr_hours']:.1f} ore")

        # Mostra top recommendation
        if result_sum['recommendations']:
            top_rec = result_sum['recommendations'][0]
            print(f"Raccomandazione prioritaria: [{top_rec['priority']}] {top_rec['component']}")

    # Confronto tabellare
    print(f"\n{'='*60}")
    print("CONFRONTO SCENARI")
    print(f"{'='*60}")
    df_comparison = calc.compare_scenarios(scenarios)
    print(df_comparison.to_string(index=False))

    # Calcolo aggregato per archetipi
    print(f"\n{'='*60}")
    print("CALCOLO AGGREGATO ARCHETIPI")
    print(f"{'='*60}")

    archetipi_results = {
        'micro': 35.2,
        'piccola': 48.7,
        'media': 62.1,
        'grande': 73.5,
        'enterprise': 81.3
    }

    gist_aggregato = calc.calcola_aggregato(archetipi_results)
    print(f"GIST Score aggregato (234 organizzazioni): {gist_aggregato}")

    # Salva report finale
    final_result = calc.calculate_score(scenarios["Target (36 mesi)"])
    report_file = calc.export_report(final_result)
    print(f"\nReport completo salvato: {report_file}")


if __name__ == "__main__":
    run_demo()