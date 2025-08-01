import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Allocation, StockDetail } from '../interfaces/portfolio';

@Injectable({
  providedIn: 'root',
})
export class PortfolioService {
  constructor(private http: HttpClient) {}

  getBalance() {
    return this.http.get<{ available_balance: number }>(
      '/api/portfolio/balance'
    );
  }

  getAssets() {
    return this.http.get('/api/portfolio/assets');
  }

  getAssetAllocation() {
    return this.http.get<Allocation[]>('/api/portfolio/asset_allocation');
  }

  buyAsset(payload: { ticker: string; asset_type: string; quantity: number }) {
    return this.http.post('/api/portfolio/assets/buy', payload);
  }

  getStockDetails(ticker: string) {
    return this.http.get<StockDetail>(`/api/portfolio/stock/${ticker}`);
  }

  deposit(amount: number) {
    return this.http.put('/api/portfolio/deposit', { amount });
  }
}
