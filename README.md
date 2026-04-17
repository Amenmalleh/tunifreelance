# Freelancehub

A full-stack freelance marketplace platform built with **Angular** (frontend) and **Django REST Framework** (backend). The platform enables clients to post job offers and freelancers to submit proposals.

## Project Structure

```
tunifreelance/
├── backend/                 # Django REST API
│   ├── project/            # Django project settings
│   ├── api/                # Main API app with models, views, serializers
│   ├── db.sqlite3          # SQLite database
│   └── manage.py           # Django management script
├── src/                    # Angular frontend
│   ├── app/
│   │   ├── services/       # API services & guards
│   │   ├── pages/          # Page components
│   │   ├── components/     # Reusable components
│   │   └── app.routes.ts   # Routing configuration
│   └── index.html
├── package.json            # Node dependencies
└── angular.json            # Angular CLI configuration
```

## Features

### Authentication & Authorization
- **User Registration**: Dual-role signup (Client or Freelancer)
- **JWT Authentication**: Secure token-based authentication
- **Role-Based Access Control**: Different access based on user role
- **Profile Management**: User profiles with role association

### Job Lifecycle
- **JobOffer Model**: Clients can create, list, and manage job offerings
  - Fields: Title, Category, Description, Budget, Deadline, Status
  - Statuses: Open (accepting proposals) / Closed

- **Proposal Model**: Freelancers can submit proposals for jobs
  - Fields: Freelancer, Job Offer, Message, Proposed Price, Status
  - Statuses: Pending (awaiting review) / Accepted / Rejected

### API Endpoints

#### Authentication
- `POST /api/signup/` - User registration with role
- `POST /api/login/` - User login

#### Job Offers (Protected by JWT)
- `GET /api/joboffers/` - List all open job offers
- `POST /api/joboffers/` - Create new job offer (Client only)
- `GET /api/joboffers/{id}/` - Get job details
- `PUT /api/joboffers/{id}/` - Update job offer (Owner only)

#### Proposals (Protected by JWT)
- `GET /api/proposals/` - List proposals (filtered by user role)
- `POST /api/proposals/` - Submit new proposal (Freelancer only)
- `GET /api/proposals/{id}/` - Get proposal details

### Frontend Components
- **Auth Page**: Dual-step authentication with role selection
- **Find Jobs**: List and filter open job offers (Freelancer view)
- **Post Job**: Stepper form to create job offers (Client view)
- **Proposal Form**: Modal to submit proposals on specific jobs
- **Dashboard**: Role-based dashboard with stats and controls
- **Navbar**: Navigation with user profile and role switching

### Services
- `AuthService`: JWT tokens, user state, role management
- `JobService`: CRUD operations for job offers
- `ProposalService`: Create and list proposals
- `AuthGuard`: Protect routes requiring authentication
- `RoleGuard`: Protect routes requiring specific user role
- `authInterceptor`: Automatically attach JWT tokens to requests

## Development Server

### Backend (Django)

Install requirements:
```bash
pip install django djangorestframework djangorestframework-simplejwt django-cors-headers
```

Run migrations:
```bash
cd backend
python manage.py makemigrations
python manage.py migrate
```

Start the development server:
```bash
python manage.py runserver
```

Backend runs on: `http://127.0.0.1:8000/`

### Frontend (Angular)

Install dependencies:
```bash
npm install
```

Start the development server:
```bash
ng serve
```

Frontend runs on: `http://localhost:4200/`

## Build & Deployment

### Build Angular
```bash
ng build --configuration production
```

### Build Django for Production
```bash
python manage.py collectstatic
# Use Gunicorn or uWSGI for production
```

## Testing

### Unit Tests (Angular)
```bash
ng test
```

### E2E Tests
```bash
ng e2e
```

## Key Technologies

**Frontend:**
- Angular 21+ (Standalone components)
- Angular Material (UI components)
- RxJS (Reactive programming)
- TypeScript

**Backend:**
- Django 6.0+
- Django REST Framework
- Simple JWT (Authentication)
- SQLite (Development database)

## API Documentation

All API endpoints require:
- `Content-Type: application/json`
- JWT Bearer token in `Authorization: Bearer <token>` header

### Example: Create Job Offer (Client)

**Request:**
```
POST http://127.0.0.1:8000/api/joboffers/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "Senior Angular Developer",
  "category": "Web Development",
  "description": "Build a responsive web application client...",
  "budget": "5000",
  "deadline": "2026-05-15",
  "status": "open"
}
```

**Response:**
```json
{
  "id": 1,
  "client": "johndoe",
  "client_role": "client",
  "title": "Senior Angular Developer",
  "category": "Web Development",
  "description": "Build a responsive web application client...",
  "budget": "5000.00",
  "deadline": "2026-05-15",
  "status": "open",
  "created_at": "2026-04-14T20:30:00Z",
  "updated_at": "2026-04-14T20:30:00Z"
}
```

### Example: Submit Proposal (Freelancer)

**Request:**
```
POST http://127.0.0.1:8000/api/proposals/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "job_offer": 1,
  "message": "I have 8 years of Angular experience and can deliver this in 2 weeks.",
  "proposed_price": "4500"
}
```

**Response:**
```json
{
  "id": 1,
  "freelance": "freelancer123",
  "freelance_role": "freelancer",
  "job_offer": 1,
  "job_offer_title": "Senior Angular Developer",
  "message": "I have 8 years of Angular experience...",
  "proposed_price": "4500.00",
  "status": "pending",
  "created_at": "2026-04-14T20:35:00Z"
}
```

## Permissions & Access Control

### Client Role
- Create, read, update job offers
- View proposals submitted for their jobs
- Accept/reject freelancer proposals
- Cannot submit proposals

### Freelancer Role
- View open job offers
- Submit and manage proposals
- Cannot create or delete job offers
- Cannot modify other users' proposals

## Security Considerations

- JWT tokens expire after 5 minutes (configurable)
- Refresh tokens last 1 day
- CORS restricted to `http://localhost:4200` (development)
- Password validation enforced
- Role-based permissions on all endpoints
- CSRF protection enabled

## Environment Variables (Backend)

Create a `.env` file in the backend directory:
```
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
```

## Future Enhancements

- [ ] Real-time notifications using WebSockets
- [ ] Payment integration (Stripe, PayPal)
- [ ] Review and rating system
- [ ] Dispute resolution
- [ ] Profile verification
- [ ] Advanced search and filtering
- [ ] Saved jobs/favorites
- [ ] Message/chat system
- [ ] Admin dashboard
- [ ] Email notifications

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions, please create an issue on the GitHub repository.

---

**Last Updated**: April 15, 2026
**Version**: 1.1.0 (Job & Proposal System)

