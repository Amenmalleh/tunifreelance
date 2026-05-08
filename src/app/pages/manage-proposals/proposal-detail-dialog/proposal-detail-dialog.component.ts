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
        <p class="highlight">{{ data.freelance }}</p>
      </div>

      <mat-divider></mat-divider>

      <div class="detail-section">
        <label>Job Title:</label>
        <p class="highlight">{{ data.job_offer_title }}</p>
      </div>

      <mat-divider></mat-divider>

      <div class="detail-section message-section">
        <label>Proposal Message:</label>
        <div class="message-box">
          <p class="full-message">{{ data.message }}</p>
        </div>
      </div>

      <mat-divider></mat-divider>

      <div class="detail-grid">
        <div class="detail-item">
          <label>Proposed Price:</label>
          <p class="price">{{ data.proposed_price }} DT</p>
        </div>

        <div class="detail-item">
          <label>Proposed Deadline:</label>
          <p class="highlight">{{ formatDate(data.proposed_deadline) }}</p>
        </div>
      </div>

      <mat-divider></mat-divider>

      <div class="detail-section">
        <label>Status:</label>
        <p class="status" [ngClass]="data.status">{{ getStatusLabel(data.status) }}</p>
      </div>

      <div class="detail-section">
        <label>Submitted:</label>
        <p class="time-stamp">{{ formatDateTime(data.created_at) }}</p>
      </div>
    </mat-dialog-content>
    <mat-dialog-actions align="end">
      <button mat-button color="primary" (click)="onClose()">Close</button>
    </mat-dialog-actions>
  `,
  styles: [`
    .detail-section {
      margin-bottom: 20px;
      margin-top: 10px;

      label {
        font-weight: 600;
        color: #555;
        display: block;
        margin-bottom: 8px;
        font-size: 0.95rem;
      }

      p {
        margin: 0;
        color: #222;
        font-size: 1rem;
      }
      
      .highlight {
        font-weight: 500;
        color: #1a237e;
      }

      .message-box {
        background: #f8f9fa;
        border-left: 4px solid #3f51b5;
        padding: 15px;
        border-radius: 4px 8px 8px 4px;
      }

      .full-message {
        white-space: pre-wrap;
        line-height: 1.8;
        color: #333;
        font-size: 1.05rem;
      }

      .price {
        font-size: 1.3rem;
        color: #4caf50;
        font-weight: 700;
      }
      
      .time-stamp {
        color: #666;
        font-style: italic;
      }

      .status {
        padding: 6px 12px;
        border-radius: 6px;
        display: inline-block;
        font-weight: 600;

        &.pending {
          background: #fff3e0;
          color: #e65100;
          border: 1px solid #ffe0b2;
        }

        &.accepted {
          background: #e8f5e9;
          color: #2e7d32;
          border: 1px solid #c8e6c9;
        }

        &.rejected {
          background: #ffebee;
          color: #c62828;
          border: 1px solid #ffcdd2;
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

  formatDateTime(date: string): string {
    return new Date(date).toLocaleString('fr-TN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  onClose(): void {
    this.dialogRef.close();
  }
}
