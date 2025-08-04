import { Component, OnInit } from '@angular/core';
import { PortfolioService } from '../../services/portfolio.service';
import { CommonModule } from '@angular/common';
import { SellModalComponent } from '../sell-modal/sell-modal.component';

@Component({
  selector: 'app-portfolio-table',
  standalone: true,
  imports: [CommonModule, SellModalComponent],
  templateUrl: './portfolio-table.component.html',
  styleUrl: './portfolio-table.component.css',
})
export class PortfolioTableComponent implements OnInit {
  assets: any[] = [];
  orders: any[] = [];

  activeTab = 'portfolio';

  selectedTicker: string = '';
  modalVisible = false;

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
    this.selectedTicker = ticker;
    this.modalVisible = true;
  }

  closeModal() {
    this.modalVisible = false;
    this.selectedTicker = '';
  }
}
