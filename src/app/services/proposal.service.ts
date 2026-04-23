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
  proposed_deadline: string;
  status: 'pending' | 'accepted' | 'rejected';
  created_at: string;
}

export interface CreateProposalPayload {
  job_offer: number;
  message: string;
  proposed_price: number;
  proposed_deadline?: string;
}

export interface Contract {
  id: number;
  proposal: number;
  job_offer: number;
  freelancer: string;
  client: string;
  job_title: string;
  contract_price: number;
  contract_deadline: string;
  status: 'active' | 'completed' | 'cancelled';
  amount_locked: number;
  is_completed: boolean;
  created_at: string;
  completed_at: string | null;
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

  getProposal(id: number): Observable<Proposal> {
    return this.http.get<Proposal>(`${this.API_URL}/proposals/${id}/`);
  }

  acceptProposal(id: number): Observable<{ message: string; contract: Contract }> {
    return this.http.post<{ message: string; contract: Contract }>(
      `${this.API_URL}/proposals/${id}/accept/`,
      {}
    );
  }

  rejectProposal(id: number): Observable<{ message: string; proposal: Proposal }> {
    return this.http.post<{ message: string; proposal: Proposal }>(
      `${this.API_URL}/proposals/${id}/reject/`,
      {}
    );
  }

  // Contract operations
  getContracts(): Observable<Contract[]> {
    return this.http.get<Contract[]>(`${this.API_URL}/contracts/`);
  }

  getContract(id: number): Observable<Contract> {
    return this.http.get<Contract>(`${this.API_URL}/contracts/${id}/`);
  }

  completeContract(id: number): Observable<{ message: string; contract: Contract }> {
    return this.http.post<{ message: string; contract: Contract }>(
      `${this.API_URL}/contracts/${id}/complete/`,
      {}
    );
  }

  cancelContract(id: number): Observable<{ message: string; contract: Contract }> {
    return this.http.post<{ message: string; contract: Contract }>(
      `${this.API_URL}/contracts/${id}/cancel/`,
      {}
    );
  }
}
