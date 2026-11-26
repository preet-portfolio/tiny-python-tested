/** A small round gremlin. "caught" puts it behind bars; "free" makes it dance. */
export function Gremlin({ mood, className = "" }: { mood: "sneaky" | "caught" | "free"; className?: string }) {
  return (
    <svg viewBox="0 0 48 48" className={`gremlin g-${mood} ${className}`} aria-hidden="true" focusable="false">
      <g className="g-body">
        <path d="M10 14 L6 4 L16 11 Z M38 14 L42 4 L32 11 Z" className="g-ear" />
        <ellipse cx="24" cy="27" rx="16" ry="15" className="g-skin" />
        <circle cx="18" cy="24" r="4.5" className="g-eye" />
        <circle cx="30" cy="24" r="4.5" className="g-eye" />
        <circle cx={mood === "sneaky" ? 19.5 : 18} cy="25" r="2" className="g-pupil" />
        <circle cx={mood === "sneaky" ? 31.5 : 30} cy="25" r="2" className="g-pupil" />
        {mood === "caught" ? (
          <path d="M18 35 Q24 31 30 35" className="g-mouth" />
        ) : (
          <path d="M17 33 Q24 39 31 33" className="g-mouth" />
        )}
        {mood !== "caught" && <path d="M21 34.5 L22.5 37 L24 34.8 L25.5 37 L27 34.5" className="g-teeth" />}
      </g>
      {mood === "caught" && (
        <g className="g-bars">
          <path d="M8 4 V46 M16 4 V46 M24 4 V46 M32 4 V46 M40 4 V46" />
          <path d="M4 6 H44 M4 44 H44" />
        </g>
      )}
    </svg>
  );
}
