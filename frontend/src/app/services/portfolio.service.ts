import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root',
})
export class PortfolioService {
  constructor(private http: HttpClient) {}

  getAssets() {
    return this.http.get('/api/portfolio/assets');
  }

  buyAsset(payload: { ticker: string; asset_type: string; quantity: number }) {
    return this.http.post('/api/portfolio/assets/buy', payload);
  }
}
