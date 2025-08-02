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

  public colors = ['#4caf50', '#2196f3', '#ff9800', '#e91e63', '#9c27b0'];

  constructor(private portfolioService: PortfolioService) {}

  ngOnInit() {
    this.reloadAllocs();
  }

  public reloadAllocs() {
    this.portfolioService.getTypeAllocation().subscribe({
      next: (data) => {
        this.typeAlloc = data;
        this.buildGradient(
          data.map((d) => d.percent),
          'pieGradientType'
        );
      },
      error: (err) => console.error('Type alloc error', err),
    });

    this.portfolioService.getValueAllocation().subscribe({
      next: (data) => {
        this.valueAlloc = data;
        this.buildGradient(
          data.map((d) => d.allocation_percentage),
          'pieGradientValue'
        );
      },
      error: (err) => console.error('Value alloc error', err),
    });
  }

  private buildGradient(
    percentages: number[],
    target: 'pieGradientType' | 'pieGradientValue'
  ) {
    let start = 0;
    const stops = percentages.map((pct, i) => {
      const end = start + pct;
      const color = this.colors[i % this.colors.length];
      const seg = `${color} ${start}% ${end}%`;
      start = end;
      return seg;
    });
    this[target] = `conic-gradient(${stops.join(', ')})`;
  }
}
