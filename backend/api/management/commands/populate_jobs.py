"""
python manage.py populate_jobs

Peuple la table JobOffer avec 90+ offres réalistes réparties sur 16 catégories,
3 niveaux d'expérience et des budgets variés (150 – 8 000 TND).
Utilise les comptes clients existants (client1-5 + client_demo).
"""
import random
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from api.models import JobOffer, Profile

# ─────────────────────────────────────────────────────────────────────────────
# Catalogue complet des offres
# Chaque entrée : titre, catégorie, description, skills, niveau, budget, délai
# ─────────────────────────────────────────────────────────────────────────────
JOBS = [

    # ── DÉVELOPPEMENT WEB ──────────────────────────────────────────────────
    {
        'title': 'Développement site e-commerce Angular + Django',
        'category': 'Développement Web',
        'description': (
            "Nous cherchons un développeur fullstack pour construire une boutique en ligne complète. "
            "Frontend Angular avec Material Design, backend Django REST Framework, intégration paiement Konnect, "
            "gestion des stocks, tableau de bord admin et espace client. Hébergement sur VPS Linux. "
            "Livraison incluant tests unitaires, documentation et déploiement."
        ),
        'skills': 'Angular, Django, PostgreSQL, REST API, Docker',
        'level': 'expert', 'budget': 3500, 'days': 60,
    },
    {
        'title': 'Refonte site vitrine WordPress – Cabinet juridique',
        'category': 'Développement Web',
        'description': (
            "Un cabinet juridique tunisien souhaite moderniser son site WordPress. "
            "Nouveau thème responsive, optimisation SEO on-page, formulaire de contact sécurisé, "
            "blog intégré et section FAQ. Compatibilité mobile indispensable. "
            "Livraison dans un délai court avec formation à l'utilisation."
        ),
        'skills': 'WordPress, Elementor, SEO, CSS, PHP',
        'level': 'intermediate', 'budget': 600, 'days': 14,
    },
    {
        'title': 'Application web React – Tableau de bord RH',
        'category': 'Développement Web',
        'description': (
            "Développement d'un tableau de bord RH en React avec gestion des employés, "
            "suivi des congés, calcul automatique des salaires et exports PDF/Excel. "
            "Authentification rôles (admin, manager, employé). API REST Node.js fournie. "
            "Respect des normes RGPD."
        ),
        'skills': 'React, TypeScript, Chart.js, Axios, Material UI',
        'level': 'intermediate', 'budget': 2200, 'days': 45,
    },
    {
        'title': 'Landing page haute conversion – Startup SaaS',
        'category': 'Développement Web',
        'description': (
            "Créer une landing page ultra-performante pour le lancement d'un SaaS tunisien. "
            "Design moderne, animations CSS, section pricing, témoignages, vidéo hero et CTA optimisés. "
            "Temps de chargement < 2s, score Lighthouse > 90. Intégration formulaire Mailchimp."
        ),
        'skills': 'HTML, CSS, JavaScript, GSAP, Lighthouse',
        'level': 'intermediate', 'budget': 800, 'days': 10,
    },
    {
        'title': 'Développement API REST Laravel – Plateforme éducative',
        'category': 'Développement Web',
        'description': (
            "Construire une API REST Laravel pour une plateforme d'apprentissage en ligne. "
            "Gestion des cours, modules, quiz, progress tracking, certificats auto-générés PDF. "
            "Auth via Sanctum, rôles enseignant/étudiant, upload vidéo via S3. "
            "Tests Feature avec PHPUnit obligatoires."
        ),
        'skills': 'Laravel, PHP, MySQL, REST API, PHPUnit, AWS S3',
        'level': 'expert', 'budget': 2800, 'days': 50,
    },
    {
        'title': 'Intégration maquette Figma en Vue.js',
        'category': 'Développement Web',
        'description': (
            "Intégration pixel-perfect d'une maquette Figma fournie en application Vue.js 3. "
            "Composants réutilisables, routing Vue Router, state management Pinia. "
            "Animations Framer Motion. Responsive mobile-first. "
            "Le design est déjà validé, seule l'intégration est requise."
        ),
        'skills': 'Vue.js, Pinia, Tailwind CSS, Figma, TypeScript',
        'level': 'intermediate', 'budget': 1200, 'days': 20,
    },
    {
        'title': 'Site portfolio développeur – Design minimal',
        'category': 'Développement Web',
        'description': (
            "Création d'un site portfolio moderne et minimaliste pour un développeur freelance. "
            "Sections : accueil hero, compétences, projets avec filtres, blog et contact. "
            "Animation au scroll, dark mode, formulaire de contact fonctionnel. "
            "Idéal pour un profil junior avec un petit budget."
        ),
        'skills': 'HTML, CSS, JavaScript, EmailJS',
        'level': 'beginner', 'budget': 300, 'days': 7,
    },
    {
        'title': 'Migration site Joomla vers WordPress',
        'category': 'Développement Web',
        'description': (
            "Migration complète d'un site institutionnel de Joomla 3 vers WordPress 6. "
            "Conservation du contenu (articles, pages, médias), redirection 301 des URLs, "
            "thème moderne Astra + Elementor, plugin de sécurité et backup automatique. "
            "Aucune perte de données ni de référencement."
        ),
        'skills': 'WordPress, Joomla, PHP, MySQL, SEO',
        'level': 'intermediate', 'budget': 750, 'days': 15,
    },

    # ── DÉVELOPPEMENT MOBILE ───────────────────────────────────────────────
    {
        'title': 'Application Flutter – Livraison à domicile',
        'category': 'Développement Mobile',
        'description': (
            "Développement d'une app Flutter cross-platform (iOS + Android) pour un service de livraison. "
            "Géolocalisation temps réel Google Maps, suivi des commandes, paiement intégré, "
            "notifications push Firebase, espace livreur et espace client. "
            "Connexion à une API REST existante (Django)."
        ),
        'skills': 'Flutter, Dart, Firebase, Google Maps API, REST API',
        'level': 'expert', 'budget': 4500, 'days': 75,
    },
    {
        'title': 'App React Native – Réseau social local',
        'category': 'Développement Mobile',
        'description': (
            "Créer un MVP de réseau social pour quartiers en React Native. "
            "Feed de posts, messagerie instantanée, groupes, événements locaux et carte interactive. "
            "Backend Node.js + MongoDB. Authentification avec Google OAuth."
        ),
        'skills': 'React Native, Node.js, MongoDB, Socket.io, Firebase',
        'level': 'expert', 'budget': 5000, 'days': 90,
    },
    {
        'title': 'Application iOS Swift – Gestion de santé',
        'category': 'Développement Mobile',
        'description': (
            "Application iOS native en SwiftUI pour le suivi de santé personnelle. "
            "Intégration HealthKit, tracker d'activité, rappels médicaments, graphiques BMI. "
            "Synchronisation iCloud, mode sombre, support iPad. "
            "Respect des guidelines HIG d'Apple."
        ),
        'skills': 'Swift, SwiftUI, HealthKit, Core Data, CloudKit',
        'level': 'expert', 'budget': 3200, 'days': 60,
    },
    {
        'title': 'App Android Kotlin – Scanner QR code',
        'category': 'Développement Mobile',
        'description': (
            "Application Android simple pour scanner des QR codes et codes-barres. "
            "Historique des scans, partage de résultats, génération de QR personnalisés. "
            "Compatible Android 8+. Interface MVVM avec Room et LiveData."
        ),
        'skills': 'Kotlin, Android SDK, CameraX, Room, MVVM',
        'level': 'beginner', 'budget': 450, 'days': 14,
    },
    {
        'title': 'Application Flutter – Réservation de terrains sportifs',
        'category': 'Développement Mobile',
        'description': (
            "App mobile pour réserver des terrains de foot, tennis et padel en Tunisie. "
            "Calendrier de disponibilité, paiement en ligne, notifications rappel, "
            "profil utilisateur avec historique. Admin web inclus pour gérer les terrains."
        ),
        'skills': 'Flutter, Firebase, Stripe, Google Calendar API',
        'level': 'intermediate', 'budget': 2000, 'days': 45,
    },

    # ── DESIGN UI/UX ───────────────────────────────────────────────────────
    {
        'title': 'Design UI/UX – Application de covoiturage',
        'category': 'Design UI/UX',
        'description': (
            "Concevoir l'expérience utilisateur complète d'une application de covoiturage tunisienne. "
            "Research utilisateur, personas, user journey, wireframes basse fidélité, "
            "prototype interactif Figma haute fidélité, design system complet. "
            "Livraison : fichier Figma organisé + guide de style."
        ),
        'skills': 'Figma, UX Research, Prototyping, Design System, Adobe XD',
        'level': 'expert', 'budget': 1800, 'days': 30,
    },
    {
        'title': 'Redesign interface SaaS – Dashboard analytique',
        'category': 'Design UI/UX',
        'description': (
            "Refonte complète de l'interface d'un outil SaaS de marketing analytics. "
            "Amélioration de l'architecture de l'information, visualisation des données, "
            "composants accessibles WCAG 2.1, dark mode. "
            "Livraison : Figma + Storybook documentation."
        ),
        'skills': 'Figma, UI Design, Data Visualization, Accessibility, Storybook',
        'level': 'expert', 'budget': 2500, 'days': 40,
    },
    {
        'title': 'Maquette e-commerce – Mode féminine',
        'category': 'Design UI/UX',
        'description': (
            "Design d'une boutique en ligne de mode féminine haut de gamme. "
            "Page d'accueil, catalogue avec filtres, fiche produit, panier et checkout. "
            "Style élégant, photographies mockup, responsive mobile. "
            "Livrables : Figma + assets exportés."
        ),
        'skills': 'Figma, UI Design, E-commerce UX, Adobe Photoshop',
        'level': 'intermediate', 'budget': 950, 'days': 15,
    },
    {
        'title': 'Audit UX – Site de réservation hôtelière',
        'category': 'Design UI/UX',
        'description': (
            "Réaliser un audit UX complet d'un site de réservation hôtelière. "
            "Analyse heuristique, tests utilisateurs (5 participants), carte de chaleur, "
            "rapport de recommandations priorisées avec wireframes correctifs."
        ),
        'skills': 'UX Research, Hotjar, Heuristic Evaluation, Wireframing',
        'level': 'intermediate', 'budget': 700, 'days': 10,
    },

    # ── LOGO DESIGN ────────────────────────────────────────────────────────
    {
        'title': 'Logo + identité visuelle – Startup FinTech',
        'category': 'Logo Design',
        'description': (
            "Création d'un logo moderne et d'une identité visuelle complète pour une startup FinTech tunisienne. "
            "3 concepts initiaux, 2 rounds de révisions, livraison en SVG, PNG, PDF. "
            "Charte graphique : couleurs, typographies, usages autorisés."
        ),
        'skills': 'Adobe Illustrator, Branding, Typography, Color Theory',
        'level': 'intermediate', 'budget': 600, 'days': 10,
    },
    {
        'title': 'Logo simple – Auto-entrepreneur',
        'category': 'Logo Design',
        'description': (
            "Création d'un logo propre et professionnel pour un auto-entrepreneur (consultant, coach, artisan). "
            "1 concept, 1 révision, livraison PNG + SVG. "
            "Style simple et moderne, adapté aux petits budgets."
        ),
        'skills': 'Adobe Illustrator, Canva Pro, Logo Design',
        'level': 'beginner', 'budget': 150, 'days': 5,
    },
    {
        'title': 'Refonte logo – Restaurant traditionnel',
        'category': 'Logo Design',
        'description': (
            "Moderniser le logo d'un restaurant de cuisine tunisienne traditionnelle "
            "tout en conservant l'authenticité de la marque. "
            "Nouvelles versions : couleur, monochrome, favicon. "
            "Usage print et digital inclus."
        ),
        'skills': 'Adobe Illustrator, Branding, Rebranding',
        'level': 'intermediate', 'budget': 350, 'days': 7,
    },

    # ── RÉDACTION & TRADUCTION ─────────────────────────────────────────────
    {
        'title': 'Rédaction 15 articles de blog SEO – Tech',
        'category': 'Rédaction & Traduction',
        'description': (
            "Rédaction de 15 articles optimisés SEO (1 200–1 800 mots chacun) sur des sujets tech : "
            "IA, cybersécurité, cloud, startups tunisiennes. "
            "Recherche des mots-clés fournie, ton professionnel mais accessible. "
            "Livraison en Google Docs avec structure Hn respectée."
        ),
        'skills': 'Copywriting, SEO, Recherche, WordPress',
        'level': 'intermediate', 'budget': 750, 'days': 30,
    },
    {
        'title': 'Traduction technique EN → FR – Logiciel SaaS',
        'category': 'Rédaction & Traduction',
        'description': (
            "Traduction de 80 pages de documentation utilisateur d'un logiciel SaaS "
            "de l'anglais vers le français. Terminologie technique (IT, cloud, API). "
            "Glossaire fourni. Livraison en format Word avec mise en page conservée."
        ),
        'skills': 'Traduction, Anglais, Terminologie technique, SDL Trados',
        'level': 'intermediate', 'budget': 900, 'days': 21,
    },
    {
        'title': 'Rédaction fiches produits – E-commerce cosmétique',
        'category': 'Rédaction & Traduction',
        'description': (
            "Rédaction de 50 fiches produits pour une boutique cosmétique en ligne. "
            "Textes persuasifs, mots-clés intégrés, descriptions des ingrédients, avantages et modes d'utilisation. "
            "Ton féminin haut de gamme."
        ),
        'skills': 'Copywriting, E-commerce, SEO, Beauté-cosmétique',
        'level': 'beginner', 'budget': 400, 'days': 14,
    },
    {
        'title': 'Correction et relecture – Roman jeunesse (200 pages)',
        'category': 'Rédaction & Traduction',
        'description': (
            "Relecture et correction d'un roman jeunesse francophone de 200 pages. "
            "Correction orthographique, grammaticale et stylistique. "
            "Commentaires sur la cohérence narrative. Livraison en mode révision Word."
        ),
        'skills': 'Correction, Relecture, Orthographe, Français',
        'level': 'intermediate', 'budget': 500, 'days': 14,
    },

    # ── MONTAGE VIDÉO ─────────────────────────────────────────────────────
    {
        'title': 'Montage vidéo – Pub TikTok 30s produit beauté',
        'category': 'Montage Vidéo',
        'description': (
            "Montage d'une vidéo publicitaire de 30 secondes pour TikTok et Instagram Reels. "
            "Rushes vidéo fournis par le client. Sous-titres animés, musique tendance, transitions dynamiques, "
            "call-to-action final. Livraison en 1080x1920 (vertical)."
        ),
        'skills': 'Premiere Pro, After Effects, CapCut, Motion Graphics',
        'level': 'beginner', 'budget': 250, 'days': 5,
    },
    {
        'title': 'Montage corporate – Présentation entreprise 3 minutes',
        'category': 'Montage Vidéo',
        'description': (
            "Production d'une vidéo corporate de 3 minutes présentant une entreprise tunisienne. "
            "Montage des rushes fournis, voix off enregistrée, infographies animées, "
            "musique de fond, générique et logo animé. Livraison 4K."
        ),
        'skills': 'Premiere Pro, After Effects, DaVinci Resolve, Motion Graphics',
        'level': 'intermediate', 'budget': 800, 'days': 10,
    },
    {
        'title': 'Intro animée + outro pour chaîne YouTube',
        'category': 'Montage Vidéo',
        'description': (
            "Création d'une intro animée de 5 secondes et un outro de 10 secondes "
            "pour une chaîne YouTube tunisienne tech. "
            "Style moderne avec logo animé, effets lumineux, sound design. "
            "Livraison fichier .mov transparent + export MP4."
        ),
        'skills': 'After Effects, Motion Design, Illustrator',
        'level': 'intermediate', 'budget': 350, 'days': 7,
    },
    {
        'title': 'Sous-titrage et traduction vidéo – Formation e-learning',
        'category': 'Montage Vidéo',
        'description': (
            "Sous-titrage et traduction (arabe → français) de 10 vidéos de formation e-learning. "
            "Durée totale : 8 heures. Synchronisation précise, fichiers .srt et intégration dans la vidéo. "
            "Format final MP4 1080p."
        ),
        'skills': 'Subtitle Edit, Premiere Pro, Traduction',
        'level': 'beginner', 'budget': 600, 'days': 20,
    },

    # ── MARKETING DIGITAL ─────────────────────────────────────────────────
    {
        'title': 'Stratégie marketing digitale – Lancement produit',
        'category': 'Marketing Digital',
        'description': (
            "Élaboration d'une stratégie marketing complète pour le lancement d'un produit agroalimentaire. "
            "Analyse concurrentielle, ciblage audience, plan médias social, contenu 3 mois, "
            "KPIs et budget publicitaire. Livraison : document stratégique complet."
        ),
        'skills': 'Marketing Digital, Facebook Ads, Instagram, Analytics, Canva',
        'level': 'expert', 'budget': 1500, 'days': 21,
    },
    {
        'title': 'Gestion campagnes Meta Ads – E-commerce',
        'category': 'Marketing Digital',
        'description': (
            "Gérer les campagnes publicitaires Facebook et Instagram pour une boutique en ligne. "
            "Création des audiences, visuels fournis, A/B testing, optimisation ROAS. "
            "Rapport hebdomadaire. Budget publicitaire mensuel alloué : 2 000 DT."
        ),
        'skills': 'Meta Ads Manager, Facebook Pixel, A/B Testing, Analytics',
        'level': 'intermediate', 'budget': 700, 'days': 30,
    },
    {
        'title': 'Email marketing – Séquence nurturing (10 emails)',
        'category': 'Marketing Digital',
        'description': (
            "Rédiger et configurer une séquence de 10 emails de nurturing pour convertir des leads. "
            "Segmentation, personnalisation, A/B test sur les objets, intégration Mailchimp/Sendinblue. "
            "Rapport de performance après 30 jours."
        ),
        'skills': 'Email Marketing, Mailchimp, Copywriting, Automation',
        'level': 'intermediate', 'budget': 550, 'days': 15,
    },
    {
        'title': 'Plan de contenu réseaux sociaux – 3 mois',
        'category': 'Marketing Digital',
        'description': (
            "Élaboration d'un calendrier éditorial complet sur 3 mois pour LinkedIn, Instagram et Facebook. "
            "Thématiques, formats (Reels, Stories, carrousels), textes et hashtags. "
            "Outils : Hootsuite ou Buffer. Formation d'un employé incluse."
        ),
        'skills': 'Content Marketing, Hootsuite, Canva, Copywriting',
        'level': 'beginner', 'budget': 400, 'days': 10,
    },

    # ── SEO ────────────────────────────────────────────────────────────────
    {
        'title': "Audit SEO technique + plan d'action",
        'category': 'SEO',
        'description': (
            "Audit SEO complet d'un site e-commerce (500 pages). "
            "Analyse Core Web Vitals, crawl Screaming Frog, audit backlinks Ahrefs, "
            "étude de mots-clés, analyse concurrentielle. "
            "Livraison : rapport PDF 50+ pages + plan d'action priorisé."
        ),
        'skills': 'SEO, Screaming Frog, Ahrefs, Google Search Console, Analytics',
        'level': 'expert', 'budget': 1200, 'days': 14,
    },
    {
        'title': 'Optimisation SEO on-page – 20 pages',
        'category': 'SEO',
        'description': (
            "Optimisation SEO on-page de 20 pages clés d'un site B2B. "
            "Balises title/meta, structure Hn, densité mots-clés, maillage interne, "
            "optimisation images (alt, poids), schema.org. "
            "Rapport avant/après avec métriques Google."
        ),
        'skills': 'SEO On-page, WordPress, Yoast, Google Analytics',
        'level': 'intermediate', 'budget': 600, 'days': 10,
    },
    {
        'title': 'Netlinking – 20 backlinks qualifiés',
        'category': 'SEO',
        'description': (
            "Campagne de link building pour obtenir 20 backlinks thématiques DA 30+. "
            "Prospection, outreach, rédaction des articles invités. "
            "Rapport détaillé avec URLs, DA, trafic organique estimé."
        ),
        'skills': 'Link Building, Ahrefs, Outreach, Copywriting',
        'level': 'expert', 'budget': 900, 'days': 45,
    },

    # ── DATA ENTRY ─────────────────────────────────────────────────────────
    {
        'title': 'Saisie de données – Base clients Excel (2 000 lignes)',
        'category': 'Data Entry',
        'description': (
            "Saisie et structuration de 2 000 fiches clients depuis des documents PDF scannés "
            "vers un fichier Excel formaté. Champs : nom, prénom, email, téléphone, adresse, "
            "ville, catégorie client. Vérification des doublons incluse."
        ),
        'skills': 'Excel, Data Entry, Rigueur, Rapidité',
        'level': 'beginner', 'budget': 200, 'days': 7,
    },
    {
        'title': 'Scraping + nettoyage données – Annuaires professionnels',
        'category': 'Data Entry',
        'description': (
            "Extraction et nettoyage de données d'annuaires professionnels en ligne. "
            "Livraison en CSV : nom entreprise, secteur, téléphone, email, adresse. "
            "Volume : 5 000 entrées. Aucun doublon, données vérifiées."
        ),
        'skills': 'Python, BeautifulSoup, Pandas, Excel',
        'level': 'intermediate', 'budget': 450, 'days': 10,
    },
    {
        'title': 'Catalogage produits – Boutique en ligne (500 produits)',
        'category': 'Data Entry',
        'description': (
            "Saisie de 500 fiches produits dans une boutique WooCommerce : "
            "titre, description courte et longue, prix, images, catégorie, attributs, SKU. "
            "Données fournies en Excel. Rigueur et respect des gabarits imposés."
        ),
        'skills': 'WooCommerce, Excel, Data Entry, WordPress',
        'level': 'beginner', 'budget': 350, 'days': 14,
    },

    # ── CYBERSÉCURITÉ ─────────────────────────────────────────────────────
    {
        'title': 'Test de pénétration – Application web',
        'category': 'Cybersécurité',
        'description': (
            "Pentest black-box d'une application web SaaS. "
            "OWASP Top 10, SQLi, XSS, CSRF, IDOR, broken auth, exposed endpoints. "
            "Rapport exécutif + rapport technique avec CVSS scores et recommandations. "
            "Certification de conformité après correction incluse."
        ),
        'skills': 'Pentest, Burp Suite, OWASP, Kali Linux, Metasploit',
        'level': 'expert', 'budget': 2500, 'days': 21,
    },
    {
        'title': 'Audit sécurité configuration serveur Linux',
        'category': 'Cybersécurité',
        'description': (
            "Audit de sécurité d'un serveur Ubuntu en production. "
            "Vérification hardening SSH, firewall iptables/UFW, services exposés, "
            "permissions fichiers, fail2ban, mises à jour critiques. "
            "Rapport avec checklist CIS Benchmarks."
        ),
        'skills': 'Linux, SSH, UFW, Fail2ban, CIS Benchmark, Bash',
        'level': 'expert', 'budget': 800, 'days': 7,
    },
    {
        'title': 'Formation cybersécurité – Sensibilisation équipe (10 personnes)',
        'category': 'Cybersécurité',
        'description': (
            "Formation de sensibilisation à la cybersécurité pour une équipe non-technique de 10 personnes. "
            "Phishing, mots de passe, réseaux Wi-Fi publics, RGPD, bonnes pratiques quotidiennes. "
            "Support de formation + quiz final. Durée : 4 heures en présentiel ou visio."
        ),
        'skills': 'Cybersécurité, Formation, RGPD, Social Engineering',
        'level': 'intermediate', 'budget': 600, 'days': 14,
    },
    {
        'title': 'Mise en place HTTPS + WAF – Site e-commerce',
        'category': 'Cybersécurité',
        'description': (
            "Configuration SSL/TLS, HSTS, Cloudflare WAF, headers de sécurité CSP, "
            "X-Frame-Options, blocage bots malveillants. "
            "Test de performance après mise en place. Score SSL Labs : A+."
        ),
        'skills': 'SSL, Cloudflare, Nginx, HTTP Security Headers',
        'level': 'intermediate', 'budget': 400, 'days': 5,
    },

    # ── IA / MACHINE LEARNING ─────────────────────────────────────────────
    {
        'title': 'Modèle ML – Prédiction churn clients',
        'category': 'IA / Machine Learning',
        'description': (
            "Développer un modèle de machine learning pour prédire le churn (résiliation) "
            "de clients d'un opérateur télécom tunisien. "
            "Feature engineering, entraînement (Random Forest, XGBoost), évaluation, "
            "déploiement API Flask. Dataset fourni (50 000 lignes)."
        ),
        'skills': 'Python, Scikit-learn, XGBoost, Pandas, Flask, MLflow',
        'level': 'expert', 'budget': 3000, 'days': 45,
    },
    {
        'title': 'Chatbot RAG – Documentation technique',
        'category': 'IA / Machine Learning',
        'description': (
            "Créer un chatbot basé sur RAG (Retrieval-Augmented Generation) pour répondre "
            "aux questions sur une documentation technique volumineuse. "
            "Utilisation de LangChain, OpenAI GPT-4, Pinecone (vector DB). "
            "Interface web React simple incluse."
        ),
        'skills': 'LangChain, OpenAI, Python, Pinecone, React, FastAPI',
        'level': 'expert', 'budget': 2200, 'days': 30,
    },
    {
        'title': 'Analyse de sentiment – Avis clients arabes',
        'category': 'IA / Machine Learning',
        'description': (
            "Modèle d'analyse de sentiment pour des avis clients en arabe dialectal tunisien. "
            "Preprocessing NLP AraBERT, fine-tuning sur dataset annoté fourni, "
            "API d'inférence déployée. Rapport d'évaluation avec métriques F1/accuracy."
        ),
        'skills': 'Python, NLP, AraBERT, Transformers, FastAPI',
        'level': 'expert', 'budget': 2800, 'days': 40,
    },
    {
        'title': 'Automatisation tâches bureautiques – Python + IA',
        'category': 'IA / Machine Learning',
        'description': (
            "Automatiser des tâches répétitives bureautiques : tri et réponse automatique d'emails, "
            "extraction de données de PDFs, génération de rapports Excel, planification agenda. "
            "Scripts Python + intégration OpenAI pour les tâches de compréhension."
        ),
        'skills': 'Python, OpenAI API, PyPDF2, openpyxl, smtplib',
        'level': 'intermediate', 'budget': 900, 'days': 20,
    },
    {
        'title': 'Dashboard Python – Visualisation données ventes',
        'category': 'IA / Machine Learning',
        'description': (
            "Créer un dashboard interactif Plotly Dash pour visualiser les données de ventes "
            "d'une PME tunisienne. KPIs, graphiques temporels, carte régionale, export PDF. "
            "Connexion directe à une base MySQL."
        ),
        'skills': 'Python, Plotly Dash, Pandas, MySQL, Matplotlib',
        'level': 'intermediate', 'budget': 750, 'days': 15,
    },

    # ── SUPPORT TECHNIQUE ─────────────────────────────────────────────────
    {
        'title': 'Support technique client – Logiciel comptable (temps partiel)',
        'category': 'Support Technique',
        'description': (
            "Assurer le support de niveau 1 et 2 pour les utilisateurs d'un logiciel comptable. "
            "Tickets via Freshdesk, documentation des bugs, escalade niveau 3. "
            "Disponibilité : lundi-vendredi 9h-17h. Connaissance comptabilité appréciée."
        ),
        'skills': 'Support client, Freshdesk, Comptabilité, Patience',
        'level': 'beginner', 'budget': 600, 'days': 30,
    },
    {
        'title': 'Administration système – Serveur Windows Server',
        'category': 'Support Technique',
        'description': (
            "Administration d'un serveur Windows Server 2022 pour une PME. "
            "Configuration Active Directory, GPO, sauvegardes Veeam, monitoring Zabbix, "
            "gestion des licences Office 365. Intervention mensuelle + astreinte."
        ),
        'skills': 'Windows Server, Active Directory, PowerShell, Veeam, Office 365',
        'level': 'intermediate', 'budget': 800, 'days': 30,
    },
    {
        'title': 'Configuration réseau – PME 20 postes',
        'category': 'Support Technique',
        'description': (
            "Mise en place d'une infrastructure réseau pour une PME de 20 postes. "
            "Routeur, switch manageable, VLANs, Wi-Fi sécurisé WPA3, VPN site-à-site. "
            "Documentation réseau complète et formation de l'équipe."
        ),
        'skills': 'Cisco, MikroTik, VPN, VLAN, Wi-Fi, Câblage RJ45',
        'level': 'intermediate', 'budget': 1200, 'days': 7,
    },

    # ── WORDPRESS ─────────────────────────────────────────────────────────
    {
        'title': 'Boutique WooCommerce – Artisanat tunisien',
        'category': 'WordPress',
        'description': (
            "Création d'une boutique WooCommerce pour vendre des produits artisanaux tunisiens. "
            "Thème Flatsome, multi-devises TND/EUR/USD, livraison Tunisie Express intégrée, "
            "passerelle paiement Konnect, page À propos storytelling."
        ),
        'skills': 'WordPress, WooCommerce, Flatsome, Konnect, SEO',
        'level': 'intermediate', 'budget': 900, 'days': 20,
    },
    {
        'title': 'Optimisation vitesse WordPress – Score 90+ PageSpeed',
        'category': 'WordPress',
        'description': (
            "Optimiser les performances d'un site WordPress lent. "
            "Minification CSS/JS, lazy loading, CDN Cloudflare, cache WP Rocket, "
            "optimisation images WebP, requêtes base de données. "
            "Objectif : LCP < 2.5s, score PageSpeed > 90."
        ),
        'skills': 'WordPress, WP Rocket, Cloudflare, PageSpeed, WebP',
        'level': 'intermediate', 'budget': 400, 'days': 5,
    },
    {
        'title': 'Site multilingue WordPress – Arabe / Français',
        'category': 'WordPress',
        'description': (
            "Configuration d'un site WordPress bilingue arabe/français avec WPML. "
            "Traduction de 30 pages, RTL pour l'arabe, switcher de langue dans le header. "
            "Optimisation SEO multilingue avec hreflang."
        ),
        'skills': 'WordPress, WPML, RTL, Traduction, SEO',
        'level': 'intermediate', 'budget': 700, 'days': 14,
    },
    {
        'title': 'Plugin WordPress personnalisé – Système de réservation',
        'category': 'WordPress',
        'description': (
            "Développer un plugin WordPress sur mesure pour gérer les réservations "
            "d'un centre de bien-être. Calendrier de disponibilité, confirmation par email, "
            "paiement Stripe, dashboard admin. Testé sur WordPress 6.x."
        ),
        'skills': 'PHP, WordPress Plugin API, MySQL, Stripe, PHPUnit',
        'level': 'expert', 'budget': 1500, 'days': 30,
    },

    # ── CRÉATION DE CONTENU ───────────────────────────────────────────────
    {
        'title': 'Pack Reels Instagram – 12 vidéos courtes par mois',
        'category': 'Création de Contenu',
        'description': (
            "Création de 12 Reels Instagram par mois pour une marque de mode. "
            "Scénario, tournage avec matériel fourni ou DIY, montage CapCut, "
            "sous-titres, musique tendance, hashtags optimisés."
        ),
        'skills': 'CapCut, Instagram Reels, Scénario, Montage, Canva',
        'level': 'intermediate', 'budget': 600, 'days': 30,
    },
    {
        'title': 'Podcast – Montage et publication (4 épisodes)',
        'category': 'Création de Contenu',
        'description': (
            "Montage audio de 4 épisodes de podcast (30-45 min chacun). "
            "Nettoyage audio (bruit de fond, silences), intégration jingle, chapitrage, "
            "export MP3 optimisé, publication Spotify + Apple Podcasts."
        ),
        'skills': 'Audacity, Adobe Audition, Podcast, Audio Editing',
        'level': 'intermediate', 'budget': 500, 'days': 14,
    },
    {
        'title': 'Infographies LinkedIn – Pack de 10',
        'category': 'Création de Contenu',
        'description': (
            "Création de 10 infographies professionnelles pour LinkedIn. "
            "Thèmes : RH, management, productivité. "
            "Format carrousel PDF + images PNG. "
            "Identité visuelle fournie par le client."
        ),
        'skills': 'Canva, Adobe Illustrator, Design Graphique, LinkedIn',
        'level': 'beginner', 'budget': 300, 'days': 7,
    },

    # ── E-COMMERCE ─────────────────────────────────────────────────────────
    {
        'title': 'Marketplace multi-vendeurs – Shopify Plus',
        'category': 'E-commerce',
        'description': (
            "Configuration avancée d'une marketplace Shopify Plus multi-vendeurs. "
            "Application Multi-Vendor Marketplace, commissions automatiques, "
            "tableau de bord vendeur, intégration DHL Tunisie. "
            "Formation à l'administration incluse."
        ),
        'skills': 'Shopify Plus, Liquid, Multi-vendor, DHL API, Stripe',
        'level': 'expert', 'budget': 3500, 'days': 45,
    },
    {
        'title': 'Optimisation taux de conversion – Boutique WooCommerce',
        'category': 'E-commerce',
        'description': (
            "Analyse et optimisation du funnel d'achat d'une boutique WooCommerce. "
            "Heatmaps Hotjar, tests A/B checkout, upsells/cross-sells, "
            "récupération paniers abandonnés, amélioration fiches produits. "
            "Rapport mensuel avec métriques CVR, AOV."
        ),
        'skills': 'WooCommerce, Hotjar, A/B Testing, CRO, Analytics',
        'level': 'expert', 'budget': 1800, 'days': 30,
    },
    {
        'title': 'Intégration dropshipping AliExpress – WooCommerce',
        'category': 'E-commerce',
        'description': (
            "Mise en place d'un système dropshipping clé en main avec WooCommerce + DSers. "
            "Import automatique des produits AliExpress, synchronisation des stocks et prix, "
            "traitement automatisé des commandes, tracking clients."
        ),
        'skills': 'WooCommerce, DSers, AliExpress, Dropshipping, WordPress',
        'level': 'intermediate', 'budget': 650, 'days': 10,
    },
    {
        'title': 'Catalogue produits 3D – Bijouterie en ligne',
        'category': 'E-commerce',
        'description': (
            "Création de visuels 3D réalistes pour 30 bijoux (bagues, colliers, bracelets). "
            "Rendu photoréaliste, fond blanc e-commerce et fond lifestyle. "
            "Livraison PNG 3000x3000px optimisé web."
        ),
        'skills': 'Blender, 3D Modeling, Rendering, Photoshop',
        'level': 'expert', 'budget': 1200, 'days': 20,
    },

    # ── COMMUNITY MANAGEMENT ───────────────────────────────────────────────
    {
        'title': 'Community manager – Restaurant Tunis (Instagram + Facebook)',
        'category': 'Community Management',
        'description': (
            "Gestion quotidienne des réseaux sociaux d'un restaurant à Tunis. "
            "3 publications par semaine (photos, vidéos, Stories), réponses aux commentaires, "
            "organisation de concours, collaboration avec influenceurs locaux. "
            "Rapport mensuel des métriques."
        ),
        'skills': 'Instagram, Facebook, Canva, Community Management, Photographie',
        'level': 'beginner', 'budget': 450, 'days': 30,
    },
    {
        'title': 'Modération communauté Discord – Serveur gaming (5 000 membres)',
        'category': 'Community Management',
        'description': (
            "Modération active d'un serveur Discord gaming francophone de 5 000 membres. "
            "Application des règles, gestion des conflits, animation d'events hebdomadaires, "
            "bot Carl-bot configuré. Disponibilité soir et week-end."
        ),
        'skills': 'Discord, Modération, Carl-bot, Gaming, Animation',
        'level': 'beginner', 'budget': 300, 'days': 30,
    },
    {
        'title': 'Lancement et croissance communauté LinkedIn B2B',
        'category': 'Community Management',
        'description': (
            "Développer une communauté LinkedIn autour d'une marque B2B fintech. "
            "Stratégie de contenu (articles, sondages, lives), engagement des abonnés, "
            "partenariats créateurs. Objectif : +500 abonnés en 60 jours."
        ),
        'skills': 'LinkedIn, Community Building, Copywriting, B2B Marketing',
        'level': 'intermediate', 'budget': 800, 'days': 60,
    },
]


