from database.db_manager import DatabaseManager

def test_database():
    print("Testing database...")
    
    # Initialize database
    db = DatabaseManager()
    
    # Create a test story
    story_id = db.create_story(
        title="Test Light Novel",
        synopsis="A test story for database verification",
        genre="Fantasy",
        themes="Adventure, Mystery",
        tone="Dark but hopeful",
        writing_style="ReZero-inspired"
    )
    print(f"✓ Created story with ID: {story_id}")
    
    # Add a test character
    char_id = db.add_character(
        story_id=story_id,
        name="Subaru Takahashi",
        role="Protagonist",
        age=17,
        personality="Determined, occasionally reckless",
        abilities="Time loop resurrection"
    )
    print(f"✓ Created character with ID: {char_id}")
    
    # Add a test location
    loc_id = db.add_world_location(
        story_id=story_id,
        name="Lugnica Kingdom",
        location_type="Nation",
        description="A medieval fantasy kingdom with magic"
    )
    print(f"✓ Created location with ID: {loc_id}")
    
    # Retrieve and display
    story = db.get_story(story_id)
    print(f"\n✓ Retrieved story: {story['title']}")
    
    characters = db.get_characters(story_id)
    print(f"✓ Retrieved {len(characters)} character(s)")
    
    locations = db.get_world_locations(story_id)
    print(f"✓ Retrieved {len(locations)} location(s)")
    
    print("\n✅ Database test completed successfully!")
    
    db.close()

if __name__ == "__main__":
    test_database()