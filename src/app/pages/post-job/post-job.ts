import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatSelectModule } from '@angular/material/select';
import { MatChipsModule } from '@angular/material/chips';
import { MatStepperModule } from '@angular/material/stepper';
import { Router } from '@angular/router';

@Component({
  selector: 'app-post-job',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
    MatSelectModule,
    MatChipsModule,
    MatStepperModule
  ],
  templateUrl: './post-job.html',
  styleUrl: './post-job.css'
})
export class PostJob {
  private fb = inject(FormBuilder);
  private router = inject(Router);

  titleForm = this.fb.group({
    title: ['', [Validators.required, Validators.minLength(10)]],
    category: ['', [Validators.required]]
  });

  detailsForm = this.fb.group({
    description: ['', [Validators.required, Validators.minLength(50)]],
    skills: [[], [Validators.required]]
  });

  budgetForm = this.fb.group({
    jobType: ['hourly', [Validators.required]],
    minBudget: ['', [Validators.required]],
    maxBudget: [''],
    fixedPrice: ['']
  });

  submitJob() {
    if (this.titleForm.valid && this.detailsForm.valid && this.budgetForm.valid) {
      console.log('Job Posted!', {
        ...this.titleForm.value,
        ...this.detailsForm.value,
        ...this.budgetForm.value
      });
      // Simulate success and redirect
      this.router.navigate(['/talent']);
    }
  }
}
