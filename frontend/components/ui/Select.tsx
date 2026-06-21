import { type SelectHTMLAttributes, forwardRef } from "react";

import { cn } from "@/lib/cn";

export const Select = forwardRef<HTMLSelectElement, SelectHTMLAttributes<HTMLSelectElement>>(
  ({ className, children, ...props }, ref) => (
    <select
      ref={ref}
      className={cn(
        "h-9 w-full appearance-none rounded border border-border bg-surface-raised px-3 text-sm text-ink-primary",
        "bg-[url('data:image/svg+xml;utf8,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 20 20%22 fill=%22%2397A0B5%22><path d=%22M5.5 7.5l4.5 4.5 4.5-4.5%22 stroke=%22%2397A0B5%22 stroke-width=%221.4%22 fill=%22none%22 stroke-linecap=%22round%22 stroke-linejoin=%22round%22/></svg>')] bg-no-repeat bg-[right_0.6rem_center] pr-8",
        "transition-colors focus:border-accent disabled:cursor-not-allowed disabled:opacity-50",
        className
      )}
      {...props}
    >
      {children}
    </select>
  )
);
Select.displayName = "Select";
