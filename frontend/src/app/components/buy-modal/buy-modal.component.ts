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
  quantity: number | null = null;
  availableTickers = ['AAPL', 'MSFT', 'GOOG', 'AMZN', 'TSLA'];
  availableStocks: StockDetail[] = [];
  errorMessage: string | null = null;

  @Output() purchased = new EventEmitter<{
    ticker: string;
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
    this.quantity = null;
    this.errorMessage = null;
  }

  selectTicker(t: string) {
    this.ticker = t;
  }

  validateInputs(): Promise<boolean> {
    if (!this.ticker.trim()) {
      this.errorMessage = 'Ticker is required.';
      return Promise.resolve(false);
    }
    if (!this.quantity || this.quantity <= 0) {
      this.errorMessage = 'Quantity must be greater than zero.';
      return Promise.resolve(false);
    }

    // 🔹 Validate ticker exists via backend
    return new Promise((resolve) => {
      this.portfolioService.getStockDetails(this.ticker).subscribe({
        next: (data) => {
          if (!data || !data.marketPrice) {
            this.errorMessage = 'Invalid ticker: No market data found.';
            resolve(false);
          } else {
            this.errorMessage = null;
            resolve(true);
          }
        },
        error: () => {
          this.errorMessage = 'Invalid ticker: Could not fetch from yfinance.';
          resolve(false);
        },
      });
    });
  }

  async onConfirm() {
    const isValid = await this.validateInputs();
    if (!isValid) return;

    this.portfolioService
      .buyAsset({
        ticker: this.ticker,
        quantity: this.quantity!,
      } as any)
      .subscribe({
        next: () => {
          this.errorMessage = null;
          this.show = false;
          alert(`Bought ${this.quantity} share(s) of ${this.ticker}`);
          window.location.reload();
        },
        error: (err) => {
          console.error('Error buying asset:', err);
          if (err.status === 400 && err.error?.error === 'Insufficient funds') {
            this.errorMessage = `Not enough funds! Available: $${err.error.available_balance}, Required: $${err.error.required}`;
          } else {
            this.errorMessage =
              err.error?.message ||
              'An unexpected error occurred while buying.';
          }
        },
      });
  }

  onCancel() {
    this.show = false;
  }
}
