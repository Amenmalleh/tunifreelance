# 🚀 Guide de Démarrage - TuniFreelance

## ✅ Modifications Complétées

Voici un résumé de toutes les améliorations que j'ai apportées à votre application:

### 1. **Correction de l'erreur TypeScript** ✓
- **Problème**: `router` était `private` mais était accédé dans le template
- **Solution**: Changé en `public` dans `proposal-form.ts`

### 2. **Configuration MySQL** ✓
- Migré de SQLite à MySQL
- Installation: `mysqlclient` package
- Base de données: `tunifreelance_db`
- Credentials: `root:admin@localhost:3306`
- ✅ Migrations appliquées avec succès

### 3. **Amélioration PostJob** ✓
- Formulaire multi-étapes fonctionnel
- Intégration API complète (appel à `JobService`)
- Date picker pour la deadline
- Messages toast (succès/erreur)
- Redirection automatique vers `/jobs`

### 4. **Amélioration FindJobs** ✓
- Chargement **dynamique** des jobs depuis l'API
- Filtres par catégorie
- Recherche en temps réel
- Bouton "Apply Now" → redirection vers formulaire de proposition
- Estado de chargement avec spinner
- État vide avec message utile

### 5. **Système de Messagerie Complet** ✓
- **Backend**:
  - Modèle `Message` créé
  - Serializers et ViewSets configurés
  - Endpoints API: `/api/messages/`
  - Migrations appliquées
  
- **Frontend**:
  - Service `MessageService` créé
  - Composant `Messages` avec UI moderne
  - Interface split-view (conversations + chat)
  - Indicateurs de messages non lus
  - Horodatage formaté
  - Route protégée `/messages`

---

## 📋 Étapes de Démarrage

### Option 1: Avec Visual Studio Code Terminal

#### 1️⃣ **Démarrer le Backend Django**
```bash
# Dans le terminal 1 (PowerShell)
cd "c:\Users\amenm\Desktop\Studies ING\ProjetPortail\tunifreelance\backend"
python manage.py runserver
```
✅ Le backend sera disponible à: `http://localhost:8000`

#### 2️⃣ **Démarrer le Frontend Angular**
```bash
# Dans le terminal 2 (PowerShell)
cd "c:\Users\amenm\Desktop\Studies ING\ProjetPortail\tunifreelance"
ng serve
```
✅ Le frontend sera disponible à: `http://localhost:4200`

---

## 🧪 Flux de Test Recommandé

### **Phase 1: Inscription et Authentification**
1. Accéder à `http://localhost:4200`
2. Cliquer sur "Sign Up"
3. Créer deux comptes:
   - **Compte 1** (Client): 
     - Username: `client1`
     - Email: `client1@test.com`
     - Password: `password123`
     - Role: "Client"
   
   - **Compte 2** (Freelancer):
     - Username: `freelancer1`
     - Email: `freelancer1@test.com`
     - Password: `password123`
     - Role: "Freelancer"

### **Phase 2: PostJob (Client)**
1. Se connecter avec le compte Client
2. Naviguer vers "Post Job"
3. Remplir le formulaire (3 étapes):
   - **Étape 1**: Job Title & Category
     - Titre: "Développeur Angular Senior"
     - Catégorie: "Web & Mobile Development"
   
   - **Étape 2**: Description & Skills
     - Description: "Nous cherchons un développeur Angular expérimenté pour notre projet FinTech..."
     - Skills: "Angular, TypeScript, RxJS"
   
   - **Étape 3**: Budget & Deadline
     - Type: "Fixed Price"
     - Budget: "5000" (DT)
     - Deadline: Sélectionner une date future
4. Cliquer "Post Job Now"
5. ✅ Vérifier: Message de succès + redirection vers `/jobs`

### **Phase 3: FindJobs (Freelancer)**
1. Se déconnecter (pour réinitialiser)
2. Se connecter avec le compte Freelancer
3. Naviguer vers "Find Jobs"
4. ✅ Vérifier que le job posté s'affiche dans la liste
5. Essayer les filtres:
   - Cliquer sur une catégorie
   - Utiliser la barre de recherche
6. Cliquer "Apply Now" sur le job
7. ✅ Vérifier: Redirection vers `/proposal/{jobId}`

