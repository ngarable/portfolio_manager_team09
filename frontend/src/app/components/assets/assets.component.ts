import { Component, OnInit } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { CommonModule } from '@angular/common';
import { PortfolioService } from '../../services/portfolio.service';
import { FormsModule } from '@angular/forms';
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

  constructor(private portfolioService: PortfolioService) {}

  ngOnInit() {
    this.loadAssets();
  }

  loadAssets() {
    this.portfolioService.getAssets().subscribe({
      next: (data: any) => (this.assets = data),
      error: (err) => console.error('API error:', err),
    });
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
}
