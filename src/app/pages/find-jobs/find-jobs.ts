import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatChipsModule } from '@angular/material/chips';
import { MatCardModule } from '@angular/material/card';
import { MatDividerModule } from '@angular/material/divider';
import { MatTooltipModule } from '@angular/material/tooltip';

@Component({
  selector: 'app-find-jobs',
  standalone: true,
  imports: [
    CommonModule, 
    MatFormFieldModule, 
    MatInputModule, 
    MatIconModule, 
    MatButtonModule, 
    MatChipsModule,
    MatCardModule,
    MatDividerModule,
    MatTooltipModule
  ],
  templateUrl: './find-jobs.html',
  styleUrl: './find-jobs.css'
})
export class FindJobs {
  jobs = [
    {
      title: 'Senior Frontend Developer (Angular)',
      company: 'Vermeg Tunisie',
      location: 'Les Berges du Lac, Tunis',
      budget: '3,500 - 5,000 DT / mois',
      duration: 'Permanent',
      description: 'Nous recherchons un développeur Angular expérimenté pour rejoindre notre équipe à Tunis. Expertise en RxJS et NgRx requise pour nos plateformes financières.',
      skills: ['Angular', 'TypeScript', 'RxJS', 'Agile'],
      posted: 'il y a 2 heures'
    },
    {
      title: 'UI/UX Designer Mobile App',
      company: 'Ooredoo Tunisie',
      location: 'Tunis',
      budget: '2,500 DT Fixe',
      duration: '3 mois+',
      description: 'Design de la nouvelle application mobile My Ooredoo. Création de parcours utilisateurs innovants et prototypage haute fidélité.',
      skills: ['Figma', 'UI/UX Design', 'Telecom', 'Prototypage'],
      posted: 'il y a 5 heures'
    },
    {
      title: 'Expert Node.js / NestJS',
      company: 'Telnet Holding',
      location: 'Sfax / Remote',
      budget: '4,000 DT / mois',
      duration: 'Ongoing',
      description: 'Développement de microservices critiques pour le secteur de l\'aéronautique et des systèmes embarqués.',
      skills: ['Node.js', 'NestJS', 'PostgreSQL', 'Microservices'],
      posted: 'il y a 1 jour'
    },
    {
      title: 'Fullstack Developer (Laravel / Vue.js)',
      company: 'Talan Tunisie',
      location: 'Tunis',
      budget: '3,000 DT / mois',
      duration: 'Mission 6 mois',
      description: 'Accompagnement de nos clients bancaires dans la digitalisation de leurs processus internes.',
      skills: ['Laravel', 'Vue.js', 'MySQL', 'Docker'],
      posted: 'il y a 3 jours'
    }
  ];

  categories = ['Développement Web', 'Design & Créatif', 'Marketing Digital', 'Data Science', 'IT & Réseaux'];
}
