import { Component, EventEmitter, OnInit, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { PortfolioService } from '../../services/portfolio.service';
import { SellModalComponent } from '../sell-modal/sell-modal.component';

@Component({
  selector: 'app-portfolio-table',
  standalone: true,
  imports: [CommonModule, SellModalComponent],
  templateUrl: './portfolio-table.component.html',
  styleUrls: ['./portfolio-table.component.css'],
})
export class PortfolioTableComponent implements OnInit {
  @Output() buy = new EventEmitter<void>();

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

  public loadAssets(): void {
    this.portfolioService.getPnlByAsset().subscribe({
      next: (data: any) => (this.assets = data),
      error: (err) => console.error('Error fetching assets:', err),
    });
  }

  private loadRecentOrders(): void {
    this.portfolioService.getRecentOrders().subscribe({
      next: (data: any) => (this.orders = data),
      error: (err) => console.error('Error fetching recent orders:', err),
    });
  }

  openSellModal(ticker: string): void {
    this.selectedTicker = ticker;
    this.modalVisible = true;
  }

  closeModal(): void {
    this.modalVisible = false;
    this.selectedTicker = '';
  }
}
