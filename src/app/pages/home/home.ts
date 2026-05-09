import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, MatButtonModule, MatIconModule, MatCardModule, MatChipsModule],
  templateUrl: './home.html',
  styleUrl: './home.css',
})
export class Home {
  categories = [
    { name: 'Development', icon: 'code', jobs: '1.2k+' },
    { name: 'AI & Data', icon: 'psychology', jobs: '450+' },
    { name: 'Design', icon: 'palette', jobs: '800+' },
    { name: 'Writing', icon: 'edit', jobs: '600+' },
    { name: 'Marketing', icon: 'trending_up', jobs: '300+' },
    { name: 'Business', icon: 'business', jobs: '200+' },
  ];
  //pour un commit 
}
