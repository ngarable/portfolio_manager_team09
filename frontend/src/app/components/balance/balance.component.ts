import { Component } from '@angular/core';
import { PortfolioService } from '../../services/portfolio.service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-balance',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './balance.component.html',
  styleUrl: './balance.component.css',
})
export class BalanceComponent {
  public currentBalance = 0;
  snapshot: any = null;

  constructor(private portfolioService: PortfolioService) {}

  ngOnInit() {
    this.portfolioService.getLatestSnapshot().subscribe({
      next: (res) => (this.snapshot = res),
      error: () => console.warn('Could not load snapshot'),
    });
  }
}
