import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSnackBarModule, MatSnackBar } from '@angular/material/snack-bar';
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
    MatSnackBarModule
  ],
  templateUrl: './auth.html',
  styleUrl: './auth.css',
})
export class Auth implements OnInit {
  private fb = inject(FormBuilder);
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private auth = inject(AuthService);
  private snackBar = inject(MatSnackBar);

  isSelectionStep = true;
  isLogin = true;
  selectedRole: 'client' | 'freelancer' | null = null;
  isLoading = false;

  authForm: FormGroup = this.fb.group({
    username: ['', [Validators.required]],
    firstName: ['', [Validators.required]],
    lastName: ['', [Validators.required]],
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required, Validators.minLength(8)]],
    password2: ['', [Validators.required]]
  });

  ngOnInit() {
    this.route.url.subscribe(url => {
      const path = url[0]?.path;
      if (path === 'signin') {
        this.isLogin = true;
        this.isSelectionStep = false;
        this.selectedRole = 'freelancer'; // Default role for login
      } else if (path === 'signup') {
        this.isLogin = false;
        this.isSelectionStep = true;
        this.selectedRole = null;
      }
      this.updateValidators();
    });
  }

  selectRole(role: 'client' | 'freelancer') {
    this.selectedRole = role;
    this.auth.setRole(role);
    this.isSelectionStep = false;
  }

  toggleAuthMode() {
    this.isLogin = !this.isLogin;
    this.router.navigate([this.isLogin ? '/signin' : '/signup']);
    this.updateValidators();
  }

  private updateValidators() {
    if (this.isLogin) {
      this.authForm.get('firstName')?.clearValidators();
      this.authForm.get('lastName')?.clearValidators();
      this.authForm.get('password2')?.clearValidators();
      this.authForm.get('username')?.setValidators([Validators.required]);
    } else {
      this.authForm.get('firstName')?.setValidators([Validators.required]);
      this.authForm.get('lastName')?.setValidators([Validators.required]);
      this.authForm.get('password2')?.setValidators([Validators.required]);
      this.authForm.get('username')?.setValidators([Validators.required]);
    }
    this.authForm.get('firstName')?.updateValueAndValidity();
    this.authForm.get('lastName')?.updateValueAndValidity();
    this.authForm.get('password2')?.updateValueAndValidity();
    this.authForm.get('username')?.updateValueAndValidity();
  }

  goBack() {
    this.isSelectionStep = true;
    this.selectedRole = null;
    this.authForm.reset();
  }

  onSubmit() {
    if (this.authForm.valid) {
      this.isLoading = true;

      if (this.isLogin) {
        this.performLogin();
      } else {
        this.performSignup();
      }
    }
  }

  private performSignup() {
    const formValue = this.authForm.value;
    const signupData: SignupData = {
      username: formValue.username,
      email: formValue.email,
      password: formValue.password,
      password2: formValue.password2,
      first_name: formValue.firstName,
      last_name: formValue.lastName
    };

    this.auth.signup(signupData).subscribe({
      next: (response) => {
        this.isLoading = false;
        this.snackBar.open('Account created successfully!', 'Close', { duration: 3000 });
        this.router.navigate(['/jobs']);
      },
      error: (error) => {
        this.isLoading = false;
        this.snackBar.open(error.message, 'Close', { duration: 5000 });
      }
    });
  }

  private performLogin() {
    const formValue = this.authForm.value;
    const loginData: LoginData = {
      username: formValue.username,
      password: formValue.password
    };

    this.auth.login(loginData).subscribe({
      next: (response) => {
        this.isLoading = false;
        this.snackBar.open('Logged in successfully!', 'Close', { duration: 3000 });
        this.router.navigate(['/jobs']);
      },
      error: (error) => {
        this.isLoading = false;
        this.snackBar.open(error.message, 'Close', { duration: 5000 });
      }
    });
  }
}
