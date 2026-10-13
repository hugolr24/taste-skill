# Atelier Vernaz — mise en ligne sur Hostinger

Le site est un site **statique** (HTML, CSS, JS) : aucun build, aucune base de données. Tout ce qui doit être en ligne est dans `site/`.

```
site/
├── index.html            Accueil 3D (écrin, montre, vue éclatée)
├── atelier.html          L'Atelier / savoir-faire
├── rendez-vous.html      Prise de rendez-vous (Calendly, chargé après consentement)
├── mentions-legales.html Mentions légales + politique de confidentialité
├── 404.html              Page d'erreur
├── .htaccess             404, cache, compression (Apache Hostinger)
├── assets/               CSS, JS, polices auto-hébergées, favicon
└── vendor/               Three.js r165 et GSAP 3.12.5 (auto-hébergés)
```

## Voir le site en local

Les modules JavaScript ne se chargent pas en double-cliquant sur `index.html` (`file://`). Lance un petit serveur :

```bash
cd site
npx serve .            # ou : python3 -m http.server 8000
```

## Déployer avec Claude Code et le MCP Hostinger

### 1. Prérequis

- Une offre **Hébergement Web** Hostinger (Premium, Business ou Cloud). C'est elle qui donne droit au **sous-domaine temporaire gratuit** (`quelquechose.hostingersite.com`).
- [Node.js](https://nodejs.org) 20 ou plus récent, et Claude Code installé sur ton ordinateur.

### 2. Récupérer le projet sur ton ordinateur

```bash
git clone -b claude/gallant-clarke-mfdyeq https://github.com/hugolr24/taste-skill.git
cd taste-skill/examples/watchmaker
```

### 3. Ajouter le serveur MCP Hostinger (une seule fois)

```bash
claude mcp add hostinger -- npx -y @hostinger/mcp
```

Aucune clé à copier : au premier appel, une fenêtre de navigateur s'ouvre pour te connecter à ton compte Hostinger (OAuth).
Variante avec un jeton API (hPanel → Profil → API) : `claude mcp add hostinger -e HOSTINGER_API_TOKEN=ton_jeton -- npx -y @hostinger/mcp`. Ne colle jamais ce jeton dans une conversation.

### 4. Lancer Claude Code dans `examples/watchmaker` et coller ce message

```text
Déploie le site statique du dossier site/ sur mon hébergement Hostinger, avec un sous-domaine temporaire gratuit.

1. Liste mes offres d'hébergement (hosting_orders_list) et mes sites existants (hosting_websites_list), et montre-les-moi avant de créer quoi que ce soit.
2. Génère un sous-domaine gratuit (hosting_domains_generate-free-subdomain), crée le site dessus (hosting_websites_create, avec le premier datacenter de hosting_datacenters_list si c'est le premier site de l'offre), puis attends que hosting_websites_list-setups indique "completed".
3. Crée une archive zip du CONTENU de site/ : index.html doit être à la racine de l'archive et .htaccess doit être inclus. Les chemins doivent utiliser des "/" (sous Windows, n'utilise pas Compress-Archive : utilise tar -a -c -f ou Python zipfile). Nomme-la vernaz_AAAAMMJJ_HHMMSS.zip et ne la mets pas dans site/.
4. Déploie l'archive avec hosting_deploy-static-website.
5. Vérifie avec curl que https://<domaine>/ répond 200 et contient le texte « façonné », et que /rendez-vous.html, /atelier.html et /vendor/three/three.module.min.js répondent 200. Si une page Hostinger par défaut s'affiche, vide le cache (hosting_cache_clear-website) et revérifie.
6. Donne-moi l'URL finale.

Demande-moi confirmation avant toute action payante ou qui écraserait un site existant.
```

### 5. Mettre à jour le site plus tard

Modifie les fichiers dans `site/`, puis demande à Claude Code : « Redéploie site/ sur le même domaine Hostinger ». Le fichier `.hostinger/site.json` créé au premier déploiement lui indique la cible.

Alternative sans Claude : déploiement automatique depuis GitHub (hPanel → Sites web → Gérer → Avancé → Git), avec le dépôt `hugolr24/taste-skill`, la branche `claude/gallant-clarke-mfdyeq` et le dossier `examples/watchmaker/site`.

## Avant le lancement officiel

- [ ] Remplacer les informations surlignées dans `mentions-legales.html` (raison sociale, adresse, SIREN, email…).
- [ ] Remplacer le nom « Vernaz », le créateur, les chiffres (12 pièces/an, 1 400 h, 214 composants, budget 38 000 CHF…) par les vrais.
- [ ] Retirer `<meta name="robots" content="noindex, nofollow">` de chaque page (il empêche Google d'indexer le domaine temporaire).
- [ ] Brancher le vrai nom de domaine (hPanel ou MCP : `hosting_domains_*`) et activer le SSL.
- [ ] Optionnel (offre Calendly payante) : les couleurs du calendrier suivent le site ; en offre gratuite, Calendly s'affiche dans ses couleurs par défaut.
