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
  private netWorthChartInstance: Chart | null = null;

  constructor(
    private portfolioService: PortfolioService,
    @Inject(PLATFORM_ID) private platformId: Object,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit() {
    this.loadBalance();
  }

  loadBalance() {
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
          setTimeout(() => this.loadLineChart(labels, netWorthData), 0);
        },
      });
    }
  }

  loadLineChart(labels: string[], netWorthData: number[]) {
    if (!this.netWorthChart) return;
    const ctx = this.netWorthChart.nativeElement.getContext('2d');
    if (!ctx) return;

    const min = Math.min(...netWorthData) * 0.9;
    const max = Math.max(...netWorthData);

    if (this.netWorthChartInstance) {
      const chart = this.netWorthChartInstance;
      chart.data.labels = labels;
      chart.data.datasets![0].data = netWorthData;
      // @ts-ignore
      chart.options.scales!.y!.suggestedMin = min;
      // @ts-ignore
      chart.options.scales!.y!.suggestedMax = max;
      chart.update();
    } else {
      this.netWorthChartInstance = new Chart(ctx, {
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
              pointRadius: 3,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: {
              ticks: { maxRotation: 45, autoSkip: true, maxTicksLimit: 10 },
            },
            y: {
              beginAtZero: false,
              suggestedMin: min,
              suggestedMax: max,
            },
          },
          plugins: { legend: { display: false } },
        },
      });
    }
  }
}
