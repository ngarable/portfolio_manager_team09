import { Component, EventEmitter, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { firstValueFrom } from 'rxjs';
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
  successMessage: string | null = null;
  isLoading = false;

  @Output() purchased = new EventEmitter<{
    ticker: string;
    quantity: number;
  }>();

  constructor(private portfolioService: PortfolioService) {}

  open() {
    this.resetForm();
    this.availableStocks = [];
    this.availableTickers.forEach((t) =>
      this.portfolioService.getStockDetails(t).subscribe((d) => {
        if (d.marketPrice != null && d.previousClose != null) {
          (d as any).pctChange =
            Math.round(
              ((d.marketPrice - d.previousClose) / d.previousClose) * 10000
            ) / 100;
        }
        this.availableStocks.push(d);
      })
    );
    this.show = true;
  }

  resetForm() {
    this.ticker = '';
    this.quantity = null;
    this.errorMessage = this.successMessage = null;
    this.isLoading = false;
  }

  selectTicker(t: string) {
    this.ticker = t;
  }

  async onConfirm() {
    this.errorMessage = null;
    if (!this.ticker.trim()) {
      this.errorMessage = 'Ticker is required.';
      return;
    }
    if (!this.quantity || this.quantity < 1) {
      this.errorMessage = 'Quantity must be at least 1.';
      return;
    }
    this.isLoading = true;
    let details: StockDetail;
    try {
      details = await firstValueFrom(
        this.portfolioService.getStockDetails(this.ticker.trim())
      );
    } catch {
      this.errorMessage = `Could not fetch data for “${this.ticker}.”`;
      this.isLoading = false;
      return;
    }
    if (!details.marketPrice) {
      this.errorMessage = 'Invalid ticker: No market data.';
      this.isLoading = false;
      return;
    }

    this.portfolioService
      .buyAsset({ ticker: this.ticker.trim(), quantity: this.quantity })
      .subscribe({
        next: () => {
          this.successMessage = `Bought ${this.quantity} share${
            this.quantity! > 1 ? 's' : ''
          } of ${this.ticker}!`;
          this.purchased.emit({
            ticker: this.ticker,
            quantity: this.quantity!,
          });
          setTimeout(() => {
            this.show = false;
            window.location.reload();
          }, 2000);
        },
        error: (err) => {
          console.error('Buy error', err);
          this.errorMessage =
            err.status === 400 && err.error?.error === 'Insufficient funds'
              ? 'Insufficient funds.'
              : 'An unexpected error occurred.';
          this.isLoading = false;
        },
      });
  }

  close() {
    this.show = false;
  }
}
