import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatChipsModule } from '@angular/material/chips';
import { MatCardModule } from '@angular/material/card';
import { MatDividerModule } from '@angular/material/divider';

@Component({
  selector: 'app-find-talent',
  standalone: true,
  imports: [
    CommonModule, 
    MatFormFieldModule, 
    MatInputModule, 
    MatIconModule, 
    MatButtonModule, 
    MatChipsModule,
    MatCardModule,
    MatDividerModule
  ],
  templateUrl: './find-talent.html',
  styleUrl: './find-talent.css'
})
export class FindTalent {
  freelancers = [
    {
      name: 'Mohamed Ali',
      title: 'Expert Angular (Diplômé ESPRIT)',
      rating: 4.9,
      earnings: '45,000 DT+',
      rate: '65 DT / hr',
      description: 'Développeur passionné avec 5 ans d\'expérience dans l\'écosystème Angular en Tunisie. J\'ai travaillé sur de grands projets pour des banques tunisiennes.',
      skills: ['Angular', 'RxJS', 'NgRx', 'Web Performance'],
      avatar: 'MA'
    },
    {
      name: 'Amira Ben Romdhane',
      title: 'UI/UX Designer (Diplômée ESSTED)',
      rating: 5.0,
      earnings: '20,000 DT+',
      rate: '50 DT / hr',
      description: 'Créative et rigoureuse, j\'accompagne les startups tunisiennes dans la définition de leur identité digitale et de leurs interfaces mobiles.',
      skills: ['Figma', 'UI/UX Design', 'Design Thinking', 'Prototypage'],
      avatar: 'AR'
    },
    {
      name: 'Yassine Mansour',
      title: 'Fullstack Engineer (Express / React)',
      rating: 4.8,
      earnings: '35,000 DT+',
      rate: '55 DT / hr',
      description: 'Développeur fullstack polyvalent, diplômé de l\'INSAT. J\'aide les entreprises locales à bâtir des solutions robustes et scalables.',
      skills: ['React', 'Node.js', 'PostgreSQL', 'Docker'],
      avatar: 'YM'
    }
  ];
}
