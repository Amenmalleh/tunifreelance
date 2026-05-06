import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatDividerModule } from '@angular/material/divider';
import { MatTableModule } from '@angular/material/table';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { AuthService } from '../../services/auth.service';
import { RouterLink } from '@angular/router';
import { ProposalService, Proposal, DashboardStats } from '../../services/proposal.service';
import { NotificationService, AppNotification } from '../../services/notification.service';

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
    RouterLink
  ],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css'
})
export class Dashboard implements OnInit {
  public auth = inject(AuthService);
  private proposalService = inject(ProposalService);
  private notifService = inject(NotificationService);
  private snackBar = inject(MatSnackBar);
  
  // Real stats from backend
  freelancerStats = {
    earnings: '0 DT',
    activeProposals: 0,
    completedJobs: 0,
    activeContracts: 0
  };

  clientStats = {
    spendings: '0 DT',
    activeJobs: 0,
    totalApplicants: 0,
    activeContracts: 0
  };

  recentNotifications: AppNotification[] = [];
  clientProposals: Proposal[] = [];
  isClientProposalLoading = false;
  isStatsLoading = true;

  ngOnInit() {
    this.loadDashboardStats();
    this.loadRecentNotifications();
    if (this.auth.currentRole() === 'client') {
      this.loadClientProposals();
    }
  }

  loadDashboardStats() {
    this.isStatsLoading = true;
    this.proposalService.getDashboardStats().subscribe({
      next: (stats: DashboardStats) => {
        if (stats.role === 'freelancer') {
          this.freelancerStats = {
            earnings: this.formatCurrency(stats.earnings || 0),
            activeProposals: stats.active_proposals || 0,
            completedJobs: stats.completed_jobs || 0,
            activeContracts: stats.active_contracts || 0
          };
        } else {
          this.clientStats = {
            spendings: this.formatCurrency(stats.spendings || 0),
            activeJobs: stats.active_jobs || 0,
            totalApplicants: stats.total_applicants || 0,
            activeContracts: stats.active_contracts || 0
          };
        }
        this.isStatsLoading = false;
      },
      error: () => {
        this.isStatsLoading = false;
      }
    });
  }

  loadRecentNotifications() {
    this.notifService.loadNotifications().subscribe({
      next: (notifications) => {
        this.recentNotifications = notifications.slice(0, 5);
      }
    });
  }

  loadClientProposals() {
    this.isClientProposalLoading = true;
    this.proposalService.getProposals().subscribe({
      next: (proposals) => {
        this.clientProposals = proposals.slice(0, 5);
        this.isClientProposalLoading = false;
      },
      error: () => {
        this.isClientProposalLoading = false;
        this.snackBar.open('Unable to load received proposals.', 'Close', { duration: 4000 });
      }
    });
  }

  getClientPendingProposalsCount(): number {
    return this.clientProposals.filter((proposal) => proposal.status === 'pending').length;
  }

  formatPrice(price: number): string {
    return new Intl.NumberFormat('fr-TN', {
      style: 'currency',
      currency: 'TND'
    }).format(price);
  }

  formatCurrency(amount: number): string {
    return new Intl.NumberFormat('fr-TN').format(amount) + ' DT';
  }

  getNotifIcon(type: string): string {
    return this.notifService.getNotificationIcon(type);
  }

  formatTimeAgo(dateStr: string): string {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    if (diffMins < 1) return 'maintenant';
    if (diffMins < 60) return `il y a ${diffMins}m`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `il y a ${diffHours}h`;
    const diffDays = Math.floor(diffHours / 24);
    return `il y a ${diffDays}j`;
  }
}
