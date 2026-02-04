import * as React from "react";

type SkeletonProps = React.HTMLAttributes<HTMLDivElement>;

export function Skeleton({ className = "", ...props }: SkeletonProps) {
  return (
    <div
      className={
        "animate-pulse rounded-md bg-muted/60 dark:bg-muted/30 " + className
      }
      {...props}
    />
  );
}
