import { Component, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { BuyModalComponent } from '../buy-modal/buy-modal.component';
import { AssetsChartsComponent } from '../assets-charts/assets-charts.component';
import { PortfolioTableComponent } from '../portfolio-table/portfolio-table.component';
import { BalanceComponent } from '../balance/balance.component';
import { DepositModalComponent } from '../deposit-modal/deposit-modal.component';
import { ChatbotComponent } from '../chatbot/chatbot.component';

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
    ChatbotComponent,
  ],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
})
export class AppComponent {
  @ViewChild('buyModal') buyModal!: BuyModalComponent;
  @ViewChild('depositModal') depositModal!: DepositModalComponent;
  @ViewChild('table') table!: PortfolioTableComponent;
  @ViewChild('charts') charts!: AssetsChartsComponent;
  @ViewChild('balance') balance!: BalanceComponent;

  openBuy() {
    this.buyModal.open();
  }
  openDeposit() {
    this.depositModal.open();
  }

  handleSold() {
    this.charts.loadAllocs();
    this.balance.loadBalance();
  }
}
