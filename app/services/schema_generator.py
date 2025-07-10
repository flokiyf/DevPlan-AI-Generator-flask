# -*- coding: utf-8 -*-
"""
Service de génération de schémas avancés pour DevPlan AI Generator.
Gère la création de schémas techniques détaillés, architectures système,
estimations de temps/coûts et recommandations technologiques.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum

from ..utils.exceptions import ValidationException, DevPlanException

logger = logging.getLogger(__name__)


class ProjectComplexity(Enum):
    """Niveaux de complexité des projets."""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    ENTERPRISE = "enterprise"


class TechStackCategory(Enum):
    """Catégories de technologies."""
    FRONTEND = "frontend"
    BACKEND = "backend"
    DATABASE = "database"
    DEVOPS = "devops"
    TESTING = "testing"
    SECURITY = "security"


@dataclass
class TechnologyRecommendation:
    """Recommandation technologique."""
    name: str
    category: TechStackCategory
    version: str
    reason: str
    alternatives: List[str]
    learning_curve: str  # "easy", "moderate", "difficult"
    popularity_score: int  # 1-10
    maintenance_cost: str  # "low", "medium", "high"


@dataclass
class ArchitectureComponent:
    """Composant d'architecture système."""
    name: str
    type: str  # "service", "database", "cache", "queue", etc.
    description: str
    technologies: List[str]
    connections: List[str]  # Connexions vers d'autres composants
    scalability: str
    estimated_complexity: int  # 1-10


@dataclass
class TimeEstimation:
    """Estimation de temps pour une phase/tâche."""
    task_name: str
    estimated_hours: int
    min_hours: int
    max_hours: int
    dependencies: List[str]
    critical_path: bool
    required_skills: List[str]


@dataclass
class CostEstimation:
    """Estimation de coûts."""
    development_cost: float
    infrastructure_cost_monthly: float
    maintenance_cost_monthly: float
    third_party_services: Dict[str, float]
    total_first_year: float
    ongoing_yearly: float


@dataclass
class ProjectPhase:
    """Phase de développement."""
    name: str
    description: str
    duration_weeks: int
    tasks: List[str]
    deliverables: List[str]
    dependencies: List[str]
    team_size: int
    time_estimations: List[TimeEstimation]


@dataclass
class DetailedSchema:
    """Schéma technique détaillé complet."""
    project_name: str
    project_type: str
    description: str
    complexity: ProjectComplexity
    
    # Architecture
    architecture_components: List[ArchitectureComponent]
    system_architecture: str  # Description textuelle
    data_flow: str
    
    # Technologies
    tech_recommendations: List[TechnologyRecommendation]
    tech_stack_summary: Dict[str, str]
    
    # Planning
    project_phases: List[ProjectPhase]
    total_duration_weeks: int
    
    # Estimations
    time_estimation: TimeEstimation
    cost_estimation: CostEstimation
    
    # Métadonnées
    generated_at: datetime
    confidence_score: float  # 0-1
    recommendations: List[str]
    risks: List[str]
    success_factors: List[str]


