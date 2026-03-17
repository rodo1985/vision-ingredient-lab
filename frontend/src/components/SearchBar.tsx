interface SearchBarProps {
  value: string;
  onChange: (value: string) => void;
}

export function SearchBar({ value, onChange }: SearchBarProps) {
  return (
    <label className="panel">
      <span className="panelTitle">Search ingredients</span>
      <input
        className="textInput"
        type="text"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder="Search tomato, basil, mozzarella..."
      />
    </label>
  );
}
