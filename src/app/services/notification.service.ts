import { Injectable, signal, computed } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, interval } from 'rxjs';
import { tap, switchMap } from 'rxjs/operators';

export interface AppNotification {
  id: number;
  notification_type: string;
  title: string;
  message: string;
  is_read: boolean;
  link: string;
  created_at: string;
}

@Injectable({
  providedIn: 'root'
})
export class NotificationService {
  private readonly API_URL = 'http://127.0.0.1:8001/api';

  private notificationsSignal = signal<AppNotification[]>([]);
  private unreadCountSignal = signal<number>(0);

  notifications = computed(() => this.notificationsSignal());
  unreadCount = computed(() => this.unreadCountSignal());

  constructor(private http: HttpClient) {}

  loadNotifications(): Observable<AppNotification[]> {
    return this.http.get<AppNotification[]>(`${this.API_URL}/notifications/`).pipe(
      tap(notifications => {
        this.notificationsSignal.set(notifications);
        this.unreadCountSignal.set(notifications.filter(n => !n.is_read).length);
      })
    );
  }

  getUnreadCount(): Observable<{ count: number }> {
    return this.http.get<{ count: number }>(`${this.API_URL}/notifications/unread-count/`).pipe(
      tap(result => this.unreadCountSignal.set(result.count))
    );
  }

  markAsRead(id: number): Observable<any> {
    return this.http.post(`${this.API_URL}/notifications/${id}/mark-read/`, {}).pipe(
      tap(() => {
        const updated = this.notificationsSignal().map(n =>
          n.id === id ? { ...n, is_read: true } : n
        );
        this.notificationsSignal.set(updated);
        this.unreadCountSignal.set(updated.filter(n => !n.is_read).length);
      })
    );
  }

  markAllAsRead(): Observable<any> {
    return this.http.post(`${this.API_URL}/notifications/mark-all-read/`, {}).pipe(
      tap(() => {
        const updated = this.notificationsSignal().map(n => ({ ...n, is_read: true }));
        this.notificationsSignal.set(updated);
        this.unreadCountSignal.set(0);
      })
    );
  }

  getNotificationIcon(type: string): string {
    switch (type) {
      case 'proposal_received': return 'person_add';
      case 'proposal_accepted': return 'check_circle';
      case 'proposal_rejected': return 'cancel';
      case 'message_received': return 'chat';
      case 'contract_created': return 'handshake';
      case 'contract_completed': return 'task_alt';
      case 'contract_cancelled': return 'block';
      default: return 'notifications';
    }
  }

  getNotificationColor(type: string): string {
    switch (type) {
      case 'proposal_received': return '#4f46e5';
      case 'proposal_accepted': return '#10b981';
      case 'proposal_rejected': return '#ef4444';
      case 'message_received': return '#06b6d4';
      case 'contract_created': return '#8b5cf6';
      case 'contract_completed': return '#10b981';
      case 'contract_cancelled': return '#f59e0b';
      default: return '#6b7280';
    }
  }
}
