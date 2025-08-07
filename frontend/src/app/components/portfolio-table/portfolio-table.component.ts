import {
  Component,
  EventEmitter,
  OnInit,
  Output,
  ViewChild,
} from '@angular/core';
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
  @Output() sold = new EventEmitter<void>();
  @ViewChild(SellModalComponent) sellModal!: SellModalComponent;

  assets: any[] = [];
  orders: any[] = [];

  activeTab = 'portfolio';

  constructor(private portfolioService: PortfolioService) {}

  ngOnInit(): void {
    this.loadAssets();
    this.loadRecentOrders();
  }

  loadAssets(): void {
    this.portfolioService.getPnlByAsset().subscribe({
      next: (data: any) => (this.assets = data),
      error: (err) => console.error('Error fetching assets:', err),
    });
  }

  loadRecentOrders(): void {
    this.portfolioService.getRecentOrders().subscribe({
      next: (data: any) => (this.orders = data),
      error: (err) => console.error('Error fetching recent orders:', err),
    });
  }

  openSell(selectedTicker: string) {
    this.sellModal.open(selectedTicker);
  }

  onSold() {
    this.loadAssets();
    this.loadRecentOrders();
    this.sold.emit();
  }
}
