import { Injectable, signal, computed } from '@angular/core';

export type UserRole = 'client' | 'freelancer';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private roleSignal = signal<UserRole>('freelancer');
  private isLoggedInSignal = signal<boolean>(false);

  // Read-only access to state
  currentRole = computed(() => this.roleSignal());
  isLoggedIn = computed(() => this.isLoggedInSignal());

  constructor() {
    // Mock: Check localStorage for persistence (frontend only)
    const savedRole = localStorage.getItem('user_role') as UserRole;
    if (savedRole) this.roleSignal.set(savedRole);
    
    const savedAuth = localStorage.getItem('is_logged_in');
    if (savedAuth === 'true') this.isLoggedInSignal.set(true);
  }

  setRole(role: UserRole) {
    this.roleSignal.set(role);
    localStorage.setItem('user_role', role);
  }

  login() {
    this.isLoggedInSignal.set(true);
    localStorage.setItem('is_logged_in', 'true');
  }

  logout() {
    this.isLoggedInSignal.set(false);
    localStorage.removeItem('is_logged_in');
  }

  toggleRole() {
    const nextRole = this.currentRole() === 'freelancer' ? 'client' : 'freelancer';
    this.setRole(nextRole);
  }
}
