export default function InlineSpark({
  values, width = 96, height = 28,
}: {
  values: number[]; width?: number; height?: number;
}) {
  if (!values || values.length < 2) return <span className="spark-empty">—</span>;
  const min = Math.min(...values), max = Math.max(...values);
  const span = max - min || 1;
  const stepX = width / (values.length - 1);
  const pts = values.map((v, i) => [
    i * stepX,
    height - 2 - ((v - min) / span) * (height - 4),
  ]);
  const path = pts.map((p, i) => `${i ? "L" : "M"}${p[0].toFixed(1)},${p[1].toFixed(1)}`).join(" ");
  const up = values[values.length - 1] >= values[0];
  const color = up ? "var(--up)" : "var(--down)";
  const area = `${path} L${width},${height} L0,${height} Z`;
  return (
    <svg viewBox={`0 0 ${width} ${height}`} width={width} height={height}
      aria-hidden="true" className="inline-spark">
      <path d={area} fill={color} opacity="0.12" stroke="none" />
      <path d={path} fill="none" stroke={color} strokeWidth="1.6"
        strokeLinejoin="round" strokeLinecap="round" />
    </svg>
  );
}
