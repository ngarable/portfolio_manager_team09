import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import {
  TypeAllocation,
  StockDetail,
  ValueAllocation,
  GainerLoser,
} from '../interfaces/portfolio';

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

  getPnlByAsset() {
    return this.http.get('/api/portfolio/pnl_by_asset');
  }

  getTypeAllocation() {
    return this.http.get<TypeAllocation[]>('/api/portfolio/asset_allocation');
  }

  getValueAllocation() {
    return this.http.get<ValueAllocation[]>(
      '/api/portfolio/asset_value_allocation'
    );
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

  sellAsset(payload: { ticker: string; quantity: number }) {
    return this.http.post('/api/portfolio/assets/sell', payload);
  }

  getPortfolioValue() {
    return this.http.get<{ portfolio_value: number }>(
      '/api/portfolio/portfolio_value'
    );
  }

  getGainersLosers() {
    return this.http.get<{ gainers: GainerLoser[]; losers: GainerLoser[] }>(
      '/api/portfolio/gainers-losers'
    );
  }

  getRecentOrders() {
    return this.http.get('/api/portfolio/recent_orders');
  }

  getLatestSnapshot() {
    return this.http.get<{
      date: string;
      total_invested_value: number;
      cash_balance: number;
      net_worth: number;
    }>('/api/portfolio/snapshot/latest');
  }
}
