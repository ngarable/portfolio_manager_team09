import { Component, OnInit } from '@angular/core';
import { PortfolioService } from '../../services/portfolio.service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'portfolio-table',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './portfolio-table.component.html',
  styleUrl: './portfolio-table.component.css',
})
export class PortfolioTableComponent implements OnInit {
  assets: any[] = [];
  orders: any[] = [];

  activeTab = 'portfolio';

  constructor(private portfolioService: PortfolioService) {}

  ngOnInit(): void {
    this.loadAssets();
    this.loadRecentOrders();
  }

  loadRecentOrders() {
    this.portfolioService.getRecentOrders().subscribe({
      next: (data: any) => {
        this.orders = data;
      },
      error: (err) => console.error('Error fetching recent orders:', err),
    });
  }

  loadAssets() {
    this.portfolioService.getAssets().subscribe({
      next: (data: any) => (this.assets = data),
      error: (err) => console.error('API error:', err),
    });
  }

  openSellModal(ticker: string) {
    // Logic to open sell modal can be added here
    alert(`Sell modal for ${ticker} not implemented yet.`);
  }
}
