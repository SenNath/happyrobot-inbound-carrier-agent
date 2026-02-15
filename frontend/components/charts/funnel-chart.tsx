"use client";

import { Cell, Funnel, FunnelChart, LabelList, ResponsiveContainer, Tooltip } from "recharts";

import type { FunnelStage } from "@/lib/api";

const colors = ["#0b3b5a", "#0f6d92", "#1da9c3"];

function FunnelTooltip({
  active,
  payload,
}: {
  active?: boolean;
  payload?: Array<{ payload: FunnelStage }>;
}) {
  if (!active || !payload?.length) {
    return null;
  }
  const row = payload[0].payload;
  return (
    <div className="rounded-lg border border-border/70 bg-card/95 px-3 py-2 text-xs shadow-soft">
      <p className="font-semibold text-foreground">{row.stage}</p>
      <p className="mt-1 text-muted-foreground">{row.value} calls</p>
    </div>
  );
}

export function FunnelInsightsChart({ data }: { data: FunnelStage[] }) {
  return (
    <div className="h-[360px] w-full">
      <ResponsiveContainer>
        <FunnelChart>
          <Tooltip content={<FunnelTooltip />} />
          <Funnel dataKey="value" data={data} isAnimationActive>
            <LabelList position="inside" fill="#e7f7fb" stroke="none" dataKey="value" />
            <LabelList position="right" fill="#1f2f3c" stroke="none" dataKey="stage" />
            {data.map((entry, index) => (
              <Cell key={entry.stage} fill={colors[index % colors.length]} />
            ))}
          </Funnel>
        </FunnelChart>
      </ResponsiveContainer>
    </div>
  );
}
