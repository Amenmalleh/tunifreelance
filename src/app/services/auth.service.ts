import { Injectable, signal, computed } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Router } from '@angular/router';
import { Observable, throwError } from 'rxjs';
import { catchError, map, tap } from 'rxjs/operators';

export type UserRole = 'client' | 'freelancer';

export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  role: UserRole;
}

export interface AuthResponse {
  user: User;
  access: string;
  refresh: string;
}

interface RefreshResponse {
  access: string;
}

export interface SignupData {
  username: string;
  email: string;
  password: string;
  password2: string;
  first_name: string;
  last_name: string;
  role: UserRole;
}

export interface LoginData {
  identifier: string;
  password: string;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private readonly API_URL = 'http://127.0.0.1:8000/api';

  private roleSignal = signal<UserRole>('freelancer');
  private isLoggedInSignal = signal<boolean>(false);
  private userSignal = signal<User | null>(null);
  private accessTokenSignal = signal<string | null>(null);
  private refreshTokenSignal = signal<string | null>(null);

  // Read-only access to state
  currentRole = computed(() => this.roleSignal());
  isLoggedIn = computed(() => this.isLoggedInSignal());
  currentUser = computed(() => this.userSignal());
  accessToken = computed(() => this.accessTokenSignal());

  constructor(private http: HttpClient, private router: Router) {
    this.loadFromStorage();
  }

  private loadFromStorage() {
    const savedRole = localStorage.getItem('user_role') as UserRole;
    if (savedRole) {
      this.roleSignal.set(savedRole);
    }

    const savedAccessToken = localStorage.getItem('access_token');
    const savedRefreshToken = localStorage.getItem('refresh_token');
    const savedUser = localStorage.getItem('user');
    if (savedUser && (savedAccessToken || savedRefreshToken)) {
      try {
        const parsedUser = JSON.parse(savedUser) as User;
        this.userSignal.set(parsedUser);
        this.isLoggedInSignal.set(true);
        if (parsedUser.role) {
          this.roleSignal.set(parsedUser.role);
        }
      } catch (e) {
        console.error('Error parsing saved user:', e);
      }
    }

    if (savedAccessToken) {
      this.accessTokenSignal.set(savedAccessToken);
    }

    if (savedRefreshToken) {
      this.refreshTokenSignal.set(savedRefreshToken);
    }
  }

  private saveToStorage(user: User, access: string, refresh: string) {
    localStorage.setItem('user', JSON.stringify(user));
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
    localStorage.setItem('user_role', user.role);
  }

  private clearStorage() {
    localStorage.removeItem('user');
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_role');
  }

  setRole(role: UserRole) {
    this.roleSignal.set(role);
    localStorage.setItem('user_role', role);
  }

  signup(data: SignupData): Observable<AuthResponse> {
    return this.http.post<AuthResponse>(`${this.API_URL}/signup/`, data).pipe(
      tap(response => {
        this.userSignal.set(response.user);
        this.accessTokenSignal.set(response.access);
        this.refreshTokenSignal.set(response.refresh);
        this.isLoggedInSignal.set(true);
        this.setRole(response.user.role);
        this.saveToStorage(response.user, response.access, response.refresh);
      }),
      catchError(this.handleError)
    );
  }

  login(data: LoginData): Observable<AuthResponse> {
    return this.http.post<AuthResponse>(`${this.API_URL}/login/`, data).pipe(
      tap(response => {
        this.userSignal.set(response.user);
        this.accessTokenSignal.set(response.access);
        this.refreshTokenSignal.set(response.refresh);
        this.isLoggedInSignal.set(true);
        this.setRole(response.user.role);
        this.saveToStorage(response.user, response.access, response.refresh);
      }),
      catchError(this.handleError)
    );
  }

  logout() {
    this.userSignal.set(null);
    this.accessTokenSignal.set(null);
    this.refreshTokenSignal.set(null);
    this.isLoggedInSignal.set(false);
    this.clearStorage();
    this.router.navigate(['/signin']);
  }

  clearInvalidToken() {
    this.accessTokenSignal.set(null);
    localStorage.removeItem('access_token');

    const refresh = this.refreshTokenSignal() ?? localStorage.getItem('refresh_token');
    if (!refresh) {
      this.isLoggedInSignal.set(false);
    }
  }

  hasRefreshToken(): boolean {
    return Boolean(this.refreshTokenSignal() ?? localStorage.getItem('refresh_token'));
  }

  refreshAccessToken(): Observable<string> {
    const refresh = this.refreshTokenSignal() ?? localStorage.getItem('refresh_token');

    if (!refresh) {
      this.logout();
      return throwError(() => new Error('No refresh token available.'));
    }

    return this.http.post<RefreshResponse>(`${this.API_URL}/token/refresh/`, { refresh }).pipe(
      tap(response => {
        this.accessTokenSignal.set(response.access);
        localStorage.setItem('access_token', response.access);
        this.isLoggedInSignal.set(true);
      }),
      map(response => response.access),
      catchError((error) => {
        this.logout();
        return this.handleError(error);
      })
    );
  }

  toggleRole() {
    const nextRole = this.currentRole() === 'freelancer' ? 'client' : 'freelancer';
    this.setRole(nextRole);
  }

  getCurrentUserId(): number | null {
    const user = this.currentUser();
    return user ? user.id : null;
  }

  private handleError(error: HttpErrorResponse) {
    let errorMessage = 'Une erreur inconnue est survenue.';
    if (error.status === 0) {
      errorMessage = 'Impossible de joindre le serveur. Vérifiez votre connexion.';
    } else if (error.error && typeof error.error === 'object') {
      const e = error.error;
      if (e.error)              errorMessage = e.error;
      else if (e.identifier)    errorMessage = Array.isArray(e.identifier) ? e.identifier[0] : e.identifier;
      else if (e.password)      errorMessage = Array.isArray(e.password)   ? e.password[0]   : e.password;
      else if (e.username)      errorMessage = Array.isArray(e.username)   ? e.username[0]   : e.username;
      else if (e.email)         errorMessage = Array.isArray(e.email)      ? e.email[0]      : e.email;
      else if (e.non_field_errors) errorMessage = e.non_field_errors[0];
      else if (e.detail)        errorMessage = e.detail;
    }
    console.error('Auth error:', error);
    return throwError(() => new Error(errorMessage));
  }
}
