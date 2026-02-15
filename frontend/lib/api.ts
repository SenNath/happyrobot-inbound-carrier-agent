export type OverviewStats = {
  total_calls: number;
  verified_carriers: number;
  booked_loads: number;
  avg_sentiment: number;
  revenue_accepted: number;
  booking_rate: number;
  avg_negotiation_rounds: number;
  avg_margin_pressure: number;
  verified_vs_unverified_ratio: number;
  verified_count: number;
  unverified_count: number;
};

export type FunnelStage = {
  stage: string;
  value: number;
};

export type NegotiationInsight = {
  decision: "accept" | "counter" | "reject" | "needs_more_info";
  count: number;
  avg_round: number;
};

export type SentimentPoint = {
  date: string;
  avg_sentiment: number;
};

export type SentimentDistributionPoint = {
  sentiment: string;
  count: number;
};

export type LoadPerformancePoint = {
  equipment_type: string;
  total_calls: number;
  booked_calls: number;
  booking_rate: number;
  avg_final_rate: number;
  avg_loadboard_rate: number;
  avg_miles: number;
  market_gap_pct: number;
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
const API_KEY = process.env.BACKEND_API_KEY ?? "";

async function fetchJSON<T>(path: string, fallback: T): Promise<T> {
  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      next: { revalidate: 60 },
      headers: {
        "Content-Type": "application/json",
        ...(API_KEY ? { "X-API-Key": API_KEY } : {}),
      },
    });

    if (!response.ok) {
      return fallback;
    }
    return (await response.json()) as T;
  } catch {
    return fallback;
  }
}

export async function getOverview(): Promise<OverviewStats> {
  return fetchJSON<OverviewStats>("/dashboard/overview", {
    total_calls: 0,
    verified_carriers: 0,
    booked_loads: 0,
    avg_sentiment: 0,
    revenue_accepted: 0,
    booking_rate: 0,
    avg_negotiation_rounds: 0,
    avg_margin_pressure: 0,
    verified_vs_unverified_ratio: 0,
    verified_count: 0,
    unverified_count: 0,
  });
}

export async function getFunnel(): Promise<FunnelStage[]> {
  return fetchJSON<FunnelStage[]>("/dashboard/funnel", []);
}

export async function getNegotiations(): Promise<NegotiationInsight[]> {
  return fetchJSON<NegotiationInsight[]>("/dashboard/negotiations", []);
}

export async function getSentiment(): Promise<SentimentPoint[]> {
  return fetchJSON<SentimentPoint[]>("/dashboard/sentiment", []);
}

export async function getSentimentDistribution(): Promise<SentimentDistributionPoint[]> {
  return fetchJSON<SentimentDistributionPoint[]>("/dashboard/sentiment-distribution", []);
}

export async function getLoadPerformance(): Promise<LoadPerformancePoint[]> {
  return fetchJSON<LoadPerformancePoint[]>("/dashboard/load-performance", []);
}
