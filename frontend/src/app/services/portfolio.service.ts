import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';

export interface Allocation {
  asset_type: string;
  percent: number;
}

@Injectable({
  providedIn: 'root',
})
export class PortfolioService {
  constructor(private http: HttpClient) {}

  getAssets() {
    return this.http.get('/api/portfolio/assets');
  }

  getAssetAllocation() {
    return this.http.get<Allocation[]>('/api/portfolio/asset_allocation');
  }

  buyAsset(payload: { ticker: string; asset_type: string; quantity: number }) {
    return this.http.post('/api/portfolio/assets/buy', payload);
  }
}
