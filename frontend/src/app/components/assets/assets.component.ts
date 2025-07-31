import { Component, OnInit } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { CommonModule } from '@angular/common';
import { PortfolioService } from '../../services/portfolio.service';

@Component({
  selector: 'app-assets',
  standalone: true,
  imports: [RouterOutlet, CommonModule],
  templateUrl: './assets.component.html',
  styleUrl: './assets.component.css',
})
export class AssetsComponent implements OnInit {
  assets: any[] = [];

  constructor(private portfolioService: PortfolioService) {}

  ngOnInit() {
    this.portfolioService.getAssets().subscribe({
      next: (data: any) => {
        this.assets = data;
        console.log(data);
      },
      error: (err) => {
        console.error('API error:', err);
      },
    });
  }
}
