import { SentimentChart } from "@/components/charts/sentiment-chart";
import { SentimentDistributionChart } from "@/components/charts/sentiment-distribution-chart";
import { Badge } from "@/components/ui/badge";
import { Card, CardDescription, CardTitle } from "@/components/ui/card";
import { getSentiment, getSentimentDistribution } from "@/lib/api";

export default async function SentimentPage() {
  const data = await getSentiment();
  const distribution = await getSentimentDistribution();
  const totalTaggedCalls = distribution.reduce((sum, row) => sum + row.count, 0);
  const positiveCount = distribution.find((row) => row.sentiment === "positive")?.count ?? 0;
  const negativeCount = distribution.find((row) => row.sentiment === "negative")?.count ?? 0;
  const latestScore = data.length > 0 ? data[data.length - 1].avg_sentiment : 0;
  const positivityRate = totalTaggedCalls > 0 ? (positiveCount / totalTaggedCalls) * 100 : 0;

  return (
    <>
      <header className="space-y-2">
        <Badge>Voice Quality</Badge>
        <h2 className="font-[var(--font-heading)] text-3xl font-semibold tracking-tight">Sentiment Analytics</h2>
      </header>
      <section className="grid gap-4 md:grid-cols-3">
        <Card className="bg-gradient-to-b from-card to-accent/20">
          <CardDescription>Latest Sentiment Score</CardDescription>
          <CardTitle className="mt-2 text-2xl">{latestScore.toFixed(2)}</CardTitle>
          <p className="mt-2 text-xs text-muted-foreground">Most recent daily score (-1 to 1)</p>
        </Card>
        <Card className="bg-gradient-to-b from-card to-accent/20">
          <CardDescription>Positive Share</CardDescription>
          <CardTitle className="mt-2 text-2xl">{positivityRate.toFixed(1)}%</CardTitle>
          <p className="mt-2 text-xs text-muted-foreground">
            {positiveCount} positive of {totalTaggedCalls} labeled calls
          </p>
        </Card>
        <Card className="bg-gradient-to-b from-card to-accent/20">
          <CardDescription>Negative Calls</CardDescription>
          <CardTitle className="mt-2 text-2xl">{negativeCount}</CardTitle>
          <p className="mt-2 text-xs text-muted-foreground">Escalation risk signals to review quickly</p>
        </Card>
      </section>
      <Card>
        <CardTitle>Daily Sentiment Trend</CardTitle>
        <CardDescription className="mt-1">
          Rolling daily average based on structured analytics submitted by HappyRobot extract nodes.
        </CardDescription>
        {data.length > 0 ? (
          <div className="mt-6">
            <SentimentChart data={data} />
          </div>
        ) : (
          <p className="mt-6 text-sm text-muted-foreground">No sentiment telemetry available yet.</p>
        )}
      </Card>

      <Card>
        <CardTitle>Sentiment Distribution</CardTitle>
        <CardDescription className="mt-1">
          Distribution of extract-level sentiment labels (`positive`, `neutral`, `negative`, `unknown`).
        </CardDescription>
        {distribution.length > 0 ? (
          <div className="mt-6">
            <SentimentDistributionChart data={distribution} />
          </div>
        ) : (
          <p className="mt-6 text-sm text-muted-foreground">No sentiment distribution data available yet.</p>
        )}
      </Card>
    </>
  );
}
