import { Component, inject, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  FormBuilder, FormGroup, FormsModule,
  ReactiveFormsModule, Validators, AbstractControl
} from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSnackBarModule, MatSnackBar } from '@angular/material/snack-bar';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { ActivatedRoute, Router } from '@angular/router';
import { AuthService, SignupData, LoginData } from '../../services/auth.service';

@Component({
  selector: 'app-auth',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    MatButtonModule,
    MatIconModule,
    MatCardModule,
    MatInputModule,
    MatFormFieldModule,
    MatSnackBarModule,
    MatProgressSpinnerModule,
  ],
  templateUrl: './auth.html',
  styleUrl: './auth.css',
})
export class Auth implements OnInit {
  private fb      = inject(FormBuilder);
  private route   = inject(ActivatedRoute);
  private router  = inject(Router);
  private auth    = inject(AuthService);
  private snackBar = inject(MatSnackBar);
  private cdr     = inject(ChangeDetectorRef);

  isSelectionStep = true;
  isLogin         = true;
  selectedRole: 'client' | 'freelancer' | null = null;
  isLoading       = false;
  showPassword    = false;
  showPassword2   = false;

  // ── Formulaire connexion ──────────────────────────────────
  loginForm: FormGroup = this.fb.group({
    identifier: ['', [Validators.required, Validators.minLength(3)]],
    password:   ['', [Validators.required]],
  });

  // ── Formulaire inscription ────────────────────────────────
  signupForm: FormGroup = this.fb.group(
    {
      username:  ['', [Validators.required, Validators.minLength(3), Validators.pattern(/^\S+$/)]],
      firstName: ['', [Validators.required]],
      lastName:  ['', [Validators.required]],
      email:     ['', [Validators.required, Validators.email]],
      password:  ['', [Validators.required, Validators.minLength(8)]],
      password2: ['', [Validators.required]],
    },
    { validators: this.passwordMatchValidator }
  );

  // ── Type d'identifiant détecté ────────────────────────────
  get identifierHint(): { icon: string; label: string } | null {
    const val: string = this.loginForm.get('identifier')?.value ?? '';
    if (!val) return null;
    return val.includes('@')
      ? { icon: 'email',  label: 'Connexion par email' }
      : { icon: 'person', label: 'Connexion par nom d\'utilisateur' };
  }

  // ── Accès rapide aux controls ─────────────────────────────
  lf(name: string): AbstractControl { return this.loginForm.get(name)!; }
  sf(name: string): AbstractControl { return this.signupForm.get(name)!; }

  ngOnInit() {
    this.route.url.subscribe(url => {
      const path = url[0]?.path;
      if (path === 'signin') {
        this.isLogin = true;
        this.isSelectionStep = false;
        this.selectedRole = 'freelancer';
      } else if (path === 'signup') {
        this.isLogin = false;
        this.isSelectionStep = true;
        this.selectedRole = null;
      }
    });
  }

  selectRole(role: 'client' | 'freelancer') {
    this.selectedRole = role;
    this.auth.setRole(role);
    this.isSelectionStep = false;
  }

  toggleAuthMode() {
    this.isLogin = !this.isLogin;
    this.loginForm.reset();
    this.signupForm.reset();
    this.router.navigate([this.isLogin ? '/signin' : '/signup']);
  }

  goBack() {
    this.isSelectionStep = true;
    this.selectedRole = null;
    this.loginForm.reset();
    this.signupForm.reset();
  }

  onSubmit() {
    if (this.isLogin) {
      if (this.loginForm.invalid) { this.loginForm.markAllAsTouched(); return; }
      this.isLoading = true;
      this.performLogin();
    } else {
      if (this.signupForm.invalid) { this.signupForm.markAllAsTouched(); return; }
      this.isLoading = true;
      this.performSignup();
    }
  }

  private performLogin() {
    const { identifier, password } = this.loginForm.value;
    const loginData: LoginData = { identifier: identifier.trim(), password };

    this.auth.login(loginData).subscribe({
      next: () => {
        this.isLoading = false;
        this.cdr.markForCheck();
        this.snackBar.open('Connexion réussie !', 'Fermer', { duration: 3000 });
        this.router.navigate(['/dashboard']);
      },
      error: (err: Error) => {
        this.isLoading = false;
        this.cdr.markForCheck();
        this.snackBar.open(err.message, 'Fermer', { duration: 5000 });
      },
    });
  }

  private performSignup() {
    const v = this.signupForm.value;
    const signupData: SignupData = {
      username:   v.username,
      email:      v.email,
      password:   v.password,
      password2:  v.password2,
      first_name: v.firstName,
      last_name:  v.lastName,
      role:       this.selectedRole ?? 'freelancer',
    };

    this.auth.signup(signupData).subscribe({
      next: () => {
        this.isLoading = false;
        this.cdr.markForCheck();
        this.snackBar.open('Compte créé avec succès !', 'Fermer', { duration: 3000 });
        this.router.navigate(['/dashboard']);
      },
      error: (err: Error) => {
        this.isLoading = false;
        this.cdr.markForCheck();
        this.snackBar.open(err.message, 'Fermer', { duration: 5000 });
      },
    });
  }

  private passwordMatchValidator(group: AbstractControl) {
    const p1 = group.get('password')?.value;
    const p2 = group.get('password2')?.value;
    if (p1 && p2 && p1 !== p2) {
      group.get('password2')?.setErrors({ mismatch: true });
      return { mismatch: true };
    }
    return null;
  }
}