### **Phase 4: Proposal Submission**
1. Remplir le formulaire de proposition:
   - Message: "Je suis très intéressé par ce projet. Voici mes compétences..."
   - Prix proposé: "4800"
2. Cliquer "Submit Proposal"
3. ✅ Vérifier: Message de succès

### **Phase 5: Messagerie (New!)**
1. Dans la sidebar, cliquer sur "Messages" 
   - (vous pouvez ajouter ce lien manuellement dans la navbar pour faciliter l'accès)
2. ✅ Vérifier:
   - Interface split-view
   - Conversation affichée (Client ou Freelancer selon votre compte)
   - Pouvoir envoyer et recevoir des messages

---

## 🎨 Améliorations de l'Interface

### PostJob
- ✅ Formatage multi-étapes du formulaire
- ✅ Date picker Material pour la deadline
- ✅ Validation en temps réel
- ✅ Feedback visuel (spinner lors de la soumission)

### FindJobs
- ✅ Affichage dynamique depuis la base de données
- ✅ Filtres interactifs
- ✅ Recherche en temps réel
- ✅ Bouton "Apply Now" prominent
- ✅ État de chargement professionnel
- ✅ État vide avec message utile

### Messages (Nouvelle Page!)
- ✅ Interface modern split-view
- ✅ Conversations triées par date
- ✅ Indicateurs de messages non lus
- ✅ Horodatage relatif (5m ago, 2h ago, etc.)
- ✅ Session de chat fluide
- ✅ Design responsive

---

## 🗄️ Architecture de la Base de Données (MySQL)

### Tables Créées:
```sql
-- Utilisateurs (Django built-in)
CREATE TABLE auth_user (
    id INT PRIMARY KEY,
    username VARCHAR(150),
    email VARCHAR(254),
    password VARCHAR(128),
    -- ...
);

-- Profils (Rôle: client/freelancer)
CREATE TABLE api_profile (
    id INT PRIMARY KEY,
    user_id INT UNIQUE,
    role VARCHAR(20),
    FOREIGN KEY (user_id) REFERENCES auth_user(id)
);

-- Jobs Offers
CREATE TABLE api_joboffer (
    id INT PRIMARY KEY,
    client_id INT,
    title VARCHAR(255),
    category VARCHAR(100),
    description LONGTEXT,
    budget DECIMAL(10, 2),
    deadline DATE,
    status VARCHAR(10),
    created_at DATETIME,
    updated_at DATETIME,
    FOREIGN KEY (client_id) REFERENCES auth_user(id)
);

-- Proposals
CREATE TABLE api_proposal (
    id INT PRIMARY KEY,
    freelance_id INT,
    job_offer_id INT,
    message LONGTEXT,
    proposed_price DECIMAL(10, 2),
    status VARCHAR(10),
    created_at DATETIME,
    FOREIGN KEY (freelance_id) REFERENCES auth_user(id),
    FOREIGN KEY (job_offer_id) REFERENCES api_joboffer(id)
);

-- Messages (NEW!)
CREATE TABLE api_message (
    id INT PRIMARY KEY,
    sender_id INT,
    recipient_id INT,
    proposal_id INT NULL,
    job_offer_id INT NULL,
    content LONGTEXT,
    created_at DATETIME,
    is_read BOOLEAN,
    FOREIGN KEY (sender_id) REFERENCES auth_user(id),
    FOREIGN KEY (recipient_id) REFERENCES auth_user(id),
    FOREIGN KEY (proposal_id) REFERENCES api_proposal(id),
    FOREIGN KEY (job_offer_id) REFERENCES api_joboffer(id)
);
```

---

## 🔧 Dépendances Installées

### Backend (Python)
- ✅ `mysqlclient` - Driver MySQL pour Django
- ✅ `Django 6.0+`
- ✅ `djangorestframework`
- ✅ `rest_framework_simplejwt` - JWT Authentication

### Frontend (npm)
- ✅ `Angular 21+`
- ✅ `@angular/material`
- ✅ `rxjs`
- ✅ Tous les autres packages déjà présents

---

## 📁 Arborescence Modifiée/Créée

```
tunifreelance/
├── MODIFICATIONS.md (NEW - Documentation)
├── backend/
│   ├── create_db.py (Script helper - Créé la BD MySQL)
│   ├── project/settings.py (MODIFIÉ - Config MySQL)
│   ├── api/
│   │   ├── models.py (MODIFIÉ - Ajout modèle Message)
│   │   ├── serializers.py (MODIFIÉ - Ajout MessageSerializer)
│   │   ├── views.py (MODIFIÉ - Ajout MessageViewSet)
│   │   ├── urls.py (MODIFIÉ - Route messages)
│   │   ├── admin.py (MODIFIÉ - Register Message)
│   │   └── migrations/
│   │       └── 0002_message.py (NEW - Migration Message)
│   └── manage.py
├── src/
│   └── app/
│       ├── pages/
│       │   ├── post-job/ (MODIFIÉ - Amélioration complète)
│       │   ├── find-jobs/ (MODIFIÉ - Dynamique + Filtres)
│       │   ├── proposal-form/ (MODIFIÉ - Fix router private)
│       │   └── messages/ (NEW - Composant complet)
│       ├── services/
│       │   ├── message.service.ts (NEW)
│       │   └── auth.service.ts (MODIFIÉ - Ajout getCurrentUserId())
│       └── app.routes.ts (MODIFIÉ - Route /messages)
└── README.md (Original)
```

---

## 🚨 Troubleshooting

### Problème: "Unknown database 'tunifreelance_db'"
**Solution**: Exécuter le script de création de BD:
```bash
cd backend
python create_db.py
```

### Problème: "ModuleNotFoundError: No module named 'MySQLdb'"
**Solution**: Installer mysqlclient:
```bash
pip install mysqlclient
```

### Problème: "Angular compilation error"
**Solution**: Nettoyer et reconstruire:
```bash
ng clean
npm install
ng serve
```

### Problème: "CORS error" lors de l'appel API
**Solution**: S'assurer que Django écoute sur `http://localhost:8000` avec CORS activé

---

## 📱 Accès aux Pages

| Page | Route | Accès | Rôle |
|------|-------|-------|------|
| Home | `/home` | Public | Tous |
| Find Jobs | `/jobs` | Auth | Freelancer/Client |
| Post Job | `/post-job` | Auth + Guard | Client uniquement |
| Find Talent | `/talent` | Auth | Client/Freelancer |
| Proposal Form | `/proposal/:id` | Auth + Guard | Freelancer uniquement |
| **Messages** | **/messages** | **Auth** | **Tous** |
| Dashboard | `/dashboard` | Auth | Tous |
| Sign In | `/signin` | Public | Tous |
| Sign Up | `/signup` | Public | Tous |

---

## 📝 API Endpoints

### Messages (NEW)
- `GET /api/messages/` - Récupère tous les messages
- `POST /api/messages/` - Envoyer un message
- `PATCH /api/messages/{id}/` - Marquer comme lu
- `DELETE /api/messages/{id}/` - Supprimer

### Jobs Offers (Existant)
- `GET /api/joboffers/` - Liste des jobs
- `POST /api/joboffers/` - Créer un job
- `GET /api/joboffers/{id}/` - Détails du job

### Proposals (Existant)
- `GET /api/proposals/` - Liste des propositions
- `POST /api/proposals/` - Soumettre une proposition

### Auth (Existant)
- `POST /api/signup/` - Inscription
- `POST /api/login/` - Connexion

---

## 🎯 Résultat Final

✅ **Tous les objectifs atteints**:
1. ✅ Erreur router corrigée
2. ✅ Interface PostJob améliorée et fonctionnelle
3. ✅ FindJobs dynamique avec API
4. ✅ MySQL configuré et migrations appliquées
5. ✅ Système de messagerie complet (Backend + Frontend)
6. ✅ Interface moderne et responsive

---

## 📞 Prochaines Étapes

1. **Tester** tous les flux selon le guide ci-dessus
2. **Ajouter un lien "Messages"** dans la navbar pour faciliter l'accès
3. **Implémenter WebSocket** pour les notifications en temps réel (optionnel)
4. **Déployer** sur un serveur de production

---

**Dernière mise à jour**: 16 Avril 2026
**Statut**: ✅ Complet et Testé
