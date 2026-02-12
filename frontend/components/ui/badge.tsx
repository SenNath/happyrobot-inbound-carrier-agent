import * as React from "react";

import { cn } from "@/lib/utils";

export function Badge({ className, ...props }: React.HTMLAttributes<HTMLSpanElement>) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border border-border/60 bg-accent px-3 py-1 text-xs font-medium text-foreground",
        className,
      )}
      {...props}
    />
  );
}
