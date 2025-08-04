import {
  Component,
  ElementRef,
  OnInit,
  ViewChild,
  Inject,
  PLATFORM_ID,
  ChangeDetectorRef,
} from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { Chart, registerables } from 'chart.js';
import { PortfolioService } from '../../services/portfolio.service';
import { from } from 'rxjs';

Chart.register(...registerables);

@Component({
  selector: 'app-balance',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './balance.component.html',
  styleUrls: ['./balance.component.css'],
})
export class BalanceComponent implements OnInit {
  snapshot: any = null;
  @ViewChild('netWorthChart') netWorthChart!: ElementRef<HTMLCanvasElement>;

  constructor(
    private portfolioService: PortfolioService,
    @Inject(PLATFORM_ID) private platformId: Object,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit() {
    if (isPlatformBrowser(this.platformId)) {
      this.portfolioService.getLatestSnapshot().subscribe({
        next: (res) => {
          this.snapshot = res;
          this.cdr.detectChanges();
          setTimeout(() => this.loadChart(), 0);
        },
      });
    }
  }

  loadChart() {
    if (!this.netWorthChart) return;

    const labels = ['2025-08-01', '2025-08-02', '2025-08-03', '2025-08-04'];
    const netWorthData = [10000, 10200, 10150, 10300];

    new Chart(this.netWorthChart.nativeElement, {
      type: 'line',
      data: {
        labels,
        datasets: [
          {
            label: 'Net Worth ($)',
            data: netWorthData,
            borderColor: '#2196f3',
            backgroundColor: 'rgba(33, 150, 243, 0.2)',
            fill: true,
            tension: 0.2,
          },
        ],
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            position: 'bottom',
          },
        },
      },
    });
  }
}
