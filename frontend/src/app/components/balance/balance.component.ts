import { Component } from '@angular/core';
import { PortfolioService } from '../../services/portfolio.service';

@Component({
  selector: 'app-balance',
  standalone: true,
  imports: [],
  templateUrl: './balance.component.html',
  styleUrl: './balance.component.css',
})
export class BalanceComponent {
  public currentBalance = 0;

  constructor(private portfolioService: PortfolioService) {}

  ngOnInit() {
    this.loadBalance();
  }

  loadBalance() {
    this.portfolioService.getBalance().subscribe({
      next: (res: any) => (this.currentBalance = res.available_balance),
      error: (_) => console.warn('Could not load balance'),
    });
  }
}
