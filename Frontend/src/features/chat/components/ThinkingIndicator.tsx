const DOT_DELAYS = ["0ms", "160ms", "320ms"];

export function ThinkingIndicator({ label }: { label?: string | null }) {
  return (
    <div className="flex justify-start">
      <div
        role="status"
        aria-label={label ?? "The assistant is thinking"}
        className="flex items-center gap-1.5"
      >
        <span aria-hidden="true" className="flex items-center gap-1 px-1 py-2">
          {DOT_DELAYS.map((delay) => (
            <span
              key={delay}
              className="thinkingDot h-1.5 w-1.5 rounded-full bg-ink-muted"
              style={{ animationDelay: delay }}
            />
          ))}
        </span>
        {label ? <span className="text-xs text-ink-muted">{label}…</span> : null}
      </div>
    </div>
  );
}
