import { Routes } from '@angular/router';
import { Home } from './pages/home/home';
import { Auth } from './pages/auth/auth';
import { FindJobs } from './pages/find-jobs/find-jobs';
import { FindTalent } from './pages/find-talent/find-talent';
import { PostJob } from './pages/post-job/post-job';
import { Dashboard } from './pages/dashboard/dashboard';

export const routes: Routes = [
    { path: '', redirectTo: 'home', pathMatch: 'full' },
    { path: 'home', component: Home },
    { path: 'jobs', component: FindJobs },
    { path: 'talent', component: FindTalent },
    { path: 'post-job', component: PostJob },
    { path: 'dashboard', component: Dashboard },
    { path: 'signin', component: Auth },
    { path: 'signup', component: Auth },
    { path: 'auth', redirectTo: 'signin' }
];