import { Component, EventEmitter, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { PortfolioService } from '../../services/portfolio.service';
import { StockDetail } from '../../interfaces/portfolio';

@Component({
  selector: 'app-buy-modal',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './buy-modal.component.html',
  styleUrls: ['./buy-modal.component.css'],
})
export class BuyModalComponent {
  show = false;
  ticker = '';
  asset_type = '';
  quantity: number | null = null;
  availableTickers = ['AAPL', 'MSFT', 'GOOG', 'AMZN', 'TSLA'];
  availableStocks: StockDetail[] = [];

  @Output() purchased = new EventEmitter<{
    ticker: string;
    asset_type: string;
    quantity: number;
  }>();

  constructor(private portfolioService: PortfolioService) {}

  open() {
    this.resetForm();
    this.availableStocks = [];
    for (const t of this.availableTickers) {
      this.portfolioService.getStockDetails(t).subscribe({
        next: (d) => {
          if (d.marketPrice != null && d.previousClose != null) {
            (d as any).pctChange =
              Math.round(
                ((d.marketPrice - d.previousClose) / d.previousClose) * 10000
              ) / 100;
          }
          this.availableStocks.push(d);
        },
      });
    }
    this.show = true;
  }

  resetForm() {
    this.ticker = '';
    this.asset_type = '';
    this.quantity = null;
  }

  selectTicker(t: string) {
    this.ticker = t;
  }

  onConfirm() {
    if (!this.ticker || !this.asset_type || this.quantity === null) {
      return;
    }
    this.purchased.emit({
      ticker: this.ticker,
      asset_type: this.asset_type,
      quantity: this.quantity,
    });
    this.show = false;
    this.resetForm();
  }

  onCancel() {
    this.show = false;
  }
}
