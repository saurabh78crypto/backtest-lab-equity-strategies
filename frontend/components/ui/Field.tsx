import { type InputHTMLAttributes, type ReactNode, forwardRef } from "react";

import { cn } from "@/lib/cn";

interface FieldProps {
  label: string;
  htmlFor?: string;
  hint?: string;
  error?: string;
  required?: boolean;
  children: ReactNode;
  className?: string;
}

export function Field({ label, htmlFor, hint, error, required, children, className }: FieldProps) {
  return (
    <div className={cn("flex flex-col gap-1.5", className)}>
      <label htmlFor={htmlFor} className="text-xs font-medium text-ink-secondary">
        {label}
        {required && <span className="ml-0.5 text-accent">*</span>}
      </label>
      {children}
      {hint && !error && <p className="text-2xs text-ink-muted">{hint}</p>}
      {error && <p className="text-2xs text-negative">{error}</p>}
    </div>
  );
}

const baseInputClasses =
  "h-9 w-full rounded border border-border bg-surface-raised px-3 text-sm text-ink-primary placeholder:text-ink-muted " +
  "transition-colors focus:border-accent disabled:cursor-not-allowed disabled:opacity-50";

export const Input = forwardRef<HTMLInputElement, InputHTMLAttributes<HTMLInputElement>>(
  ({ className, ...props }, ref) => (
    <input ref={ref} className={cn(baseInputClasses, "font-mono", className)} {...props} />
  )
);
Input.displayName = "Input";

interface NumberInputProps extends Omit<InputHTMLAttributes<HTMLInputElement>, "onChange" | "value" | "type"> {
  value: number | null;
  onChange: (value: number | null) => void;
  prefix?: string;
  suffix?: string;
}

export const NumberInput = forwardRef<HTMLInputElement, NumberInputProps>(
  ({ className, value, onChange, prefix, suffix, ...props }, ref) => {
    return (
      <div className="relative flex items-center">
        {prefix && (
          <span className="pointer-events-none absolute left-3 text-sm text-ink-muted">{prefix}</span>
        )}
        <input
          ref={ref}
          type="number"
          inputMode="decimal"
          value={value === null || value === undefined ? "" : value}
          onChange={(e) => {
            const raw = e.target.value;
            onChange(raw === "" ? null : Number(raw));
          }}
          className={cn(baseInputClasses, "font-mono", prefix && "pl-7", suffix && "pr-9", className)}
          {...props}
        />
        {suffix && (
          <span className="pointer-events-none absolute right-3 text-sm text-ink-muted">{suffix}</span>
        )}
      </div>
    );
  }
);
NumberInput.displayName = "NumberInput";
