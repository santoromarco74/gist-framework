#!/usr/bin/env python3
"""
ASSA-GDO Algorithm
==================

Attack Surface Score Aggregated per Grande Distribuzione Organizzata.
Quantifica la superficie di attacco considerando vulnerabilità tecniche
e fattori organizzativi specifici del settore retail.

Author: GIST Framework Research
License: MIT
Version: 1.0
"""

import numpy as np
import networkx as nx
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import json

@dataclass
class Node:
    """Rappresenta un nodo nell'infrastruttura GDO"""
    id: str
    type: str  # 'pos', 'server', 'network', 'iot', 'database'
    cvss_score: float
    exposure: float  # 0-1, livello di esposizione
    privileges: Dict[str, float]
    services: List[str]

class ASSA_GDO:
    """
    Attack Surface Score Aggregated per GDO
    Quantifica la superficie di attacco considerando vulnerabilità
    tecniche e fattori organizzativi
    """

    def __init__(self, infrastructure: nx.Graph, org_factor: float = 1.0):
        """
        Inizializza il calcolatore ASSA-GDO

        Args:
            infrastructure: Grafo dell'infrastruttura
            org_factor: Fattore organizzativo (default 1.0)
        """
        self.G = infrastructure
        self.org_factor = org_factor
        self.alpha = 0.73  # Fattore di amplificazione calibrato

    def calculate_assa(self) -> Tuple[float, Dict]:
        """
        Calcola ASSA totale e per componente

        Returns:
            total_assa: Score totale
            component_scores: Dictionary con score per componente
        """
        total_assa = 0
        component_scores = {}

        for node_id in self.G.nodes():
            node = self.G.nodes[node_id]['data']

            # Vulnerabilità base del nodo
            V_i = self._normalize_cvss(node.cvss_score)

            # Esposizione del nodo
            E_i = node.exposure

            # Calcolo propagazione
            propagation_factor = 1.0
            for neighbor_id in self.G.neighbors(node_id):
                edge_data = self.G[node_id][neighbor_id]
                P_ij = edge_data.get('propagation_prob', 0.1)
                propagation_factor *= (1 + self.alpha * P_ij)

            # Score del nodo
            node_score = V_i * E_i * propagation_factor

            # Applicazione fattore organizzativo
            node_score *= self.org_factor

            component_scores[node_id] = node_score
            total_assa += node_score

        return total_assa, component_scores

    def _normalize_cvss(self, cvss: float) -> float:
        """Normalizza CVSS score a range 0-1"""
        return min(cvss / 10.0, 1.0)

    def identify_critical_paths(self, threshold: float = 0.7) -> List[List[str]]:
        """
        Identifica percorsi critici nella rete con alta probabilità
        di propagazione

        Args:
            threshold: Soglia di criticità (default 0.7)

        Returns:
            Lista di percorsi critici
        """
        critical_paths = []

        # Trova nodi ad alta esposizione
        exposed_nodes = [n for n in self.G.nodes()
                        if self.G.nodes[n]['data'].exposure > 0.5]

        # Trova nodi critici (high value targets)
        critical_nodes = [n for n in self.G.nodes()
                         if self.G.nodes[n]['data'].type in ['server', 'database']]

        # Calcola percorsi da nodi esposti a nodi critici
        for source in exposed_nodes:
            for target in critical_nodes:
                if source != target:
                    try:
                        paths = list(nx.all_simple_paths(
                            self.G, source, target, cutoff=5
                        ))
                        for path in paths:
                            path_prob = self._calculate_path_probability(path)
                            if path_prob > threshold:
                                critical_paths.append({
                                    'path': path,
                                    'probability': path_prob,
                                    'risk_score': self._calculate_path_risk(path)
                                })
                    except nx.NetworkXNoPath:
                        continue

        return sorted(critical_paths, key=lambda x: x['risk_score'], reverse=True)

    def _calculate_path_probability(self, path: List[str]) -> float:
        """Calcola probabilità di compromissione lungo un percorso"""
        prob = 1.0
        for i in range(len(path) - 1):
            edge_data = self.G[path[i]][path[i+1]]
            edge_prob = edge_data.get('propagation_prob', 0.1)
            prob *= edge_prob
        return prob

    def _calculate_path_risk(self, path: List[str]) -> float:
        """Calcola rischio aggregato di un percorso"""
        total_risk = 0
        for node_id in path:
            node = self.G.nodes[node_id]['data']
            node_risk = self._normalize_cvss(node.cvss_score) * node.exposure
            total_risk += node_risk
        return total_risk / len(path)

    def recommend_mitigations(self, budget: float = 100000) -> Dict:
        """
        Raccomanda mitigazioni ottimali dato un budget

        Args:
            budget: Budget disponibile in euro

        Returns:
            Dictionary con mitigazioni raccomandate e ROI atteso
        """
        _, component_scores = self.calculate_assa()

        # Ordina componenti per criticità
        sorted_components = sorted(
            component_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        mitigations = []
        remaining_budget = budget
        total_risk_reduction = 0

        for node_id, score in sorted_components[:10]:
            node = self.G.nodes[node_id]['data']

            # Stima costo mitigazione basato su tipo
            mitigation_cost = self._estimate_mitigation_cost(node)

            if mitigation_cost <= remaining_budget:
                # Stima riduzione del rischio
                risk_reduction = score * self._estimate_effectiveness(node)
                roi = (risk_reduction * 100000) / mitigation_cost  # €100k per point

                mitigation = {
                    'node': node_id,
                    'type': node.type,
                    'current_score': round(score, 3),
                    'cost': mitigation_cost,
                    'risk_reduction': round(risk_reduction, 3),
                    'roi': round(roi, 2),
                    'recommendation': self._get_specific_recommendation(node),
                    'priority': 'CRITICAL' if score > 0.8 else 'HIGH' if score > 0.5 else 'MEDIUM'
                }

                mitigations.append(mitigation)
                remaining_budget -= mitigation_cost
                total_risk_reduction += risk_reduction

        return {
            'mitigations': mitigations,
            'total_cost': budget - remaining_budget,
            'total_risk_reduction': round(total_risk_reduction, 3),
            'overall_roi': round((total_risk_reduction * 100000) / (budget - remaining_budget), 2) if budget > remaining_budget else 0,
            'budget_utilization': round((budget - remaining_budget) / budget * 100, 1)
        }

    def _estimate_mitigation_cost(self, node: Node) -> float:
        """Stima costo di mitigazione per tipo di nodo"""
        base_costs = {
            'pos': 500,       # Patch/update POS
            'server': 5000,   # Harden server
            'network': 3000,  # Segment network
            'iot': 200,       # Update firmware
            'database': 8000, # Encrypt and secure DB
        }

        base_cost = base_costs.get(node.type, 1000)

        # Aggiusta per severità
        severity_multiplier = 1 + (node.cvss_score / 10)

        return int(base_cost * severity_multiplier)

    def _estimate_effectiveness(self, node: Node) -> float:
        """Stima efficacia della mitigazione (0-1)"""
        effectiveness_map = {
            'pos': 0.70,      # Patch generalmente efficaci
            'server': 0.80,   # Hardening molto efficace
            'network': 0.85,  # Segmentazione molto efficace
            'iot': 0.60,      # Aggiornamenti IoT limitati
            'database': 0.90  # Encryption molto efficace
        }
        return effectiveness_map.get(node.type, 0.70)

    def _get_specific_recommendation(self, node: Node) -> str:
        """Genera raccomandazione specifica per tipo di nodo"""
        recommendations = {
            'pos': "Aggiornare firmware POS, implementare network segmentation",
            'server': "Hardening OS, patch management automatico, monitoring avanzato",
            'network': "Microsegmentazione, Zero Trust architecture, monitoring traffico",
            'iot': "Aggiornamento firmware, isolamento VLAN, monitoring anomalie",
            'database': "Crittografia at-rest/in-transit, access control, audit logging"
        }
        return recommendations.get(node.type, "Revisione configurazione sicurezza")

    def generate_report(self) -> Dict:
        """Genera report completo ASSA-GDO"""
        total_assa, component_scores = self.calculate_assa()
        critical_paths = self.identify_critical_paths()
        mitigations = self.recommend_mitigations()

        # Analisi distribuzione componenti
        scores_by_type = {}
        for node_id, score in component_scores.items():
            node_type = self.G.nodes[node_id]['data'].type
            if node_type not in scores_by_type:
                scores_by_type[node_type] = []
            scores_by_type[node_type].append(score)

        # Statistiche per tipo
        type_stats = {}
        for node_type, scores in scores_by_type.items():
            type_stats[node_type] = {
                'count': len(scores),
                'mean_score': round(np.mean(scores), 3),
                'max_score': round(np.max(scores), 3),
                'contribution_percent': round(np.sum(scores) / total_assa * 100, 1)
            }

        return {
            'timestamp': np.datetime64('now').astype(str),
            'total_assa_score': round(total_assa, 3),
            'risk_level': self._assess_risk_level(total_assa),
            'components_analyzed': len(component_scores),
            'critical_paths_found': len(critical_paths),
            'top_critical_paths': critical_paths[:5],
            'component_distribution': type_stats,
            'top_vulnerable_components': sorted(
                [(k, v) for k, v in component_scores.items()],
                key=lambda x: x[1], reverse=True
            )[:10],
            'recommended_mitigations': mitigations,
            'org_factor_applied': self.org_factor
        }

    def _assess_risk_level(self, assa_score: float) -> str:
        """Valuta livello di rischio basato su ASSA score"""
        if assa_score < 100:
            return "LOW"
        elif assa_score < 300:
            return "MEDIUM"
        elif assa_score < 600:
            return "HIGH"
        else:
            return "CRITICAL"


def create_sample_infrastructure() -> nx.Graph:
    """Crea infrastruttura di esempio per testing"""
    G = nx.Graph()

    # Definisci nodi di esempio
    nodes = [
        Node('pos_001', 'pos', 6.5, 0.8, {'user': 0.3}, ['payment', 'inventory']),
        Node('pos_002', 'pos', 5.8, 0.7, {'user': 0.3}, ['payment']),
        Node('server_main', 'server', 7.8, 0.3, {'admin': 0.9}, ['api', 'web']),
        Node('db_primary', 'database', 8.2, 0.1, {'admin': 1.0}, ['storage', 'backup']),
        Node('network_core', 'network', 6.1, 0.5, {'admin': 0.7}, ['routing', 'firewall']),
        Node('iot_sensor_1', 'iot', 5.2, 0.9, {'device': 0.1}, ['monitoring']),
        Node('iot_sensor_2', 'iot', 4.8, 0.85, {'device': 0.1}, ['environmental'])
    ]

    # Aggiungi nodi al grafo
    for node in nodes:
        G.add_node(node.id, data=node)

    # Definisci connessioni con probabilità di propagazione
    connections = [
        ('pos_001', 'network_core', 0.6),
        ('pos_002', 'network_core', 0.6),
        ('network_core', 'server_main', 0.7),
        ('server_main', 'db_primary', 0.8),
        ('iot_sensor_1', 'network_core', 0.3),
        ('iot_sensor_2', 'network_core', 0.3),
        ('pos_001', 'server_main', 0.4),  # Connessione diretta per alcuni servizi
    ]

    for source, target, prob in connections:
        G.add_edge(source, target, propagation_prob=prob)

    return G


if __name__ == "__main__":
    # Esempio di utilizzo
    print("=== ASSA-GDO Calculator Demo ===\n")

    # Crea infrastruttura di test
    infrastructure = create_sample_infrastructure()

    # Inizializza calcolatore
    assa_calculator = ASSA_GDO(infrastructure, org_factor=1.2)

    # Genera report completo
    report = assa_calculator.generate_report()

    # Stampa risultati
    print(f"ASSA Score Totale: {report['total_assa_score']}")
    print(f"Livello di Rischio: {report['risk_level']}")
    print(f"Componenti Analizzati: {report['components_analyzed']}")
    print(f"Percorsi Critici Trovati: {report['critical_paths_found']}")

    print("\n=== Top 5 Componenti Vulnerabili ===")
    for i, (node_id, score) in enumerate(report['top_vulnerable_components'][:5], 1):
        print(f"{i}. {node_id}: {score:.3f}")

    print("\n=== Distribuzione per Tipo ===")
    for node_type, stats in report['component_distribution'].items():
        print(f"{node_type.upper()}: {stats['count']} nodi, "
              f"score medio {stats['mean_score']}, "
              f"contributo {stats['contribution_percent']}%")

    print("\n=== Raccomandazioni di Mitigazione ===")
    mitigations = report['recommended_mitigations']
    print(f"Budget utilizzato: €{mitigations['total_cost']:,.0f}")
    print(f"ROI complessivo: {mitigations['overall_roi']:.1f}")

    for i, mitigation in enumerate(mitigations['mitigations'][:3], 1):
        print(f"\n{i}. {mitigation['node']} ({mitigation['priority']})")
        print(f"   Costo: €{mitigation['cost']:,}")
        print(f"   ROI: {mitigation['roi']:.1f}")
        print(f"   Azione: {mitigation['recommendation']}")

    # Salva report completo
    with open('assa_gdo_report.json', 'w') as f:
        json.dump(report, f, indent=2, default=str)

    print(f"\nReport completo salvato in 'assa_gdo_report.json'")