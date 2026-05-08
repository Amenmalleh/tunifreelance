import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface ClientStats {
  total_expenses: number;
  active_jobs: number;
  hire_rate: number;
}

export interface ActiveProposal {
  id: number;
  job_title: string;
  proposed_price: number;
  created_at: string;
}

export interface FreelancerStats {
  total_revenue: number;
  active_proposals: number;
  active_proposals_list: ActiveProposal[];
  profile_score: number | null;
  ratings_count: number;
}

@Injectable({ providedIn: 'root' })
export class DashboardService {
  private http = inject(HttpClient);
  private base = 'http://127.0.0.1:8000/api';

  getClientStats(): Observable<ClientStats> {
    return this.http.get<ClientStats>(`${this.base}/dashboard/client/stats/`);
  }

  getFreelancerStats(): Observable<FreelancerStats> {
    return this.http.get<FreelancerStats>(`${this.base}/dashboard/freelancer/stats/`);
  }
}
