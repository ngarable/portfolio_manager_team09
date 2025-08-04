import { Component, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { BuyModalComponent } from '../buy-modal/buy-modal.component';
import { AssetsChartsComponent } from '../assets-charts/assets-charts.component';
import { PortfolioTableComponent } from '../portfolio-table/portfolio-table.component';
import { PortfolioService } from '../../services/portfolio.service';
import { BalanceComponent } from '../balance/balance.component';
import { DepositModalComponent } from '../deposit-modal/deposit-modal.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    CommonModule,
    BuyModalComponent,
    AssetsChartsComponent,
    PortfolioTableComponent,
    BalanceComponent,
    DepositModalComponent,
  ],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
})
export class AppComponent {
  @ViewChild(BuyModalComponent) buyModal!: BuyModalComponent;
  @ViewChild(AssetsChartsComponent) charts!: AssetsChartsComponent;
  @ViewChild(PortfolioTableComponent) table!: PortfolioTableComponent;
  @ViewChild(DepositModalComponent) depositModal!: DepositModalComponent;

  constructor(private portfolioService: PortfolioService) {}

  openBuy() {
    this.buyModal.open();
  }

  openDeposit() {
    this.depositModal.open();
  }

  handleDeposit(amount: number) {
    this.table.loadAssets();
    this.charts.reloadAllocs();
  }

  handlePurchase(evt: { ticker: string; quantity: number }) {
    this.portfolioService.buyAsset(evt).subscribe({
      next: () => {
        this.table.loadAssets();
        this.charts.reloadAllocs();
      },
      error: (err) => {
        if (err.status === 400 && err.error?.error === 'Insufficient funds') {
          alert(
            `Not enough funds!\nYou have $${err.error.available_balance}, but need $${err.error.required}.`
          );
        } else {
          console.error('Buy failed', err);
          alert('Buy failed; see console for details.');
        }
      },
    });
  }
}
