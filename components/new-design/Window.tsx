export default function Window({
  title,
  id,
  className = "",
  children,
}: {
  title: string;
  id?: string;
  className?: string;
  children: React.ReactNode;
}) {
  return (
    <section id={id} className={`window ${className}`} aria-label={title}>
      <div className="window-title">
        <span className="window-box" aria-hidden="true" />
        <h2>{title}</h2>
      </div>
      <div className="window-body">{children}</div>
    </section>
  );
}
