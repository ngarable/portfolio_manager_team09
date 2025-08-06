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
  errorMessage: string | null = null;
  successMessage: string | null = null;
  isLoading = false;

  constructor(private portfolioService: PortfolioService) {}

  open() {
    this.amount = null;
    this.errorMessage = null;
    this.successMessage = null;
    this.isLoading = false;
    this.isOpen = true;
  }

  close() {
    this.isOpen = false;
  }

  submitDeposit() {
    if (!this.amount || this.amount <= 0) {
      this.errorMessage = 'Amount must be greater than zero.';
      return;
    }

    this.errorMessage = null;
    this.isLoading = true;

    this.portfolioService.deposit(this.amount).subscribe({
      next: (res: any) => {
        this.isLoading = false;
        this.successMessage =
          `You deposited $${this.amount!.toFixed(2)}! ` +
          `New balance: $${res.available_balance.toFixed(2)}.`;
        this.deposited.emit(this.amount!);

        setTimeout(() => {
          this.close();
          window.location.reload();
        }, 2000);
      },
      error: (err) => {
        this.isLoading = false;
        console.error('Deposit failed', err);
        this.errorMessage = 'An unexpected error occurred.';
      },
    });
  }
}
