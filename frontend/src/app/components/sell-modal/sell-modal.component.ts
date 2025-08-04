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
  templateUrl: './sell-modal.component.html',
  imports: [CommonModule],
  styleUrls: ['./sell-modal.component.css'],
})
export class SellModalComponent implements OnChanges {
  @ViewChild('quantityInput') quantityInput!: ElementRef<HTMLInputElement>;
  @Input() ticker: string = '';
  @Input() visible: boolean = false;
  @Output() close = new EventEmitter<void>();

  constructor(private portfolioService: PortfolioService) {}

  marketPrice: number | undefined = 0;
  assetType: string | undefined = '';

  errorMessage: string | null = null;

  ngOnChanges(changes: SimpleChanges) {
    if (changes['visible'] && changes['visible'].currentValue === true) {
      this.portfolioService.getStockDetails(this.ticker).subscribe({
        next: (data) => {
          this.marketPrice = data.marketPrice;
          this.assetType = data.assetType;
        },
        error: (err) => {
          console.error('Error fetching stock details:', err);
        },
      });
    }
  }

  onClose() {
    this.close.emit();
    this.errorMessage = null; // Reset error message on close
  }

  confirmSell() {
    // /assets/sell
    // body: { ticker: string, quantity: number }
    const quantity = this.quantityInput.nativeElement.valueAsNumber;
    if (!quantity) {
      this.errorMessage = 'Please enter a valid quantity.';
      return;
    }
    console.log('Quantity:', quantity);

    this.portfolioService
      .sellAsset({
        ticker: this.ticker,
        quantity: quantity,
      })
      .subscribe({
        next: () => {
          this.errorMessage = null;
          this.onClose();
          alert(`Sold ${quantity} share(s) of ${this.ticker}`);
          window.location.reload();
        },
        error: (err) => {
          if (err.status === 400 && err.error?.message.includes('Not enough')) {
            this.errorMessage = err.error.message;
          } else {
            this.errorMessage = 'An unexpected error occurred while selling.';
          }
        },
      });
  }
}
