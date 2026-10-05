export default function Sparkline({
  points, width = 720, height = 160,
}: {
  points: { d: string; s: number }[]; width?: number; height?: number;
}) {
  if (points.length < 2) return null;
  const vals = points.map((p) => p.s);
  const min = Math.min(...vals), max = Math.max(...vals);
  const span = max - min || 1;
  const stepX = width / (points.length - 1);
  const coords = points.map((p, i) => [
    i * stepX,
    height - 8 - ((p.s - min) / span) * (height - 16),
  ]);
  const path = coords.map((c, i) => `${i ? "L" : "M"}${c[0].toFixed(1)},${c[1].toFixed(1)}`).join(" ");
  return (
    <svg viewBox={`0 0 ${width} ${height}`} width="100%" height={height}
      role="img" aria-label="star history" preserveAspectRatio="none">
      <path d={path} fill="none" stroke="#1e9e62" strokeWidth="2" />
      <text x={0} y={12} fill="#8a8578" fontSize="11" fontFamily="monospace">
        {max.toLocaleString()}
      </text>
      <text x={0} y={height - 2} fill="#8a8578" fontSize="11" fontFamily="monospace">
        {min.toLocaleString()}
      </text>
    </svg>
  );
}
