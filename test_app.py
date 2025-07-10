#!/usr/bin/env python3
"""
Test simple pour valider le setup de l'application DevPlan Flask
"""

import os
import sys
import traceback

def test_imports():
    """Test des imports nécessaires"""
    print("🔍 Test des imports...")
    
    try:
        import flask
        print(f"✅ Flask: {flask.__version__}")
    except ImportError as e:
        print(f"❌ Flask: {e}")
        return False
    
    try:
        from app import create_app
        print("✅ App factory import: OK")
    except ImportError as e:
        print(f"❌ App factory: {e}")
        return False
    
    try:
        from app.config import Config, DevelopmentConfig
        print("✅ Configuration import: OK")
    except ImportError as e:
        print(f"❌ Configuration: {e}")
        return False
    
    return True

def test_app_creation():
    """Test de création de l'application"""
    print("\n🏗️ Test de création de l'application...")
    
    try:
        from app import create_app
        app = create_app('development')
        print("✅ Application créée avec succès")
        
        # Test de configuration
        print(f"✅ Debug mode: {app.debug}")
        print(f"✅ Secret key configuré: {bool(app.secret_key)}")
        
        return True
    except Exception as e:
        print(f"❌ Erreur création app: {e}")
        traceback.print_exc()
        return False

def test_routes():
    """Test des routes principales"""
    print("\n🛣️ Test des routes...")
    
    try:
        from app import create_app
        app = create_app('testing')
        
        with app.test_client() as client:
            # Test route principale
            response = client.get('/')
            print(f"✅ Route /: {response.status_code}")
            
            # Test health check
            response = client.get('/health')
            print(f"✅ Route /health: {response.status_code}")
            
            # Test status
            response = client.get('/status')
            print(f"✅ Route /status: {response.status_code}")
            
            # Test about
            response = client.get('/about')
            print(f"✅ Route /about: {response.status_code}")
            
        return True
    except Exception as e:
        print(f"❌ Erreur test routes: {e}")
        traceback.print_exc()
        return False

def test_templates():
    """Test des templates"""
    print("\n📄 Test des templates...")
    
    template_files = [
        'base.html',
        'index.html',
        'generator.html',
        'status.html',
        'config.html',
        'about.html'
    ]
    
    all_exist = True
    for template in template_files:
        path = f"app/templates/{template}"
        if os.path.exists(path):
            print(f"✅ Template {template}: OK")
        else:
            print(f"❌ Template {template}: Manquant")
            all_exist = False
    
    return all_exist

def test_config_files():
    """Test des fichiers de configuration"""
    print("\n⚙️ Test des fichiers de configuration...")
    
    config_files = [
        'requirements.txt',
        'env.example',
        'run.py',
        '.gitignore',
        'README.md'
    ]
    
    all_exist = True
    for config_file in config_files:
        if os.path.exists(config_file):
            print(f"✅ {config_file}: OK")
        else:
            print(f"❌ {config_file}: Manquant")
            all_exist = False
    
    return all_exist

def main():
    """Test principal"""
    print("🚀 DevPlan Flask - Tests de validation")
    print("=" * 50)
    
    # Ajouter le répertoire actuel au Python path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    tests = [
        ("Imports", test_imports),
        ("Création App", test_app_creation),
        ("Routes", test_routes),
        ("Templates", test_templates),
        ("Fichiers Config", test_config_files),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erreur dans {test_name}: {e}")
            results.append((test_name, False))
    
    # Résumé
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSÉ" if result else "❌ ÉCHEC"
        print(f"{test_name:20} : {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Résultat: {passed}/{total} tests passés")
    
    if passed == total:
        print("🎉 Tous les tests sont passés ! L'application est prête.")
        print("\n🚀 Pour démarrer l'application:")
        print("   python run.py")
    else:
        print("⚠️ Certains tests ont échoué. Vérifiez la configuration.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 