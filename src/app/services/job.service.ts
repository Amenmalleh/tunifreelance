import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface JobOffer {
  id: number;
  client: string;
  client_role: string;
  title: string;
  category: string;
  location?: string;
  description: string;
  budget: number;
  deadline: string;
  status: 'open' | 'closed';
  created_at: string;
  updated_at: string;
}

export interface CreateJobOfferPayload {
  title: string;
  category: string;
  location?: string;
  description: string;
  budget: number;
  deadline: string;
}

export interface JobSearchFilters {
  search?: string;
  category?: string;
  location?: string;
  min_budget?: number;
  max_budget?: number;
  sort?: string;
}

@Injectable({
  providedIn: 'root'
})
export class JobService {
  private readonly API_URL = 'http://127.0.0.1:8001/api';

  constructor(private http: HttpClient) { }

  getJobOffers(filters?: JobSearchFilters): Observable<JobOffer[]> {
    let params = new HttpParams();
    if (filters) {
      if (filters.search) params = params.set('search', filters.search);
      if (filters.category) params = params.set('category', filters.category);
      if (filters.location) params = params.set('location', filters.location);
      if (filters.min_budget) params = params.set('min_budget', filters.min_budget.toString());
      if (filters.max_budget) params = params.set('max_budget', filters.max_budget.toString());
      if (filters.sort) params = params.set('sort', filters.sort);
    }
    return this.http.get<JobOffer[]>(`${this.API_URL}/joboffers/`, { params });
  }

  getJobOffer(id: number): Observable<JobOffer> {
    return this.http.get<JobOffer>(`${this.API_URL}/joboffers/${id}/`);
  }

  createJobOffer(payload: CreateJobOfferPayload): Observable<JobOffer> {
    return this.http.post<JobOffer>(`${this.API_URL}/joboffers/`, payload);
  }
}
