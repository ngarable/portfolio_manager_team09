export interface Allocation {
  asset_type: string;
  percent: number;
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
