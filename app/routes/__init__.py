"""
Package des routes pour DevPlan AI Generator
"""

# Import des blueprints principaux
from .main import main_bp

# Liste des blueprints à enregistrer
blueprints = [
    main_bp,
    # Ajout des autres blueprints à venir :
    # api_bp,
    # export_bp,
    # config_bp
]

__all__ = ['blueprints', 'main_bp'] 