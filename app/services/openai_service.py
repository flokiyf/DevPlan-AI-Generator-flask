"""
Service OpenAI pour DevPlan AI Generator

Ce service gère toutes les interactions avec l'API OpenAI
"""

from openai import OpenAI
import os
import json
from typing import Dict, List, Optional, Any
from flask import current_app
from ..utils.exceptions import OpenAIException, ConfigurationException


class OpenAIService:
    """Service pour gérer les interactions avec OpenAI"""
    
    def __init__(self):
        self.client = None
        self.model = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialise le client OpenAI avec la configuration"""
        try:
            api_key = current_app.config.get('OPENAI_API_KEY')
            if not api_key:
                raise ConfigurationException(
                    "Clé API OpenAI manquante. Veuillez configurer OPENAI_API_KEY.",
                    setting="OPENAI_API_KEY"
                )
            
            # Configuration du client OpenAI (nouvelle API v1.0+)
            self.client = OpenAI(
                api_key=api_key,
                organization=current_app.config.get('OPENAI_ORGANIZATION')
            )
            
            self.model = current_app.config.get('OPENAI_MODEL', 'gpt-3.5-turbo')
            
            current_app.logger.info(f"✅ Client OpenAI initialisé avec le modèle: {self.model}")
            
        except Exception as e:
            current_app.logger.error(f"❌ Erreur initialisation OpenAI: {str(e)}")
            raise ConfigurationException(f"Impossible d'initialiser OpenAI: {str(e)}")
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Teste la connexion à OpenAI
        
        Returns:
            Dict contenant le statut et les informations de connexion
        """
        try:
            # Test simple avec une requête minimale
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": "Test de connexion - répondez simplement 'OK'"}
                ],
                max_tokens=10,
                temperature=0
            )
            
            return {
                "status": "success",
                "message": "Connexion OpenAI réussie",
                "model": self.model,
                "response": response.choices[0].message.content.strip(),
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
            
        except Exception as e:
            error_msg = str(e)
            
            # Gestion des erreurs spécifiques OpenAI
            if "authentication" in error_msg.lower() or "api_key" in error_msg.lower():
                raise OpenAIException(
                    "Erreur d'authentification OpenAI. Vérifiez votre clé API.",
                    code="AUTH_ERROR"
                )
            elif "rate_limit" in error_msg.lower() or "quota" in error_msg.lower():
                raise OpenAIException(
                    "Limite de taux OpenAI atteinte. Réessayez plus tard.",
                    code="RATE_LIMIT_ERROR"
                )
            elif "model" in error_msg.lower():
                raise OpenAIException(
                    f"Modèle non disponible: {self.model}",
                    code="MODEL_ERROR",
                    details=error_msg
                )
            else:
                raise OpenAIException(
                    f"Erreur inattendue lors du test de connexion: {error_msg}",
                    code="UNKNOWN_ERROR",
                    details=error_msg
                )
    
    def generate_development_plan(self, project_description: str, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Génère un plan de développement basé sur la description du projet
        
        Args:
            project_description: Description du projet
            requirements: Exigences et spécifications
            
        Returns:
            Dict contenant le plan de développement généré
        """
        try:
            # Construction du prompt pour la génération du plan
            prompt = self._build_development_plan_prompt(project_description, requirements)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "Tu es un expert en gestion de projet et développement logiciel. Tu génères des plans de développement structurés et détaillés."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.7,
                presence_penalty=0.1,
                frequency_penalty=0.1
            )
            
            plan_content = response.choices[0].message.content
            
            return {
                "status": "success",
                "plan": plan_content,
                "metadata": {
                    "model": self.model,
                    "tokens_used": response.usage.total_tokens,
                    "project_description": project_description,
                    "requirements": requirements
                }
            }
            
        except Exception as e:
            current_app.logger.error(f"Erreur génération plan: {str(e)}")
            raise OpenAIException(
                f"Erreur lors de la génération du plan: {str(e)}",
                code="GENERATION_ERROR",
                details=str(e)
            )
    
    def _build_development_plan_prompt(self, description: str, requirements: Dict[str, Any]) -> str:
        """
        Construit le prompt pour la génération du plan de développement
        
        Args:
            description: Description du projet
            requirements: Exigences du projet
            
        Returns:
            Prompt formaté pour OpenAI
        """
        prompt = f"""
Génère un plan de développement complet pour le projet suivant :

## Description du Projet
{description}

## Exigences
"""
        
        # Ajout des exigences au prompt
        if requirements.get('technology_stack'):
            prompt += f"\n**Stack Technologique :** {', '.join(requirements['technology_stack'])}"
        
        if requirements.get('timeline'):
            prompt += f"\n**Timeline :** {requirements['timeline']}"
        
        if requirements.get('team_size'):
            prompt += f"\n**Taille d'équipe :** {requirements['team_size']} développeurs"
        
        if requirements.get('budget'):
            prompt += f"\n**Budget :** {requirements['budget']}"
        
        if requirements.get('features'):
            prompt += f"\n**Fonctionnalités clés :** {', '.join(requirements['features'])}"
        
        prompt += """

## Format de Réponse Attendu

Génère un plan structuré avec les sections suivantes :

### 1. 📋 Analyse du Projet
- Objectifs principaux
- Défis identifiés
- Opportunités

### 2. 🏗️ Architecture Technique
- Stack technologique recommandée
- Architecture système
- Choix de base de données

### 3. 📅 Planning de Développement
- Phases du projet
- Jalons importants
- Timeline détaillée

### 4. 👥 Organisation de l'Équipe
- Rôles et responsabilités
- Compétences requises
- Structure de collaboration

### 5. 🚀 Stratégie de Déploiement
- Environnements
- CI/CD
- Monitoring

### 6. 📊 Gestion des Risques
- Risques identifiés
- Plans de mitigation
- Contingences

### 7. 💰 Estimation Budgétaire
- Coûts de développement
- Infrastructure
- Maintenance

Sois précis, pratique et actionnable dans tes recommandations.
"""
        
        return prompt
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Retourne les informations sur le modèle utilisé
        
        Returns:
            Dict avec les informations du modèle
        """
        return {
            "model": self.model,
            "api_key_configured": bool(current_app.config.get('OPENAI_API_KEY')),
            "organization": current_app.config.get('OPENAI_ORGANIZATION'),
            "status": "configured" if self.client else "not_configured"
        } 