class SchemaGenerator:
    """Générateur de schémas techniques avancés."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._load_templates()
        self._load_tech_database()
    
    def _load_templates(self) -> None:
        """Charge les templates de projets prédéfinis."""
        self.project_templates = {
            "ecommerce": {
                "name": "Plateforme E-commerce",
                "base_components": ["web_frontend", "api_backend", "database", "payment_gateway", "cdn"],
                "required_features": ["user_auth", "product_catalog", "cart", "checkout", "admin_panel"],
                "complexity_multiplier": 1.3,
                "estimated_weeks": 16
            },
            "saas": {
                "name": "Application SaaS",
                "base_components": ["web_frontend", "api_backend", "database", "auth_service", "billing"],
                "required_features": ["multi_tenant", "subscription", "analytics", "api_access"],
                "complexity_multiplier": 1.5,
                "estimated_weeks": 20
            },
            "mobile": {
                "name": "Application Mobile",
                "base_components": ["mobile_app", "api_backend", "database", "push_notifications"],
                "required_features": ["offline_sync", "real_time", "user_auth"],
                "complexity_multiplier": 1.2,
                "estimated_weeks": 14
            },
            "api": {
                "name": "API REST",
                "base_components": ["api_backend", "database", "documentation", "monitoring"],
                "required_features": ["versioning", "rate_limiting", "auth", "caching"],
                "complexity_multiplier": 0.8,
                "estimated_weeks": 8
            },
            "dashboard": {
                "name": "Dashboard Analytics",
                "base_components": ["web_frontend", "api_backend", "database", "analytics_engine"],
                "required_features": ["real_time_data", "charts", "export", "user_management"],
                "complexity_multiplier": 1.1,
                "estimated_weeks": 12
            }
        }
    
    def _load_tech_database(self) -> None:
        """Charge la base de données des technologies."""
        self.tech_database = {
            TechStackCategory.FRONTEND: {
                "react": {
                    "name": "React",
                    "version": "18.x",
                    "learning_curve": "moderate",
                    "popularity_score": 9,
                    "maintenance_cost": "medium",
                    "best_for": ["spa", "interactive_ui", "large_teams"]
                },
                "vue": {
                    "name": "Vue.js",
                    "version": "3.x",
                    "learning_curve": "easy",
                    "popularity_score": 8,
                    "maintenance_cost": "low",
                    "best_for": ["rapid_prototyping", "small_teams", "progressive_enhancement"]
                },
                "nextjs": {
                    "name": "Next.js",
                    "version": "14.x",
                    "learning_curve": "moderate",
                    "popularity_score": 9,
                    "maintenance_cost": "medium",
                    "best_for": ["seo_important", "ssr", "full_stack"]
                }
            },
            TechStackCategory.BACKEND: {
                "nodejs": {
                    "name": "Node.js",
                    "version": "20.x LTS",
                    "learning_curve": "easy",
                    "popularity_score": 9,
                    "maintenance_cost": "medium",
                    "best_for": ["api_development", "real_time", "microservices"]
                },
                "python": {
                    "name": "Python",
                    "version": "3.12",
                    "learning_curve": "easy",
                    "popularity_score": 10,
                    "maintenance_cost": "low",
                    "best_for": ["data_processing", "ai_ml", "rapid_development"]
                },
                "java": {
                    "name": "Java",
                    "version": "21 LTS",
                    "learning_curve": "moderate",
                    "popularity_score": 8,
                    "maintenance_cost": "high",
                    "best_for": ["enterprise", "high_performance", "large_teams"]
                }
            },
            TechStackCategory.DATABASE: {
                "postgresql": {
                    "name": "PostgreSQL",
                    "version": "16.x",
                    "learning_curve": "moderate",
                    "popularity_score": 9,
                    "maintenance_cost": "medium",
                    "best_for": ["relational_data", "complex_queries", "acid_compliance"]
                },
                "mongodb": {
                    "name": "MongoDB",
                    "version": "7.x",
                    "learning_curve": "easy",
                    "popularity_score": 8,
                    "maintenance_cost": "medium",
                    "best_for": ["document_storage", "rapid_prototyping", "flexible_schema"]
                },
                "redis": {
                    "name": "Redis",
                    "version": "7.x",
                    "learning_curve": "easy",
                    "popularity_score": 9,
                    "maintenance_cost": "low",
                    "best_for": ["caching", "session_storage", "real_time"]
                }
            }
        }
    
    def analyze_project_complexity(self, project_data: Dict[str, Any]) -> ProjectComplexity:
        """Analyse la complexité du projet."""
        complexity_score = 0
        
        # Facteurs de complexité
        if project_data.get('scale') == 'large':
            complexity_score += 3
        elif project_data.get('scale') == 'medium':
            complexity_score += 2
        else:
            complexity_score += 1
        
        # Type de projet
        project_type = project_data.get('project_type', '')
        if project_type in ['saas', 'enterprise']:
            complexity_score += 2
        elif project_type in ['ecommerce', 'dashboard']:
            complexity_score += 1
        
        # Exigences spéciales
        requirements = project_data.get('requirements', '').lower()
        if any(term in requirements for term in ['paiement', 'sécurité', 'performance', 'scalabilité']):
            complexity_score += 1
        if any(term in requirements for term in ['temps réel', 'microservices', 'multi-tenant']):
            complexity_score += 2
        
        # Déterminer la complexité
        if complexity_score <= 2:
            return ProjectComplexity.SIMPLE
        elif complexity_score <= 4:
            return ProjectComplexity.MODERATE
        elif complexity_score <= 6:
            return ProjectComplexity.COMPLEX
        else:
            return ProjectComplexity.ENTERPRISE
    
    def generate_tech_recommendations(self, project_data: Dict[str, Any], 
                                    complexity: ProjectComplexity) -> List[TechnologyRecommendation]:
        """Génère les recommandations technologiques."""
        recommendations = []
        
        # Frontend
        frontend_pref = project_data.get('frontend_preference')
        if frontend_pref and frontend_pref in self.tech_database[TechStackCategory.FRONTEND]:
            tech = self.tech_database[TechStackCategory.FRONTEND][frontend_pref]
            recommendations.append(TechnologyRecommendation(
                name=tech['name'],
                category=TechStackCategory.FRONTEND,
                version=tech['version'],
                reason=f"Préférence utilisateur - {', '.join(tech['best_for'])}",
                alternatives=list(self.tech_database[TechStackCategory.FRONTEND].keys()),
                learning_curve=tech['learning_curve'],
                popularity_score=tech['popularity_score'],
                maintenance_cost=tech['maintenance_cost']
            ))
        else:
            # Recommandation automatique basée sur la complexité
            if complexity in [ProjectComplexity.SIMPLE, ProjectComplexity.MODERATE]:
                tech = self.tech_database[TechStackCategory.FRONTEND]['vue']
                reason = "Facilité d'apprentissage et développement rapide"
            else:
                tech = self.tech_database[TechStackCategory.FRONTEND]['react']
                reason = "Écosystème riche et support pour projets complexes"
            
            recommendations.append(TechnologyRecommendation(
                name=tech['name'],
                category=TechStackCategory.FRONTEND,
                version=tech['version'],
                reason=reason,
                alternatives=['React', 'Vue.js', 'Angular'],
                learning_curve=tech['learning_curve'],
                popularity_score=tech['popularity_score'],
                maintenance_cost=tech['maintenance_cost']
            ))
        
        # Backend
        backend_pref = project_data.get('backend_preference')
        if backend_pref and backend_pref in self.tech_database[TechStackCategory.BACKEND]:
            tech = self.tech_database[TechStackCategory.BACKEND][backend_pref]
            recommendations.append(TechnologyRecommendation(
                name=tech['name'],
                category=TechStackCategory.BACKEND,
                version=tech['version'],
                reason=f"Préférence utilisateur - {', '.join(tech['best_for'])}",
                alternatives=list(self.tech_database[TechStackCategory.BACKEND].keys()),
                learning_curve=tech['learning_curve'],
                popularity_score=tech['popularity_score'],
                maintenance_cost=tech['maintenance_cost']
            ))
        else:
            # Recommandation automatique
            if complexity == ProjectComplexity.ENTERPRISE:
                tech = self.tech_database[TechStackCategory.BACKEND]['java']
                reason = "Performance et robustesse pour applications d'entreprise"
            else:
                tech = self.tech_database[TechStackCategory.BACKEND]['nodejs']
                reason = "Développement rapide et écosystème JavaScript unifié"
            
            recommendations.append(TechnologyRecommendation(
                name=tech['name'],
                category=TechStackCategory.BACKEND,
                version=tech['version'],
                reason=reason,
                alternatives=['Node.js', 'Python', 'Java', 'C#'],
                learning_curve=tech['learning_curve'],
                popularity_score=tech['popularity_score'],
                maintenance_cost=tech['maintenance_cost']
            ))
        
        # Database
        db_pref = project_data.get('database_preference')
        if db_pref and db_pref in self.tech_database[TechStackCategory.DATABASE]:
            tech = self.tech_database[TechStackCategory.DATABASE][db_pref]
            recommendations.append(TechnologyRecommendation(
                name=tech['name'],
                category=TechStackCategory.DATABASE,
                version=tech['version'],
                reason=f"Préférence utilisateur - {', '.join(tech['best_for'])}",
                alternatives=list(self.tech_database[TechStackCategory.DATABASE].keys()),
                learning_curve=tech['learning_curve'],
                popularity_score=tech['popularity_score'],
                maintenance_cost=tech['maintenance_cost']
            ))
        else:
            # Recommandation automatique
            tech = self.tech_database[TechStackCategory.DATABASE]['postgresql']
            recommendations.append(TechnologyRecommendation(
                name=tech['name'],
                category=TechStackCategory.DATABASE,
                version=tech['version'],
                reason="Base de données relationnelle robuste et performante",
                alternatives=['PostgreSQL', 'MySQL', 'MongoDB'],
                learning_curve=tech['learning_curve'],
                popularity_score=tech['popularity_score'],
                maintenance_cost=tech['maintenance_cost']
            ))
        
        return recommendations
    
    def generate_architecture_components(self, project_data: Dict[str, Any], 
                                       tech_recommendations: List[TechnologyRecommendation]) -> List[ArchitectureComponent]:
        """Génère les composants d'architecture."""
        components = []
        project_type = project_data.get('project_type', 'custom')
        
        # Obtenir le template de base
        template = self.project_templates.get(project_type, self.project_templates['api'])
        
        # Frontend
        if 'web_frontend' in template['base_components']:
            frontend_tech = next((t for t in tech_recommendations if t.category == TechStackCategory.FRONTEND), None)
            components.append(ArchitectureComponent(
                name="Frontend Application",
                type="web_application",
                description="Interface utilisateur interactive et responsive",
                technologies=[frontend_tech.name if frontend_tech else "React"],
                connections=["api_backend"],
                scalability="CDN + Edge Caching",
                estimated_complexity=6
            ))
        
        # Backend API
        if 'api_backend' in template['base_components']:
            backend_tech = next((t for t in tech_recommendations if t.category == TechStackCategory.BACKEND), None)
            components.append(ArchitectureComponent(
                name="API Backend",
                type="rest_api",
                description="API REST pour la logique métier et gestion des données",
                technologies=[backend_tech.name if backend_tech else "Node.js", "Express/Fastify"],
                connections=["database", "cache"],
                scalability="Horizontal scaling + Load Balancer",
                estimated_complexity=8
            ))
        
        # Database
        if 'database' in template['base_components']:
            db_tech = next((t for t in tech_recommendations if t.category == TechStackCategory.DATABASE), None)
            components.append(ArchitectureComponent(
                name="Primary Database",
                type="database",
                description="Stockage principal des données",
                technologies=[db_tech.name if db_tech else "PostgreSQL"],
                connections=["api_backend"],
                scalability="Read replicas + Partitioning",
                estimated_complexity=7
            ))
        
        # Cache (Redis) - Ajouté automatiquement pour projets moyens/complexes
        if project_data.get('scale') in ['medium', 'large']:
            components.append(ArchitectureComponent(
                name="Cache Layer",
                type="cache",
                description="Cache en mémoire pour optimiser les performances",
                technologies=["Redis"],
                connections=["api_backend"],
                scalability="Redis Cluster",
                estimated_complexity=4
            ))
        
        # Services spécifiques selon le type de projet
        if project_type == 'ecommerce':
            components.append(ArchitectureComponent(
                name="Payment Gateway",
                type="external_service",
                description="Intégration système de paiement sécurisé",
                technologies=["Stripe", "PayPal API"],
                connections=["api_backend"],
                scalability="Service géré externe",
                estimated_complexity=6
            ))
        
        elif project_type == 'mobile':
            components.append(ArchitectureComponent(
                name="Push Notification Service",
                type="notification_service",
                description="Service de notifications push pour mobile",
                technologies=["FCM", "APNs"],
                connections=["api_backend"],
                scalability="Service géré externe",
                estimated_complexity=5
            ))
        
        return components
    
    def estimate_project_timeline(self, project_data: Dict[str, Any], 
                                complexity: ProjectComplexity,
                                components: List[ArchitectureComponent]) -> Tuple[List[ProjectPhase], int]:
        """Estime le timeline du projet."""
        project_type = project_data.get('project_type', 'custom')
        template = self.project_templates.get(project_type, self.project_templates['api'])
        
        base_weeks = template['estimated_weeks']
        complexity_multiplier = {
            ProjectComplexity.SIMPLE: 0.7,
            ProjectComplexity.MODERATE: 1.0,
            ProjectComplexity.COMPLEX: 1.3,
            ProjectComplexity.ENTERPRISE: 1.6
        }
        
        total_weeks = int(base_weeks * complexity_multiplier[complexity])
        
        phases = [
            ProjectPhase(
                name="Planning & Setup",
                description="Analyse des besoins, setup environnement, architecture détaillée",
                duration_weeks=max(1, total_weeks // 8),
                tasks=[
                    "Analyse des requirements",
                    "Architecture système détaillée",
                    "Setup environnement de développement",
                    "Configuration CI/CD",
                    "Setup base de données"
                ],
                deliverables=[
                    "Document d'architecture",
                    "Environnement de développement",
                    "Repository configuré"
                ],
                dependencies=[],
                team_size=2,
                time_estimations=[]
            ),
            ProjectPhase(
                name="Backend Development",
                description="Développement API, base de données, logique métier",
                duration_weeks=max(2, total_weeks // 3),
                tasks=[
                    "Modèles de données",
                    "API endpoints",
                    "Authentification",
                    "Logique métier",
                    "Tests unitaires"
                ],
                deliverables=[
                    "API fonctionnelle",
                    "Documentation API",
                    "Tests backend"
                ],
                dependencies=["Planning & Setup"],
                team_size=2,
                time_estimations=[]
            ),
            ProjectPhase(
                name="Frontend Development",
                description="Interface utilisateur, intégration API",
                duration_weeks=max(2, total_weeks // 3),
                tasks=[
                    "Interface utilisateur",
                    "Intégration API",
                    "Gestion d'état",
                    "Responsive design",
                    "Tests frontend"
                ],
                deliverables=[
                    "Interface utilisateur complète",
                    "Application responsive",
                    "Tests frontend"
                ],
                dependencies=["Backend Development"],
                team_size=2,
                time_estimations=[]
            ),
            ProjectPhase(
                name="Integration & Testing",
                description="Tests d'intégration, optimisation, préparation déploiement",
                duration_weeks=max(1, total_weeks // 6),
                tasks=[
                    "Tests d'intégration",
                    "Tests E2E",
                    "Optimisation performance",
                    "Sécurité",
                    "Préparation déploiement"
                ],
                deliverables=[
                    "Application testée",
                    "Rapport de sécurité",
                    "Guide de déploiement"
                ],
                dependencies=["Frontend Development"],
                team_size=3,
                time_estimations=[]
            ),
            ProjectPhase(
                name="Deployment & Launch",
                description="Déploiement production, monitoring, documentation",
                duration_weeks=max(1, total_weeks // 10),
                tasks=[
                    "Déploiement production",
                    "Configuration monitoring",
                    "Documentation utilisateur",
                    "Formation équipe",
                    "Go-live"
                ],
                deliverables=[
                    "Application en production",
                    "Monitoring actif",
                    "Documentation complète"
                ],
                dependencies=["Integration & Testing"],
                team_size=2,
                time_estimations=[]
            )
        ]
        
        return phases, total_weeks
    
    def estimate_costs(self, project_data: Dict[str, Any], 
                      complexity: ProjectComplexity, 
                      total_weeks: int) -> CostEstimation:
        """Estime les coûts du projet."""
        
        # Coût de développement (basé sur équipe de 2-3 développeurs)
        hourly_rate = 75  # EUR/heure (taux moyen)
        hours_per_week = 40
        team_size = 2.5  # Moyenne
        
        development_hours = total_weeks * hours_per_week * team_size
        development_cost = development_hours * hourly_rate
        
        # Coûts infrastructure mensuels
        base_infra_cost = {
            ProjectComplexity.SIMPLE: 50,
            ProjectComplexity.MODERATE: 150,
            ProjectComplexity.COMPLEX: 300,
            ProjectComplexity.ENTERPRISE: 600
        }
        
        infrastructure_monthly = base_infra_cost[complexity]
        
        # Services tiers
        third_party_services = {}
        project_type = project_data.get('project_type')
        
        if project_type == 'ecommerce':
            third_party_services['Payment Processing'] = 29
            third_party_services['Email Service'] = 15
            third_party_services['CDN'] = 20
        elif project_type == 'saas':
            third_party_services['Auth Service'] = 25
            third_party_services['Analytics'] = 35
            third_party_services['Monitoring'] = 25
        
        third_party_monthly = sum(third_party_services.values())
        
        # Maintenance (20% du coût de développement par an)
        maintenance_monthly = (development_cost * 0.2) / 12
        
        total_monthly = infrastructure_monthly + third_party_monthly + maintenance_monthly
        
        return CostEstimation(
            development_cost=development_cost,
            infrastructure_cost_monthly=infrastructure_monthly,
            maintenance_cost_monthly=maintenance_monthly,
            third_party_services=third_party_services,
            total_first_year=development_cost + (total_monthly * 12),
            ongoing_yearly=total_monthly * 12
        )
    
    def generate_detailed_schema(self, project_data: Dict[str, Any]) -> DetailedSchema:
        """Génère un schéma technique détaillé complet."""
        try:
            self.logger.info(f"Génération schéma détaillé pour: {project_data.get('project_type')}")
            
            # Analyse de complexité
            complexity = self.analyze_project_complexity(project_data)
            
            # Recommandations technologiques
            tech_recommendations = self.generate_tech_recommendations(project_data, complexity)
            
            # Architecture système
            architecture_components = self.generate_architecture_components(project_data, tech_recommendations)
            
            # Timeline et phases
            project_phases, total_weeks = self.estimate_project_timeline(project_data, complexity, architecture_components)
            
            # Estimations de coûts
            cost_estimation = self.estimate_costs(project_data, complexity, total_weeks)
            
            # Estimation de temps globale
            time_estimation = TimeEstimation(
                task_name="Projet complet",
                estimated_hours=int(total_weeks * 40 * 2.5),
                min_hours=int(total_weeks * 40 * 2),
                max_hours=int(total_weeks * 40 * 3),
                dependencies=[],
                critical_path=True,
                required_skills=["Full-stack development", "DevOps", "UI/UX"]
            )
            
            # Génération des recommandations et risques
            recommendations = self._generate_recommendations(complexity, tech_recommendations)
            risks = self._identify_risks(project_data, complexity)
            success_factors = self._identify_success_factors(project_data, complexity)
            
            # Création du schéma complet
            schema = DetailedSchema(
                project_name=f"Projet {project_data.get('project_type', 'Custom').title()}",
                project_type=project_data.get('project_type', 'custom'),
                description=project_data.get('description', ''),
                complexity=complexity,
                architecture_components=architecture_components,
                system_architecture=self._generate_architecture_description(architecture_components),
                data_flow=self._generate_data_flow_description(architecture_components),
                tech_recommendations=tech_recommendations,
                tech_stack_summary={t.category.value: t.name for t in tech_recommendations},
                project_phases=project_phases,
                total_duration_weeks=total_weeks,
                time_estimation=time_estimation,
                cost_estimation=cost_estimation,
                generated_at=datetime.now(),
                confidence_score=0.85,  # Score de confiance élevé
                recommendations=recommendations,
                risks=risks,
                success_factors=success_factors
            )
            
            self.logger.info(f"Schéma généré avec succès - Complexité: {complexity.value}")
            return schema
            
        except Exception as e:
            self.logger.error(f"Erreur génération schéma: {str(e)}")
            raise DevPlanException(f"Erreur lors de la génération du schéma: {str(e)}")
    
    def _generate_architecture_description(self, components: List[ArchitectureComponent]) -> str:
        """Génère une description textuelle de l'architecture."""
        description = "Architecture système recommandée:\n\n"
        
        for component in components:
            description += f"• **{component.name}** ({component.type})\n"
            description += f"  - {component.description}\n"
            description += f"  - Technologies: {', '.join(component.technologies)}\n"
            description += f"  - Scalabilité: {component.scalability}\n\n"
        
        return description
    
    def _generate_data_flow_description(self, components: List[ArchitectureComponent]) -> str:
        """Génère une description du flux de données."""
        return """Flux de données principal:

1. **Utilisateur** → Interface Frontend
2. **Frontend** → API Backend (REST/GraphQL)
3. **API Backend** → Cache Layer (si applicable)
4. **API Backend** → Base de données
5. **Services externes** ↔ API Backend (authentification, paiement, etc.)

Les données sont sécurisées en transit (HTTPS/TLS) et au repos (chiffrement base de données)."""
    
    def _generate_recommendations(self, complexity: ProjectComplexity, 
                                tech_recommendations: List[TechnologyRecommendation]) -> List[str]:
        """Génère les recommandations générales."""
        recommendations = [
            "Commencer par un MVP (Minimum Viable Product) pour valider le concept",
            "Implementer une architecture modulaire pour faciliter la maintenance",
            "Mettre en place un système de monitoring dès le début",
            "Prévoir une stratégie de sauvegarde et de récupération",
            "Documenter l'API et maintenir la documentation à jour"
        ]
        
        if complexity in [ProjectComplexity.COMPLEX, ProjectComplexity.ENTERPRISE]:
            recommendations.extend([
                "Considérer une architecture microservices pour la scalabilité",
                "Implementer un système de CI/CD robuste",
                "Prévoir des tests automatisés complets (unit, integration, E2E)",
                "Mettre en place un système de monitoring et d'alertes"
            ])
        
        return recommendations
    
    def _identify_risks(self, project_data: Dict[str, Any], complexity: ProjectComplexity) -> List[str]:
        """Identifie les risques potentiels."""
        risks = [
            "Dépassement de budget si les requirements changent",
            "Délais prolongés en cas de problèmes techniques imprévus",
            "Problèmes de performance si la charge utilisateur est sous-estimée"
        ]
        
        if complexity == ProjectComplexity.ENTERPRISE:
            risks.extend([
                "Complexité d'intégration avec les systèmes existants",
                "Défis de migration de données",
                "Besoin d'expertise technique avancée"
            ])
        
        project_type = project_data.get('project_type')
        if project_type == 'ecommerce':
            risks.append("Conformité PCI DSS pour le traitement des paiements")
        elif project_type == 'saas':
            risks.append("Défis de scalabilité multi-tenant")
        
        return risks
    
    def _identify_success_factors(self, project_data: Dict[str, Any], complexity: ProjectComplexity) -> List[str]:
        """Identifie les facteurs de succès."""
        return [
            "Équipe de développement expérimentée",
            "Requirements clairs et validés",
            "Tests utilisateurs réguliers",
            "Communication continue avec les stakeholders",
            "Approche agile avec livraisons itératives",
            "Monitoring et feedback continus",
            "Documentation technique maintenue à jour"
        ]
    
    def export_schema_to_dict(self, schema: DetailedSchema) -> Dict[str, Any]:
        """Exporte le schéma en dictionnaire pour JSON."""
        def convert_enum_and_datetime(obj):
            if isinstance(obj, Enum):
                return obj.value
            elif isinstance(obj, datetime):
                return obj.isoformat()
            return obj
        
        schema_dict = asdict(schema)
        
        # Conversion récursive des enums et dates
        def recursive_convert(d):
            if isinstance(d, dict):
                return {k: recursive_convert(v) for k, v in d.items()}
            elif isinstance(d, list):
                return [recursive_convert(item) for item in d]
            else:
                return convert_enum_and_datetime(d)
        
        return recursive_convert(schema_dict) 