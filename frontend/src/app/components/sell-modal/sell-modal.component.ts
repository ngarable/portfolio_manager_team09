import {
  Component,
  Input,
  Output,
  EventEmitter,
  OnChanges,
  SimpleChanges,
  ViewChild,
  ElementRef,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { PortfolioService } from '../../services/portfolio.service';

@Component({
  selector: 'app-sell-modal',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './sell-modal.component.html',
  styleUrls: ['./sell-modal.component.css'],
})
export class SellModalComponent implements OnChanges {
  @ViewChild('quantityInput') quantityInput!: ElementRef<HTMLInputElement>;
  @Input() ticker = '';
  @Input() visible = false;
  @Output() close = new EventEmitter<void>();

  errorMessage: string | null = null;
  successMessage: string | null = null;
  isLoading = false;

  constructor(private portfolioService: PortfolioService) {}

  ngOnChanges(changes: SimpleChanges) {
    if (changes['visible'] && this.visible) {
      // you already fetch details elsewhere if needed
      this.errorMessage = this.successMessage = null;
      this.isLoading = false;
    }
  }

  confirmSell() {
    const qty = this.quantityInput.nativeElement.valueAsNumber;
    if (!qty || qty < 1) {
      this.errorMessage = 'Quantity must be at least 1.';
      return;
    }
    this.errorMessage = null;
    this.isLoading = true;

    this.portfolioService
      .sellAsset({ ticker: this.ticker, quantity: qty })
      .subscribe({
        next: () => {
          this.successMessage = `Sold ${qty} share${qty > 1 ? 's' : ''} of ${
            this.ticker
          }!`;
          // auto-close & reload
          setTimeout(() => {
            this.onClose();
            window.location.reload();
          }, 2000);
        },
        error: (err) => {
          console.error('Sell error:', err);
          this.errorMessage =
            err.status === 400 && err.error?.message?.includes('Not enough')
              ? err.error.message
              : 'An unexpected error occurred.';
          this.isLoading = false;
        },
      });
  }

  onClose() {
    this.errorMessage = this.successMessage = null;
    this.close.emit();
  }
}
