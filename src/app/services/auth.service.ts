import { Injectable, signal, computed } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Router } from '@angular/router';
import { Observable, throwError } from 'rxjs';
import { catchError, tap } from 'rxjs/operators';

export type UserRole = 'client' | 'freelancer';

export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
}

export interface AuthResponse {
  user: User;
  access: string;
  refresh: string;
}

export interface SignupData {
  username: string;
  email: string;
  password: string;
  password2: string;
  first_name: string;
  last_name: string;
}

export interface LoginData {
  username: string;
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
    if (savedRole) this.roleSignal.set(savedRole);

    const savedUser = localStorage.getItem('user');
    if (savedUser) {
      try {
        this.userSignal.set(JSON.parse(savedUser));
        this.isLoggedInSignal.set(true);
      } catch (e) {
        console.error('Error parsing saved user:', e);
      }
    }

    const savedAccessToken = localStorage.getItem('access_token');
    if (savedAccessToken) {
      this.accessTokenSignal.set(savedAccessToken);
    }

    const savedRefreshToken = localStorage.getItem('refresh_token');
    if (savedRefreshToken) {
      this.refreshTokenSignal.set(savedRefreshToken);
    }
  }

  private saveToStorage(user: User, access: string, refresh: string) {
    localStorage.setItem('user', JSON.stringify(user));
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
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

  toggleRole() {
    const nextRole = this.currentRole() === 'freelancer' ? 'client' : 'freelancer';
    this.setRole(nextRole);
  }

  private handleError(error: HttpErrorResponse) {
    let errorMessage = 'An unknown error occurred!';
    if (error.error instanceof ErrorEvent) {
      // Client-side or network error
      errorMessage = `Error: ${error.error.message}`;
    } else {
      // Backend returned an unsuccessful response code
      if (error.error && typeof error.error === 'object') {
        // Handle Django REST framework error format
        const errors = error.error;
        if (errors.username) errorMessage = errors.username[0];
        else if (errors.email) errorMessage = errors.email[0];
        else if (errors.password) errorMessage = errors.password[0];
        else if (errors.non_field_errors) errorMessage = errors.non_field_errors[0];
        else if (errors.detail) errorMessage = errors.detail;
      } else {
        errorMessage = `Error Code: ${error.status}\nMessage: ${error.message}`;
      }
    }
    console.error('Auth error:', error);
    return throwError(() => new Error(errorMessage));
  }
}
