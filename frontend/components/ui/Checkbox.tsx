import { type InputHTMLAttributes, forwardRef } from "react";

import { cn } from "@/lib/cn";

interface CheckboxProps extends Omit<InputHTMLAttributes<HTMLInputElement>, "type"> {
  label: string;
  description?: string;
}

export const Checkbox = forwardRef<HTMLInputElement, CheckboxProps>(
  ({ className, label, description, id, ...props }, ref) => (
    <label
      htmlFor={id}
      className={cn(
        "flex cursor-pointer items-start gap-2.5 rounded border border-border bg-surface-raised px-3 py-2.5",
        "transition-colors hover:border-ink-muted",
        className
      )}
    >
      <input
        ref={ref}
        id={id}
        type="checkbox"
        className="mt-0.5 h-4 w-4 shrink-0 rounded-sm border-border bg-surface text-accent accent-accent focus:ring-accent/70"
        {...props}
      />
      <span className="flex flex-col">
        <span className="text-sm text-ink-primary">{label}</span>
        {description && <span className="text-2xs text-ink-muted">{description}</span>}
      </span>
    </label>
  )
);
Checkbox.displayName = "Checkbox";
