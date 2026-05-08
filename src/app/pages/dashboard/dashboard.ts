import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatDividerModule } from '@angular/material/divider';
import { MatTableModule } from '@angular/material/table';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { AuthService } from '../../services/auth.service';
import { RouterLink } from '@angular/router';
import { ProposalService, Proposal } from '../../services/proposal.service';
import { DashboardService, ClientStats, FreelancerStats } from '../../services/dashboard.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatProgressBarModule,
    MatDividerModule,
    MatTableModule,
    MatSnackBarModule,
    MatProgressSpinnerModule,
    RouterLink,
  ],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css',
})
export class Dashboard implements OnInit {
  public auth = inject(AuthService);
  private proposalService = inject(ProposalService);
  private dashboardService = inject(DashboardService);
  private snackBar = inject(MatSnackBar);

  isLoadingStats = false;

  clientStats: ClientStats = { total_expenses: 0, active_jobs: 0, hire_rate: 0 };
  freelancerStats: FreelancerStats = {
    total_revenue: 0,
    active_proposals: 0,
    active_proposals_list: [],
    profile_score: null,
    ratings_count: 0,
  };

  recentActivity = [
    { label: 'Nouvelle candidature reçue', time: 'il y a 2h', icon: 'person_add' },
    { label: 'Paiement de 450 DT validé', time: 'il y a 5h', icon: 'payments' },
    { label: 'Projet "Banking App" terminé', time: 'il y a 1j', icon: 'check_circle' },
  ];

  clientProposals: Proposal[] = [];
  isClientProposalLoading = false;

  ngOnInit() {
    const role = this.auth.currentRole();
    if (role === 'client') {
      this.loadClientStats();
      this.loadClientProposals();
    } else {
      this.loadFreelancerStats();
    }
  }

  loadClientStats() {
    this.isLoadingStats = true;
    this.dashboardService.getClientStats().subscribe({
      next: (stats) => {
        this.clientStats = stats;
        this.isLoadingStats = false;
      },
      error: () => {
        this.isLoadingStats = false;
        this.snackBar.open('Impossible de charger les statistiques.', 'Fermer', { duration: 4000 });
      },
    });
  }

  loadFreelancerStats() {
    this.isLoadingStats = true;
    this.dashboardService.getFreelancerStats().subscribe({
      next: (stats) => {
        this.freelancerStats = stats;
        this.isLoadingStats = false;
      },
      error: () => {
        this.isLoadingStats = false;
        this.snackBar.open('Impossible de charger les statistiques.', 'Fermer', { duration: 4000 });
      },
    });
  }

  loadClientProposals() {
    this.isClientProposalLoading = true;
    this.proposalService.getProposals().subscribe({
      next: (proposals) => {
        this.clientProposals = proposals.slice(0, 3);
        this.isClientProposalLoading = false;
      },
      error: () => {
        this.isClientProposalLoading = false;
        this.snackBar.open('Impossible de charger les propositions.', 'Fermer', { duration: 4000 });
      },
    });
  }

  getClientPendingProposalsCount(): number {
    return this.clientProposals.filter((p) => p.status === 'pending').length;
  }

  getStarsArray(score: number | null): number[] {
    if (!score) return [];
    return Array.from({ length: Math.round(score) }, (_, i) => i);
  }

  formatCurrency(amount: number): string {
    return new Intl.NumberFormat('fr-TN', {
      style: 'currency',
      currency: 'TND',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  }

  formatPrice(price: number): string {
    return new Intl.NumberFormat('fr-TN', {
      style: 'currency',
      currency: 'TND',
    }).format(price);
  }
}
