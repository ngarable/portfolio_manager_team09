import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';

import { PortfolioService } from '../../services/portfolio.service';
import { TypeAllocation, ValueAllocation } from '../../interfaces/portfolio';

@Component({
  selector: 'app-assets-charts',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './assets-charts.component.html',
  styleUrls: ['./assets-charts.component.css'],
})
export class AssetsChartsComponent implements OnInit {
  typeAlloc: TypeAllocation[] = [];
  valueAlloc: ValueAllocation[] = [];

  pieGradientType = '';
  pieGradientValue = '';

  typeColors: string[] = [];
  valueColors: string[] = [];

  constructor(private portfolioService: PortfolioService) {}

  ngOnInit() {
    this.loadAllocs();
  }

  loadAllocs() {
    this.portfolioService.getTypeAllocation().subscribe({
      next: (data) => {
        this.typeAlloc = data;
        this.buildGradient(
          data.map((d) => d.percent),
          'pieGradientType',
          'typeColors'
        );
      },
      error: (err) => console.error('Type alloc error', err),
    });

    this.portfolioService.getValueAllocation().subscribe({
      next: (data) => {
        this.valueAlloc = data;
        this.buildGradient(
          data.map((d) => d.allocation_percentage),
          'pieGradientValue',
          'valueColors'
        );
      },
      error: (err) => console.error('Value alloc error', err),
    });
  }

  private generateColors(count: number): string[] {
    return Array.from({ length: count }, (_, i) => {
      const hue = Math.round((360 * i) / count);
      return `hsl(${hue}, 60%, 55%)`;
    });
  }

  private buildGradient(
    percentages: number[],
    target: 'pieGradientType' | 'pieGradientValue',
    colorKey: 'typeColors' | 'valueColors'
  ) {
    const colors = this.generateColors(percentages.length);
    this[colorKey] = colors;

    let start = 0;
    const stops = percentages.map((pct, i) => {
      const end = start + pct;
      const seg = `${colors[i]} ${start}% ${end}%`;
      start = end;
      return seg;
    });

    this[target] = `conic-gradient(${stops.join(', ')})`;
  }
}
