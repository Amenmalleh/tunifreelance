import { Component, inject, OnInit, ChangeDetectorRef } from '@angular/core';
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
import { MatSelectModule } from '@angular/material/select';
import { Router } from '@angular/router';
import { JobService, JobOffer, JobSearchFilters } from '../../services/job.service';

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
    MatSnackBarModule,
    MatSelectModule
  ],
  templateUrl: './find-jobs.html',
  styleUrl: './find-jobs.css'
})
export class FindJobs implements OnInit {
  private jobService = inject(JobService);
  private router = inject(Router);
  private snackBar = inject(MatSnackBar);
  private cdr = inject(ChangeDetectorRef);

  jobs: JobOffer[] = [];
  filteredJobs: JobOffer[] = [];
  isLoading = true;
  categories = ['Development', 'Design', 'Marketing', 'Admin Support', 'Data Science'];
  selectedCategory = '';
  searchText = '';
  headerSearchText = '';
  locationText = '';
  sortBy = '-created_at';
  minBudget: number | null = null;
  maxBudget: number | null = null;

  ngOnInit() {
    this.loadJobs();
  }

  loadJobs() {
    this.isLoading = true;
    const filters: JobSearchFilters = {};
    
    const searchQuery = this.searchText || this.headerSearchText;
    if (searchQuery) filters.search = searchQuery;
    if (this.selectedCategory) filters.category = this.selectedCategory;
    if (this.locationText) filters.location = this.locationText;
    if (this.minBudget) filters.min_budget = this.minBudget;
    if (this.maxBudget) filters.max_budget = this.maxBudget;
    if (this.sortBy) filters.sort = this.sortBy;

    this.jobService.getJobOffers(filters).subscribe({
      next: (data) => {
        this.jobs = data;
        this.filteredJobs = data;
        this.isLoading = false;
        this.cdr.markForCheck();
      },
      error: (err) => {
        console.error('Error loading jobs:', err);
        this.snackBar.open('Error loading jobs. Please try again.', 'Close', { duration: 4000 });
        this.isLoading = false;
        this.jobs = [];
        this.filteredJobs = [];
        this.cdr.markForCheck();
      }
    });
  }

  filterByCategory(category: string) {
    this.selectedCategory = this.selectedCategory === category ? '' : category;
    this.loadJobs();
  }

  search() {
    this.loadJobs();
  }

  headerSearch() {
    this.searchText = this.headerSearchText;
    this.loadJobs();
  }

  clearFilters() {
    this.selectedCategory = '';
    this.searchText = '';
    this.headerSearchText = '';
    this.locationText = '';
    this.minBudget = null;
    this.maxBudget = null;
    this.sortBy = '-created_at';
    this.loadJobs();
  }

  applyForJob(jobId: number) {
    this.router.navigate(['/proposal', jobId]);
  }

  saveJob(jobId: number) {
    this.snackBar.open('Job saved to your profile!', 'Close', { duration: 3000 });
  }
}
