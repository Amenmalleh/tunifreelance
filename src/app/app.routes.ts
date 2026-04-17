import { Routes } from '@angular/router';
import { Home } from './pages/home/home';
import { Auth } from './pages/auth/auth';
import { FindJobs } from './pages/find-jobs/find-jobs';
import { FindTalent } from './pages/find-talent/find-talent';
import { PostJob } from './pages/post-job/post-job';
import { Dashboard } from './pages/dashboard/dashboard';
import { ProposalForm } from './pages/proposal-form/proposal-form';
import { Messages } from './pages/messages/messages';
import { AuthGuard } from './services/auth.guard';
import { RoleGuard } from './services/role.guard';

export const routes: Routes = [
    { path: '', redirectTo: 'home', pathMatch: 'full' },
    { path: 'home', component: Home },
    { path: 'jobs', component: FindJobs, canActivate: [AuthGuard] },
    { path: 'talent', component: FindTalent, canActivate: [AuthGuard] },
    { path: 'post-job', component: PostJob, canActivate: [AuthGuard, RoleGuard], data: { role: 'client' } },
    { path: 'dashboard', component: Dashboard, canActivate: [AuthGuard] },
    { path: 'proposal/:id', component: ProposalForm, canActivate: [AuthGuard, RoleGuard], data: { role: 'freelancer' } },
    { path: 'messages', component: Messages, canActivate: [AuthGuard] },
    { path: 'signin', component: Auth },
    { path: 'signup', component: Auth },
    { path: 'settings', component: Dashboard },
    { path: 'auth', redirectTo: 'signin' }
];