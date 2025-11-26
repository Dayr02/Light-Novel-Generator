import sqlite3
import json
from datetime import datetime
import os

class DatabaseManager:
    def __init__(self, db_path=None):
        # If no db_path given, locate project root (one level up from database package)
        if db_path is None:
            package_dir = os.path.dirname(os.path.abspath(__file__))           # .../project/database
            project_root = os.path.abspath(os.path.join(package_dir, ".."))    # .../project
            db_dir = os.path.join(project_root, "data")
            os.makedirs(db_dir, exist_ok=True)
            db_path = os.path.join(db_dir, "lightnovel.db")

        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        self.create_tables()
    
    def create_tables(self):
        """Create all necessary database tables"""
        cursor = self.conn.cursor()
        
        # Stories table - Main story projects
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                synopsis TEXT,
                genre TEXT,
                themes TEXT,
                tone TEXT,
                writing_style TEXT,
                target_length INTEGER,
                current_chapter INTEGER DEFAULT 0,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Characters table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS characters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                story_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                role TEXT NOT NULL,
                age INTEGER,
                gender TEXT,
                appearance TEXT,
                personality TEXT,
                background TEXT,
                abilities TEXT,
                motivations TEXT,
                relationships TEXT,
                character_arc TEXT,
                voice_style TEXT,
                quirks TEXT,
                combat_style TEXT,
                equipment TEXT,
                status TEXT DEFAULT 'alive',
                importance INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (story_id) REFERENCES stories(id) ON DELETE CASCADE
            )
        ''')
        
        # World structure table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS world_structure (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                story_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                description TEXT,
                geography TEXT,
                climate TEXT,
                population TEXT,
                government TEXT,
                economy TEXT,
                culture TEXT,
                history TEXT,
                notable_locations TEXT,
                relationships TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (story_id) REFERENCES stories(id) ON DELETE CASCADE
            )
        ''')
        
        # Magic/Power Systems table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS power_systems (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                story_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                rules TEXT,
                limitations TEXT,
                acquisition_method TEXT,
                power_levels TEXT,
                examples TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (story_id) REFERENCES stories(id) ON DELETE CASCADE
            )
        ''')
        
        # Lore/History table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lore (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                story_id INTEGER NOT NULL,
                category TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT,
                timeline_position TEXT,
                related_characters TEXT,
                related_locations TEXT,
                importance INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (story_id) REFERENCES stories(id) ON DELETE CASCADE
            )
        ''')
        
        # Organizations/Factions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS organizations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                story_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                type TEXT,
                description TEXT,
                goals TEXT,
                structure TEXT,
                members TEXT,
                resources TEXT,
                relationships TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (story_id) REFERENCES stories(id) ON DELETE CASCADE
            )
        ''')
        
        # Story progression tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS story_progression (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                story_id INTEGER NOT NULL,
                arc_name TEXT,
                arc_number INTEGER,
                current_plot_points TEXT,
                completed_plot_points TEXT,
                character_development TEXT,
                foreshadowing TEXT,
                unresolved_threads TEXT,
                next_major_events TEXT,
                pacing_notes TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (story_id) REFERENCES stories(id) ON DELETE CASCADE
            )
        ''')
        
        # Chapters table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chapters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                story_id INTEGER NOT NULL,
                chapter_number INTEGER NOT NULL,
                title TEXT,
                content TEXT,
                word_count INTEGER,
                summary TEXT,
                pov_character TEXT,
                location TEXT,
                time_period TEXT,
                key_events TEXT,
                characters_involved TEXT,
                plot_advancement TEXT,
                prompt_used TEXT,
                generation_params TEXT,
                status TEXT DEFAULT 'draft',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (story_id) REFERENCES stories(id) ON DELETE CASCADE,
                UNIQUE(story_id, chapter_number)
            )
        ''')
        
        # Generation templates
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS generation_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                story_id INTEGER NOT NULL,
                template_name TEXT NOT NULL,
                template_type TEXT,
                prompt_structure TEXT,
                include_elements TEXT,
                style_guidelines TEXT,
                temperature REAL DEFAULT 0.8,
                max_tokens INTEGER DEFAULT 4000,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (story_id) REFERENCES stories(id) ON DELETE CASCADE
            )
        ''')
        
        # World generation prompts/results
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS world_generation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                story_id INTEGER NOT NULL,
                prompt TEXT,
                result TEXT,
                elements_generated TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (story_id) REFERENCES stories(id) ON DELETE CASCADE
            )
        ''')
        
        self.conn.commit()
        print("Database tables created successfully!")

        # Story arcs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS story_arcs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                story_id INTEGER NOT NULL,
                arc_number INTEGER,
                arc_name TEXT,
                synopsis TEXT,
                start_chapter INTEGER,
                end_chapter INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(story_id) REFERENCES stories(id) ON DELETE CASCADE
            )
        ''')

        # Arc progression table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS arc_progression (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                story_id INTEGER NOT NULL,
                arc_id INTEGER NOT NULL,
                progression_data TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(story_id) REFERENCES stories(id) ON DELETE CASCADE,
                FOREIGN KEY(arc_id) REFERENCES story_arcs(id) ON DELETE CASCADE
            )
        ''')
        
        # Media table for storing file paths and metadata for images and other assets
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS media (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                story_id INTEGER NOT NULL,
                entity_type TEXT NOT NULL,
                entity_id INTEGER,
                file_path TEXT NOT NULL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(story_id) REFERENCES stories(id) ON DELETE CASCADE
            )
        ''')
        self.conn.commit()
        # ============== ARC OPERATIONS ==============
        # ============== ARC OPERATIONS ==============
    
    # ============== STORY OPERATIONS ==============
    
    def create_story(self, title, synopsis="", genre="Light Novel", 
                     themes="", tone="", writing_style="ReZero/Fate-inspired",
                     target_length: int | None = None):
        """Create a new story project"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO stories (title, synopsis, genre, themes, tone, writing_style, target_length)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (title, synopsis, genre, themes, tone, writing_style, target_length))
        self.conn.commit()
        return cursor.lastrowid

    # ============== ARC OPERATIONS ==============

    def add_arc(self, story_id, arc_number, arc_name, synopsis="", start_chapter=None, end_chapter=None):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO story_arcs (story_id, arc_number, arc_name, synopsis, start_chapter, end_chapter)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (story_id, arc_number, arc_name, synopsis, start_chapter, end_chapter))
        self.conn.commit()
        return cursor.lastrowid

    def get_arcs(self, story_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM story_arcs WHERE story_id = ? ORDER BY arc_number ASC
        ''', (story_id,))
        return [dict(row) for row in cursor.fetchall()]

    def get_arcs_with_progression(self, story_id):
        arcs = self.get_arcs(story_id)
        for arc in arcs:
            arc['progression'] = self.get_arc_progression(story_id, arc['id'])
        return arcs

    def update_arc(self, arc_id, **kwargs):
        cursor = self.conn.cursor()
        fields = ', '.join([f"{k} = ?" for k in kwargs.keys()])
        values = list(kwargs.values())
        values.append(arc_id)
        cursor.execute(f"""
            UPDATE story_arcs SET {fields} WHERE id = ?
        """, values)
        self.conn.commit()

    def delete_arc(self, arc_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            DELETE FROM story_arcs WHERE id = ?
        ''', (arc_id,))
        self.conn.commit()

    # ============== ARC PROGRESSION OPERATIONS ==============

    def save_arc_progression(self, story_id, arc_id, progression_data):
        cursor = self.conn.cursor()
        # Use INSERT OR REPLACE by key: we'll store unique by story_id+arc_id
        cursor.execute('''
            SELECT id FROM arc_progression WHERE story_id = ? AND arc_id = ?
        ''', (story_id, arc_id))
        existing = cursor.fetchone()
        if existing:
            cursor.execute('''
                UPDATE arc_progression SET progression_data = ?, last_updated = CURRENT_TIMESTAMP
                WHERE story_id = ? AND arc_id = ?
            ''', (progression_data, story_id, arc_id))
        else:
            cursor.execute('''
                INSERT INTO arc_progression (story_id, arc_id, progression_data, last_updated)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ''', (story_id, arc_id, progression_data))
        self.conn.commit()

    def get_arc_progression(self, story_id, arc_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT progression_data FROM arc_progression WHERE story_id = ? AND arc_id = ?
        ''', (story_id, arc_id))
        result = cursor.fetchone()
        return result[0] if result else None
    
    def get_arcs_with_progression(self, story_id):
        arcs = self.get_arcs(story_id)
        for arc in arcs:
            arc['progression'] = self.get_arc_progression(story_id, arc['id'])
        return arcs

    def update_arc_progression(self, story_id, arc_id, progression_data):
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE arc_progression SET progression_data = ?, last_updated = CURRENT_TIMESTAMP
            WHERE story_id = ? AND arc_id = ?
        ''', (progression_data, story_id, arc_id))
        self.conn.commit()

    def delete_arc_progression(self, story_id, arc_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            DELETE FROM arc_progression WHERE story_id = ? AND arc_id = ?
        ''', (story_id, arc_id))
        self.conn.commit()

    # ============== MEDIA OPERATIONS ==============
    def add_media(self, story_id, entity_type, entity_id, file_path, metadata=None):
        """Add a media reference (image/file) linked to a story/entity."""
        cursor = self.conn.cursor()
        # Ensure media folder exists inside data directory next to DB
        try:
            db_dir = os.path.dirname(os.path.abspath(self.db_path))
            media_dir = os.path.join(db_dir, 'media')
            os.makedirs(media_dir, exist_ok=True)

            # If the file is already in the media dir and exists, just store relative path
            abs_path = os.path.abspath(file_path)
            if os.path.commonpath([abs_path, media_dir]) == media_dir and os.path.exists(abs_path):
                rel_path = os.path.relpath(abs_path, db_dir)
            else:
                # Copy file into media_dir using a unique name
                base = os.path.basename(file_path)
                name, ext = os.path.splitext(base)
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                safe_name = f"{name}_{timestamp}{ext}"
                dest = os.path.join(media_dir, safe_name)
                try:
                    import shutil
                    shutil.copy2(file_path, dest)
                    rel_path = os.path.relpath(dest, db_dir)
                except Exception:
                    # Fallback: store the original path
                    rel_path = file_path
        except Exception:
            rel_path = file_path

        cursor.execute('''
            INSERT INTO media (story_id, entity_type, entity_id, file_path, metadata)
            VALUES (?, ?, ?, ?, ?)
        ''', (story_id, entity_type, entity_id, rel_path, json.dumps(metadata) if metadata else None))
        self.conn.commit()
        return cursor.lastrowid

    def get_media_for(self, story_id, entity_type=None, entity_id=None):
        """Return a list of media rows for a story, optionally filtered by entity type/id."""
        cursor = self.conn.cursor()
        if entity_type and entity_id is not None:
            cursor.execute('''SELECT * FROM media WHERE story_id = ? AND entity_type = ? AND entity_id = ? ORDER BY created_at DESC''', (story_id, entity_type, entity_id))
        elif entity_type:
            cursor.execute('''SELECT * FROM media WHERE story_id = ? AND entity_type = ? ORDER BY created_at DESC''', (story_id, entity_type))
        else:
            cursor.execute('''SELECT * FROM media WHERE story_id = ? ORDER BY created_at DESC''', (story_id,))
        return [dict(row) for row in cursor.fetchall()]

    def delete_media(self, media_id):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM media WHERE id = ?', (media_id,))
        self.conn.commit()
    
    def get_story(self, story_id):
        """Get story details"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM stories WHERE id = ?', (story_id,))
        return dict(cursor.fetchone())
    
    def get_all_stories(self):
        """Get all story projects"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM stories ORDER BY updated_at DESC')
        return [dict(row) for row in cursor.fetchall()]
    
    def update_story(self, story_id, **kwargs):
        """Update story details"""
        cursor = self.conn.cursor()
        
        # Build dynamic update query
        fields = ', '.join([f"{key} = ?" for key in kwargs.keys()])
        values = list(kwargs.values())
        values.append(datetime.now())
        values.append(story_id)
        
        query = f'UPDATE stories SET {fields}, updated_at = ? WHERE id = ?'
        cursor.execute(query, values)
        self.conn.commit()
    
    def delete_story(self, story_id):
        """Delete a story and all related data"""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM stories WHERE id = ?', (story_id,))
        self.conn.commit()
    
    # ============== CHARACTER OPERATIONS ==============
    
    def add_character(self, story_id, name, role, **kwargs):
        """Add a character to a story"""
        cursor = self.conn.cursor()
        
        # Default values for character attributes
        defaults = {
            'age': None,
            'gender': '',
            'appearance': '',
            'personality': '',
            'background': '',
            'abilities': '',
            'motivations': '',
            'relationships': '',
            'character_arc': '',
            'voice_style': '',
            'quirks': '',
            'combat_style': '',
            'equipment': '',
            'status': 'alive',
            'importance': 1
        }
        
        # Merge with provided kwargs
        defaults.update(kwargs)
        
        cursor.execute('''
            INSERT INTO characters (
                story_id, name, role, age, gender, appearance, personality,
                background, abilities, motivations, relationships, character_arc,
                voice_style, quirks, combat_style, equipment, status, importance
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            story_id, name, role, defaults['age'], defaults['gender'],
            defaults['appearance'], defaults['personality'], defaults['background'],
            defaults['abilities'], defaults['motivations'], defaults['relationships'],
            defaults['character_arc'], defaults['voice_style'], defaults['quirks'],
            defaults['combat_style'], defaults['equipment'], defaults['status'],
            defaults['importance']
        ))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_characters(self, story_id, role=None):
        """Get all characters for a story, optionally filtered by role"""
        cursor = self.conn.cursor()
        if role:
            cursor.execute('''
                SELECT * FROM characters 
                WHERE story_id = ? AND role = ?
                ORDER BY importance DESC, name
            ''', (story_id, role))
        else:
            cursor.execute('''
                SELECT * FROM characters 
                WHERE story_id = ?
                ORDER BY importance DESC, name
            ''', (story_id,))
        return [dict(row) for row in cursor.fetchall()]
    
    def get_character(self, character_id):
        """Get specific character details"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM characters WHERE id = ?', (character_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def update_character(self, character_id, **kwargs):
        """Update character details"""
        cursor = self.conn.cursor()
        fields = ', '.join([f"{key} = ?" for key in kwargs.keys()])
        values = list(kwargs.values())
        values.append(character_id)
        
        query = f'UPDATE characters SET {fields} WHERE id = ?'
        cursor.execute(query, values)
        self.conn.commit()
    
    def delete_character(self, character_id):
        """Delete a character"""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM characters WHERE id = ?', (character_id,))
        self.conn.commit()
    
    # ============== WORLD STRUCTURE OPERATIONS ==============
    
    def add_world_location(self, story_id, name, location_type, **kwargs):
        """Add a location/region to the world"""
        cursor = self.conn.cursor()
        
        defaults = {
            'description': '',
            'geography': '',
            'climate': '',
            'population': '',
            'government': '',
            'economy': '',
            'culture': '',
            'history': '',
            'notable_locations': '',
            'relationships': ''
        }
        defaults.update(kwargs)
        
        cursor.execute('''
            INSERT INTO world_structure (
                story_id, name, type, description, geography, climate,
                population, government, economy, culture, history,
                notable_locations, relationships
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            story_id, name, location_type, defaults['description'],
            defaults['geography'], defaults['climate'], defaults['population'],
            defaults['government'], defaults['economy'], defaults['culture'],
            defaults['history'], defaults['notable_locations'], defaults['relationships']
        ))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_world_locations(self, story_id, location_type=None):
        """Get world locations for a story"""
        cursor = self.conn.cursor()
        if location_type:
            cursor.execute('''
                SELECT * FROM world_structure 
                WHERE story_id = ? AND type = ?
                ORDER BY name
            ''', (story_id, location_type))
        else:
            cursor.execute('''
                SELECT * FROM world_structure 
                WHERE story_id = ?
                ORDER BY name
            ''', (story_id,))
        return [dict(row) for row in cursor.fetchall()]
    
    def update_world_location(self, location_id, **kwargs):
        """Update world location details"""
        cursor = self.conn.cursor()
        fields = ', '.join([f"{key} = ?" for key in kwargs.keys()])
        values = list(kwargs.values())
        values.append(location_id)
        
        query = f'UPDATE world_structure SET {fields} WHERE id = ?'
        cursor.execute(query, values)
        self.conn.commit()
    
    # ============== POWER SYSTEM OPERATIONS ==============
    
    def add_power_system(self, story_id, name, description, rules, **kwargs):
        """Add a magic/power system"""
        cursor = self.conn.cursor()
        
        defaults = {
            'limitations': '',
            'acquisition_method': '',
            'power_levels': '',
            'examples': ''
        }
        defaults.update(kwargs)
        
        cursor.execute('''
            INSERT INTO power_systems (
                story_id, name, description, rules, limitations,
                acquisition_method, power_levels, examples
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            story_id, name, description, rules, defaults['limitations'],
            defaults['acquisition_method'], defaults['power_levels'], defaults['examples']
        ))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_power_systems(self, story_id):
        """Get all power systems for a story"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM power_systems WHERE story_id = ?', (story_id,))
        return [dict(row) for row in cursor.fetchall()]
    
    # ============== LORE OPERATIONS ==============
    
    def add_lore(self, story_id, category, title, content, **kwargs):
        """Add lore entry"""
        cursor = self.conn.cursor()
        
        defaults = {
            'timeline_position': '',
            'related_characters': '',
            'related_locations': '',
            'importance': 1
        }
        defaults.update(kwargs)
        
        cursor.execute('''
            INSERT INTO lore (
                story_id, category, title, content, timeline_position,
                related_characters, related_locations, importance
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            story_id, category, title, content, defaults['timeline_position'],
            defaults['related_characters'], defaults['related_locations'],
            defaults['importance']
        ))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_lore(self, story_id, category=None):
        """Get lore entries for a story"""
        cursor = self.conn.cursor()
        if category:
            cursor.execute('''
                SELECT * FROM lore 
                WHERE story_id = ? AND category = ?
                ORDER BY importance DESC, title
            ''', (story_id, category))
        else:
            cursor.execute('''
                SELECT * FROM lore 
                WHERE story_id = ?
                ORDER BY category, importance DESC, title
            ''', (story_id,))
        return [dict(row) for row in cursor.fetchall()]
    
    # ============== CHAPTER OPERATIONS ==============
    
    def save_chapter(self, story_id, chapter_number, content, **kwargs):
        """Save a generated chapter"""
        cursor = self.conn.cursor()
        
        word_count = len(content.split())
        
        defaults = {
            'title': f"Chapter {chapter_number}",
            'summary': '',
            'pov_character': '',
            'location': '',
            'time_period': '',
            'key_events': '',
            'characters_involved': '',
            'plot_advancement': '',
            'prompt_used': '',
            'generation_params': '',
            'status': 'draft'
        }
        defaults.update(kwargs)
        
        # Check if chapter exists
        cursor.execute('''
            SELECT id FROM chapters 
            WHERE story_id = ? AND chapter_number = ?
        ''', (story_id, chapter_number))
        
        existing = cursor.fetchone()
        
        if existing:
            # Update existing chapter
            cursor.execute('''
                UPDATE chapters SET
                    title = ?, content = ?, word_count = ?, summary = ?,
                    pov_character = ?, location = ?, time_period = ?,
                    key_events = ?, characters_involved = ?, plot_advancement = ?,
                    prompt_used = ?, generation_params = ?, status = ?,
                    updated_at = ?
                WHERE id = ?
            ''', (
                defaults['title'], content, word_count, defaults['summary'],
                defaults['pov_character'], defaults['location'], defaults['time_period'],
                defaults['key_events'], defaults['characters_involved'],
                defaults['plot_advancement'], defaults['prompt_used'],
                defaults['generation_params'], defaults['status'],
                datetime.now(), existing[0]
            ))
        else:
            # Insert new chapter
            cursor.execute('''
                INSERT INTO chapters (
                    story_id, chapter_number, title, content, word_count,
                    summary, pov_character, location, time_period, key_events,
                    characters_involved, plot_advancement, prompt_used,
                    generation_params, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                story_id, chapter_number, defaults['title'], content, word_count,
                defaults['summary'], defaults['pov_character'], defaults['location'],
                defaults['time_period'], defaults['key_events'],
                defaults['characters_involved'], defaults['plot_advancement'],
                defaults['prompt_used'], defaults['generation_params'], defaults['status']
            ))
        
        # Update story's current chapter
        cursor.execute('''
            UPDATE stories 
            SET current_chapter = MAX(current_chapter, ?), updated_at = ?
            WHERE id = ?
        ''', (chapter_number, datetime.now(), story_id))
        
        self.conn.commit()
        return cursor.lastrowid if not existing else existing[0]
    
    def get_chapter(self, story_id, chapter_number):
        """Get a specific chapter"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM chapters 
            WHERE story_id = ? AND chapter_number = ?
        ''', (story_id, chapter_number))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_all_chapters(self, story_id):
        """Get all chapters for a story"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM chapters 
            WHERE story_id = ?
            ORDER BY chapter_number
        ''', (story_id,))
        return [dict(row) for row in cursor.fetchall()]
    
    def delete_chapter(self, chapter_id):
        """Delete a chapter"""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM chapters WHERE id = ?', (chapter_id,))
        self.conn.commit()
    
    # ============== STORY PROGRESSION OPERATIONS ==============
    
    def update_progression(self, story_id, **kwargs):
        """Update story progression tracking"""
        cursor = self.conn.cursor()
        
        # Check if progression exists
        cursor.execute('SELECT id FROM story_progression WHERE story_id = ?', (story_id,))
        existing = cursor.fetchone()
        
        if existing:
            fields = ', '.join([f"{key} = ?" for key in kwargs.keys()])
            values = list(kwargs.values())
            values.append(datetime.now())
            values.append(existing[0])
            
            query = f'UPDATE story_progression SET {fields}, updated_at = ? WHERE id = ?'
            cursor.execute(query, values)
        else:
            # Create new progression entry
            fields = ', '.join(kwargs.keys())
            placeholders = ', '.join(['?' for _ in kwargs])
            values = list(kwargs.values())
            
            query = f'''
                INSERT INTO story_progression (story_id, {fields})
                VALUES (?, {placeholders})
            '''
            cursor.execute(query, [story_id] + values)
        
        self.conn.commit()
    
    def get_progression(self, story_id):
        """Get story progression data"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM story_progression WHERE story_id = ?', (story_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    # ============== WORLD GENERATION HISTORY ==============
    
    def save_world_generation(self, story_id, prompt, result, elements_generated):
        """Save world generation history"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO world_generation_history (
                story_id, prompt, result, elements_generated
            ) VALUES (?, ?, ?, ?)
        ''', (story_id, prompt, result, json.dumps(elements_generated)))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_world_generation_history(self, story_id):
        """Get world generation history"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM world_generation_history 
            WHERE story_id = ?
            ORDER BY created_at DESC
        ''', (story_id,))
        return [dict(row) for row in cursor.fetchall()]
    
    def close(self):
        """Close database connection"""
        self.conn.close()
    