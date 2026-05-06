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
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { Router } from '@angular/router';
import { JobService, CreateJobOfferPayload } from '../../services/job.service';

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
    MatStepperModule,
    MatDatepickerModule,
    MatNativeDateModule,
    MatSnackBarModule
  ],
  templateUrl: './post-job.html',
  styleUrl: './post-job.css'
})
export class PostJob {
  private fb = inject(FormBuilder);
  router = inject(Router);
  private jobService = inject(JobService);
  private snackBar = inject(MatSnackBar);

  isSubmitting = false;
  categories = [
    { value: 'web', label: 'Web & Mobile Development' },
    { value: 'design', label: 'Design & Creative' },
    { value: 'marketing', label: 'Digital Marketing' },
    { value: 'admin', label: 'Admin Support' },
    { value: 'data', label: 'Data Science' }
  ];

  titleForm = this.fb.group({
    title: ['', [Validators.required, Validators.minLength(10)]],
    category: ['web', [Validators.required]]
  });

  detailsForm = this.fb.group({
    description: ['', [Validators.required, Validators.minLength(50)]],
    skills: ['']
  });

  budgetForm = this.fb.group({
    jobType: ['fixed', [Validators.required]],
    minBudget: ['', [Validators.required, Validators.min(1)]],
    maxBudget: [''],
    deadline: ['', [Validators.required]]
  });

  submitJob() {
    if (this.titleForm.invalid || this.detailsForm.invalid || this.budgetForm.invalid) {
      this.snackBar.open('Please fill in all required fields correctly.', 'Close', { duration: 3000 });
      return;
    }

    this.isSubmitting = true;

    const titleData = this.titleForm.value;
    const detailsData = this.detailsForm.value;
    const budgetData = this.budgetForm.value;

    // Format the deadline to YYYY-MM-DD
    const deadlineDate = new Date(budgetData.deadline!);
    const deadline = deadlineDate.toISOString().split('T')[0];

    // Determine budget based on job type
    const budget = budgetData.jobType === 'fixed'
      ? parseFloat(budgetData.minBudget as string)
      : parseFloat(budgetData.minBudget as string);

    const payload: CreateJobOfferPayload = {
      title: titleData.title!,
      category: titleData.category!,
      description: detailsData.description!,
      budget: budget,
      deadline: deadline
    };

    this.jobService.createJobOffer(payload).subscribe({
      next: (response) => {
        this.isSubmitting = false;
        this.snackBar.open('Job posted successfully! 🎉', 'Close', { duration: 4000 });
        setTimeout(() => {
          this.router.navigate(['/jobs']);
        }, 1000);
      },
      error: (err) => {
        this.isSubmitting = false;
        console.error('Error posting job:', err);
        this.snackBar.open('Error posting job. Please try again.', 'Close', { duration: 4000 });
      }
    });
  }
}
