import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Allocation, StockDetail } from '../../interfaces/portfolio';
import { PortfolioService } from '../../services/portfolio.service';

@Component({
  selector: 'app-assets',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './assets.component.html',
  styleUrl: './assets.component.css',
})
export class AssetsComponent implements OnInit {
  assets: any[] = [];
  newAsset = { ticker: '', asset_type: '', quantity: null as number | null };
  allocation: Allocation[] = [];

  showBuyModal = false;
  availableTickers = ['AAPL', 'MSFT', 'GOOG', 'AMZN', 'TSLA'];
  availableStocks: StockDetail[] = [];

  public pieGradient = '';
  public colors = ['#4caf50', '#2196f3', '#ff9800', '#e91e63', '#9c27b0'];

  constructor(private portfolioService: PortfolioService) {}

  ngOnInit() {
    this.loadAssets();
    this.loadAllocation();
  }

  loadAssets() {
    this.portfolioService.getAssets().subscribe({
      next: (data: any) => (this.assets = data),
      error: (err) => console.error('API error:', err),
    });
  }

  loadAllocation() {
    this.portfolioService.getAssetAllocation().subscribe({
      next: (data) => {
        this.allocation = data;
        this.updatePieGradient();
      },
      error: (err) => console.error(err),
    });
  }

  openBuyModal() {
    this.newAsset = { ticker: '', asset_type: '', quantity: null };
    this.availableStocks = [];
    for (const t of this.availableTickers) {
      this.portfolioService.getStockDetails(t).subscribe({
        next: (detail) => {
          if (detail.marketPrice != null && detail.previousClose) {
            (detail as any).pctChange =
              Math.round(
                ((detail.marketPrice - detail.previousClose) /
                  detail.previousClose) *
                  100 *
                  100
              ) / 100;
          }
          this.availableStocks.push(detail);
        },
        error: (err) => console.warn(`no data for ${t}`, err),
      });
    }
    this.showBuyModal = true;
  }

  selectTicker(t: string) {
    this.newAsset.ticker = t;
  }
  closeBuyModal() {
    this.showBuyModal = false;
  }

  buyAsset() {
    const { ticker, asset_type, quantity } = this.newAsset;
    if (!ticker || !asset_type || quantity == null) {
      return;
    }

    this.portfolioService.buyAsset({ ticker, asset_type, quantity }).subscribe({
      next: (res: any) => {
        console.log('Buy response:', res);
        this.assets.push({
          ticker: res.ticker,
          asset_type: res.asset_type,
          quantity: res.quantity,
        });
        this.newAsset = { ticker: '', asset_type: '', quantity: null };
      },
      error: (err) => console.error('Buy error:', err),
    });
  }

  private updatePieGradient() {
    let start = 0;
    const stops = this.allocation.map((a, i) => {
      const percent = a.percent;
      const end = start + percent;
      const color = this.colors[i % this.colors.length];
      const seg = `${color} ${start}% ${end}%`;
      start = end;
      return seg;
    });
    this.pieGradient = `conic-gradient(${stops.join(', ')})`;
  }
}
