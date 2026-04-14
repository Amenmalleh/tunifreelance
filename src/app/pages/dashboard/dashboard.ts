import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatDividerModule } from '@angular/material/divider';
import { MatTableModule } from '@angular/material/table';
import { AuthService } from '../../services/auth.service';
import { RouterLink } from '@angular/router';

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
    RouterLink
  ],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css'
})
export class Dashboard implements OnInit {
  public auth = inject(AuthService);
  
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

  ngOnInit() {}
}
