import { Component, OnInit } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { PortfolioService } from './services/portfolio.service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, CommonModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent implements OnInit {
  portfolios: any[] = [];

  constructor(private portfolioService: PortfolioService) {}

  ngOnInit() {
    this.portfolioService.getPortfolios().subscribe({
      next: (data: any) => {
        this.portfolios = data;
      },
      error: (err) => {
        console.error('API error:', err);
      }
    });
  }
}