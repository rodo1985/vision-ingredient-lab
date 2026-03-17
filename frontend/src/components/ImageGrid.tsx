import type { SearchResult } from "../types/api";

interface ImageGridProps {
  items: SearchResult[];
  selectedIds: string[];
  onToggle: (imageId: string) => void;
}

export function ImageGrid({ items, selectedIds, onToggle }: ImageGridProps) {
  return (
    <section className="panel">
      <div className="panelHeader">
        <h2 className="panelTitle">Matches</h2>
        <span>{items.length} result(s)</span>
      </div>
      <div className="grid">
        {items.map((item) => {
          const selected = selectedIds.includes(item.image.id);
          return (
            <button
              key={item.image.id}
              className={`card ${selected ? "selected" : ""}`}
              onClick={() => onToggle(item.image.id)}
              type="button"
            >
              <img alt={item.image.filename} className="cardImage" src={item.image.imageUrl} />
              <div className="cardBody">
                <strong>{item.image.filename}</strong>
                <p>{item.image.description}</p>
                <div className="tagList">
                  {item.image.tags.map((tag) => (
                    <span className="tag" key={tag}>
                      {tag}
                    </span>
                  ))}
                </div>
                <small>Reasons: {item.matchReasons.join(", ") || "none"}</small>
              </div>
            </button>
          );
        })}
      </div>
    </section>
  );
}
