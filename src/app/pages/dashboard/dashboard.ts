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
import { JobService, JobOffer } from '../../services/job.service';

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
  private jobService = inject(JobService);
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

  freelancerProposals: Proposal[] = [];
  isFreelancerProposalLoading = false;
  favoriteJobs: JobOffer[] = [];
  favoriteTalents: Array<{ id: number; first_name: string; last_name: string; title: string; location?: string; rating: number; avatar: string; }> = [];

  ngOnInit() {
    this.loadDashboardStats();
    this.loadFavoriteItems();
    this.loadRecentNotifications();
    if (this.auth.currentRole() === 'client') {
      this.loadClientProposals();
    } else {
      this.loadFreelancerProposals();
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
        // Limit to 3 most recent notifications for better performance
        this.recentNotifications = notifications.slice(0, 3);
      }
    });
  }

  loadClientProposals() {
    this.isClientProposalLoading = true;
    this.proposalService.getProposals().subscribe({
      next: (proposals) => {
        // Limit to 3 most recent proposals for better performance
        this.clientProposals = proposals.slice(0, 3);
        this.isClientProposalLoading = false;
      },
      error: () => {
        this.isClientProposalLoading = false;
        this.snackBar.open('Unable to load received proposals.', 'Close', { duration: 4000 });
      }
    });
  }

  loadFreelancerProposals() {
    this.isFreelancerProposalLoading = true;
    this.proposalService.getProposals().subscribe({
      next: (proposals) => {
        // Show accepted proposals first, then pending, limit to 3 for performance
        this.freelancerProposals = proposals
          .sort((a, b) => {
            if (a.status === 'accepted' && b.status !== 'accepted') return -1;
            if (a.status !== 'accepted' && b.status === 'accepted') return 1;
            return 0;
          })
          .slice(0, 3);
        this.isFreelancerProposalLoading = false;
      },
      error: () => {
        this.isFreelancerProposalLoading = false;
        this.snackBar.open('Unable to load your proposals.', 'Close', { duration: 4000 });
      }
    });
  }

  approveProposal(proposal: Proposal) {
    this.proposalService.approveProposal(proposal.id).subscribe({
      next: () => {
        this.snackBar.open('Proposal approved! Contract created successfully.', 'Close', { duration: 4000 });
        this.loadFreelancerProposals();
        this.loadDashboardStats(); // refresh stats
      },
      error: (err) => {
        this.snackBar.open(err.error?.error || 'Error approving proposal.', 'Close', { duration: 4000 });
      }
    });
  }

  getClientPendingProposalsCount(): number {
    return this.clientProposals.filter((proposal) => proposal.status === 'pending').length;
  }

  getFreelancerAcceptedProposalsCount(): number {
    return this.freelancerProposals.filter(
      (proposal) => proposal.status === 'accepted' && !proposal.has_contract
    ).length;
  }

  private loadFavoriteItems() {
    try {
      const savedJobs = localStorage.getItem('saved_jobs');
      if (savedJobs) {
        this.favoriteJobs = JSON.parse(savedJobs);
      } else {
        const legacyIds = JSON.parse(localStorage.getItem('saved_job_ids') || '[]');
        if (Array.isArray(legacyIds)) {
          this.favoriteJobs = legacyIds.map((id: number) => ({
            id,
            client: '',
            client_role: '',
            title: 'Saved job',
            category: '',
            location: '',
            description: '',
            budget: 0,
            deadline: '',
            status: 'open',
            created_at: '',
            updated_at: ''
          }));
        }
      }

      const savedTalents = localStorage.getItem('saved_talent_data');
      if (savedTalents) {
        this.favoriteTalents = JSON.parse(savedTalents);
      } else {
        const legacyTalentIds = JSON.parse(localStorage.getItem('saved_talent_ids') || '[]');
        if (Array.isArray(legacyTalentIds)) {
          this.favoriteTalents = legacyTalentIds.map((id: number) => ({ id, first_name: 'Saved', last_name: 'Talent', title: '', location: '', rating: 0, avatar: '?' }));
        }
      }
    } catch (err) {
      console.error('Unable to load favorite items', err);
      this.favoriteJobs = [];
      this.favoriteTalents = [];
    }
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
