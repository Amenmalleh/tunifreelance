import { Component, inject, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatDividerModule } from '@angular/material/divider';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatDialogModule, MatDialog } from '@angular/material/dialog';
import { MatTabsModule } from '@angular/material/tabs';
import { MatBadgeModule } from '@angular/material/badge';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { ProposalService, Proposal } from '../../services/proposal.service';
import { AuthService } from '../../services/auth.service';
import { FilterPipe } from './filter.pipe';
import { ProposalDetailDialogComponent } from './proposal-detail-dialog/proposal-detail-dialog.component';

@Component({
  selector: 'app-manage-proposals',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatChipsModule,
    MatDividerModule,
    MatSnackBarModule,
    MatDialogModule,
    MatTabsModule,
    MatBadgeModule,
    MatProgressSpinnerModule,
    FilterPipe
  ],
  templateUrl: './manage-proposals.html',
  styleUrl: './manage-proposals.css'
})
export class ManageProposals implements OnInit {
  private proposalService = inject(ProposalService);
  private authService = inject(AuthService);
  private snackBar = inject(MatSnackBar);
  private dialog = inject(MatDialog);
  private cdr = inject(ChangeDetectorRef);

  proposals: Proposal[] = [];
  isLoading = true;

  ngOnInit() {
    this.loadProposals();
  }

  loadProposals() {
    this.isLoading = true;
    this.proposalService.getProposals().subscribe({
      next: (proposals) => {
        this.proposals = proposals;
        this.isLoading = false;
        this.cdr.markForCheck();
      },
      error: (err) => {
        console.error('Error loading proposals:', err);
        this.snackBar.open('Error loading proposals.', 'Close', { duration: 4000 });
        this.isLoading = false;
        this.cdr.markForCheck();
      }
    });
  }

  getStatusColor(status: string): string {
    switch (status) {
      case 'pending':
        return 'warn';
      case 'accepted':
        return 'accent';
      case 'rejected':
        return '';
      default:
        return '';
    }
  }

  getStatusLabel(status: string): string {
    switch (status) {
      case 'pending':
        return 'En attente';
      case 'accepted':
        return 'Acceptée';
      case 'rejected':
        return 'Rejetée';
      default:
        return status;
    }
  }

  getPendingCount(): number {
    return this.proposals.filter(p => p.status === 'pending').length;
  }

  getAcceptedCount(): number {
    return this.proposals.filter(p => p.status === 'accepted').length;
  }

  getRejectedCount(): number {
    return this.proposals.filter(p => p.status === 'rejected').length;
  }

  openProposalDetails(proposal: Proposal) {
    const dialogRef = this.dialog.open(ProposalDetailDialogComponent, {
      width: '600px',
      data: proposal
    });

    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        this.loadProposals();
      }
    });
  }

  acceptProposal(proposal: Proposal, event: Event) {
    event.stopPropagation();
    this.proposalService.acceptProposal(proposal.id).subscribe({
      next: () => {
        this.snackBar.open('Proposal accepted! Contract created.', 'Close', { duration: 3000 });
        this.loadProposals();
      },
      error: (err) => {
        this.snackBar.open(err.error?.error || 'Error accepting proposal.', 'Close', { duration: 4000 });
      }
    });
  }

  rejectProposal(proposal: Proposal, event: Event) {
    event.stopPropagation();
    this.proposalService.rejectProposal(proposal.id).subscribe({
      next: () => {
        this.snackBar.open('Proposal rejected.', 'Close', { duration: 3000 });
        this.loadProposals();
      },
      error: (err) => {
        this.snackBar.open(err.error?.error || 'Error rejecting proposal.', 'Close', { duration: 4000 });
      }
    });
  }

  formatPrice(price: number): string {
    return new Intl.NumberFormat('fr-TN', {
      style: 'currency',
      currency: 'TND'
    }).format(price);
  }

  formatDate(date: string): string {
    return new Date(date).toLocaleDateString('fr-TN');
  }
}
