import { SentimentChart } from "@/components/charts/sentiment-chart";
import { Badge } from "@/components/ui/badge";
import { Card, CardDescription, CardTitle } from "@/components/ui/card";
import { getSentiment } from "@/lib/api";

export default async function SentimentPage() {
  const data = await getSentiment();

  return (
    <>
      <header className="space-y-2">
        <Badge>Voice Quality</Badge>
        <h2 className="font-[var(--font-heading)] text-3xl font-semibold tracking-tight">Sentiment Analytics</h2>
      </header>
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
    </>
  );
}
