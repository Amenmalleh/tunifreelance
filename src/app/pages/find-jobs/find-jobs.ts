import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatChipsModule } from '@angular/material/chips';
import { MatCardModule } from '@angular/material/card';
import { MatDividerModule } from '@angular/material/divider';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { Router } from '@angular/router';
import { JobService, JobOffer } from '../../services/job.service';

@Component({
  selector: 'app-find-jobs',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatFormFieldModule, 
    MatInputModule, 
    MatIconModule, 
    MatButtonModule, 
    MatChipsModule,
    MatCardModule,
    MatDividerModule,
    MatTooltipModule,
    MatProgressSpinnerModule,
    MatSnackBarModule
  ],
  templateUrl: './find-jobs.html',
  styleUrl: './find-jobs.css'
})
export class FindJobs implements OnInit {
  private jobService = inject(JobService);
  private router = inject(Router);
  private snackBar = inject(MatSnackBar);

  jobs: JobOffer[] = [];
  filteredJobs: JobOffer[] = [];
  isLoading = true;
  categories = ['Web & Mobile Development', 'Design & Creative', 'Digital Marketing', 'Admin Support', 'Data Science'];
  selectedCategory = '';
  searchText = '';

  ngOnInit() {
    this.loadJobs();
  }

  loadJobs() {
    this.isLoading = true;
    this.jobService.getJobOffers().subscribe({
      next: (data) => {
        this.jobs = data;
        this.filteredJobs = data;
        this.isLoading = false;
      },
      error: (err) => {
        console.error('Error loading jobs:', err);
        this.snackBar.open('Error loading jobs. Please try again.', 'Close', { duration: 4000 });
        this.isLoading = false;
        // Fallback to empty array
        this.jobs = [];
        this.filteredJobs = [];
      }
    });
  }

  filterByCategory(category: string) {
    this.selectedCategory = this.selectedCategory === category ? '' : category;
    this.applyFilters();
  }

  search() {
    this.applyFilters();
  }

  applyFilters() {
    this.filteredJobs = this.jobs.filter(job => {
      const matchesCategory = !this.selectedCategory || job.category === this.selectedCategory;
      const matchesSearch = !this.searchText || 
        job.title.toLowerCase().includes(this.searchText.toLowerCase()) ||
        job.description.toLowerCase().includes(this.searchText.toLowerCase());
      return matchesCategory && matchesSearch;
    });
  }

  applyForJob(jobId: number) {
    this.router.navigate(['/proposal', jobId]);
  }

  saveJob(jobId: number) {
    this.snackBar.open('Job saved to your profile!', 'Close', { duration: 3000 });
  }
}
