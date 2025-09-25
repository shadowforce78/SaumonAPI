# Configuration CORS et CSP - SaumonAPI

## CORS (Cross-Origin Resource Sharing)

### Domaines autorisés

**Développement :**
- `http://localhost:3000` (React)
- `http://localhost:5173` (Vite)
- `http://localhost:8080` (Vue)
- `http://localhost:4200` (Angular)
- `http://127.0.0.1:*` (variantes locales)

**Production :**
- `https://saumondeluxe.com`
- `https://www.saumondeluxe.com`
- `https://api.saumondeluxe.com`

### Configuration

La configuration CORS permet :
- **Méthodes** : GET, POST, PUT, DELETE, OPTIONS, HEAD
- **En-têtes** : Content-Type, Authorization, X-Requested-With, etc.
- **Credentials** : Autorisés (cookies, tokens)

## CSP (Content Security Policy)

### Politique de sécurité

La CSP est configurée pour :
- Permettre le contenu depuis les domaines autorisés
- Bloquer l'exécution de scripts non autorisés
- Contrôler les sources d'images, styles et polices
- Empêcher l'intégration dans des iframes malveillants

### En-têtes de sécurité ajoutés

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy: geolocation=(), microphone=(), camera=()`
- `Strict-Transport-Security` (en production uniquement)

## Variables d'environnement

```env
# Configuration de l'environnement
ENVIRONMENT=production  # ou "development"

# Origines CORS supplémentaires
CORS_ORIGINS=https://saumondeluxe.com,https://www.saumondeluxe.com

# Configuration serveur (production)
PORT=63246
WORKERS=4
```

## Utilisation

### Développement
```bash
python run_api.py
```

### Production
```bash
python run_production.py
```

## Test CORS

Utilisez l'endpoint `/test-cors` pour vérifier la configuration :

```bash
curl -X GET https://api.saumondeluxe.com/test-cors
```

## Résolution des problèmes CORS courants

### Erreur : "Access-Control-Allow-Origin"
- Vérifiez que votre domaine est dans la liste `CORS_ORIGINS`
- Assurez-vous que l'environnement est correctement configuré

### Erreur : "Preflight request failed"
- L'endpoint OPTIONS est automatiquement géré
- Vérifiez les en-têtes de la requête

### Erreur CSP
- Vérifiez la console du navigateur
- Ajustez la politique CSP si nécessaire pour votre application

## Sécurité en production

1. **HTTPS obligatoire** : Tous les domaines de production utilisent HTTPS
2. **Hôtes de confiance** : Middleware activé en production
3. **HSTS** : Activé automatiquement en production
4. **CSP stricte** : Politique restrictive pour la sécurité
