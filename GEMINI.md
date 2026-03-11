# Text Editor Mandate (GEMINI.md)

This project follows a strict **Mediator Architecture**. All future development must adhere to these rules.

## 1. Architectural Layers

- **`core/`**: The "Brainless" Data Model. Must be GUI-agnostic (no imports from `tkinter` or `ui`).
  - `Document`: Handles raw text strings.
  - `EditorState`: Handles logical positions (Line/Col).
- **`ui/`**: The Visual Layer. Handles pixels and OS events.
  - `Renderer`: A "Dumb Painter" that only accepts raw coordinates and strings.
  - `LayoutManager`: The "Translator" between logical indexes and pixels.
  - `InputHandler`: Maps OS events to logical actions.
- **`services/`**: Infrastructure (Clipboard, File I/O).

## 2. The Mediator Rule

`EditorApp` (in `main.py`) is the **Mediator**.

- It is the ONLY class allowed to coordinate between the Model (`core`) and the View (`ui`).
- **Forbidden:** Never pass the `LayoutManager` into the `Renderer`. The Mediator must get the pixels from the Layout and pass them as raw numbers to the Renderer.

## 3. Data Flow

`User Input` -> `InputHandler` -> `EditorState/Document` -> `Mediator` -> `LayoutManager (Math)` -> `Renderer (Draw)`.

## 4. Coding Standards

- Methods starting with `_` are internal (e.g., `_clamp_scroll`).
- Use Type Hinting for all public methods.
- Favor Composition over Inheritance.

## 5. Implementation Roadmap

### Phase 2: Navigation (COMPLETED)

- [x] Basic typing and navigation (Arrows, Home, End).
- [x] Vertical scrolling with `ScrollManager`.
- [x] Cursor tracking (keep cursor in view).

### Phase 3: Selection & Clipboard (COMPLETED)

- [x] Mouse support (Click to place cursor, Drag to select).
- [x] Shift+Arrow selection.
- [x] Clipboard Service (Copy/Cut/Paste) integrated with `InputHandler`.

### Phase 4: Advanced Features

- [ ] Undo/Redo stack (Command pattern).
- [ ] Syntax Highlighting (using a separate service).
- [ ] Horizontal scrolling and line wrapping.
