import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatCardModule } from '@angular/material/card';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { ActivatedRoute, Router } from '@angular/router';
import { JobService, JobOffer } from '../../services/job.service';
import { ProposalService, CreateProposalPayload } from '../../services/proposal.service';

@Component({
  selector: 'app-proposal-form',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    MatButtonModule,
    MatIconModule,
    MatInputModule,
    MatFormFieldModule,
    MatCardModule,
    MatSnackBarModule
  ],
  templateUrl: './proposal-form.html',
  styleUrl: './proposal-form.css'
})
export class ProposalForm implements OnInit {
  private fb = inject(FormBuilder);
  private route = inject(ActivatedRoute);
  router = inject(Router);
  private jobService = inject(JobService);
  private proposalService = inject(ProposalService);
  private snackBar = inject(MatSnackBar);

  job: JobOffer | null = null;
  isLoading = false;

  proposalForm: FormGroup = this.fb.group({
    message: ['', [Validators.required, Validators.minLength(20)]],
    proposedPrice: ['', [Validators.required, Validators.min(1)]]
  });

  ngOnInit() {
    this.route.paramMap.subscribe(params => {
      const jobId = Number(params.get('id'));
      if (jobId) {
        this.loadJob(jobId);
      }
    });
  }

  loadJob(jobId: number) {
    this.jobService.getJobOffer(jobId).subscribe({
      next: job => this.job = job,
      error: () => {
        this.snackBar.open('Unable to load job details.', 'Close', { duration: 4000 });
        this.router.navigate(['/jobs']);
      }
    });
  }

  submitProposal() {
    if (this.proposalForm.invalid || !this.job) {
      return;
    }

    this.isLoading = true;
    const values = this.proposalForm.value;
    const payload: CreateProposalPayload = {
      job_offer: this.job.id,
      message: values.message,
      proposed_price: Number(values.proposedPrice)
    };

    this.proposalService.createProposal(payload).subscribe({
      next: () => {
        this.isLoading = false;
        this.snackBar.open('Proposal submitted successfully!', 'Close', { duration: 3000 });
        this.router.navigate(['/jobs']);
      },
      error: (err) => {
        this.isLoading = false;
        this.snackBar.open(err.message || 'Unable to submit proposal.', 'Close', { duration: 5000 });
      }
    });
  }
}
