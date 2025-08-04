import { Component, EventEmitter, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { PortfolioService } from '../../services/portfolio.service';

@Component({
  selector: 'app-deposit-modal',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './deposit-modal.component.html',
  styleUrls: ['./deposit-modal.component.css'],
})
export class DepositModalComponent {
  @Output() deposited = new EventEmitter<number>();

  isOpen = false;
  amount: number | null = null;
  isLoading = false;

  constructor(private portfolioService: PortfolioService) {}

  open() {
    this.amount = null;
    this.isOpen = true;
  }

  close() {
    this.isOpen = false;
  }

  submitDeposit() {
    if (!this.amount || this.amount <= 0) {
      alert('Please enter a valid amount.');
      return;
    }

    this.isLoading = true;
    this.portfolioService.deposit(this.amount).subscribe({
      next: (res: any) => {
        this.isLoading = false;
        this.deposited.emit(this.amount!);
        alert(`Deposit successful! New balance: $${res.available_balance}`);
        this.close();
        window.location.reload();
      },
      error: (err) => {
        this.isLoading = false;
        console.error('Deposit failed', err);
        alert('Deposit failed; see console for details.');
      },
    });
  }
}