class Command(BaseCommand):
    help = 'Peuple la base avec 90+ offres réalistes couvrant 16 catégories'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear', action='store_true',
            help='Supprimer les offres populate_jobs existantes avant de recréer',
        )

    def handle(self, *args, **options):
        clients = self._get_or_create_clients()

        if options['clear']:
            deleted = JobOffer.objects.filter(
                client__username__in=[u.username for u in clients]
            ).delete()
            self.stdout.write(self.style.WARNING(f'  {deleted[0]} offres supprimées.'))

        created = self._create_jobs(clients)

        self._print_summary(created)

    # ─────────────────────────────────────────────────────────────────────
    def _get_or_create_clients(self):
        """Utilise les comptes clients existants + en crée si besoin."""
        clients = list(
            User.objects.filter(
                profile__role=Profile.ROLE_CLIENT,
                username__in=[f'client{i}' for i in range(1, 6)] + ['client_demo'],
            )
        )

        # Fallback : créer client_demo s'il n'existe pas
        if not clients:
            user, created = User.objects.get_or_create(
                username='client_demo',
                defaults={'email': 'demo@tunifreelance.com',
                          'first_name': 'Demo', 'last_name': 'Client'},
            )
            if created:
                user.set_password('Test1234')
                user.save()
                Profile.objects.update_or_create(
                    user=user, defaults={'role': Profile.ROLE_CLIENT}
                )
                self.stdout.write(self.style.SUCCESS('  Compte client_demo créé.'))
            clients = [user]

        self.stdout.write(
            f'  {len(clients)} compte(s) client trouvé(s) : '
            + ', '.join(u.username for u in clients)
        )
        return clients

    def _create_jobs(self, clients):
        created_count = 0
        today = date.today()

        for i, job in enumerate(JOBS):
            client = clients[i % len(clients)]
            deadline = today + timedelta(days=job['days'])

            _, created = JobOffer.objects.get_or_create(
                title=job['title'],
                client=client,
                defaults={
                    'category':         job['category'],
                    'description':      job['description'],
                    'budget':           Decimal(str(job['budget'])),
                    'deadline':         deadline,
                    'skills_required':  job['skills'],
                    'experience_level': job['level'],
                    'status':           JobOffer.STATUS_OPEN,
                },
            )
            safe_title = job["title"].encode('ascii', 'replace').decode('ascii')
            if created:
                created_count += 1
                self.stdout.write(f'  + {safe_title[:65]}')
            else:
                self.stdout.write(f'  ~ skip : {safe_title[:60]}')

        return created_count

    def _print_summary(self, created_count):
        total = JobOffer.objects.filter(status=JobOffer.STATUS_OPEN).count()
        cats  = JobOffer.objects.values_list('category', flat=True).distinct().count()

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 55))
        self.stdout.write(self.style.SUCCESS(f'  {created_count} nouvelles offres ajoutées'))
        self.stdout.write(f'  Total offres ouvertes en base : {total}')
        self.stdout.write(f'  Catégories couvertes : {cats}')
        self.stdout.write(self.style.SUCCESS('=' * 55))
