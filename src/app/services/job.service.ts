import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface JobOffer {
  id: number;
  client: string;
  client_role: string;
  title: string;
  category: string;
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
  description: string;
  budget: number;
  deadline: string;
}

@Injectable({
  providedIn: 'root'
})
export class JobService {
  private readonly API_URL = 'http://127.0.0.1:8000/api';

  constructor(private http: HttpClient) {}

  getJobOffers(): Observable<JobOffer[]> {
    return this.http.get<JobOffer[]>(`${this.API_URL}/joboffers/`);
  }

  getJobOffer(id: number): Observable<JobOffer> {
    return this.http.get<JobOffer>(`${this.API_URL}/joboffers/${id}/`);
  }

  createJobOffer(payload: CreateJobOfferPayload): Observable<JobOffer> {
    return this.http.post<JobOffer>(`${this.API_URL}/joboffers/`, payload);
  }
}
