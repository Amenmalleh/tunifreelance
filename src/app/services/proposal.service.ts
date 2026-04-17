import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Proposal {
  id: number;
  freelance: string;
  freelance_role: string;
  job_offer: number;
  job_offer_title: string;
  message: string;
  proposed_price: number;
  status: 'pending' | 'accepted' | 'rejected';
  created_at: string;
}

export interface CreateProposalPayload {
  job_offer: number;
  message: string;
  proposed_price: number;
}

@Injectable({
  providedIn: 'root'
})
export class ProposalService {
  private readonly API_URL = 'http://127.0.0.1:8000/api';

  constructor(private http: HttpClient) {}

  createProposal(payload: CreateProposalPayload): Observable<Proposal> {
    return this.http.post<Proposal>(`${this.API_URL}/proposals/`, payload);
  }

  getProposals(): Observable<Proposal[]> {
    return this.http.get<Proposal[]>(`${this.API_URL}/proposals/`);
  }
}
