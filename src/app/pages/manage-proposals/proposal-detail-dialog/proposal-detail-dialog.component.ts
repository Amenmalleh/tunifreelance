import { Component, Inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatDialogModule, MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatDividerModule } from '@angular/material/divider';
import { Proposal } from '../../../services/proposal.service';

@Component({
  selector: 'app-proposal-detail-dialog',
  standalone: true,
  imports: [CommonModule, MatDialogModule, MatButtonModule, MatIconModule, MatDividerModule],
  template: `
    <h2 mat-dialog-title>Proposal Details</h2>
    <mat-dialog-content>
      <div class="detail-section">
        <label>Freelancer:</label>
        <p>{{ data.freelance }}</p>
      </div>

      <mat-divider></mat-divider>

      <div class="detail-section">
        <label>Job Title:</label>
        <p>{{ data.job_offer_title }}</p>
      </div>

      <mat-divider></mat-divider>

      <div class="detail-section">
        <label>Proposal Message:</label>
        <p class="full-message">{{ data.message }}</p>
      </div>

      <mat-divider></mat-divider>

      <div class="detail-grid">
        <div class="detail-item">
          <label>Proposed Price:</label>
          <p class="price">{{ data.proposed_price }} DT</p>
        </div>

        <div class="detail-item">
          <label>Proposed Deadline:</label>
          <p>{{ formatDate(data.proposed_deadline) }}</p>
        </div>
      </div>

      <mat-divider></mat-divider>

      <div class="detail-section">
        <label>Status:</label>
        <p class="status" [ngClass]="data.status">{{ getStatusLabel(data.status) }}</p>
      </div>

      <div class="detail-section">
        <label>Submitted:</label>
        <p>{{ formatDate(data.created_at) }}</p>
      </div>
    </mat-dialog-content>
    <mat-dialog-actions align="end">
      <button mat-button (click)="onClose()">Close</button>
    </mat-dialog-actions>
  `,
  styles: [`
    .detail-section {
      margin-bottom: 15px;

      label {
        font-weight: 600;
        color: #666;
        display: block;
        margin-bottom: 5px;
      }

      p {
        margin: 0;
        color: #333;
      }

      .full-message {
        white-space: pre-wrap;
        line-height: 1.5;
      }

      .price {
        font-size: 1.2rem;
        color: #4caf50;
        font-weight: 600;
      }

      .status {
        padding: 5px 10px;
        border-radius: 4px;
        display: inline-block;

        &.pending {
          background: #fff3e0;
          color: #e65100;
        }

        &.accepted {
          background: #e8f5e9;
          color: #2e7d32;
        }

        &.rejected {
          background: #ffebee;
          color: #c62828;
        }
      }
    }

    .detail-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 15px;
    }

    .detail-item {
      label {
        font-weight: 600;
        color: #666;
        display: block;
        margin-bottom: 5px;
      }

      p {
        margin: 0;
        color: #333;
      }
    }

    mat-dialog-actions {
      padding-top: 20px;
    }
  `]
})
export class ProposalDetailDialogComponent {
  constructor(
    public dialogRef: MatDialogRef<ProposalDetailDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: Proposal
  ) {}

  getStatusLabel(status: string): string {
    switch (status) {
      case 'pending':
        return 'Pending';
      case 'accepted':
        return 'Accepted';
      case 'rejected':
        return 'Rejected';
      default:
        return status;
    }
  }

  formatDate(date: string): string {
    return new Date(date).toLocaleDateString('fr-TN');
  }

  onClose(): void {
    this.dialogRef.close();
  }
}
