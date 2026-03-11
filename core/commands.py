from abc import ABC, abstractmethod
from .types import Position
from .document import Document

class Command(ABC):
    """Abstract base class for all editor commands."""
    @abstractmethod
    def execute(self) -> None:
        """Apply the command."""
        pass

    @abstractmethod
    def undo(self) -> None:
        """Revert the command."""
        pass

class InsertTextCommand(Command):
    def __init__(self, document: Document, pos: Position, text: str):
        self.document = document
        self.pos = pos
        self.text = text
        self.end_pos = None # To be calculated during execution

    def execute(self) -> None:
        # TODO: Implement execution logic
        pass

    def undo(self) -> None:
        # TODO: Implement undo logic
        pass

class DeleteRangeCommand(Command):
    def __init__(self, document: Document, start: Position, end: Position):
        self.document = document
        self.start = start
        self.end = end
        self.deleted_text = "" # To be stored during execution

    def execute(self) -> None:
        # TODO: Implement execution logic
        pass

    def undo(self) -> None:
        # TODO: Implement undo logic
        pass

class UndoManager:
    def __init__(self):
        self.undo_stack: list[Command] = []
        self.redo_stack: list[Command] = []

    def execute(self, command: Command):
        """Executes a command and adds it to the undo stack."""
        # TODO: Implement
        pass

    def undo(self):
        """Undoes the last command."""
        # TODO: Implement
        pass

    def redo(self):
        """Redoes the last undone command."""
        # TODO: Implement
        pass
