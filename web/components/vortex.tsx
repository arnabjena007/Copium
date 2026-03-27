type VortexProps = {
  className?: string;
};

export function Vortex({ className = "" }: VortexProps) {
  return (
    <div className={`vortex-shell ${className}`.trim()}>
      <div className="vortex-ring vortex-ring-a" />
      <div className="vortex-ring vortex-ring-b" />
      <div className="vortex-ring vortex-ring-c" />
      <div className="vortex-grid" />
    </div>
  );
}
