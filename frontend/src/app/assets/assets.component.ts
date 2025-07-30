import { Component, OnInit } from '@angular/core';
import { PortfolioService } from '../services/portfolio.service';
import { RouterOutlet } from '@angular/router';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-assets',
  standalone: true,
  imports: [RouterOutlet, CommonModule],
  templateUrl: './assets.component.html',
  styleUrl: './assets.component.css',
})
export class AssetsComponent implements OnInit {
  portfolio: any[] = [];

  constructor(private portfolioService: PortfolioService) {}

  ngOnInit() {
    this.portfolioService.getAssets().subscribe({
      next: (data: any) => {
        this.portfolio = data;
        console.log(data);
      },
      error: (err) => {
        console.error('API error:', err);
      },
    });
  }
}
