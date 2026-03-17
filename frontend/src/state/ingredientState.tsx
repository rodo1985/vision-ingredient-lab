import { ReactNode, createContext, useContext, useReducer } from "react";

/** Supported lifecycle states for the creative image generation flow. */
export type GenerationStatus = "idle" | "loading" | "success" | "error";

/** Search result row adapted for frontend selection and rendering. */
export interface IngredientResult {
  id: string;
  name: string;
  description: string;
  keywords: string[];
}

/** Creative image payload returned after generation completes successfully. */
export interface GeneratedResult {
  prompt: string;
  imageUrl: string;
  metadata: {
    description?: string;
    keywords?: string[];
  };
}

/** Shared frontend state that powers search, selection, and generation. */
export interface IngredientState {
  query: string;
  results: IngredientResult[];
  selectedIds: string[];
  generationStatus: GenerationStatus;
  generatedResult: GeneratedResult | null;
}

export const initialIngredientState: IngredientState = {
  query: "",
  results: [],
  selectedIds: [],
  generationStatus: "idle",
  generatedResult: null,
};

/** Reducer actions that mutate the shared ingredient lab state. */
export type IngredientAction =
  | { type: "setQuery"; payload: string }
  | { type: "setResults"; payload: IngredientResult[] }
  | { type: "addIngredient"; payload: IngredientResult }
  | { type: "removeIngredient"; payload: string }
  | { type: "clearSelection" }
  | { type: "setGenerationStatus"; payload: GenerationStatus }
  | { type: "setGeneratedResult"; payload: GeneratedResult | null }
  | { type: "resetGeneratedResult" };

/**
 * Apply a single action to the shared ingredient lab state.
 *
 * Parameters:
 *   state: Current reducer state snapshot.
 *   action: State transition to apply.
 *
 * Returns:
 *   IngredientState: Updated reducer state after the action is applied.
 */
export function ingredientReducer(
  state: IngredientState,
  action: IngredientAction,
): IngredientState {
  switch (action.type) {
    case "setQuery":
      return { ...state, query: action.payload };
    case "setResults":
      return { ...state, results: [...action.payload] };
    case "addIngredient": {
      if (state.selectedIds.includes(action.payload.id)) {
        return state;
      }
      return { ...state, selectedIds: [...state.selectedIds, action.payload.id] };
    }
    case "removeIngredient":
      return {
        ...state,
        selectedIds: state.selectedIds.filter((id) => id !== action.payload),
      };
    case "clearSelection":
      return { ...state, selectedIds: [] };
    case "setGenerationStatus":
      return { ...state, generationStatus: action.payload };
    case "setGeneratedResult":
      return { ...state, generatedResult: action.payload };
    case "resetGeneratedResult":
      return { ...state, generatedResult: null };
    default:
      return state;
  }
}

const IngredientStateContext = createContext<IngredientState | undefined>(undefined);
const IngredientDispatchContext = createContext<
  React.Dispatch<IngredientAction> | undefined
>(undefined);

interface IngredientProviderProps {
  children: ReactNode;
}

/**
 * Provide shared ingredient lab state to the React component tree.
 *
 * Parameters:
 *   children: Nested React elements that consume shared state.
 *
 * Returns:
 *   JSX.Element: Context providers wrapping the provided children.
 */
export function IngredientProvider({ children }: IngredientProviderProps) {
  const [state, dispatch] = useReducer(ingredientReducer, initialIngredientState);
  return (
    <IngredientStateContext.Provider value={state}>
      <IngredientDispatchContext.Provider value={dispatch}>
        {children}
      </IngredientDispatchContext.Provider>
    </IngredientStateContext.Provider>
  );
}

/**
 * Read the current ingredient lab state from context.
 *
 * Returns:
 *   IngredientState: Shared state snapshot for the current render.
 *
 * Raises:
 *   Error: If the hook is used outside `IngredientProvider`.
 */
export function useIngredientState(): IngredientState {
  const context = useContext(IngredientStateContext);
  if (!context) {
    throw new Error("useIngredientState must be used within IngredientProvider");
  }
  return context;
}

/**
 * Read the shared ingredient lab dispatcher from context.
 *
 * Returns:
 *   React.Dispatch<IngredientAction>: Dispatch function for reducer actions.
 *
 * Raises:
 *   Error: If the hook is used outside `IngredientProvider`.
 */
export function useIngredientActions(): React.Dispatch<IngredientAction> {
  const context = useContext(IngredientDispatchContext);
  if (!context) {
    throw new Error("useIngredientActions must be used within IngredientProvider");
  }
  return context;
}
