import { Component, inject, OnInit, ChangeDetectorRef } from '@angular/core';
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
import { MatSelectModule } from '@angular/material/select';
import { Router } from '@angular/router';

export interface Freelancer {
  id: number;
  username: string;
  first_name: string;
  last_name: string;
  avatar?: string;
  title?: string;
  category?: string;
  location?: string;
  skills?: string[];
  rating?: number;
  hourly_rate?: number;
  bio?: string;
  profile_completed?: number;
  saved?: boolean;
}

@Component({
  selector: 'app-find-talent',
  standalone: true,
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
    MatSelectModule
  ],
  templateUrl: './find-talent.html',
  styleUrl: './find-talent.css'
})
export class FindTalent implements OnInit {
  private router = inject(Router);
  private snackBar = inject(MatSnackBar);
  private cdr = inject(ChangeDetectorRef);

  freelancers: Freelancer[] = [];
  filteredFreelancers: Freelancer[] = [];
  isLoading = true;
  categories = ['Development', 'Design', 'Marketing', 'Admin Support', 'Data Science'];
  selectedCategory = '';
  searchText = '';
  headerSearchText = '';
  locationText = '';
  sortBy = '-rating';
  minRate: number | null = null;
  maxRate: number | null = null;
  showTopRated = false;
  savedTalents: Set<number> = new Set();
  savedTalentSummaries: Freelancer[] = [];

  ngOnInit() {
    this.loadSavedTalents();
    this.loadTalent();
  }

  loadTalent() {
    this.isLoading = true;

    // Sample data - TODO: Replace with actual backend API call
    this.freelancers = [
      {
        id: 1,
        username: 'mohamedali',
        first_name: 'Mohamed',
        last_name: 'Ali',
        avatar: 'MA',
        title: 'Expert Angular Developer',
        category: 'Development',
        location: 'Tunis, Tunisia',
        skills: ['Angular', 'RxJS', 'NgRx', 'TypeScript', 'Web Performance'],
        rating: 4.9,
        hourly_rate: 65,
        bio: 'Experienced Angular developer with 5+ years in the ecosystem. Expert in building scalable and performant web applications.',
        profile_completed: 95,
        saved: false
      },
      {
        id: 2,
        username: 'amirabenromdhane',
        first_name: 'Amira',
        last_name: 'Ben Romdhane',
        avatar: 'AB',
        title: 'UI/UX Designer',
        category: 'Design',
        location: 'Sousse, Tunisia',
        skills: ['Figma', 'UI Design', 'UX Research', 'Prototyping', 'Design Systems'],
        rating: 5.0,
        hourly_rate: 50,
        bio: 'Creative and detail-oriented designer specialized in creating beautiful and functional user interfaces.',
        profile_completed: 100,
        saved: false
      },
      {
        id: 3,
        username: 'yassinemansour',
        first_name: 'Yassine',
        last_name: 'Mansour',
        avatar: 'YM',
        title: 'Fullstack Developer',
        category: 'Development',
        location: 'Sfax, Tunisia',
        skills: ['React', 'Node.js', 'PostgreSQL', 'Docker', 'AWS'],
        rating: 4.8,
        hourly_rate: 55,
        bio: 'Fullstack developer passionate about building end-to-end solutions with modern technologies.',
        profile_completed: 90,
        saved: false
      }
    ];

    this.freelancers.forEach((freelancer) => {
      freelancer.saved = this.savedTalents.has(freelancer.id);
    });

    this.applyFilters();
    this.isLoading = false;
    this.cdr.markForCheck();
  }

  applyFilters() {
    let filtered = [...this.freelancers];

    const searchQuery = this.searchText || this.headerSearchText;
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(f =>
        f.first_name.toLowerCase().includes(query) ||
        f.last_name.toLowerCase().includes(query) ||
        f.title?.toLowerCase().includes(query) ||
        f.bio?.toLowerCase().includes(query) ||
        f.skills?.some(s => s.toLowerCase().includes(query))
      );
    }

    if (this.selectedCategory) {
      filtered = filtered.filter(f => f.category === this.selectedCategory);
    }

    if (this.locationText) {
      const loc = this.locationText.toLowerCase();
      filtered = filtered.filter(f => f.location?.toLowerCase().includes(loc));
    }

    if (this.minRate) {
      filtered = filtered.filter(f => (f.hourly_rate || 0) >= this.minRate!);
    }
    if (this.maxRate) {
      filtered = filtered.filter(f => (f.hourly_rate || 0) <= this.maxRate!);
    }

    // Filter for top rated if selected
    if (this.showTopRated) {
      filtered = filtered.filter(f => (f.rating || 0) >= 4.5);
    }

    // Sort
    if (this.sortBy === '-rating') {
      filtered.sort((a, b) => (b.rating || 0) - (a.rating || 0));
    } else if (this.sortBy === 'rating') {
      filtered.sort((a, b) => (a.rating || 0) - (b.rating || 0));
    } else if (this.sortBy === '-rate') {
      filtered.sort((a, b) => (b.hourly_rate || 0) - (a.hourly_rate || 0));
    } else if (this.sortBy === 'rate') {
      filtered.sort((a, b) => (a.hourly_rate || 0) - (b.hourly_rate || 0));
    }

    this.filteredFreelancers = filtered;
  }

  filterByCategory(category: string) {
    this.selectedCategory = this.selectedCategory === category ? '' : category;
    this.applyFilters();
  }

  search() {
    this.applyFilters();
  }

  headerSearch() {
    this.searchText = this.headerSearchText;
    this.applyFilters();
  }

  clearFilters() {
    this.selectedCategory = '';
    this.searchText = '';
    this.headerSearchText = '';
    this.locationText = '';
    this.minRate = null;
    this.maxRate = null;
    this.sortBy = '-rating';
    this.applyFilters();
  }

  inviteToJob(freelancerId: number) {
    const freelancer = this.freelancers.find(f => f.id === freelancerId);
    this.snackBar.open(`Invitation sent to ${freelancer?.first_name}!`, 'Close', { duration: 3000 });
  }

  saveTalent(freelancerId: number) {
    const freelancer = this.freelancers.find(f => f.id === freelancerId);
    if (freelancer) {
      freelancer.saved = !freelancer.saved;
      if (freelancer.saved) {
        this.savedTalents.add(freelancerId);
        this.savedTalentSummaries.push({ ...freelancer });
      } else {
        this.savedTalents.delete(freelancerId);
        this.savedTalentSummaries = this.savedTalentSummaries.filter((talent) => talent.id !== freelancerId);
      }
      this.persistSavedTalents();
      this.snackBar.open(
        freelancer.saved ? 'Talent added to favorites!' : 'Talent removed from favorites!',
        'Close',
        { duration: 3000 }
      );
    }
  }

  private loadSavedTalents() {
    try {
      const stored = localStorage.getItem('saved_talent_data');
      if (stored) {
        const talents: Freelancer[] = JSON.parse(stored);
        talents.forEach((talent) => {
          this.savedTalents.add(talent.id);
          this.savedTalentSummaries.push(talent);
        });
      } else {
        const legacy = localStorage.getItem('saved_talent_ids');
        if (legacy) {
          JSON.parse(legacy).forEach((talentId: number) => this.savedTalents.add(talentId));
        }
      }
    } catch (err) {
      console.error('Unable to load saved talents', err);
    }
  }

  private persistSavedTalents() {
    localStorage.setItem('saved_talent_data', JSON.stringify(this.savedTalentSummaries));
    localStorage.setItem('saved_talent_ids', JSON.stringify(Array.from(this.savedTalents)));
  }
}

