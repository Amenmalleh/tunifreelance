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
import { ProposalService, Proposal } from '../../services/proposal.service';

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
  private snackBar = inject(MatSnackBar);
  
  // Mock data for Freelancer
  freelancerStats = {
    earnings: '8,450 DT',
    activeProposals: 12,
    completedJobs: 24,
    profileScore: 92
  };

  // Mock data for Client
  clientStats = {
    spendings: '15,200 DT',
    activeJobs: 3,
    totalApplicants: 45,
    hireRate: 78
  };

  recentActivity = [
    { label: 'New application received', time: 'il y a 2h', icon: 'person_add' },
    { label: 'Payment of 450 DT cleared', time: 'il y a 5h', icon: 'payments' },
    { label: 'Project "Banking App" completed', time: 'il y a 1j', icon: 'check_circle' }
  ];

  clientProposals: Proposal[] = [];
  isClientProposalLoading = false;

  ngOnInit() {
    if (this.auth.currentRole() === 'client') {
      this.loadClientProposals();
    }
  }

  loadClientProposals() {
    this.isClientProposalLoading = true;
    this.proposalService.getProposals().subscribe({
      next: (proposals) => {
        this.clientProposals = proposals.slice(0, 3);
        this.clientStats.totalApplicants = proposals.length;
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
}
