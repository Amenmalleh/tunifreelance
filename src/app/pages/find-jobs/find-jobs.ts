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
  activeTab = 'most_recent';
  minBudget: number | null = null;
  maxBudget: number | null = null;
  savedJobs: Set<number> = new Set();
  savedJobSummaries: JobOffer[] = [];

  ngOnInit() {
    this.loadSavedJobs();
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
        this.filteredJobs = this.sortJobs(data);
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
    // After search, we clear the search input to reset the form, while keeping the filtered jobs displayed
    // Actually, "clear filters after search" might mean a button to clear filters.
  }

  headerSearch() {
    this.searchText = this.headerSearchText;
    this.loadJobs();
    this.headerSearchText = '';
  }

  setTab(tab: string) {
    this.activeTab = tab;
    if (tab === 'best_matches') {
      this.sortBy = ''; // Or some AI matching logic if available
    } else if (tab === 'most_recent') {
      this.sortBy = '-created_at';
    }
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

  private loadSavedJobs() {
    try {
      const stored = localStorage.getItem('saved_jobs');
      if (stored) {
        const jobs: JobOffer[] = JSON.parse(stored);
        jobs.forEach((job) => {
          this.savedJobs.add(job.id);
          this.savedJobSummaries.push(job);
        });
      } else {
        const legacy = localStorage.getItem('saved_job_ids');
        if (legacy) {
          JSON.parse(legacy).forEach((jobId: number) => this.savedJobs.add(jobId));
        }
      }
    } catch (err) {
      console.error('Unable to load saved jobs', err);
    }
  }

  private persistSavedJobs() {
    localStorage.setItem('saved_jobs', JSON.stringify(this.savedJobSummaries));
    localStorage.setItem('saved_job_ids', JSON.stringify(Array.from(this.savedJobs)));
  }

  private sortJobs(jobs: JobOffer[]): JobOffer[] {
    const sorted = [...jobs];
    switch (this.sortBy) {
      case '-created_at':
        return sorted.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
      case 'created_at':
        return sorted.sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime());
      case '-budget':
        return sorted.sort((a, b) => b.budget - a.budget);
      case 'budget':
        return sorted.sort((a, b) => a.budget - b.budget);
      case 'deadline':
        return sorted.sort((a, b) => new Date(a.deadline).getTime() - new Date(b.deadline).getTime());
      default:
        return sorted;
    }
  }

  applyForJob(jobId: number) {
    this.router.navigate(['/proposal', jobId]);
  }

  isSaved(jobId: number): boolean {
    return this.savedJobs.has(jobId);
  }

  saveJob(jobId: number) {
    const job = this.jobs.find((item) => item.id === jobId);
    if (!job) {
      this.snackBar.open('Unable to save job at the moment.', 'Close', { duration: 3000 });
      return;
    }

    if (this.savedJobs.has(jobId)) {
      this.savedJobs.delete(jobId);
      this.savedJobSummaries = this.savedJobSummaries.filter((saved) => saved.id !== jobId);
      this.persistSavedJobs();
      this.snackBar.open('Job removed from favorites.', 'Close', { duration: 3000 });
    } else {
      this.savedJobs.add(jobId);
      this.savedJobSummaries.push(job);
      this.persistSavedJobs();
      this.snackBar.open('Job added to favorites.', 'Close', { duration: 3000 });
    }
  }
}

