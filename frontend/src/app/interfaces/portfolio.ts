export interface TypeAllocation {
  asset_type: string;
  percent: number;
}

export interface ValueAllocation {
  ticker: string;
  allocation_percentage: number;
}

export interface StockDetail {
  ticker: string;
  shortName?: string;
  marketPrice?: number;
  previousClose?: number;
  pctChange?: number;
  sector?: string;
  industry?: string;
}

export interface GainerLoser {
  ticker: string;
  name: string;
  change: number;
}
