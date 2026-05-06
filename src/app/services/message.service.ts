import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Message {
  id: number;
  sender: string;
  sender_id: number;
  recipient: number;
  recipient_username: string;
  recipient_id: number;
  proposal?: number;
  job_offer?: number;
  content: string;
  created_at: string;
  is_read: boolean;
}

export interface CreateMessagePayload {
  recipient: number;
  proposal?: number;
  job_offer?: number;
  content: string;
}

export interface UserSearchResult {
  id: number;
  username: string;
  first_name: string;
  last_name: string;
  role: string;
}

@Injectable({
  providedIn: 'root'
})
export class MessageService {
  private readonly API_URL = 'http://127.0.0.1:8001/api';

  constructor(private http: HttpClient) {}

  getMessages(): Observable<Message[]> {
    return this.http.get<Message[]>(`${this.API_URL}/messages/`);
  }

  getConversation(userId: number): Observable<Message[]> {
    return this.http.get<Message[]>(`${this.API_URL}/messages/?partner=${userId}`);
  }

  sendMessage(payload: CreateMessagePayload): Observable<Message> {
    return this.http.post<Message>(`${this.API_URL}/messages/`, payload);
  }

  markConversationRead(partnerId: number): Observable<any> {
    return this.http.post(`${this.API_URL}/messages/mark-read/`, { partner_id: partnerId });
  }

  markAsRead(messageId: number): Observable<Message> {
    return this.http.patch<Message>(`${this.API_URL}/messages/${messageId}/`, { is_read: true });
  }

  deleteMessage(messageId: number): Observable<void> {
    return this.http.delete<void>(`${this.API_URL}/messages/${messageId}/`);
  }

  searchUsers(query: string): Observable<UserSearchResult[]> {
    return this.http.get<UserSearchResult[]>(`${this.API_URL}/users/search/?q=${query}`);
  }
}
