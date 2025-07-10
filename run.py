#!/usr/bin/env python3
"""
Point d'entrée principal pour DevPlan AI Generator Flask Application
"""

import os
from dotenv import load_dotenv
from app import create_app

# Charger les variables d'environnement
load_dotenv()

# Créer l'application Flask
app = create_app(os.getenv('FLASK_ENV', 'development'))

if __name__ == '__main__':
    # Configuration de démarrage
    debug_mode = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '127.0.0.1')
    
    print("🚀 Démarrage de DevPlan AI Generator...")
    print(f"📍 URL: http://{host}:{port}")
    print(f"🔧 Mode: {os.getenv('FLASK_ENV', 'development')}")
    print(f"🐛 Debug: {debug_mode}")
    
    # Démarrer l'application
    app.run(
        host=host,
        port=port,
        debug=debug_mode,
        threaded=True
    ) 