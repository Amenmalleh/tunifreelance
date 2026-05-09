import { Component, inject, OnInit, OnDestroy, ChangeDetectorRef, ChangeDetectionStrategy } from '@angular/core';
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
import { Subject, Subscription } from 'rxjs';
import { debounceTime, distinctUntilChanged, switchMap } from 'rxjs/operators';
import { JobService, JobOffer } from '../../services/job.service';

@Component({
  selector: 'app-find-jobs',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
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
  ],
  templateUrl: './find-jobs.html',
  styleUrl: './find-jobs.css',
})
export class FindJobs implements OnInit, OnDestroy {
  private jobService  = inject(JobService);
  private router      = inject(Router);
  private snackBar    = inject(MatSnackBar);
  private cdr         = inject(ChangeDetectorRef);

  jobs: JobOffer[]     = [];
  isLoading            = false;
  isSearching          = false;
  resultCount          = 0;

  searchText           = '';
  selectedCategory     = '';

  // Catégories réelles présentes en base (issues du seed)
  categories = [
    'Développement Web',
    'Design Graphique',
    'Marketing Digital',
    'Mobile',
    'SEO',
    'Data Science',
    'Rédaction',
    'Montage Vidéo',
  ];

  private searchSubject = new Subject<{ q: string; cat: string }>();
  private sub!: Subscription;

  ngOnInit() {
    // Pipeline réactif : debounce → distinctUntilChanged → switchMap (annule l'ancienne requête)
    this.sub = this.searchSubject.pipe(
      debounceTime(350),
      distinctUntilChanged((a, b) => a.q === b.q && a.cat === b.cat),
      switchMap(({ q, cat }) => {
        this.isSearching = true;
        this.cdr.markForCheck();
        return this.jobService.getJobOffers(q, cat);
      }),
    ).subscribe({
      next: (data) => {
        this.jobs        = data;
        this.resultCount = data.length;
        this.isSearching = false;
        this.isLoading   = false;
        this.cdr.markForCheck();
      },
      error: () => {
        this.isSearching = false;
        this.isLoading   = false;
        this.snackBar.open('Erreur lors de la recherche.', 'Fermer', { duration: 4000 });
        this.cdr.markForCheck();
      },
    });

    // Chargement initial de tous les jobs
    this.isLoading = true;
    this.dispatch();
  }

  ngOnDestroy() {
    this.sub?.unsubscribe();
  }

  // Appelé à chaque frappe (ngModel)
  onSearchInput() {
    this.dispatch();
  }
  //pour un commit
  // Clic sur une puce de catégorie
  filterByCategory(cat: string) {
    this.selectedCategory = this.selectedCategory === cat ? '' : cat;
    this.dispatch();
  }

  // Vider la recherche
  clearSearch() {
    this.searchText      = '';
    this.selectedCategory = '';
    this.dispatch();
  }

  applyForJob(jobId: number) {
    this.router.navigate(['/proposal', jobId]);
  }

  saveJob(_jobId: number) {
    this.snackBar.open('Offre sauvegardée !', 'Fermer', { duration: 3000 });
  }

  formatBudget(budget: number): string {
    return new Intl.NumberFormat('fr-TN', {
      style: 'currency',
      currency: 'TND',
      minimumFractionDigits: 0,
    }).format(budget);
  }

  // Émet dans le Subject → déclenche le pipeline debounce
  private dispatch() {
    this.searchSubject.next({ q: this.searchText, cat: this.selectedCategory });
  }
}
