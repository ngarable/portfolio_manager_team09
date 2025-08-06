import {
  Component,
  ElementRef,
  OnInit,
  ViewChild,
  Inject,
  PLATFORM_ID,
  ChangeDetectorRef,
  EventEmitter,
  Output,
} from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { Chart, registerables } from 'chart.js';
import { PortfolioService } from '../../services/portfolio.service';

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
  @Output() deposit = new EventEmitter<void>();
  
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
        },
      });

      this.portfolioService.getSnapshotHistory().subscribe({
        next: (history) => {
          const lastMonth = history.filter((s) => {
            const snapshotDate = new Date(s.date);
            const cutoff = new Date();
            cutoff.setDate(cutoff.getDate() - 30);
            return snapshotDate >= cutoff;
          });

          const labels = lastMonth.map((s) => s.date);
          const netWorthData = lastMonth.map((s) => s.net_worth);

          this.cdr.detectChanges();
          setTimeout(() => this.loadChart(labels, netWorthData), 0);
        },
      });
    }
  }

  loadChart(labels: string[], netWorthData: number[]) {
    if (!this.netWorthChart) return;

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
          legend: { display: false },
        },
      },
    });
  }
}
