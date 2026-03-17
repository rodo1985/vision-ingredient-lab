import type { ImageRecord } from "../types/api";

interface SelectedIngredientsProps {
  items: ImageRecord[];
  onRemove: (imageId: string) => void;
}

export function SelectedIngredients({ items, onRemove }: SelectedIngredientsProps) {
  return (
    <section className="panel">
      <div className="panelHeader">
        <h2 className="panelTitle">Selected ingredients</h2>
        <span>{items.length} selected</span>
      </div>
      <ul className="selectionList">
        {items.map((item) => (
          <li className="selectionItem" key={item.id}>
            <span>{item.filename}</span>
            <button className="ghostButton" onClick={() => onRemove(item.id)} type="button">
              Remove
            </button>
          </li>
        ))}
      </ul>
    </section>
  );
}
