import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { ActivatedRoute, Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';

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
    MatFormFieldModule
  ],
  templateUrl: './auth.html',
  styleUrl: './auth.css',
})
export class Auth implements OnInit {
  private fb = inject(FormBuilder);
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private auth = inject(AuthService);

  isSelectionStep = true;
  isLogin = true;
  selectedRole: 'client' | 'freelancer' | null = null;
  
  authForm: FormGroup = this.fb.group({
    firstName: ['', [Validators.required]],
    lastName: ['', [Validators.required]],
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required, Validators.minLength(8)]]
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
    } else {
      this.authForm.get('firstName')?.setValidators([Validators.required]);
      this.authForm.get('lastName')?.setValidators([Validators.required]);
    }
    this.authForm.get('firstName')?.updateValueAndValidity();
    this.authForm.get('lastName')?.updateValueAndValidity();
  }

  goBack() {
    this.isSelectionStep = true;
    this.selectedRole = null;
    this.authForm.reset();
  }

  onSubmit() {
    if (this.authForm.valid) {
      // Logic for frontend only: set role and login
      this.auth.setRole(this.selectedRole || 'freelancer');
      this.auth.login();
      this.router.navigate(['/jobs']);
    }
  }
}
