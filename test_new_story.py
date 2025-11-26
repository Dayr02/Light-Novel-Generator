#!/usr/bin/env python3
"""Unit test: ensure create_and_open_story loads the created story into Overview

This test avoids creating real UI windows by invoking the MainWindow method
as an unbound function on a lightweight stub object that provides the
attributes used by the method.
"""

from database.db_manager import DatabaseManager
from ui.main_window import MainWindow


def test_create_and_open_story_loads_overview():
    db_path = "data/test_lightnovel.db"
    db = DatabaseManager(db_path)

    class NotebookStub:
        def __init__(self):
            self.last_selected = None

        def select(self, idx):
            self.last_selected = idx

    class StubWindowContext:
        def __init__(self, db):
            self.db = db
            self.current_story_id = None
            self.load_story_data_called = False
            self.load_stories_called = False
            self.notebook = NotebookStub()

        def load_story_data(self, story_id):
            self.load_story_data_called = True

        def load_stories(self):
            self.load_stories_called = True

        def update_status(self, text):
            pass

    stub = StubWindowContext(db)

    title = "UnitTest Story"
    synopsis = "A test synopsis for unit testing."
    genre = "Test Genre"

    # Call the MainWindow.create_and_open_story as an unbound method
    story_id = MainWindow.create_and_open_story(stub, title, synopsis, genre, ask_ai=False)

    # Assertions
    assert story_id is not None and isinstance(story_id, int)
    assert stub.current_story_id == story_id
    assert stub.notebook.last_selected == 0
    assert stub.load_story_data_called is True

    # Cleanup
    try:
        db.delete_story(story_id)
    except Exception:
        pass
    db.close()


if __name__ == "__main__":
    test_create_and_open_story_loads_overview()
    print("test_create_and_open_story_loads_overview: PASS")
