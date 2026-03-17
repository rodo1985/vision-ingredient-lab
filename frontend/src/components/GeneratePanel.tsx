interface GeneratePanelProps {
  creativeDirection: string;
  disabled: boolean;
  loading: boolean;
  onChange: (value: string) => void;
  onGenerate: () => void;
}

export function GeneratePanel({
  creativeDirection,
  disabled,
  loading,
  onChange,
  onGenerate,
}: GeneratePanelProps) {
  return (
    <section className="panel">
      <h2 className="panelTitle">Generate composition</h2>
      <textarea
        className="textArea"
        value={creativeDirection}
        onChange={(event) => onChange(event.target.value)}
        placeholder="Optional creative direction..."
      />
      <button className="primaryButton" disabled={disabled || loading} onClick={onGenerate} type="button">
        {loading ? "Generating..." : "Generate image"}
      </button>
    </section>
  );
}
