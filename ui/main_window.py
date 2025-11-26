import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import os
from datetime import datetime
from database.db_manager import DatabaseManager
from ai.ollama_client import OllamaClient
from ai.world_generator import WorldGenerator
from ui.theme_manager import ThemeManager

class MainWindow:
    """Main application window with theme support"""
    
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Light Novel Story Generator - ReZero/Fate Style")
        self.window.geometry("1500x900")
        
        style = ttk.Style(self.window)
        try:
            style.theme_use('clam')  # 'clam' or 'alt' often looks cleaner
        except Exception:
            pass

        # Configure global fonts and padding
        default_font = ('Segoe UI', 10)  # or 'Arial' depending on platform
        self.window.option_add("*Font", default_font)
        style.configure('TButton', padding=(8,6), relief='flat', background='#2b7cff', foreground='white')
        style.map('TButton',
                background=[('active', '#1155cc')],
                foreground=[('disabled', 'gray')])
        # Notebook tab padding
        style.configure('TNotebook.Tab', padding=[12, 8])

        # Initialize theme manager
        self.theme_manager = ThemeManager()
        
        # Initialize backends
        self.db = DatabaseManager()
        self.ai = OllamaClient()
        self.world_gen = WorldGenerator(self.db, self.ai)
        
        # Current story selection
        self.current_story_id = None
        self.current_character_id = None
        self.current_location_id = None
        
        # Check AI connection
        if not self.ai.test_connection():
            messagebox.showwarning(
                "AI Not Connected",
                "Cannot connect to Ollama. Make sure it's running.\n"
                "Generation features will not work until connected.\n\n"
                "Run: ollama serve"
            )
        
        self.setup_ui()
        self.apply_theme()
        self.load_stories()
    
    def setup_ui(self):
        """Setup the main UI layout"""
        
        # Create menu bar
        self.create_menu_bar()
        
        # Main container
        self.main_container = ttk.Frame(self.window)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create toolbar
        self.create_toolbar()
        
        # Create main content area
        content_container = ttk.PanedWindow(self.main_container, orient=tk.HORIZONTAL)
        content_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left sidebar - Story selection
        self.create_sidebar(content_container)
        
        # Right side - Main content with tabs
        self.create_main_content(content_container)
        
        # Status bar at bottom
        self.create_status_bar()
    
    def create_menu_bar(self):
        """Create application menu bar"""
        menubar = tk.Menu(self.window)
        self.window.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="📁 File", menu=file_menu)
        file_menu.add_command(label="New Story", command=self.new_story, accelerator="Ctrl+N")
        file_menu.add_command(label="Open Story", command=self.select_story, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Save All", command=self.save_all, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Export Chapter", command=self.export_chapter)
        file_menu.add_command(label="Export All Chapters", command=self.export_all_chapters)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.window.quit, accelerator="Alt+F4")
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="✏️ Edit", menu=edit_menu)
        edit_menu.add_command(label="Add Character", command=self.add_character)
        edit_menu.add_command(label="Add Location", command=self.add_location)
        edit_menu.add_command(label="Add Power System", command=self.add_power_system)
        edit_menu.add_command(label="Add Lore Entry", command=self.add_lore)
        
        # Generate menu
        generate_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="🎨 Generate", menu=generate_menu)
        generate_menu.add_command(label="Generate Chapter", command=self.go_to_chapter_generator)
        generate_menu.add_command(label="Generate World from Synopsis", command=self.generate_from_synopsis)
        generate_menu.add_separator()
        generate_menu.add_command(label="AI Expand Location", command=self.ai_generate_location)
        generate_menu.add_command(label="AI Generate Power System", command=self.ai_generate_power_system)
        generate_menu.add_command(label="AI Generate Lore", command=self.ai_generate_lore)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="👁️ View", menu=view_menu)
        view_menu.add_command(label="Overview", command=lambda: self.select_tab_by_text('Overview'))
        view_menu.add_command(label="Characters", command=lambda: self.select_tab_by_text('Characters'))
        view_menu.add_command(label="World", command=lambda: self.select_tab_by_text('World'))
        view_menu.add_command(label="Bestiary", command=lambda: self.select_tab_by_text('Bestiary'))
        view_menu.add_command(label="Lore & Powers", command=lambda: self.select_tab_by_text('Lore'))
        view_menu.add_command(label="Progression", command=lambda: self.select_tab_by_text('Progression'))
        view_menu.add_command(label="Generate Chapter", command=lambda: self.select_tab_by_text('Generate'))
        view_menu.add_command(label="Chapters List", command=lambda: self.select_tab_by_text('Chapters'))
        
        # Theme menu
        theme_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="🎨 Theme", menu=theme_menu)
        theme_menu.add_command(label="Light Mode", command=lambda: self.set_theme('light'))
        theme_menu.add_command(label="Dark Mode", command=lambda: self.set_theme('dark'))
        theme_menu.add_separator()
        theme_menu.add_command(label="Toggle Theme", command=self.toggle_theme, accelerator="Ctrl+T")
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="🔧 Tools", menu=tools_menu)
        tools_menu.add_command(label="Test AI Connection", command=self.test_ai)
        tools_menu.add_command(label="Database Statistics", command=self.show_db_info)
        tools_menu.add_separator()
        tools_menu.add_command(label="Backup Database", command=self.backup_database)
        tools_menu.add_command(label="Settings", command=self.show_settings)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="❓ Help", menu=help_menu)
        help_menu.add_command(label="Quick Start Guide", command=self.show_quick_start)
        help_menu.add_command(label="Keyboard Shortcuts", command=self.show_shortcuts)
        help_menu.add_separator()
        help_menu.add_command(label="About", command=self.show_about)
        
        # Bind keyboard shortcuts
        self.window.bind('<Control-n>', lambda e: self.new_story())
        self.window.bind('<Control-o>', lambda e: self.select_story())
        self.window.bind('<Control-s>', lambda e: self.save_all())
        self.window.bind('<Control-t>', lambda e: self.toggle_theme())
    
    def create_toolbar(self):
        """Create quick access toolbar"""
        toolbar = ttk.Frame(self.main_container)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        # Quick action buttons
        ttk.Button(
            toolbar,
            text="📝 New Story",
            command=self.new_story,
            width=15
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            toolbar,
            text="👤 Add Character",
            command=self.add_character,
            width=15
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            toolbar,
            text="🌍 Add Location",
            command=self.add_location,
            width=15
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            toolbar,
            text="🎨 Generate Chapter",
            command=self.go_to_chapter_generator,
            width=18
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=5)
        
        ttk.Button(
            toolbar,
            text="💾 Save All",
            command=self.save_all,
            width=12
        ).pack(side=tk.LEFT, padx=2)
        
        # Theme toggle on right
        ttk.Button(
            toolbar,
            text="🌓 Toggle Theme",
            command=self.toggle_theme,
            width=15
        ).pack(side=tk.RIGHT, padx=2)

        # Accent color picker
        try:
            import tkinter.colorchooser as colorchooser
            def pick_accent():
                color = colorchooser.askcolor(title='Choose Accent Color')
                if color and color[1]:
                    # Update current theme accent and reapply
                    try:
                        cur = self.theme_manager.current_theme
                        self.theme_manager.themes[cur]['accent'] = color[1]
                        self.theme_manager.themes[cur]['accent_light'] = color[1]
                        self.apply_theme()
                        self.update_status('Accent color updated')
                    except Exception:
                        pass
            ttk.Button(toolbar, text='🎨 Accent', command=pick_accent, width=12).pack(side=tk.RIGHT, padx=6)
        except Exception:
            pass

    def go_to_chapter_generator(self):
        """Navigate to the Chapter Generator tab (safe, with fallbacks)."""
        try:
            # Try to find a tab whose text mentions 'Generate' or 'Chapter'
            if hasattr(self, 'notebook'):
                try:
                    end = self.notebook.index('end')
                except Exception:
                    end = None
                if end is not None:
                    for i in range(end):
                        try:
                            text = str(self.notebook.tab(i, 'text') or '')
                        except Exception:
                            text = ''
                        if 'Generate' in text or 'Chapter' in text:
                            self.notebook.select(i)
                            return

            # Fallback: create the chapter generator tab if it doesn't exist
            if hasattr(self, 'create_chapter_generator_tab'):
                self.create_chapter_generator_tab()
                # select the last tab
                try:
                    self.notebook.select(self.notebook.index('end') - 1)
                    return
                except Exception:
                    pass

        except Exception as e:
            # Final fallback: show an error to the user
            try:
                messagebox.showerror('Navigation Error', f'Could not open Chapter Generator: {e}')
            except Exception:
                print('Could not open Chapter Generator:', e)

    def generate_from_synopsis(self):
        """Generate world details using the current story's synopsis.

        If no story is selected or synopsis is empty, prompt the user for input.
        Uses `WorldGenerator.generate_from_synopsis` and displays a brief result.
        """
        try:
            if not self.current_story_id:
                messagebox.showwarning('No Story Selected', 'Please select or create a story first.')
                return

            story = self.db.get_story(self.current_story_id)
            if not story:
                messagebox.showerror('Story Not Found', 'Selected story could not be loaded from the database.')
                return

            synopsis = story.get('synopsis') or ''
            genre = story.get('genre') or ''

            if not synopsis:
                # Ask the user to paste/enter a synopsis
                synopsis = simpledialog.askstring('Synopsis Required', 'Enter a short synopsis to generate world details:')
                if not synopsis:
                    return

            if not genre:
                genre = simpledialog.askstring('Genre (optional)', 'Enter genre (optional):', initialvalue='Light Novel') or 'Light Novel'

            # Inform user that generation may take some time
            messagebox.showinfo('Generating', 'World generation will start. This may take a minute.')

            result = self.world_gen.generate_from_synopsis(self.current_story_id, synopsis, genre)

            # Show a short summary of the result to the user
            raw = result.get('raw_result') if isinstance(result, dict) else str(result)
            preview = raw
            if isinstance(preview, str) and len(preview) > 2000:
                preview = preview[:2000] + '\n\n...[truncated]'

            # Use a simple Toplevel to show the long text so messagebox isn't truncated
            dlg = tk.Toplevel(self.window)
            dlg.title('World Generation Result')
            dlg.geometry('800x600')
            txt = tk.Text(dlg, wrap=tk.WORD)
            txt.insert('1.0', preview)
            txt.config(state=tk.DISABLED)
            txt.pack(fill=tk.BOTH, expand=True)

        except Exception as e:
            messagebox.showerror('Generation Error', f'World generation failed: {e}')
    
    def create_sidebar(self, parent):
        """Create left sidebar with story list"""
        sidebar = ttk.Frame(parent, width=280)
        parent.add(sidebar, weight=0)
        
        # Header
        header_frame = ttk.Frame(sidebar)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(
            header_frame,
            text="📚 My Stories",
            font=('Arial', 14, 'bold')
        ).pack(side=tk.LEFT)
        
        # New story button
        ttk.Button(
            sidebar,
            text="➕ Create New Story",
            command=self.new_story
        ).pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Search box
        search_frame = ttk.Frame(sidebar)
        search_frame.pack(fill=tk.X, padx=10, pady=(0, 5))
        
        ttk.Label(search_frame, text="🔍").pack(side=tk.LEFT)
        self.story_search = ttk.Entry(search_frame)
        self.story_search.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        self.story_search.bind('<KeyRelease>', self.filter_stories)
        
        # Story listbox
        list_frame = ttk.Frame(sidebar)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.story_listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            font=('Arial', 10),
            selectmode=tk.SINGLE
        )
        self.story_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.story_listbox.yview)
        
        self.story_listbox.bind('<<ListboxSelect>>', self.on_story_select)
        self.story_listbox.bind('<Double-Button-1>', lambda e: self.notebook.select(0))
        
        # Current story info panel
        self.story_info_frame = ttk.LabelFrame(sidebar, text="Current Story", padding=15)
        self.story_info_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.story_title_label = ttk.Label(
            self.story_info_frame,
            text="No story selected",
            wraplength=240,
            font=('Arial', 10, 'bold'),
            justify=tk.LEFT
        )
        self.story_title_label.pack(anchor='w')
        
        self.story_stats_label = ttk.Label(
            self.story_info_frame,
            text="",
            wraplength=240,
            justify=tk.LEFT
        )
        self.story_stats_label.pack(anchor='w', pady=(5, 0))
        
        # Quick actions for selected story
        actions_frame = ttk.Frame(sidebar)
        actions_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Button(
            actions_frame,
            text="Delete Story",
            command=self.delete_current_story
        ).pack(fill=tk.X, pady=2)
        
        
    
    def create_main_content(self, parent):
        """Create main content area with tabs"""
        content_frame = ttk.Frame(parent)
        parent.add(content_frame, weight=1)
        
        # Create notebook with tabs
        self.notebook = ttk.Notebook(content_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create all tabs
        self.create_overview_tab()
        self.create_characters_tab()
        self.create_world_tab()
        self.create_bestiary_tab()  # NEW
        self.create_manage_media_tab()
        self.create_lore_tab()
        self.create_progression_tab()
        self.create_chapter_generator_tab()
        self.create_chapters_list_tab()

        # Create small colored icons for tabs to produce a left->right gradient
        try:
            tab_ids = list(self.notebook.tabs())
            n = len(tab_ids)
            if n > 0:
                self._tab_color_images = []
                # Gradient anchors
                blue = (43, 124, 255)      # #2b7cff
                purple = (138, 43, 226)    # #8a2be2
                darkred = (139, 0, 0)      # #8b0000

                def lerp(a, b, t):
                    return int(a + (b - a) * t)

                for idx, tab_id in enumerate(tab_ids):
                    ratio = idx / (n - 1) if n > 1 else 0.0
                    if ratio <= 0.5:
                        t = ratio * 2.0
                        r = lerp(blue[0], purple[0], t)
                        g = lerp(blue[1], purple[1], t)
                        b = lerp(blue[2], purple[2], t)
                    else:
                        t = (ratio - 0.5) * 2.0
                        r = lerp(purple[0], darkred[0], t)
                        g = lerp(purple[1], darkred[1], t)
                        b = lerp(purple[2], darkred[2], t)

                    hexcol = f"#{r:02x}{g:02x}{b:02x}"
                    try:
                        img = tk.PhotoImage(width=14, height=14)
                        img.put(hexcol, to=(0, 0, 14, 14))
                        self._tab_color_images.append(img)
                        try:
                            self.notebook.tab(tab_id, image=img, compound='left')
                        except Exception:
                            pass
                    except Exception:
                        # If image creation fails, ignore
                        pass
        except Exception:
            pass
    
    def create_status_bar(self):
        """Create bottom status bar"""
        status_frame = ttk.Frame(self.window)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_bar = ttk.Label(
            status_frame,
            text="Ready | Click 'New Story' to begin",
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding=(5, 2)
        )
        self.status_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # AI status indicator
        self.ai_status_label = ttk.Label(
            status_frame,
            text="AI: " + ("🟢 Connected" if self.ai.test_connection() else "🔴 Disconnected"),
            relief=tk.SUNKEN,
            padding=(5, 2)
        )
        self.ai_status_label.pack(side=tk.RIGHT)

    def test_ai(self):
        """Manual test of AI connection from Tools menu."""
        try:
            ok = self.ai.test_connection()
            if ok:
                messagebox.showinfo('AI Connection', 'Ollama is reachable and responded successfully.')
                self.ai_status_label.config(text="AI: 🟢 Connected")
            else:
                messagebox.showwarning('AI Connection', 'Ollama did not respond. Ensure it is running (ollama serve).')
                self.ai_status_label.config(text="AI: 🔴 Disconnected")
        except Exception as e:
            messagebox.showerror('AI Test Error', f'Error testing AI connection: {e}')

    def show_db_info(self):
        """Show basic database statistics."""
        try:
            stories = self.db.get_all_stories()
            count_stories = len(stories)
            # Quick counts for tables we care about
            msg = f"Stories: {count_stories}\n"
            # Optionally fetch more counts
            msg += "\nOpen the database file for full details."
            messagebox.showinfo('Database Statistics', msg)
        except Exception as e:
            messagebox.showerror('DB Error', f'Could not get DB info: {e}')

    def backup_database(self):
        """Create a timestamped backup copy of the database file."""
        try:
            db_path = getattr(self.db, 'db_path', None)
            if not db_path or not os.path.exists(db_path):
                messagebox.showerror('Backup Error', 'Database file not found.')
                return
            folder = os.path.dirname(db_path)
            base = os.path.basename(db_path)
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            dest = os.path.join(folder, f"{base}.backup.{timestamp}")
            import shutil
            shutil.copy2(db_path, dest)
            messagebox.showinfo('Backup Complete', f'Backup created:\n{dest}')
        except Exception as e:
            messagebox.showerror('Backup Error', f'Failed to create backup: {e}')

    def show_settings(self):
        """Open a minimal settings dialog (placeholder)."""
        messagebox.showinfo('Settings', 'Settings dialog not implemented yet.')

    def show_quick_start(self):
        qs = (
            "Quick Start:\n"
            "1. Create a new story (File -> New Story).\n"
            "2. Add characters, locations, and lore.\n"
            "3. Use Generate -> Generate Chapter to create chapters.\n"
            "4. Export chapters via File -> Export Chapter.\n"
        )
        messagebox.showinfo('Quick Start Guide', qs)

    def show_shortcuts(self):
        shortcuts = (
            "Keyboard Shortcuts:\n"
            "Ctrl+N - New Story\n"
            "Ctrl+O - Open Story\n"
            "Ctrl+S - Save All\n"
            "Ctrl+T - Toggle Theme\n"
        )
        messagebox.showinfo('Keyboard Shortcuts', shortcuts)

    def show_about(self):
        about = (
            "Light Novel Story Generator\n"
            "Version: development\n"
            "Features: AI-assisted chapter generation, world building, progression tracking.\n"
        )
        messagebox.showinfo('About', about)

    def show_story_stats(self):
        """Display basic statistics about the currently selected story."""
        try:
            if not self.current_story_id:
                messagebox.showwarning('No Story Selected', 'Please select a story first.')
                return
            story = self.db.get_story(self.current_story_id)
            chapters = self.db.get_all_chapters(self.current_story_id)
            chars = self.db.get_characters(self.current_story_id)
            msg = (
                f"Title: {story.get('title')}\n"
                f"Chapters: {len(chapters)}\n"
                f"Characters: {len(chars)}\n"
                f"Current chapter index: {story.get('current_chapter', 0)}\n"
            )
            messagebox.showinfo('Story Statistics', msg)
        except Exception as e:
            messagebox.showerror('Error', f'Failed to get story stats: {e}')

    def show_chapter_stats(self):
        """Show simple stats for the chapter being edited/generated (placeholder)."""
        try:
            chapter_num = getattr(self, 'gen_chapter_number', None)
            msg = 'Chapter statistics not implemented yet.'
            messagebox.showinfo('Chapter Statistics', msg)
        except Exception as e:
            messagebox.showerror('Error', f'Failed to show chapter stats: {e}')

    def show_timeline(self):
        """Open a simple timeline view (placeholder)."""
        try:
            dlg = tk.Toplevel(self.window)
            dlg.title('Timeline (Preview)')
            dlg.geometry('700x500')
            txt = tk.Text(dlg, wrap=tk.WORD)
            txt.insert('1.0', 'Timeline view is a placeholder. Saved arc progression will appear here in future updates.')
            txt.config(state=tk.DISABLED)
            txt.pack(fill=tk.BOTH, expand=True)
        except Exception as e:
            messagebox.showerror('Error', f'Failed to open timeline: {e}')

    def set_next_chapter_number(self):
        """Set the chapter number entry to next available chapter number for current story."""
        try:
            if not self.current_story_id:
                messagebox.showwarning('No Story Selected', 'Please select a story first.')
                return
            chapters = self.db.get_all_chapters(self.current_story_id)
            max_num = 0
            for ch in chapters:
                try:
                    num = int(ch.get('chapter_number', 0) or 0)
                    if num > max_num:
                        max_num = num
                except Exception:
                    pass
            next_num = max_num + 1
            if hasattr(self, 'gen_chapter_number') and isinstance(self.gen_chapter_number, ttk.Entry):
                try:
                    self.gen_chapter_number.delete(0, tk.END)
                    self.gen_chapter_number.insert(0, str(next_num))
                except Exception:
                    pass
        except Exception as e:
            messagebox.showerror('Error', f'Failed to compute next chapter number: {e}')

    def update_status(self, text: str):
        """Update the bottom status bar text."""
        try:
            if hasattr(self, 'status_bar'):
                self.status_bar.config(text=text)
        except Exception:
            pass

    def view_generation_prompt(self):
        """Build the generation prompt and show it in a dialog for preview."""
        try:
            if not self.current_story_id:
                messagebox.showwarning('No Story Selected', 'Select a story first.')
                return
            from ai.prompt_templates import PromptTemplates

            story = self.db.get_story(self.current_story_id)
            characters = self.db.get_characters(self.current_story_id)
            world = self.db.get_world_locations(self.current_story_id)
            powers = self.db.get_power_systems(self.current_story_id)
            lore = self.db.get_lore(self.current_story_id)
            progression = None
            try:
                # If current arc selected, get progression
                arc_id = getattr(self, 'current_arc_id', None)
                if arc_id:
                    progression = self.db.get_arc_progression(self.current_story_id, arc_id)
            except Exception:
                progression = None

            chapter_number = 1
            try:
                chapter_number = int(self.gen_chapter_number.get()) if self.gen_chapter_number.get() else 1
            except Exception:
                chapter_number = 1

            plot = self.gen_plot_directive.get('1.0', tk.END).strip() if hasattr(self, 'gen_plot_directive') else ''
            prev = self.gen_previous_summary.get('1.0', tk.END).strip() if hasattr(self, 'gen_previous_summary') else ''
            target = None
            try:
                target = int(self.gen_max_words.get())
            except Exception:
                target = None

            prompt = PromptTemplates.chapter_generation_prompt(
                story_info=story,
                characters=characters,
                world_info=world,
                power_systems=powers,
                lore=lore,
                progression=progression,
                chapter_number=chapter_number,
                plot_directive=plot,
                previous_chapter_summary=prev,
                target_word_count=target
            )

            dlg = tk.Toplevel(self.window)
            dlg.title('Generation Prompt Preview')
            dlg.geometry('900x700')
            txt = tk.Text(dlg, wrap=tk.WORD)
            txt.insert('1.0', prompt)
            txt.config(state=tk.DISABLED)
            txt.pack(fill=tk.BOTH, expand=True)

        except Exception as e:
            messagebox.showerror('Error', f'Could not build prompt: {e}')

    def load_previous_chapter_summary(self):
        """Load the summary of the previous chapter into the 'previous summary' box."""
        try:
            if not self.current_story_id:
                messagebox.showwarning('No Story Selected', 'Select a story first.')
                return
            chap_num = 1
            try:
                chap_num = int(self.gen_chapter_number.get())
            except Exception:
                chap_num = 1
            prev_num = max(1, chap_num - 1)
            ch = self.db.get_chapter(self.current_story_id, prev_num)
            if ch and ch.get('summary'):
                if hasattr(self, 'gen_previous_summary'):
                    self.gen_previous_summary.delete('1.0', tk.END)
                    self.gen_previous_summary.insert('1.0', ch.get('summary'))
            else:
                messagebox.showinfo('No Previous Chapter', 'No previous chapter summary found.')
        except Exception as e:
            messagebox.showerror('Error', f'Failed to load previous chapter: {e}')

    def generate_chapter(self):
        """Collect settings, build prompt, call AI to generate chapter, and save it."""
        try:
            if not self.current_story_id:
                messagebox.showwarning('No Story Selected', 'Please select or create a story first.')
                return

            # Gather inputs
            try:
                chapter_number = int(self.gen_chapter_number.get()) if self.gen_chapter_number.get() else 1
            except Exception:
                chapter_number = 1

            title = self.gen_chapter_title.get() if hasattr(self, 'gen_chapter_title') else ''
            pov = self.gen_pov_character.get() if hasattr(self, 'gen_pov_character') else ''
            plot = self.gen_plot_directive.get('1.0', tk.END).strip() if hasattr(self, 'gen_plot_directive') else ''
            prev = self.gen_previous_summary.get('1.0', tk.END).strip() if hasattr(self, 'gen_previous_summary') else ''
            temp = float(self.gen_temperature.get()) if hasattr(self, 'gen_temperature') else 0.85
            try:
                max_words = int(self.gen_max_words.get())
            except Exception:
                max_words = None

            # Build prompt
            from ai.prompt_templates import PromptTemplates

            story = self.db.get_story(self.current_story_id)
            characters = self.db.get_characters(self.current_story_id)
            world = self.db.get_world_locations(self.current_story_id)
            powers = self.db.get_power_systems(self.current_story_id)
            lore = self.db.get_lore(self.current_story_id)
            progression = None
            arc_id = getattr(self, 'current_arc_id', None)
            if arc_id:
                progression = self.db.get_arc_progression(self.current_story_id, arc_id)

            prompt = PromptTemplates.chapter_generation_prompt(
                story_info=story,
                characters=characters,
                world_info=world,
                power_systems=powers,
                lore=lore,
                progression=progression,
                chapter_number=chapter_number,
                plot_directive=plot,
                previous_chapter_summary=prev,
                target_word_count=max_words
            )

            # Call AI
            self.generate_btn.config(state=tk.DISABLED)
            self.gen_progress.start()
            self.update_status('Generating chapter...')
            result = self.ai.generate_chapter(prompt=prompt, temperature=temp, max_words=max_words)
            self.gen_progress.stop()
            self.generate_btn.config(state=tk.NORMAL)
            self.update_status('Generation complete')

            # Save chapter
            try:
                content = result
                word_count = len(content.split()) if isinstance(content, str) else 0
                self.db.save_chapter(self.current_story_id, chapter_number, content, title=title, word_count=word_count, pov_character=pov)
                messagebox.showinfo('Saved', f'Chapter {chapter_number} saved to database.')
            except Exception as e:
                messagebox.showerror('Save Error', f'Failed to save chapter: {e}')

            # Display result in output area if present
            try:
                if hasattr(self, 'gen_output'):
                    self.gen_output.config(state=tk.NORMAL)
                    self.gen_output.delete('1.0', tk.END)
                    self.gen_output.insert('1.0', result)
                    self.gen_output.config(state=tk.DISABLED)
                else:
                    # Fallback: show in a dialog
                    dlg = tk.Toplevel(self.window)
                    dlg.title(f'Chapter {chapter_number}')
                    txt = tk.Text(dlg, wrap=tk.WORD)
                    txt.insert('1.0', result)
                    txt.config(state=tk.DISABLED)
                    txt.pack(fill=tk.BOTH, expand=True)
            except Exception:
                pass

        except Exception as e:
            self.gen_progress.stop()
            try:
                self.generate_btn.config(state=tk.NORMAL)
            except Exception:
                pass
            messagebox.showerror('Generation Error', f'Failed to generate chapter: {e}')

    def save_generated_chapter(self):
        """Save the content currently shown in the generated output area to the database."""
        try:
            if not self.current_story_id:
                messagebox.showwarning('No Story Selected', 'Please select a story first.')
                return
            content = ''
            if hasattr(self, 'gen_output'):
                content = self.gen_output.get('1.0', tk.END).strip()
            if not content:
                messagebox.showwarning('No Content', 'There is no generated content to save.')
                return

            try:
                chapter_number = int(self.gen_chapter_number.get()) if self.gen_chapter_number.get() else 1
            except Exception:
                chapter_number = 1

            title = self.gen_chapter_title.get() if hasattr(self, 'gen_chapter_title') else ''
            pov = self.gen_pov_character.get() if hasattr(self, 'gen_pov_character') else ''
            word_count = len(content.split())

            self.db.save_chapter(self.current_story_id, chapter_number, content, title=title, word_count=word_count, pov_character=pov)
            messagebox.showinfo('Saved', f'Chapter {chapter_number} saved to database.')
        except Exception as e:
            messagebox.showerror('Save Error', f'Failed to save generated chapter: {e}')
    
    def create_overview_tab(self):
        """Story overview and settings tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📋 Overview")
        
        # Scrollable canvas
        canvas = tk.Canvas(tab)
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Bind mousewheel for progression scroll area
        try:
            self._bind_mousewheel_widget(canvas)
        except Exception:
            pass
        
        # Content
        content = ttk.Frame(scrollable_frame, padding=30)
        content.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header = ttk.Label(
            content,
            text="Story Overview & Settings",
            font=('Arial', 16, 'bold')
        )
        header.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky='w')
        
        row = 1
        
        # Title
        ttk.Label(content, text="Story Title:", font=('Arial', 11, 'bold')).grid(
            row=row, column=0, sticky='w', pady=8
        )
        self.overview_title = ttk.Entry(content, width=70, font=('Arial', 12))
        self.overview_title.grid(row=row, column=1, sticky='ew', pady=8, padx=(15, 0))
        row += 1
        
        # Synopsis
        ttk.Label(content, text="Synopsis:", font=('Arial', 11, 'bold')).grid(
            row=row, column=0, sticky='nw', pady=8
        )
        synopsis_frame = ttk.Frame(content)
        synopsis_frame.grid(row=row, column=1, sticky='ew', pady=8, padx=(15, 0))
        
        synopsis_scroll = ttk.Scrollbar(synopsis_frame)
        synopsis_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.overview_synopsis = tk.Text(
            synopsis_frame,
            width=70,
            height=6,
            font=('Arial', 11),
            wrap=tk.WORD,
            yscrollcommand=synopsis_scroll.set
        )
        self.overview_synopsis.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        synopsis_scroll.config(command=self.overview_synopsis.yview)
        row += 1
        
        # Genre
        ttk.Label(content, text="Genre:", font=('Arial', 11, 'bold')).grid(
            row=row, column=0, sticky='w', pady=8
        )
        self.overview_genre = ttk.Entry(content, width=70, font=('Arial', 11))
        self.overview_genre.grid(row=row, column=1, sticky='ew', pady=8, padx=(15, 0))
        self.overview_genre.insert(0, "Light Novel / Fantasy")
        row += 1
        
        # Themes
        ttk.Label(content, text="Themes:", font=('Arial', 11, 'bold')).grid(
            row=row, column=0, sticky='w', pady=8
        )
        self.overview_themes = ttk.Entry(content, width=70, font=('Arial', 11))
        self.overview_themes.grid(row=row, column=1, sticky='ew', pady=8, padx=(15, 0))
        row += 1
        
        # Tone
        ttk.Label(content, text="Tone:", font=('Arial', 11, 'bold')).grid(
            row=row, column=0, sticky='w', pady=8
        )
        self.overview_tone = ttk.Entry(content, width=70, font=('Arial', 11))
        self.overview_tone.grid(row=row, column=1, sticky='ew', pady=8, padx=(15, 0))
        row += 1
        
        # Writing Style
        ttk.Label(content, text="Writing Style:", font=('Arial', 11, 'bold')).grid(
            row=row, column=0, sticky='w', pady=8
        )
        self.overview_style = ttk.Entry(content, width=70, font=('Arial', 11))
        self.overview_style.grid(row=row, column=1, sticky='ew', pady=8, padx=(15, 0))
        self.overview_style.insert(0, "ReZero/Fate-inspired - Internal monologue, detailed sensory descriptions")
        row += 1
        
        # Target Length
        ttk.Label(content, text="Target Length:", font=('Arial', 11, 'bold')).grid(
            row=row, column=0, sticky='w', pady=8
        )
        length_frame = ttk.Frame(content)
        length_frame.grid(row=row, column=1, sticky='w', pady=8, padx=(15, 0))
        
        self.overview_target_length = ttk.Combobox(
            length_frame,
            width=20,
            values=['Short (10-20 chapters)', 'Medium (20-50 chapters)', 
                    'Long (50-100 chapters)', 'Epic (100+ chapters)'],
            state='readonly'
        )
        self.overview_target_length.set('Medium (20-50 chapters)')
        row += 1

        # Target chapter words (numeric)
        ttk.Label(content, text="Target chapter words:", font=('Arial', 11, 'bold')).grid(
            row=row, column=0, sticky='w', pady=8
        )
        self.overview_target_words = ttk.Entry(content, width=30, font=('Arial', 11))
        self.overview_target_words.grid(row=row, column=1, sticky='w', pady=8, padx=(15, 0))
        self.overview_target_words.insert(0, "3000")
        row += 1
        self.overview_target_length.pack(side=tk.LEFT)
        row += 1
        
        # Buttons
        button_frame = ttk.Frame(content)
        button_frame.grid(row=row, column=0, columnspan=2, pady=30)
        
        ttk.Button(
            button_frame,
            text="💾 Save Story Information",
            command=self.save_overview,
            width=25
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="🎨 Generate World from Synopsis",
            command=self.generate_from_synopsis,
            width=30
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="📊 View Story Statistics",
            command=self.show_story_stats,
            width=25
        ).pack(side=tk.LEFT, padx=5)
        
        content.columnconfigure(1, weight=1)
    
    def create_characters_tab(self):
        """Characters management tab with enhanced UI"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="👤 Characters")
        
        # Split into list and details
        paned = ttk.PanedWindow(tab, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left: Character list
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)
        
        # Header with filter
        header_frame = ttk.Frame(left_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(
            header_frame,
            text="Characters",
            font=('Arial', 13, 'bold')
        ).pack(side=tk.LEFT)
        
        # Filter by role
        ttk.Label(header_frame, text="Filter:").pack(side=tk.LEFT, padx=(20, 5))
        self.char_role_filter = ttk.Combobox(
            header_frame,
            width=15,
            values=['All', 'Protagonist', 'Major Character', 'Supporting Character', 
                    'Minor Character', 'Antagonist'],
            state='readonly'
        )
        self.char_role_filter.set('All')
        self.char_role_filter.pack(side=tk.LEFT, padx=5)
        self.char_role_filter.bind('<<ComboboxSelected>>', lambda e: self.load_characters())
        
        # Action buttons
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(
            button_frame,
            text="➕ Add Character",
            command=self.add_character
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            button_frame,
            text="🎨 AI Expand",
            command=self.ai_expand_character
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            button_frame,
            text="🖼️ Add Image",
            command=lambda: self.add_media_ui('character')
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            button_frame,
            text="🗑️ Delete",
            command=self.delete_character
        ).pack(side=tk.LEFT, padx=2)
        
        # Character list
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        char_scrollbar = ttk.Scrollbar(list_frame)
        char_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.char_listbox = tk.Listbox(
            list_frame,
            yscrollcommand=char_scrollbar.set,
            font=('Arial', 11),
            selectmode=tk.SINGLE
        )
        self.char_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        char_scrollbar.config(command=self.char_listbox.yview)
        
        self.char_listbox.bind('<<ListboxSelect>>', self.on_character_select)
        
        # Right: Character details
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=2)
        
        # Scrollable details
        canvas = tk.Canvas(right_frame)
        scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=canvas.yview)
        self.char_details_frame = ttk.Frame(canvas)
        
        self.char_details_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.char_details_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Enable mouse wheel scrolling
        # Use a focused binding so only this canvas scrolls when hovered
        self._bind_mousewheel_widget(canvas)
        
        self.setup_character_details_form()
    
    def setup_character_details_form(self):
        """Setup enhanced character details form"""
        frame = self.char_details_frame
        self.char_widgets = {}
        
        # Header
        header = ttk.Label(
            frame,
            text="Character Details",
            font=('Arial', 14, 'bold')
        )
        header.grid(row=0, column=0, columnspan=2, pady=(10, 20), sticky='w', padx=15)
        # Media thumbnail placeholder (right aligned in header)
        try:
            self.char_media_label = ttk.Label(frame, text='', width=20)
            self.char_media_label.grid(row=0, column=2, rowspan=2, sticky='e', padx=10)
        except Exception:
            self.char_media_label = None
        
        row = 1
        
        # Name
        ttk.Label(frame, text="Name:", font=('Arial', 11, 'bold')).grid(
            row=row, column=0, sticky='w', padx=15, pady=6
        )
        self.char_widgets['name'] = ttk.Entry(frame, width=50, font=('Arial', 12))
        self.char_widgets['name'].grid(row=row, column=1, sticky='ew', padx=15, pady=6)
        row += 1
        
        # Role
        ttk.Label(frame, text="Role:", font=('Arial', 11, 'bold')).grid(
            row=row, column=0, sticky='w', padx=15, pady=6
        )
        self.char_widgets['role'] = ttk.Combobox(
            frame,
            width=48,
            values=['Protagonist', 'Deuteragonist', 'Major Character',
                    'Supporting Character', 'Minor Character', 'Antagonist',
                    'Love Interest', 'Mentor', 'Rival'],
            state='readonly'
        )
        self.char_widgets['role'].grid(row=row, column=1, sticky='ew', padx=15, pady=6)
        row += 1
        
        # Age and Gender row
        ttk.Label(frame, text="Age & Gender:", font=('Arial', 11, 'bold')).grid(
            row=row, column=0, sticky='w', padx=15, pady=6
        )
        age_gender_frame = ttk.Frame(frame)
        age_gender_frame.grid(row=row, column=1, sticky='ew', padx=15, pady=6)
        
        self.char_widgets['age'] = ttk.Entry(age_gender_frame, width=10)
        self.char_widgets['age'].pack(side=tk.LEFT)
        
        ttk.Label(age_gender_frame, text="Gender:").pack(side=tk.LEFT, padx=(15, 5))
        self.char_widgets['gender'] = ttk.Combobox(
            age_gender_frame,
            width=15,
            values=['Male', 'Female', 'Non-binary', 'Other'],
            state='readonly'
        )
        self.char_widgets['gender'].pack(side=tk.LEFT)
        row += 1
        
        # Importance slider
        ttk.Label(frame, text="Importance:", font=('Arial', 11, 'bold')).grid(
            row=row, column=0, sticky='w', padx=15, pady=6
        )
        importance_frame = ttk.Frame(frame)
        importance_frame.grid(row=row, column=1, sticky='ew', padx=15, pady=6)
        
        self.char_widgets['importance'] = tk.Scale(
            importance_frame,
            from_=1, to=5,
            orient=tk.HORIZONTAL,
            length=250,
            tickinterval=1
        )
        self.char_widgets['importance'].pack(side=tk.LEFT)
        self.char_widgets['importance'].set(3)
        
        ttk.Label(importance_frame, text="(1=Minor, 5=Critical)").pack(side=tk.LEFT, padx=10)
        row += 1
        
        # Status
        ttk.Label(frame, text="Status:", font=('Arial', 11, 'bold')).grid(
            row=row, column=0, sticky='w', padx=15, pady=6
        )
        self.char_widgets['status'] = ttk.Combobox(
            frame,
            width=48,
            values=['Alive', 'Deceased', 'Unknown', 'MIA'],
            state='readonly'
        )
        self.char_widgets['status'].set('Alive')
        self.char_widgets['status'].grid(row=row, column=1, sticky='ew', padx=15, pady=6)
        row += 1
        
        # Separator
        ttk.Separator(frame, orient=tk.HORIZONTAL).grid(
            row=row, column=0, columnspan=2, sticky='ew', padx=15, pady=15
        )
        row += 1

        # Create the larger text fields for detailed character attributes
        text_fields = [
            ('appearance', 'Physical Appearance', 4),
            ('personality', 'Personality Traits', 4),
            ('background', 'Background Story', 6),
            ('motivations', 'Goals & Motivations', 4),
            ('abilities', 'Abilities & Powers', 4),
            ('combat_style', 'Combat Style', 3),
            ('equipment', 'Equipment & Belongings', 3),
            ('relationships', 'Relationships', 3),
            ('character_arc', 'Character Development Arc', 4),
            ('voice_style', 'Voice & Speech Pattern', 3),
            ('quirks', 'Quirks & Mannerisms', 3)
        ]

        for key, label, height in text_fields:
            ttk.Label(frame, text=label+':', font=('Arial', 11, 'bold')).grid(
                row=row, column=0, sticky='nw', padx=15, pady=(6, 4)
            )
            tf = ttk.Frame(frame)
            tf.grid(row=row, column=1, sticky='ew', padx=15, pady=(6, 4))
            sc = ttk.Scrollbar(tf)
            sc.pack(side=tk.RIGHT, fill=tk.Y)
            txt = tk.Text(tf, width=70, height=height, wrap=tk.WORD, yscrollcommand=sc.set)
            txt.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            sc.config(command=txt.yview)
            self.char_widgets[key] = txt
            row += 1

        # Action buttons for character form
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=12, padx=15, sticky='e')

        try:
            save_btn = tk.Button(btn_frame, text="💾 Save Character", command=self.save_character,
                                 bg='#9B111E', fg='white', activebackground='#2F3E9E')
        except Exception:
            save_btn = ttk.Button(btn_frame, text="💾 Save Character", command=self.save_character)

        save_btn.pack(side=tk.RIGHT, padx=6)
        ttk.Button(btn_frame, text="🗑️ Delete", command=self.delete_character).pack(side=tk.RIGHT, padx=6)

        # after creating form columns
        frame.columnconfigure(0, weight=0)
        frame.columnconfigure(1, weight=1)  # content column expands

    def create_world_tab(self):
        """World builder tab with locations list and details form"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="🌍 World")

        paned = ttk.PanedWindow(tab, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left: Locations list and controls
        left_frame = ttk.Frame(paned, width=300)
        paned.add(left_frame, weight=1)

        header = ttk.Frame(left_frame)
        header.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(header, text="Locations", font=('Arial', 13, 'bold')).pack(side=tk.LEFT)

        ttk.Button(left_frame, text="➕ Add Location", command=self.add_location).pack(fill=tk.X, padx=8, pady=(6, 8))
        ttk.Button(left_frame, text="🖼️ Add Image", command=lambda: self.add_media_ui('location')).pack(fill=tk.X, padx=8, pady=(0, 8))

        filter_frame = ttk.Frame(left_frame)
        filter_frame.pack(fill=tk.X, padx=8)
        ttk.Label(filter_frame, text="Type:").pack(side=tk.LEFT)
        self.location_type_filter = ttk.Combobox(filter_frame, width=18, values=['All', 'City', 'Town', 'Region', 'Country', 'Dungeon', 'Other'], state='readonly')
        self.location_type_filter.set('All')
        self.location_type_filter.pack(side=tk.LEFT, padx=(6, 0))
        self.location_type_filter.bind('<<ComboboxSelected>>', lambda e: self.load_locations())

        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=(8, 8))
        scroll = ttk.Scrollbar(list_frame)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.location_listbox = tk.Listbox(list_frame, yscrollcommand=scroll.set, font=('Arial', 11))
        self.location_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.config(command=self.location_listbox.yview)
        self.location_listbox.bind('<<ListboxSelect>>', self.on_location_select)

        # Right: Location detail form
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=3)

        canvas = tk.Canvas(right_frame)
        scrollbar = ttk.Scrollbar(right_frame, orient='vertical', command=canvas.yview)
        form_frame = ttk.Frame(canvas)
        form_frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=form_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Bind mousewheel for this canvas region
        try:
            self._bind_mousewheel_widget(canvas)
        except Exception:
            pass

        self.location_widgets = {}

        ttk.Label(form_frame, text="Location Name:", font=('Arial', 11, 'bold')).grid(row=0, column=0, sticky='w', padx=10, pady=(10, 6))
        self.location_widgets['name'] = ttk.Entry(form_frame, width=60)
        self.location_widgets['name'].grid(row=0, column=1, sticky='ew', padx=10, pady=(10, 6))
        # Location media thumbnail
        try:
            self.location_media_label = ttk.Label(form_frame, text='', width=20)
            self.location_media_label.grid(row=0, column=2, rowspan=2, sticky='e', padx=10)
        except Exception:
            self.location_media_label = None

        ttk.Label(form_frame, text="Type:", font=('Arial', 11, 'bold')).grid(row=1, column=0, sticky='w', padx=10, pady=(0, 6))
        self.location_widgets['type'] = ttk.Combobox(form_frame, width=30, values=['City', 'Town', 'Region', 'Country', 'Dungeon', 'Other'], state='readonly')
        self.location_widgets['type'].grid(row=1, column=1, sticky='w', padx=10, pady=(0, 6))

        # Large text fields used elsewhere
        text_fields = [
            ('description', 'Description', 6),
            ('geography', 'Geography', 4),
            ('climate', 'Climate', 3),
            ('population', 'Population', 3),
            ('government', 'Government', 3),
            ('economy', 'Economy', 3),
            ('culture', 'Culture', 4),
            ('history', 'History', 5),
            ('notable_locations', 'Notable Locations', 4),
            ('relationships', 'Relationships', 3)
        ]

        r = 2
        for key, label, h in text_fields:
            ttk.Label(form_frame, text=label+":", font=('Arial', 11, 'bold')).grid(row=r, column=0, sticky='nw', padx=10, pady=(8, 4))
            tf = ttk.Frame(form_frame)
            tf.grid(row=r, column=1, sticky='ew', padx=10, pady=(8, 4))
            sc = ttk.Scrollbar(tf)
            sc.pack(side=tk.RIGHT, fill=tk.Y)
            txt = tk.Text(tf, width=80, height=h, wrap=tk.WORD, yscrollcommand=sc.set)
            txt.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            sc.config(command=txt.yview)
            self.location_widgets[key] = txt
            r += 1

        # Action buttons
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=r, column=0, columnspan=2, pady=12)
        ttk.Button(btn_frame, text="💾 Save Location", command=self.save_location).pack(side=tk.LEFT, padx=6)
        ttk.Button(btn_frame, text="🗑️ Delete", command=self.delete_location).pack(side=tk.LEFT, padx=6)

        form_frame.columnconfigure(0, weight=0)
        form_frame.columnconfigure(1, weight=1)  # content column expands

        # Load initial data
        self.load_locations()

    def create_bestiary_tab(self):
        """Bestiary tab: list of creatures and a details pane"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="🐉 Bestiary")

        paned = ttk.PanedWindow(tab, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        left = ttk.Frame(paned, width=300)
        paned.add(left, weight=1)

        header = ttk.Frame(left)
        header.pack(fill=tk.X, pady=(0, 6))
        ttk.Label(header, text="Creatures", font=('Arial', 13, 'bold')).pack(side=tk.LEFT)

        ttk.Button(left, text="➕ Add Creature", command=self.add_creature).pack(fill=tk.X, padx=8, pady=(6, 6))
        ttk.Button(left, text="🖼️ Add Image", command=lambda: self.add_media_ui('creature')).pack(fill=tk.X, padx=8, pady=(0, 6))

        list_frame = ttk.Frame(left)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=(6, 8))
        cs = ttk.Scrollbar(list_frame)
        cs.pack(side=tk.RIGHT, fill=tk.Y)
        self.creature_listbox = tk.Listbox(list_frame, yscrollcommand=cs.set, font=('Arial', 11))
        self.creature_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        cs.config(command=self.creature_listbox.yview)
        self.creature_listbox.bind('<<ListboxSelect>>', self.on_creature_select)

        right = ttk.Frame(paned)
        paned.add(right, weight=3)

        # Detail form (scrollable)
        canvas = tk.Canvas(right)
        scrollbar = ttk.Scrollbar(right, orient='vertical', command=canvas.yview)
        frame = ttk.Frame(canvas)
        frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.creature_widgets = {}

        ttk.Label(frame, text="Name:", font=('Arial', 11, 'bold')).grid(row=0, column=0, sticky='w', padx=10, pady=(10, 6))
        self.creature_widgets['name'] = ttk.Entry(frame, width=60)
        self.creature_widgets['name'].grid(row=0, column=1, sticky='ew', padx=10, pady=(10, 6))
        # Media label for creature thumbnail
        try:
            self.creature_media_label = ttk.Label(frame, text='', width=20)
            self.creature_media_label.grid(row=0, column=2, rowspan=2, sticky='e', padx=10)
        except Exception:
            self.creature_media_label = None

        ttk.Label(frame, text="Type:", font=('Arial', 11, 'bold')).grid(row=1, column=0, sticky='w', padx=10, pady=(0, 6))
        self.creature_widgets['type'] = ttk.Entry(frame, width=30)
        self.creature_widgets['type'].grid(row=1, column=1, sticky='w', padx=10, pady=(0, 6))

        ttk.Label(frame, text="Threat Level:", font=('Arial', 11, 'bold')).grid(row=2, column=0, sticky='w', padx=10, pady=(0, 6))
        self.creature_widgets['threat_level'] = ttk.Combobox(frame, width=20, values=['Low', 'Moderate', 'High', 'Extreme'], state='readonly')
        self.creature_widgets['threat_level'].grid(row=2, column=1, sticky='w', padx=10, pady=(0, 6))

        text_keys = ['description', 'habitat', 'behavior', 'abilities', 'weaknesses', 'diet', 'lore', 'drops']
        r = 3
        for key in text_keys:
            ttk.Label(frame, text=f"{key.replace('_', ' ').title()}:", font=('Arial', 11, 'bold')).grid(row=r, column=0, sticky='nw', padx=10, pady=(8, 4))
            tf = ttk.Frame(frame)
            tf.grid(row=r, column=1, sticky='ew', padx=10, pady=(8, 4))
            sc = ttk.Scrollbar(tf)
            sc.pack(side=tk.RIGHT, fill=tk.Y)
            txt = tk.Text(tf, width=80, height=4, wrap=tk.WORD, yscrollcommand=sc.set)
            txt.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            sc.config(command=txt.yview)
            self.creature_widgets[key] = txt
            r += 1

        frame.columnconfigure(1, weight=1)

        # Action buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=r, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="💾 Save Creature", command=self.save_creature).pack(side=tk.LEFT, padx=6)
        ttk.Button(btn_frame, text="🗑️ Delete", command=self.delete_creature).pack(side=tk.LEFT, padx=6)

        # Load initial data
        self.load_creatures()

    def create_manage_media_tab(self):
        """Manage Media tab: list all media for the current story and provide preview/delete/open actions."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="🖼️ Manage Media")

        paned = ttk.PanedWindow(tab, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        left = ttk.Frame(paned, width=360)
        paned.add(left, weight=1)

        header = ttk.Frame(left)
        header.pack(fill=tk.X, pady=(0,6))
        ttk.Label(header, text="Media Library", font=('Arial', 13, 'bold')).pack(side=tk.LEFT)

        btns = ttk.Frame(left)
        btns.pack(fill=tk.X, pady=(8,4))
        ttk.Button(btns, text='🔄 Refresh', command=self.refresh_media_list).pack(side=tk.LEFT, padx=4)
        ttk.Button(btns, text='🗑️ Delete', command=self.delete_media_item).pack(side=tk.LEFT, padx=4)
        ttk.Button(btns, text='📂 Open', command=self.open_media_in_explorer).pack(side=tk.LEFT, padx=4)

        list_frame = ttk.Frame(left)
        list_frame.pack(fill=tk.BOTH, expand=True)
        lb_scroll = ttk.Scrollbar(list_frame)
        lb_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.media_listbox = tk.Listbox(list_frame, yscrollcommand=lb_scroll.set, font=('Arial', 11))
        self.media_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        lb_scroll.config(command=self.media_listbox.yview)
        self.media_listbox.bind('<<ListboxSelect>>', self.on_media_select)

        # Right: preview and metadata
        right = ttk.Frame(paned)
        paned.add(right, weight=2)

        preview_frame = ttk.LabelFrame(right, text='Preview', padding=8)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        # Image/preview label
        self.media_preview_label = ttk.Label(preview_frame, text='Select an item to preview', anchor='center')
        self.media_preview_label.pack(fill=tk.BOTH, expand=True)

        meta_frame = ttk.LabelFrame(right, text='Metadata', padding=8)
        meta_frame.pack(fill=tk.BOTH, expand=True, padx=6, pady=(0,6))
        self.media_meta_text = tk.Text(meta_frame, height=8, wrap=tk.WORD, state='disabled')
        self.media_meta_text.pack(fill=tk.BOTH, expand=True)

        # Internal cache for media rows
        self._media_cache = []

        # Load initial list
        try:
            self.load_media_list()
        except Exception:
            pass

    def load_media_list(self):
        """Load media rows for the current story into the listbox."""
        self.media_listbox.delete(0, tk.END)
        self._media_cache = []
        if not self.current_story_id:
            return
        try:
            rows = self.db.get_media_for(self.current_story_id)
            for r in rows:
                display = f"[{r.get('id')}] {r.get('entity_type')} - {os.path.basename(r.get('file_path') or '')}"
                self.media_listbox.insert(tk.END, display)
                self._media_cache.append(r)
        except Exception as e:
            messagebox.showerror('Media Load Error', f'Failed to load media: {e}')

    def on_media_select(self, event=None):
        try:
            sel = self.media_listbox.curselection()
            if not sel:
                return
            idx = sel[0]
            row = self._media_cache[idx]
            self._display_media_preview(row)
        except Exception as e:
            messagebox.showerror('Preview Error', f'Failed to preview media: {e}')

    def _display_media_preview(self, media_row):
        """Show a thumbnail or filename and metadata for a media row."""
        try:
            # Resolve absolute path
            fp = media_row.get('file_path')
            db_dir = os.path.dirname(os.path.abspath(self.db.db_path))
            abs_path = fp if os.path.isabs(fp) else os.path.join(db_dir, fp)

            # Try to load as image
            loaded = False
            try:
                from PIL import Image, ImageTk
                if os.path.exists(abs_path):
                    img = Image.open(abs_path)
                    img.thumbnail((400, 400))
                    imgtk = ImageTk.PhotoImage(img)
                    self.media_preview_label.config(image=imgtk, text='')
                    self.media_preview_label.image = imgtk
                    loaded = True
            except Exception:
                loaded = False

            if not loaded:
                # Fallback: show filename
                self.media_preview_label.config(image='', text=os.path.basename(abs_path))

            # Show metadata
            meta_lines = []
            meta_lines.append(f"ID: {media_row.get('id')}")
            meta_lines.append(f"Entity Type: {media_row.get('entity_type')}")
            meta_lines.append(f"Entity ID: {media_row.get('entity_id')}")
            meta_lines.append(f"Stored Path: {media_row.get('file_path')}")
            if os.path.exists(abs_path):
                meta_lines.append(f"Absolute Path: {abs_path}")
            meta_lines.append(f"Created At: {media_row.get('created_at')}")

            self.media_meta_text.config(state='normal')
            self.media_meta_text.delete('1.0', tk.END)
            self.media_meta_text.insert('1.0', '\n'.join(meta_lines))
            self.media_meta_text.config(state='disabled')

        except Exception as e:
            messagebox.showerror('Preview Error', f'Error displaying preview: {e}')

    def delete_media_item(self):
        try:
            sel = self.media_listbox.curselection()
            if not sel:
                messagebox.showinfo('Delete Media', 'Select a media item first.')
                return
            idx = sel[0]
            row = self._media_cache[idx]
            if not messagebox.askyesno('Confirm Delete', f"Delete media ID {row.get('id')}? This will remove the DB record."):
                return
            self.db.delete_media(row.get('id'))
            messagebox.showinfo('Deleted', 'Media record deleted.')
            self.load_media_list()
            self.media_preview_label.config(image='', text='Select an item to preview')
            self.media_meta_text.config(state='normal')
            self.media_meta_text.delete('1.0', tk.END)
            self.media_meta_text.config(state='disabled')
        except Exception as e:
            messagebox.showerror('Delete Error', f'Failed to delete media: {e}')

    def open_media_in_explorer(self):
        try:
            sel = self.media_listbox.curselection()
            if not sel:
                messagebox.showinfo('Open Media', 'Select a media item first.')
                return
            idx = sel[0]
            row = self._media_cache[idx]
            fp = row.get('file_path')
            db_dir = os.path.dirname(os.path.abspath(self.db.db_path))
            abs_path = fp if os.path.isabs(fp) else os.path.join(db_dir, fp)
            if os.path.exists(abs_path):
                try:
                    os.startfile(abs_path)
                except Exception:
                    # Fallback: open containing folder
                    folder = os.path.dirname(abs_path)
                    os.startfile(folder)
            else:
                messagebox.showwarning('File Not Found', f'The file does not exist: {abs_path}')
        except Exception as e:
            messagebox.showerror('Open Error', f'Failed to open file: {e}')

    def refresh_media_list(self):
        try:
            self.load_media_list()
            self.update_status('Media list refreshed')
        except Exception as e:
            messagebox.showerror('Refresh Error', f'Failed to refresh media list: {e}')

    def create_lore_tab(self):
        """Lore & powers tab (list and content display)"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📚 Lore & Powers")

        paned = ttk.PanedWindow(tab, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left: Lore list + controls
        left = ttk.Frame(paned, width=320)
        paned.add(left, weight=1)

        header = ttk.Frame(left)
        header.pack(fill=tk.X)
        ttk.Label(header, text="Lore Entries", font=('Arial', 14, 'bold')).pack(side=tk.LEFT)

        ttk.Label(header, text="Category:").pack(side=tk.LEFT, padx=(10,4))
        self.lore_category_filter = ttk.Combobox(header, width=14, values=['All', 'History', 'Culture', 'Religion', 'Technology', 'Magic', 'Events', 'Legends', 'Prophecies', 'Other'], state='readonly')
        self.lore_category_filter.set('All')
        self.lore_category_filter.pack(side=tk.LEFT)
        self.lore_category_filter.bind('<<ComboboxSelected>>', lambda e: self.load_lore())

        btns = ttk.Frame(left)
        btns.pack(fill=tk.X, pady=(8,4))
        ttk.Button(btns, text='➕ Add', command=self.add_lore).pack(side=tk.LEFT, padx=4)
        ttk.Button(btns, text='✏️ Edit', command=lambda: self.edit_lore(getattr(self, 'current_lore_id', None))).pack(side=tk.LEFT, padx=4)
        ttk.Button(btns, text='🗑️ Delete', command=lambda: self.delete_lore(getattr(self, 'current_lore_id', None))).pack(side=tk.LEFT, padx=4)

        list_frame = ttk.Frame(left)
        list_frame.pack(fill=tk.BOTH, expand=True)
        lb_scroll = ttk.Scrollbar(list_frame)
        lb_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.lore_listbox = tk.Listbox(list_frame, yscrollcommand=lb_scroll.set, font=('Arial', 11))
        self.lore_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        lb_scroll.config(command=self.lore_listbox.yview)
        self.lore_listbox.bind('<<ListboxSelect>>', self.on_lore_select)

        # Right: Details (Lore display on top, Power Systems below)
        right = ttk.Frame(paned)
        paned.add(right, weight=3)

        # Lore detail area
        lore_frame = ttk.LabelFrame(right, text='Lore Detail', padding=8)
        lore_frame.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        lore_scroll = ttk.Scrollbar(lore_frame)
        lore_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.lore_text = tk.Text(lore_frame, wrap=tk.WORD, yscrollcommand=lore_scroll.set, font=('Arial', 10), state='normal')
        self.lore_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        lore_scroll.config(command=self.lore_text.yview)

        # Power systems area
        ps_frame = ttk.LabelFrame(right, text='Power Systems', padding=8)
        ps_frame.pack(fill=tk.BOTH, expand=True, padx=6, pady=(0,6))

        ps_btns = ttk.Frame(ps_frame)
        ps_btns.pack(fill=tk.X)
        ttk.Button(ps_btns, text='➕ Add System', command=self.add_power_system).pack(side=tk.LEFT, padx=4)
        ttk.Button(ps_btns, text='✏️ Edit System', command=lambda: self.edit_power_system(getattr(self, 'current_power_id', None))).pack(side=tk.LEFT, padx=4)
        ttk.Button(ps_btns, text='🗑️ Delete System', command=lambda: self.delete_power_system(getattr(self, 'current_power_id', None))).pack(side=tk.LEFT, padx=4)

        ps_list_frame = ttk.Frame(ps_frame)
        ps_list_frame.pack(fill=tk.BOTH, expand=True, pady=(6,0))
        ps_scroll = ttk.Scrollbar(ps_list_frame)
        ps_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.power_listbox = tk.Listbox(ps_list_frame, yscrollcommand=ps_scroll.set, font=('Arial', 11))
        self.power_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ps_scroll.config(command=self.power_listbox.yview)
        self.power_listbox.bind('<<ListboxSelect>>', self.on_power_select)

        self.power_systems_text = tk.Text(ps_list_frame, height=10, wrap=tk.WORD, state='disabled', font=('Arial', 10))

        # Initial load
        self.load_lore()
        self.load_power_systems()
    
    def create_progression_tab(self):
        """Progression tracking per story arc"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📈 Progression")

        # Scrollable area
        canvas = tk.Canvas(tab)
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Container for progression widgets
        content = ttk.Frame(scroll_frame, padding=20)
        content.pack(fill=tk.BOTH, expand=True)

        self.progression_widgets = {}

        # Arc selector
        ttk.Label(content, text="Select Arc:", font=('Arial', 11, 'bold')).grid(row=0, column=0, sticky='w')
        self.progression_widgets['arc_selector'] = ttk.Combobox(content, width=50, state='readonly')
        self.progression_widgets['arc_selector'].grid(row=0, column=1, sticky='w', padx=(10, 0))
        self.progression_widgets['arc_selector'].bind('<<ComboboxSelected>>', self.on_arc_selected)

        # After creating arc selector
        arc_controls = ttk.Frame(content)
        arc_controls.grid(row=0, column=2, sticky='w', padx=(10,0))
        ttk.Button(arc_controls, text="➕ Add Arc", command=self.add_arc_dialog, width=12).pack(side=tk.LEFT, padx=3)
        ttk.Button(arc_controls, text="🗑️ Delete Arc", command=self.delete_arc, width=12).pack(side=tk.LEFT, padx=3)

        # Arc name & number
        ttk.Label(content, text="Arc Name:", font=('Arial', 11, 'bold')).grid(row=1, column=0, sticky='w', pady=(10, 5))
        self.progression_widgets['arc_name'] = ttk.Entry(content, width=60)
        self.progression_widgets['arc_name'].grid(row=1, column=1, sticky='w', padx=(10, 0), pady=(10, 5))

        ttk.Label(content, text="Arc Number:", font=('Arial', 11, 'bold')).grid(row=2, column=0, sticky='w', pady=(0, 10))
        self.progression_widgets['arc_number'] = ttk.Entry(content, width=10)
        self.progression_widgets['arc_number'].grid(row=2, column=1, sticky='w', padx=(10, 0), pady=(0, 10))

        # Progression text fields
        text_fields = [
            ('current_plot_points', 'Current Plot Points', 6,
             "What's happening now? Active storylines, conflicts, immediate goals..."),
            ('completed_plot_points', 'Completed Plot Points', 6,
             "What has been resolved? Major events that have concluded..."),
            ('character_development', 'Character Development Notes', 7,
             "How are characters changing? Growth, relationships, realizations..."),
            ('foreshadowing', 'Active Foreshadowing', 6,
             "Hints and setup for future events, mysteries to be revealed..."),
            ('unresolved_threads', 'Unresolved Plot Threads', 6,
             "Open questions, unfinished business, mysteries to address..."),
            ('next_major_events', 'Planned Major Events', 6,
             "What's coming next? Major plot points, confrontations, revelations..."),
            ('pacing_notes', 'Pacing & Structure Notes', 5,
             "Notes on story rhythm, when to speed up/slow down...")
        ]

        row = 3
        for field, label, height, placeholder in text_fields:
            ttk.Label(content, text=label, font=('Arial', 12, 'bold')).grid(row=row, column=0, columnspan=2, pady=(15, 5), sticky='w')
            row += 1

            ttk.Label(content, text=placeholder, font=('Arial', 9, 'italic'), foreground='gray').grid(
                row=row, column=0, columnspan=2, pady=(0, 5), sticky='w')
            row += 1

            text_frame = ttk.Frame(content)
            text_frame.grid(row=row, column=0, columnspan=2, sticky='ew', pady=(0, 10))

            text_scroll = ttk.Scrollbar(text_frame)
            text_scroll.pack(side=tk.RIGHT, fill=tk.Y)

            self.progression_widgets[field] = tk.Text(
                text_frame,
                width=100,
                height=height,
                font=('Arial', 10),
                wrap=tk.WORD,
                yscrollcommand=text_scroll.set
            )
            self.progression_widgets[field].pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            text_scroll.config(command=self.progression_widgets[field].yview)

            row += 1

        # Action buttons
        button_frame = ttk.Frame(content)
        button_frame.grid(row=row, column=0, columnspan=2, pady=25)

        ttk.Button(button_frame, text="💾 Save Progression Data", command=self.save_progression, width=25).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="📊 View Timeline", command=self.show_timeline, width=20).pack(side=tk.LEFT, padx=5)

        content.columnconfigure(1, weight=1)

        # Populate arcs for current story
        self.load_progression()

    def create_chapter_generator_tab(self):
        """Enhanced chapter generation tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="🎨 Generate Chapter")
        
        # Split view
        paned = ttk.PanedWindow(tab, orient=tk.VERTICAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top: Generation settings
        top_frame = ttk.Frame(paned)
        paned.add(top_frame, weight=1)
        
        settings_frame = ttk.LabelFrame(top_frame, text="Chapter Generation Settings", padding=20)
        settings_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a grid layout
        row = 0
        
        # Chapter number
        ttk.Label(
            settings_frame,
            text="Chapter Number:",
            font=('Arial', 11, 'bold')
        ).grid(row=row, column=0, sticky='w', pady=8)
        
        chapter_frame = ttk.Frame(settings_frame)
        chapter_frame.grid(row=row, column=1, sticky='w', pady=8, padx=(10, 0))
        
        self.gen_chapter_number = ttk.Entry(chapter_frame, width=10, font=('Arial', 11))
        self.gen_chapter_number.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            chapter_frame,
            text="Auto (Next)",
            command=self.set_next_chapter_number,
            width=12
        ).pack(side=tk.LEFT)
        row += 1
        
        # Chapter title
        ttk.Label(
            settings_frame,
            text="Chapter Title:",
            font=('Arial', 11, 'bold')
        ).grid(row=row, column=0, sticky='w', pady=8)
        
        ttk.Label(
            settings_frame,
            text="(Optional - leave blank for 'Chapter X')",
            font=('Arial', 9, 'italic'),
            foreground='gray'
        ).grid(row=row, column=2, sticky='w', padx=(10, 0))
        
        self.gen_chapter_title = ttk.Entry(settings_frame, width=50, font=('Arial', 11))
        self.gen_chapter_title.grid(row=row, column=1, sticky='ew', pady=8, padx=(10, 0))
        row += 1
        
        # POV Character
        ttk.Label(
            settings_frame,
            text="POV Character:",
            font=('Arial', 11, 'bold')
        ).grid(row=row, column=0, sticky='w', pady=8)
        
        self.gen_pov_character = ttk.Combobox(settings_frame, width=48)
        self.gen_pov_character.grid(row=row, column=1, sticky='ew', pady=8, padx=(10, 0))
        row += 1
        
        # Plot directive
        ttk.Label(
            settings_frame,
            text="Plot Directive:",
            font=('Arial', 11, 'bold')
        ).grid(row=row, column=0, sticky='nw', pady=8)
        
        ttk.Label(
            settings_frame,
            text="What should happen in this chapter? Be specific!",
            font=('Arial', 9, 'italic'),
            foreground='gray'
        ).grid(row=row+1, column=0, sticky='nw', pady=0)
        
        plot_frame = ttk.Frame(settings_frame)
        plot_frame.grid(row=row, column=1, rowspan=2, sticky='ew', pady=8, padx=(10, 0))
        
        plot_scroll = ttk.Scrollbar(plot_frame)
        plot_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.gen_plot_directive = tk.Text(
            plot_frame,
            width=50,
            height=6,
            font=('Arial', 10),
            wrap=tk.WORD,
            yscrollcommand=plot_scroll.set
        )
        self.gen_plot_directive.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        plot_scroll.config(command=self.gen_plot_directive.yview)
        row += 2
        
        # Previous chapter summary
        ttk.Label(
            settings_frame,
            text="Previous Chapter Summary:",
            font=('Arial', 11, 'bold')
        ).grid(row=row, column=0, sticky='nw', pady=8)
        
        ttk.Label(
            settings_frame,
            text="(Optional - helps with continuity)",
            font=('Arial', 9, 'italic'),
            foreground='gray'
        ).grid(row=row+1, column=0, sticky='nw', pady=0)
        
        prev_frame = ttk.Frame(settings_frame)
        prev_frame.grid(row=row, column=1, rowspan=2, sticky='ew', pady=8, padx=(10, 0))
        
        prev_scroll = ttk.Scrollbar(prev_frame)
        prev_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.gen_previous_summary = tk.Text(
            prev_frame,
            width=50,
            height=4,
            font=('Arial', 10),
            wrap=tk.WORD,
            yscrollcommand=prev_scroll.set
        )
        self.gen_previous_summary.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        prev_scroll.config(command=self.gen_previous_summary.yview)
        row += 2
        
        # AI Parameters
        params_frame = ttk.LabelFrame(settings_frame, text="AI Generation Parameters", padding=15)
        params_frame.grid(row=row, column=0, columnspan=3, sticky='ew', pady=15)
        
        param_row = 0
        
        # Temperature
        ttk.Label(
            params_frame,
            text="Creativity Level (Temperature):",
            font=('Arial', 10, 'bold')
        ).grid(row=param_row, column=0, sticky='w', padx=5)
        
        temp_frame = ttk.Frame(params_frame)
        temp_frame.grid(row=param_row, column=1, sticky='ew', padx=5)
        
        self.gen_temperature = tk.Scale(
            temp_frame,
            from_=0.5, to=1.0,
            orient=tk.HORIZONTAL,
            resolution=0.05,
            length=250,
            tickinterval=0.1
        )
        self.gen_temperature.set(0.85)
        self.gen_temperature.pack(side=tk.LEFT)
        
        ttk.Label(
            temp_frame,
            text="Lower = More focused | Higher = More creative",
            font=('Arial', 9, 'italic')
        ).pack(side=tk.LEFT, padx=10)
        param_row += 1
        
        # Max words
        ttk.Label(
            params_frame,
            text="Target Word Count:",
            font=('Arial', 10, 'bold')
        ).grid(row=param_row, column=0, sticky='w', padx=5, pady=10)
        
        words_frame = ttk.Frame(params_frame)
        words_frame.grid(row=param_row, column=1, sticky='w', padx=5, pady=10)
        
        self.gen_max_words = ttk.Combobox(
            words_frame,
            width=15,
            values=['2000', '2500', '3000', '3500', '4000', '5000'],
            state='readonly'
        )
        self.gen_max_words.set('3000')
        self.gen_max_words.pack(side=tk.LEFT)
        
        ttk.Label(
            words_frame,
            text="words",
            font=('Arial', 10)
        ).pack(side=tk.LEFT, padx=5)
        
        row += 1
        
        # Action buttons
        button_frame = ttk.Frame(settings_frame)
        button_frame.grid(row=row, column=0, columnspan=3, pady=20)
        
        self.generate_btn = ttk.Button(
            button_frame,
            text="🎨 Generate Chapter",
            command=self.generate_chapter,
            width=25
        )
        self.generate_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="👁️ Preview Prompt",
            command=self.view_generation_prompt,
            width=20
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="📋 Load Previous Chapter",
            command=self.load_previous_chapter_summary,
            width=25
        ).pack(side=tk.LEFT, padx=5)
        
        settings_frame.columnconfigure(1, weight=1)
        
        # Bottom: Generated chapter display
        bottom_frame = ttk.Frame(paned)
        paned.add(bottom_frame, weight=3)
        
        output_frame = ttk.LabelFrame(bottom_frame, text="Generated Chapter", padding=10)
        output_frame.pack(fill=tk.BOTH, expand=True)
        
        # Progress bar
        self.gen_progress = ttk.Progressbar(output_frame, mode='indeterminate')
        self.gen_progress.pack(fill=tk.X, pady=(0, 10))
        
        # Status label
        self.gen_status_label = ttk.Label(
            output_frame,
            text="Ready to generate",
            font=('Arial', 10, 'italic')
        )
        self.gen_status_label.pack(pady=5)
        
        # Output text
        text_frame = ttk.Frame(output_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        text_scroll = ttk.Scrollbar(text_frame)
        text_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.gen_output = tk.Text(
            text_frame,
            yscrollcommand=text_scroll.set,
            font=('Georgia', 11),
            wrap=tk.WORD,
            padx=20,
            pady=15
        )
        self.gen_output.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        text_scroll.config(command=self.gen_output.yview)
        
        # Output action buttons
        output_button_frame = ttk.Frame(output_frame)
        output_button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(
            output_button_frame,
            text="💾 Save Chapter",
            command=self.save_generated_chapter,
            width=18
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            output_button_frame,
            text="🔄 Regenerate",
            command=self.generate_chapter,
            width=18
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            output_button_frame,
            text="📋 Copy to Clipboard",
            command=self.copy_chapter_to_clipboard,
            width=20
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            output_button_frame,
            text="📄 Export as TXT",
            command=self.export_chapter_txt,
            width=18
        ).pack(side=tk.LEFT, padx=5)
    
    def create_chapters_list_tab(self):
        """Enhanced chapters list tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📚 Chapters List")
        
        # Top controls
        control_frame = ttk.Frame(tab)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(
            control_frame,
            text="All Chapters",
            font=('Arial', 14, 'bold')
        ).pack(side=tk.LEFT, padx=5)
        
        # Filter by status
        ttk.Label(control_frame, text="Status:").pack(side=tk.LEFT, padx=(30, 5))
        self.chapter_status_filter = ttk.Combobox(
            control_frame,
            width=12,
            values=['All', 'draft', 'complete', 'revised'],
            state='readonly'
        )
        self.chapter_status_filter.set('All')
        self.chapter_status_filter.pack(side=tk.LEFT, padx=5)
        self.chapter_status_filter.bind('<<ComboboxSelected>>', lambda e: self.load_chapters_list())
        
        ttk.Button(
            control_frame,
            text="🔄 Refresh",
            command=self.load_chapters_list,
            width=12
        ).pack(side=tk.LEFT, padx=5)

    def load_chapters_list(self):
        """Load chapters into the chapters tree for the current story."""
        try:
            if not self.current_story_id:
                # Clear tree
                try:
                    for i in self.chapters_tree.get_children():
                        self.chapters_tree.delete(i)
                except Exception:
                    pass
                return

            status_filter = getattr(self, 'chapter_status_filter', None)
            status = status_filter.get() if status_filter else 'All'

            chapters = self.db.get_all_chapters(self.current_story_id)
            # Clear tree
            for i in self.chapters_tree.get_children():
                self.chapters_tree.delete(i)

            for ch in chapters:
                ch_status = ch.get('status', 'draft')
                if status != 'All' and ch_status != status:
                    continue
                cid = ch.get('id')
                chap_num = ch.get('chapter_number')
                title = ch.get('title') or ''
                words = ch.get('word_count') or 0
                pov = ch.get('pov_character') or ''
                created = ch.get('created_at') or ''
                self.chapters_tree.insert('', 'end', iid=str(cid), text=str(cid), values=(chap_num, title, words, pov, ch_status, created))
            self.update_status(f'Loaded {len(chapters)} chapters')
        except Exception as e:
            messagebox.showerror('Error', f'Failed to load chapters: {e}')
        
        ttk.Button(
            control_frame,
            text="📊 Statistics",
            command=self.show_chapter_stats,
            width=15
        ).pack(side=tk.RIGHT, padx=5)
        
        # Chapters tree view
        tree_frame = ttk.Frame(tab)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Treeview with scrollbar
        tree_scroll = ttk.Scrollbar(tree_frame)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        columns = ('Chapter', 'Title', 'Words', 'POV', 'Status', 'Date')
        self.chapters_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show='tree headings',
            height=12,
            yscrollcommand=tree_scroll.set
        )
        
        self.chapters_tree.heading('#0', text='ID')
        self.chapters_tree.heading('Chapter', text='Chapter #')
        self.chapters_tree.heading('Title', text='Title')
        self.chapters_tree.heading('Words', text='Word Count')
        self.chapters_tree.heading('POV', text='POV')
        self.chapters_tree.heading('Status', text='Status')
        self.chapters_tree.heading('Date', text='Created')
        
        self.chapters_tree.column('#0', width=50)
        self.chapters_tree.column('Chapter', width=80)
        self.chapters_tree.column('Title', width=350)
        self.chapters_tree.column('Words', width=100)
        self.chapters_tree.column('POV', width=150)
        self.chapters_tree.column('Status', width=100)
        self.chapters_tree.column('Date', width=120)
        
        self.chapters_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.config(command=self.chapters_tree.yview)
        
        self.chapters_tree.bind('<Double-1>', self.view_chapter_from_list)
        self.chapters_tree.bind('<<TreeviewSelect>>', self.on_chapter_tree_select)
        
        # Chapter viewer/editor
        viewer_frame = ttk.LabelFrame(tab, text="Chapter Content", padding=10)
        viewer_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        viewer_scroll = ttk.Scrollbar(viewer_frame)
        viewer_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.chapter_viewer = tk.Text(
            viewer_frame,
            yscrollcommand=viewer_scroll.set,
            font=('Georgia', 11),
            wrap=tk.WORD,
            padx=20,
            pady=15
        )
        self.chapter_viewer.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        viewer_scroll.config(command=self.chapter_viewer.yview)
        
        # Viewer action buttons
        viewer_button_frame = ttk.Frame(viewer_frame)
        viewer_button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(
            viewer_button_frame,
            text="✏️ Edit Chapter",
            command=self.edit_selected_chapter,
            width=18
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            viewer_button_frame,
            text="🗑️ Delete Chapter",
            command=self.delete_selected_chapter,
            width=18
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            viewer_button_frame,
            text="📄 Export Chapter",
            command=self.export_selected_chapter,
            width=18
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            viewer_button_frame,
            text="✅ Mark as Complete",
            command=self.mark_chapter_complete,
            width=20
        ).pack(side=tk.LEFT, padx=5)

    def view_chapter_from_list(self, event=None):
        """Open selected chapter in the viewer on double-click."""
        try:
            sel = self.chapters_tree.selection()
            if not sel:
                return
            cid = sel[0]
            chapter = self.db.get_chapter(self.current_story_id, None)
            # db.get_chapter expects story_id and chapter_number; try by id instead
            try:
                # If db has method to fetch by id, use get_chapter_by_id if available
                chapter = self.db.get_chapter(self.current_story_id, int(self.chapters_tree.set(cid, 'Chapter')))
            except Exception:
                # Fallback: try reading from tree values
                vals = self.chapters_tree.item(cid, 'values')
                chap_num = int(vals[0]) if vals else None
                if chap_num is not None:
                    chapter = self.db.get_chapter(self.current_story_id, chap_num)

            if chapter:
                content = chapter.get('content') or ''
                self.chapter_viewer.config(state=tk.NORMAL)
                self.chapter_viewer.delete('1.0', tk.END)
                self.chapter_viewer.insert('1.0', content)
                self.chapter_viewer.config(state=tk.DISABLED)
        except Exception as e:
            messagebox.showerror('Error', f'Failed to open chapter: {e}')

    def on_chapter_tree_select(self, event=None):
        try:
            sel = self.chapters_tree.selection()
            if not sel:
                return
            cid = sel[0]
            # Load viewer for selected
            vals = self.chapters_tree.item(cid, 'values')
            chap_num = int(vals[0]) if vals else None
            if chap_num is not None:
                ch = self.db.get_chapter(self.current_story_id, chap_num)
                if ch:
                    self.chapter_viewer.config(state=tk.NORMAL)
                    self.chapter_viewer.delete('1.0', tk.END)
                    self.chapter_viewer.insert('1.0', ch.get('content') or '')
                    self.chapter_viewer.config(state=tk.DISABLED)
        except Exception:
            pass

    def edit_selected_chapter(self):
        """Open an editor to modify the selected chapter's content and save changes."""
        try:
            sel = self.chapters_tree.selection()
            if not sel:
                messagebox.showwarning('No Selection', 'Select a chapter to edit.')
                return
            cid = sel[0]
            vals = self.chapters_tree.item(cid, 'values')
            chap_num = int(vals[0]) if vals else None
            chapter = None
            if chap_num is not None:
                chapter = self.db.get_chapter(self.current_story_id, chap_num)

            if not chapter:
                messagebox.showerror('Error', 'Chapter data not found.')
                return

            dlg = tk.Toplevel(self.window)
            dlg.title(f'Edit Chapter {chap_num}')
            dlg.geometry('800x600')
            txt = tk.Text(dlg, wrap=tk.WORD)
            txt.insert('1.0', chapter.get('content') or '')
            txt.pack(fill=tk.BOTH, expand=True)

            def do_save():
                content = txt.get('1.0', tk.END).rstrip()
                title = chapter.get('title') or ''
                pov = chapter.get('pov_character') or ''
                word_count = len(content.split())
                try:
                    self.db.save_chapter(self.current_story_id, chap_num, content, title=title, word_count=word_count, pov_character=pov)
                    messagebox.showinfo('Saved', f'Chapter {chap_num} saved.')
                    dlg.destroy()
                    self.load_chapters_list()
                except Exception as e:
                    messagebox.showerror('Save Error', f'Failed to save chapter: {e}')

            btns = ttk.Frame(dlg)
            btns.pack(fill=tk.X)
            ttk.Button(btns, text='Save', command=do_save).pack(side=tk.LEFT, padx=6, pady=6)
            ttk.Button(btns, text='Cancel', command=dlg.destroy).pack(side=tk.LEFT, padx=6, pady=6)

        except Exception as e:
            messagebox.showerror('Error', f'Failed to edit chapter: {e}')

    def delete_selected_chapter(self):
        try:
            sel = self.chapters_tree.selection()
            if not sel:
                messagebox.showwarning('No Selection', 'Select a chapter to delete.')
                return
            cid = sel[0]
            vals = self.chapters_tree.item(cid, 'values')
            chap_num = int(vals[0]) if vals else None
            if chap_num is None:
                messagebox.showerror('Error', 'Could not determine chapter number.')
                return
            confirm = messagebox.askyesno('Confirm Delete', f'Are you sure you want to delete chapter {chap_num}?')
            if not confirm:
                return
            # find chapter id by querying chapters list
            chapters = self.db.get_all_chapters(self.current_story_id)
            chapter_id = None
            for ch in chapters:
                if ch.get('chapter_number') == chap_num:
                    chapter_id = ch.get('id')
                    break
            if chapter_id:
                self.db.delete_chapter(chapter_id)
                messagebox.showinfo('Deleted', f'Chapter {chap_num} deleted.')
                self.load_chapters_list()
        except Exception as e:
            messagebox.showerror('Error', f'Failed to delete chapter: {e}')

    def mark_chapter_complete(self):
        try:
            sel = self.chapters_tree.selection()
            if not sel:
                messagebox.showwarning('No Selection', 'Select a chapter to mark complete.')
                return
            cid = sel[0]
            vals = self.chapters_tree.item(cid, 'values')
            chap_num = int(vals[0]) if vals else None
            if chap_num is None:
                return
            # fetch chapter and save with status 'complete'
            chapters = self.db.get_all_chapters(self.current_story_id)
            for ch in chapters:
                if ch.get('chapter_number') == chap_num:
                    content = ch.get('content') or ''
                    title = ch.get('title') or ''
                    pov = ch.get('pov_character') or ''
                    word_count = ch.get('word_count') or len(content.split())
                    self.db.save_chapter(self.current_story_id, chap_num, content, title=title, word_count=word_count, pov_character=pov, status='complete')
                    messagebox.showinfo('Marked', f'Chapter {chap_num} marked as complete.')
                    self.load_chapters_list()
                    break
        except Exception as e:
            messagebox.showerror('Error', f'Failed to mark chapter complete: {e}')

    def run(self):
        """Start the Tk main loop (application entry point)."""
        try:
            self.window.mainloop()
        except Exception:
            try:
                self.window.destroy()
            except Exception:
                pass
    
    # ==================== THEME MANAGEMENT ====================
    
    def apply_theme(self):
        """Apply current theme to all widgets with comprehensive styling"""
        theme = self.theme_manager.get_theme()
        
        # Configure main window
        self.window.configure(bg=theme['bg'])
        
        # Configure ttk styles
        style = ttk.Style(self.window)
        try:
            style.theme_use('clam')  # 'clam' or 'alt' often looks cleaner
        except Exception:
            pass

        # Configure global fonts and padding
        default_font = ('Segoe UI', 10)  # or 'Arial' depending on platform
        self.window.option_add("*Font", default_font)
        style.configure('TButton', padding=(8,6), relief='flat', background='#2b7cff', foreground='white')
        style.map('TButton',
                  background=[('active', '#1155cc')],
                  foreground=[('disabled', 'gray')])
        # Notebook tab padding
        style.configure('TNotebook.Tab', padding=[12, 8])
        
        # ===== FRAMES =====
        style.configure('TFrame', background=theme['frame_bg'])
        style.configure('TLabelframe', 
                       background=theme['labelframe_bg'],
                       foreground=theme['labelframe_fg'],
                       bordercolor=theme['labelframe_border'],
                       relief='solid')
        style.configure('TLabelframe.Label',
                       background=theme['labelframe_bg'],
                       foreground=theme['labelframe_fg'],
                       font=('Arial', 10, 'bold'))
        
        # ===== LABELS =====
        style.configure('TLabel',
                       background=theme['frame_bg'],
                       foreground=theme['fg'])
        
        # ===== BUTTONS =====
        style.configure('TButton',
                       background=theme['button_bg'],
                       foreground=theme['button_fg'],
                       bordercolor=theme['button_border'],
                       lightcolor=theme['button_bg'],
                       darkcolor=theme['button_border'],
                       borderwidth=1,
                       focuscolor=theme['focus_border'],
                       relief='raised',
                       padding=(10, 5))
        
        style.map('TButton',
                 background=[('active', theme['button_hover_bg']),
                           ('pressed', theme['button_active_bg']),
                           ('disabled', theme['disabled_bg'])],
                 foreground=[('disabled', theme['disabled_fg'])],
                 bordercolor=[('focus', theme['focus_border'])])
        
        # ===== ENTRIES =====
        style.configure('TEntry',
                       fieldbackground=theme['input_bg'],
                       foreground=theme['input_fg'],
                       bordercolor=theme['input_border'],
                       lightcolor=theme['input_bg'],
                       darkcolor=theme['input_border'],
                       insertcolor=theme['text_cursor'],
                       borderwidth=1,
                       relief='solid')
        
        style.map('TEntry',
                 bordercolor=[('focus', theme['input_focus_border'])],
                 lightcolor=[('focus', theme['accent_light'])])
        
        # ===== COMBOBOX =====
        style.configure('TCombobox',
                       fieldbackground=theme['input_bg'],
                       foreground=theme['input_fg'],
                       background=theme['input_bg'],
                       bordercolor=theme['input_border'],
                       arrowcolor=theme['fg'],
                       borderwidth=1,
                       relief='solid')
        
        style.map('TCombobox',
                 fieldbackground=[('readonly', theme['input_bg'])],
                 selectbackground=[('readonly', theme['input_bg'])],
                 selectforeground=[('readonly', theme['input_fg'])],
                 bordercolor=[('focus', theme['input_focus_border'])])
        
        # ===== NOTEBOOK (TABS) =====
        style.configure('TNotebook',
                       background=theme['bg'],
                       borderwidth=0,
                       tabmargins=[2, 5, 2, 0])
        
        style.configure('TNotebook.Tab',
                       background=theme['tab_bg'],
                       foreground=theme['tab_fg'],
                       padding=[20, 10],
                       borderwidth=1,
                       focuscolor='')
        
        style.map('TNotebook.Tab',
                 background=[('selected', theme['tab_selected_bg']),
                           ('active', theme['tab_hover_bg'])],
                 foreground=[('selected', theme['tab_selected_fg']),
                           ('active', theme['fg'])],
                 expand=[('selected', [1, 1, 1, 0])])
        
        # ===== PROGRESSBAR =====
        style.configure('TProgressbar',
                       background=theme['accent'],
                       troughcolor=theme['tertiary_bg'],
                       bordercolor=theme['border'],
                       lightcolor=theme['accent'],
                       darkcolor=theme['accent'])
        
        # ===== SEPARATOR =====
        style.configure('TSeparator',
                       background=theme['separator'])
        
        # ===== SCROLLBAR =====
        style.configure('TScrollbar',
                       background=theme['scrollbar_bg'],
                       troughcolor=theme['scrollbar_bg'],
                       bordercolor=theme['border'],
                       arrowcolor=theme['fg'])
        
        style.map('TScrollbar',
                 background=[('active', theme['scrollbar_active'])],
                 arrowcolor=[('active', theme['fg'])])
        
        # ===== TREEVIEW =====
        style.configure('Treeview',
                       background=theme['list_bg'],
                       foreground=theme['list_fg'],
                       fieldbackground=theme['list_bg'],
                       borderwidth=1,
                       relief='solid')
        
        style.map('Treeview',
                 background=[('selected', theme['list_select_bg'])],
                 foreground=[('selected', theme['list_select_fg'])])
        
        style.configure('Treeview.Heading',
                       background=theme['header_bg'],
                       foreground=theme['header_fg'],
                       borderwidth=1,
                       relief='raised')
        
        style.map('Treeview.Heading',
                 background=[('active', theme['hover_bg'])])
        
        # ===== PANEDWINDOW =====
        style.configure('TPanedwindow',
                       background=theme['bg'])
        style.configure('Sash',
                       sashthickness=6,
                       sashrelief='flat',
                       background=theme['separator'])
        
        # ===== TEXT WIDGETS =====
        text_widgets = []
        
        # Collect all text widgets
        if hasattr(self, 'overview_synopsis'):
            text_widgets.append(self.overview_synopsis)
        if hasattr(self, 'gen_plot_directive'):
            text_widgets.append(self.gen_plot_directive)
        if hasattr(self, 'gen_previous_summary'):
            text_widgets.append(self.gen_previous_summary)
        if hasattr(self, 'gen_output'):
            text_widgets.append(self.gen_output)
        if hasattr(self, 'chapter_viewer'):
            text_widgets.append(self.chapter_viewer)
        if hasattr(self, 'power_systems_text'):
            text_widgets.append(self.power_systems_text)
        if hasattr(self, 'lore_text'):
            text_widgets.append(self.lore_text)
        if hasattr(self, 'organizations_text'):
            text_widgets.append(self.organizations_text)
        
        for widget in text_widgets:
            try:
                widget.configure(
                    bg=theme['text_bg'],
                    fg=theme['text_fg'],
                    insertbackground=theme['text_cursor'],
                    selectbackground=theme['text_selection_bg'],
                    selectforeground=theme['text_selection_fg'],
                    borderwidth=1,
                    relief='solid'
                )
            except Exception:
                pass
        
        # Character form text widgets
        if hasattr(self, 'char_widgets'):
            for widget in self.char_widgets.values():
                if isinstance(widget, tk.Text):
                    try:
                        widget.configure(
                            bg=theme['text_bg'],
                            fg=theme['text_fg'],
                            insertbackground=theme['text_cursor'],
                            selectbackground=theme['text_selection_bg'],
                            selectforeground=theme['text_selection_fg']
                        )
                    except Exception:
                        pass
        
        # Location form text widgets
        if hasattr(self, 'location_widgets'):
            for widget in self.location_widgets.values():
                if isinstance(widget, tk.Text):
                    try:
                        widget.configure(
                            bg=theme['text_bg'],
                            fg=theme['text_fg'],
                            insertbackground=theme['text_cursor'],
                            selectbackground=theme['text_selection_bg'],
                            selectforeground=theme['text_selection_fg']
                        )
                    except Exception:
                        pass
        
        # Creature form text widgets
        if hasattr(self, 'creature_widgets'):
            for widget in self.creature_widgets.values():
                if isinstance(widget, tk.Text):
                    try:
                        widget.configure(
                            bg=theme['text_bg'],
                            fg=theme['text_fg'],
                            insertbackground=theme['text_cursor'],
                            selectbackground=theme['text_selection_bg'],
                            selectforeground=theme['text_selection_fg']
                        )
                    except Exception:
                        pass
        
        # Progression form text widgets
        if hasattr(self, 'progression_widgets'):
            for widget in self.progression_widgets.values():
                if isinstance(widget, tk.Text):
                    try:
                        widget.configure(
                            bg=theme['text_bg'],
                            fg=theme['text_fg'],
                            insertbackground=theme['text_cursor'],
                            selectbackground=theme['text_selection_bg'],
                            selectforeground=theme['text_selection_fg']
                        )
                    except Exception:
                        pass
        
        # ===== LISTBOX WIDGETS =====
        listbox_widgets = []
        
        if hasattr(self, 'story_listbox'):
            listbox_widgets.append(self.story_listbox)
        if hasattr(self, 'char_listbox'):
            listbox_widgets.append(self.char_listbox)
        if hasattr(self, 'location_listbox'):
            listbox_widgets.append(self.location_listbox)
        if hasattr(self, 'creature_listbox'):
            listbox_widgets.append(self.creature_listbox)
        
        for widget in listbox_widgets:
            try:
                widget.configure(
                    bg=theme['list_bg'],
                    fg=theme['list_fg'],
                    selectbackground=theme['list_select_bg'],
                    selectforeground=theme['list_select_fg'],
                    borderwidth=1,
                    relief='solid',
                    highlightthickness=0
                )
            except Exception:
                pass
        
        # ===== ENTRY WIDGETS =====
        entry_widgets = []
        
        if hasattr(self, 'overview_title'):
            entry_widgets.append(self.overview_title)
        if hasattr(self, 'overview_genre'):
            entry_widgets.append(self.overview_genre)
        if hasattr(self, 'overview_themes'):
            entry_widgets.append(self.overview_themes)
        if hasattr(self, 'overview_tone'):
            entry_widgets.append(self.overview_tone)
        if hasattr(self, 'overview_style'):
            entry_widgets.append(self.overview_style)
        if hasattr(self, 'gen_chapter_number'):
            entry_widgets.append(self.gen_chapter_number)
        if hasattr(self, 'gen_chapter_title'):
            entry_widgets.append(self.gen_chapter_title)
        if hasattr(self, 'story_search'):
            entry_widgets.append(self.story_search)
        
        for widget in entry_widgets:
            try:
                widget.configure(
                    background=theme['input_bg'],
                    foreground=theme['input_fg']
                )
            except Exception:
                pass
        
        # ===== STATUS BAR =====
        if hasattr(self, 'status_bar'):
            self.status_bar.configure(
                background=theme['statusbar_bg'],
                foreground=theme['statusbar_fg']
            )
        
        if hasattr(self, 'ai_status_label'):
            self.ai_status_label.configure(
                background=theme['statusbar_bg'],
                foreground=theme['statusbar_fg']
            )
        
        # ===== CANVAS WIDGETS =====
        canvas_widgets = []
        for widget in self.window.winfo_children():
            self._apply_theme_recursive(widget, theme)
        
        # Force update
        self.window.update_idletasks()
        
        # Update status message
        theme_name = self.theme_manager.current_theme.capitalize()
        self.update_status(f"{theme_name} theme applied successfully")
    
    def _apply_theme_recursive(self, widget, theme):
        """Recursively apply theme to all child widgets"""
        try:
            widget_class = widget.winfo_class()
            
            # Canvas
            if widget_class == 'Canvas':
                widget.configure(bg=theme['bg'], highlightthickness=0)
            
            # Frame
            elif widget_class == 'Frame':
                widget.configure(bg=theme['frame_bg'])
            
            # Label
            elif widget_class == 'Label':
                widget.configure(bg=theme['frame_bg'], fg=theme['fg'])
            
            # Entry
            elif widget_class == 'Entry':
                widget.configure(bg=theme['input_bg'], fg=theme['input_fg'],
                               insertbackground=theme['text_cursor'])
            
            # Text
            elif widget_class == 'Text':
                widget.configure(
                    bg=theme['text_bg'],
                    fg=theme['text_fg'],
                    insertbackground=theme['text_cursor'],
                    selectbackground=theme['text_selection_bg'],
                    selectforeground=theme['text_selection_fg']
                )
            
            # Listbox
            elif widget_class == 'Listbox':
                widget.configure(
                    bg=theme['list_bg'],
                    fg=theme['list_fg'],
                    selectbackground=theme['list_select_bg'],
                    selectforeground=theme['list_select_fg']
                )
            
            # Scale
            elif widget_class == 'Scale':
                widget.configure(
                    bg=theme['frame_bg'],
                    fg=theme['fg'],
                    troughcolor=theme['tertiary_bg'],
                    activebackground=theme['accent']
                )
            
            # Recurse through children
            for child in widget.winfo_children():
                self._apply_theme_recursive(child, theme)
        
        except Exception:
            pass
    
    def toggle_theme(self):
        """Toggle between light and dark theme"""
        self.theme_manager.toggle_theme()
        self.apply_theme()
    
    def set_theme(self, theme_name):
        """Set specific theme"""
        self.theme_manager.set_theme(theme_name)
        self.apply_theme()

    # ====== UI Helpers: mousewheel scrolling and media handling ======
    def _on_mousewheel(self, event):
        """Generic mousewheel handler: forwards scroll to the widget under mouse."""
        try:
            target = getattr(self, '_mousewheel_target', None)
            if target and hasattr(target, 'yview_scroll'):
                # On Windows delta is multiple of 120
                units = int(-1 * (event.delta / 120))
                target.yview_scroll(units, 'units')
        except Exception:
            pass

    def _bind_mousewheel_widget(self, widget):
        """Make a canvas-like widget receive mousewheel events when hovered."""
        try:
            def enter(e):
                self._mousewheel_target = widget
            def leave(e):
                if getattr(self, '_mousewheel_target', None) == widget:
                    self._mousewheel_target = None
            widget.bind('<Enter>', enter)
            widget.bind('<Leave>', leave)
            # Ensure global binding exists
            if not hasattr(self, '_mousewheel_bound') or not self._mousewheel_bound:
                try:
                    self.window.bind_all('<MouseWheel>', self._on_mousewheel)
                    self._mousewheel_bound = True
                except Exception:
                    pass
        except Exception:
            pass

    def add_media_ui(self, entity_type):
        """Open file dialog to attach an image/file for the currently selected entity."""
        if not self.current_story_id:
            messagebox.showwarning('No Story Selected', 'Select a story first.')
            return
        # Determine entity id depending on type
        entity_id = None
        if entity_type == 'character':
            entity_id = getattr(self, 'current_character_id', None)
        elif entity_type == 'location':
            entity_id = getattr(self, 'current_location_id', None)
        elif entity_type == 'creature':
            entity_id = getattr(self, 'current_creature_id', None)
        # If entity not saved yet, prompt to save
        if entity_id is None:
            if entity_type == 'character':
                if messagebox.askyesno('Save Character', 'This character is not saved yet. Save now?'):
                    self.save_character()
                    entity_id = getattr(self, 'current_character_id', None)
                else:
                    return
            elif entity_type == 'location':
                if messagebox.askyesno('Save Location', 'This location is not saved yet. Save now?'):
                    self.save_location()
                    entity_id = getattr(self, 'current_location_id', None)
                else:
                    return
            elif entity_type == 'creature':
                if messagebox.askyesno('Save Creature', 'This creature is not saved yet. Save now?'):
                    self.save_creature()
                    entity_id = getattr(self, 'current_creature_id', None)
                else:
                    return

        # Prompt for file
        f = filedialog.askopenfilename(title='Select Image or File', filetypes=[('Images', '*.png;*.jpg;*.jpeg;*.gif;*.bmp'), ('All files', '*.*')])
        if not f:
            return
        try:
            self.db.add_media(self.current_story_id, entity_type, entity_id, f)
            messagebox.showinfo('Media Added', 'Media added to the story and linked to the entity.')
            # Refresh any media display
            self._display_media_for_entity(entity_type, entity_id)
        except Exception as e:
            messagebox.showerror('Error', f'Failed to add media: {e}')

    def _display_media_for_entity(self, entity_type, entity_id):
        """Load and display first media item for the given entity in the right-hand form area (if available)."""
        try:
            # Determine target label widget to place thumbnail
            target_label = None
            if entity_type == 'character' and hasattr(self, 'char_media_label'):
                target_label = self.char_media_label
            elif entity_type == 'location' and hasattr(self, 'location_media_label'):
                target_label = self.location_media_label
            elif entity_type == 'creature' and hasattr(self, 'creature_media_label'):
                target_label = self.creature_media_label
            else:
                target_label = None

            media = self.db.get_media_for(self.current_story_id, entity_type=entity_type, entity_id=entity_id)
            if not media:
                if target_label:
                    try:
                        target_label.config(image='')
                        target_label.photo = None
                    except Exception:
                        pass
                return

            first = media[0]
            path = first.get('file_path')
            # Try to show image using PIL if available
            try:
                from PIL import Image, ImageTk
                img = Image.open(path)
                img.thumbnail((160, 160))
                photo = ImageTk.PhotoImage(img)
                if target_label:
                    target_label.config(image=photo)
                    target_label.photo = photo
            except Exception:
                # If PIL not available or file not an image, show filename text
                if target_label:
                    target_label.config(text=os.path.basename(path))
        except Exception:
            pass

    def select_tab_by_text(self, text_fragment: str):
        """Select a notebook tab by matching a fragment of its text label."""
        try:
            if not hasattr(self, 'notebook'):
                return
            end = self.notebook.index('end')
            for i in range(end):
                try:
                    label = str(self.notebook.tab(i, 'text') or '')
                except Exception:
                    label = ''
                if text_fragment.lower() in label.lower():
                    self.notebook.select(i)
                    return
        except Exception:
            pass
    
    # ==================== STORY MANAGEMENT ====================
    
    def load_stories(self):
        """Load all stories into the listbox"""
        self.story_listbox.delete(0, tk.END)
        stories = self.db.get_all_stories()
        
        self.stories_data = {}
        for story in stories:
            display_text = f"{story['title']}"
            self.story_listbox.insert(tk.END, display_text)
            self.stories_data[display_text] = story
    
    def filter_stories(self, event=None):
        """Filter stories based on search"""
        search_term = self.story_search.get().lower()
        self.story_listbox.delete(0, tk.END)
        
        for display_text, story in self.stories_data.items():
            if search_term in display_text.lower():
                self.story_listbox.insert(tk.END, display_text)
    
    def on_story_select(self, event):
        """Handle story selection"""
        selection = self.story_listbox.curselection()
        if not selection:
            return
        
        selected_text = self.story_listbox.get(selection[0])
        story = self.stories_data.get(selected_text)
        
        if not story:
            return
        
        self.current_story_id = story['id']
        self.load_story_data(story['id'])
        
        # Update sidebar info
        self.story_title_label.config(text=story['title'])
        
        stats_text = f"Chapters: {story['current_chapter']}\n"
        stats_text += f"Genre: {story['genre'] or 'Not set'}\n"
        stats_text += f"Status: {story['status']}"
        self.story_stats_label.config(text=stats_text)
        
        self.update_status(f"Loaded: {story['title']}")
    
    def load_story_data(self, story_id):
        """Load all data for a story into the UI"""
        story = self.db.get_story(story_id)
        
        # Load overview
        self.overview_title.delete(0, tk.END)
        self.overview_title.insert(0, story['title'])
        
        self.overview_synopsis.delete('1.0', tk.END)
        self.overview_synopsis.insert('1.0', story['synopsis'] or '')
        
        self.overview_genre.delete(0, tk.END)
        self.overview_genre.insert(0, story['genre'] or 'Light Novel / Fantasy')
        
        self.overview_themes.delete(0, tk.END)
        self.overview_themes.insert(0, story['themes'] or '')
        
        self.overview_tone.delete(0, tk.END)
        self.overview_tone.insert(0, story['tone'] or '')
        
        self.overview_style.delete(0, tk.END)
        self.overview_style.insert(0, story['writing_style'] or 'ReZero/Fate-inspired')

        # Target chapter words (numeric)
        try:
            if hasattr(self, 'overview_target_words'):
                self.overview_target_words.delete(0, tk.END)
                if story.get('target_length') is not None:
                    self.overview_target_words.insert(0, str(story.get('target_length')))
                else:
                    self.overview_target_words.insert(0, "3000")
        except Exception:
            pass

        # Load all data
        self.load_characters()
        self.load_locations()
        self.load_creatures()
        self.load_power_systems()
        self.load_lore()
        self.load_organizations()
        self.load_progression()
        self.load_chapters_list()
        
        # Update POV character dropdown
        self.update_pov_dropdown()
    
    def update_pov_dropdown(self):
        """Update POV character dropdown with current characters"""
        if not self.current_story_id:
            return
        
        characters = self.db.get_characters(self.current_story_id)
        char_names = [c['name'] for c in characters]
        self.gen_pov_character['values'] = char_names
        
        # Set default to protagonist if exists
        protagonists = [c['name'] for c in characters if c['role'] == 'Protagonist']
        if protagonists:
            self.gen_pov_character.set(protagonists[0])
    
    def new_story(self):
        """Create a new story"""
        dialog = tk.Toplevel(self.window)
        dialog.title("Create New Story")
        dialog.geometry("600x500")
        dialog.transient(self.window)
        dialog.grab_set()
        
        # Apply theme to dialog
        theme = self.theme_manager.get_theme()
        dialog.configure(bg=theme['bg'])
        
        frame = ttk.Frame(dialog, padding=30)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(
            frame,
            text="Create New Light Novel",
            font=('Arial', 16, 'bold')
        ).pack(pady=(0, 20))
        
        # Title
        ttk.Label(frame, text="Story Title:", font=('Arial', 11, 'bold')).pack(anchor='w', pady=(10, 5))
        title_entry = ttk.Entry(frame, width=60, font=('Arial', 11))
        title_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Synopsis
        ttk.Label(frame, text="Synopsis:", font=('Arial', 11, 'bold')).pack(anchor='w', pady=(10, 5))
        ttk.Label(
            frame,
            text="Brief description of your story (helps AI generate world structure)",
            font=('Arial', 9, 'italic'),
            foreground='gray'
        ).pack(anchor='w')
        
        synopsis_frame = ttk.Frame(frame)
        synopsis_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 10))
        
        synopsis_scroll = ttk.Scrollbar(synopsis_frame)
        synopsis_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        synopsis_text = tk.Text(
            synopsis_frame,
            width=60,
            height=8,
            font=('Arial', 10),
            wrap=tk.WORD,
            yscrollcommand=synopsis_scroll.set
        )
        synopsis_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        synopsis_scroll.config(command=synopsis_text.yview)
        
        # Genre
        ttk.Label(frame, text="Genre:", font=('Arial', 11, 'bold')).pack(anchor='w', pady=(10, 5))
        genre_entry = ttk.Entry(frame, width=60, font=('Arial', 11))
        genre_entry.insert(0, "Light Novel / Fantasy")
        genre_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Target chapter length
        ttk.Label(frame, text="Target chapter length (words):", font=('Arial', 11, 'bold')).pack(anchor='w', pady=(8, 4))
        target_length_entry = ttk.Entry(frame, width=30, font=('Arial', 11))
        target_length_entry.insert(0, "3000")
        target_length_entry.pack(anchor='w', pady=(0, 8))

        # Themes
        ttk.Label(frame, text="Themes (comma separated):", font=('Arial', 11, 'bold')).pack(anchor='w', pady=(8, 4))
        themes_entry = ttk.Entry(frame, width=60, font=('Arial', 11))
        themes_entry.pack(fill=tk.X, pady=(0, 8))

        # Tone
        ttk.Label(frame, text="Tone:", font=('Arial', 11, 'bold')).pack(anchor='w', pady=(8, 4))
        tone_entry = ttk.Entry(frame, width=60, font=('Arial', 11))
        tone_entry.insert(0, "Varied")
        tone_entry.pack(fill=tk.X, pady=(0, 8))

        # Writing style
        ttk.Label(frame, text="Writing style:", font=('Arial', 11, 'bold')).pack(anchor='w', pady=(8, 4))
        style_entry = ttk.Entry(frame, width=60, font=('Arial', 11))
        style_entry.insert(0, "ReZero/Fate-inspired")
        style_entry.pack(fill=tk.X, pady=(0, 8))
        
        def _create_and_open(title: str, synopsis: str, genre: str, ask_ai: bool = True,
                     target_length: int | None = None, themes: str = "",
                     tone: str = "", writing_style: str = ""):
            """
            Internal helper to create a story in the DB and open it in the UI.
            Exposed as a small helper so tests can call the same logic without
            instantiating the full dialog UI.
            """
            # Delegate to the public helper to keep logic centralized
            return self.create_and_open_story(
                title=title,
                synopsis=synopsis,
                genre=genre,
                ask_ai=ask_ai,
                target_length=target_length,
                themes=themes,
                tone=tone,
                writing_style=writing_style
            )

            # Refresh story list in UI
            try:
                self.load_stories()
            except Exception:
                pass

            # Select the newly created story and switch to Overview tab
            try:
                self.current_story_id = story_id
                try:
                    self.load_story_data(story_id)
                except Exception:
                    # load_story_data may rely on more UI state in tests; ignore
                    pass
                try:
                    self.notebook.select(0)
                except Exception:
                    pass
                try:
                    self.update_status(f"Created story: {title}")
                except Exception:
                    pass
            except Exception:
                pass

            # Inform the user
            try:
                messagebox.showinfo(
                    "Success",
                    f"Story '{title}' created successfully!\n\n"
                    "You can now:\n"
                    "• Add characters\n"
                    "• Build the world\n"
                    "• Create lore and power systems\n"
                    "• Generate chapters"
                )
            except Exception:
                pass

            # Optionally run AI analysis
            if ask_ai and synopsis:
                try:
                    if messagebox.askyesno(
                        "AI World Generation",
                        "Would you like AI to analyze your synopsis and suggest:\n"
                        "• Key characters\n"
                        "• World locations\n"
                        "• Power systems\n"
                        "• Story arcs\n\n"
                        "This may take 1-2 minutes."
                    ):
                        try:
                            self.current_story_id = story_id
                            self.load_story_data(story_id)
                            self.generate_from_synopsis()
                        except Exception:
                            pass
                except Exception:
                    pass

            return story_id

        def create():
            title = title_entry.get().strip()
            if not title:
                messagebox.showerror("Error", "Story title is required!")
                return

            synopsis = synopsis_text.get('1.0', tk.END).strip()
            genre = genre_entry.get().strip()

            # Gather additional fields
            try:
                tl = int(target_length_entry.get().strip())
            except Exception:
                tl = None
            themes_val = themes_entry.get().strip()
            tone_val = tone_entry.get().strip()
            style_val = style_entry.get().strip()

            self.create_and_open_story(title, synopsis, genre, ask_ai=True,
                                       target_length=tl, themes=themes_val,
                                       tone=tone_val, writing_style=style_val)
            dialog.destroy()
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=20)

        ttk.Button(
            button_frame,
            text="Create Story",
            command=create,
            width=18
        ).pack(side=tk.LEFT, padx=5)

        # Explicit Save & Open Overview button
        def save_and_open():
            title = title_entry.get().strip()
            if not title:
                messagebox.showerror("Error", "Story title is required!")
                return
            synopsis = synopsis_text.get('1.0', tk.END).strip()
            genre = genre_entry.get().strip()
            try:
                tl = int(target_length_entry.get().strip())
            except Exception:
                tl = None
            themes_val = themes_entry.get().strip()
            tone_val = tone_entry.get().strip()
            style_val = style_entry.get().strip()

            self.create_and_open_story(title, synopsis, genre, ask_ai=False,
                                       target_length=tl, themes=themes_val,
                                       tone=tone_val, writing_style=style_val)
            dialog.destroy()

        ttk.Button(
            button_frame,
            text="Save & Open Overview",
            command=save_and_open,
            width=20
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="Cancel",
            command=dialog.destroy,
            width=18
        ).pack(side=tk.LEFT, padx=5)
        
        title_entry.focus()
        # Auto-save when the user closes the dialog via window manager
        def _on_close():
            # If user provided a title, create and open the story automatically
            try:
                title = title_entry.get().strip()
            except Exception:
                title = ""

            if title:
                synopsis = synopsis_text.get('1.0', tk.END).strip()
                genre = genre_entry.get().strip()
                try:
                    try:
                        tl = int(target_length_entry.get().strip())
                    except Exception:
                        tl = None
                    themes_val = themes_entry.get().strip()
                    tone_val = tone_entry.get().strip()
                    style_val = style_entry.get().strip()

                    self.create_and_open_story(title, synopsis, genre, ask_ai=False,
                                               target_length=tl, themes=themes_val,
                                               tone=tone_val, writing_style=style_val)
                except Exception:
                    pass
            else:
                try:
                    dialog.destroy()
                except Exception:
                    pass

        try:
            dialog.protocol("WM_DELETE_WINDOW", _on_close)
        except Exception:
            pass
    
    def create_and_open_story(self, title: str, synopsis: str, genre: str,
                              ask_ai: bool = True, target_length: int | None = None,
                              themes: str = "", tone: str = "",
                              writing_style: str = "ReZero/Fate-inspired"):
        """Create a story in the DB and open it in the Overview tab.

        This is exposed as a method so unit tests can call it directly without
        constructing the full dialog UI.
        """
        story_id = self.db.create_story(
            title=title,
            synopsis=synopsis,
            genre=genre,
            themes=themes,
            tone=tone,
            writing_style=writing_style,
            target_length=target_length
        )

        # Refresh story list in UI
        try:
            self.load_stories()
        except Exception:
            pass

        # Select the newly created story and switch to Overview tab
        try:
            self.current_story_id = story_id
            try:
                self.load_story_data(story_id)
            except Exception:
                pass
            try:
                self.notebook.select(0)
            except Exception:
                pass
            try:
                self.update_status(f"Created story: {title}")
            except Exception:
                pass
        except Exception:
            pass

        # Inform the user
        try:
            messagebox.showinfo(
                "Success",
                f"Story '{title}' created successfully!\n\n"
                "You can now:\n"
                "• Add characters\n"
                "• Build the world\n"
                "• Create lore and power systems\n"
                "• Generate chapters"
            )
        except Exception:
            pass

        # Optionally run AI analysis
        if ask_ai and synopsis:
            try:
                if messagebox.askyesno(
                    "AI World Generation",
                    "Would you like AI to analyze your synopsis and suggest:\n"
                    "• Key characters\n"
                    "• World locations\n"
                    "• Power systems\n"
                    "• Story arcs\n\n"
                    "This may take 1-2 minutes."
                ):
                    try:
                        self.current_story_id = story_id
                        self.load_story_data(story_id)
                        self.generate_from_synopsis()
                    except Exception:
                        pass
            except Exception:
                pass

        return story_id
    
    def select_story(self):
        """Prompt user to select a story"""
        if self.story_listbox.size() == 0:
            messagebox.showinfo(
                "No Stories",
                "No stories available. Create a new story first."
            )
            return
        
        # Switch to first tab to show story info
        self.notebook.select(0)
    
    def save_all(self):
        """Save all current changes"""
        if not self.current_story_id:
            messagebox.showwarning("No Story", "Please select a story first.")
            return
        
        try:
            # Save overview
            self.save_overview()
            
            # Save progression if changed
            self.save_progression()
            
            messagebox.showinfo("Saved", "All changes saved successfully!")
        except Exception as e:
            messagebox.showerror("Save Error", f"Error saving: {str(e)}")
    
    def save_overview(self):
        """Save story overview"""
        if not self.current_story_id:
            return
        # Collect numeric target length if available
        target_len = None
        try:
            if hasattr(self, 'overview_target_words'):
                try:
                    target_len = int(self.overview_target_words.get().strip())
                except Exception:
                    target_len = None
        except Exception:
            target_len = None

        self.db.update_story(
            self.current_story_id,
            title=self.overview_title.get(),
            synopsis=self.overview_synopsis.get('1.0', tk.END).strip(),
            genre=self.overview_genre.get(),
            themes=self.overview_themes.get(),
            tone=self.overview_tone.get(),
            writing_style=self.overview_style.get(),
            target_length=target_len
        )
        
        self.load_stories()
        self.update_status("Story information saved")
        try:
            messagebox.showinfo("Saved", "Story information saved successfully.")
        except Exception:
            pass
    
    def delete_current_story(self):
        """Delete the currently selected story"""
        if not self.current_story_id:
            messagebox.showwarning("No Selection", "Please select a story first.")
            return
        
        story = self.db.get_story(self.current_story_id)
        
        if messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete '{story['title']}'?\n\n"
            "This will delete:\n"
            "• All characters\n"
            "• All locations\n"
            "• All lore\n"
            "• All chapters\n\n"
            "This cannot be undone!"
        ):
            self.db.delete_story(self.current_story_id)
            self.current_story_id = None
            self.load_stories()
            
            # Clear all fields
            self.story_title_label.config(text="No story selected")
            self.story_stats_label.config(text="")
            
            messagebox.showinfo("Deleted", "Story deleted successfully.")
    
    # ==================== CHARACTER MANAGEMENT ====================
    
    def load_characters(self):
        """Load characters for current story"""
        if not self.current_story_id:
            return
        
        self.char_listbox.delete(0, tk.END)
        
        role_filter = self.char_role_filter.get()
        if role_filter == 'All':
            characters = self.db.get_characters(self.current_story_id)
        else:
            characters = self.db.get_characters(self.current_story_id, role=role_filter)
        
        self.characters_data = {}
        for char in characters:
            # Use emoji indicators
            role_emoji = {
                'Protagonist': '⭐',
                'Deuteragonist': '🌟',
                'Major Character': '●',
                'Supporting Character': '○',
                'Minor Character': '·',
                'Antagonist': '⚔️',
                'Love Interest': '💕',
                'Mentor': '📚',
                'Rival': '⚡'
            }.get(char['role'], '●')
            
            display_text = f"{role_emoji} {char['name']} - {char['role']}"
            self.char_listbox.insert(tk.END, display_text)
            self.characters_data[display_text] = char
    
    def on_character_select(self, event):
        """Handle character selection"""
        selection = self.char_listbox.curselection()
        if not selection:
            return
        
        selected_text = self.char_listbox.get(selection[0])
        char = self.characters_data.get(selected_text)
        
        if not char:
            return
        
        self.current_character_id = char['id']
        
        # Populate form
        self.char_widgets['name'].delete(0, tk.END)
        self.char_widgets['name'].insert(0, char['name'])
        
        self.char_widgets['role'].set(char['role'])
        
        self.char_widgets['age'].delete(0, tk.END)
        if char['age']:
            self.char_widgets['age'].insert(0, str(char['age']))
        
        self.char_widgets['gender'].set(char['gender'] or '')
        self.char_widgets['status'].set(char['status'] or 'Alive')
        
        # Text fields
        text_fields = ['appearance', 'personality', 'background', 'abilities',
                      'motivations', 'relationships', 'character_arc', 'voice_style',
                      'quirks', 'combat_style', 'equipment']
        
        for field in text_fields:
            widget = self.char_widgets[field]
            widget.delete('1.0', tk.END)
            if char[field]:
                widget.insert('1.0', char[field])
        
        self.char_widgets['importance'].set(char['importance'])
        # Show media (if any)
        try:
            self._display_media_for_entity('character', self.current_character_id)
        except Exception:
            pass
    
    def add_character(self):
        """Clear form for new character"""
        if not self.current_story_id:
            messagebox.showwarning("No Story", "Please select a story first.")
            return
        
        self.current_character_id = None
        
        # Clear all fields
        self.char_widgets['name'].delete(0, tk.END)
        self.char_widgets['role'].set('')
        self.char_widgets['age'].delete(0, tk.END)
        self.char_widgets['gender'].set('')
        self.char_widgets['status'].set('Alive')
        
        text_fields = ['appearance', 'personality', 'background', 'abilities',
                      'motivations', 'relationships', 'character_arc', 'voice_style',
                      'quirks', 'combat_style', 'equipment']
        
        for field in text_fields:
            self.char_widgets[field].delete('1.0', tk.END)
        
        self.char_widgets['importance'].set(3)
        self.char_widgets['name'].focus()
    
    def save_character(self):
        """Save character (new or update)"""
        if not self.current_story_id:
            messagebox.showwarning("No Story", "Please select a story first.")
            return
        # Gather data from the character form widgets
        name = self.char_widgets['name'].get().strip()
        role = self.char_widgets['role'].get().strip()
        if not name or not role:
            messagebox.showerror("Error", "Name and Role are required!")
            return

        char_data = {
            'age': int(self.char_widgets['age'].get()) if self.char_widgets['age'].get().strip() else None,
            'gender': self.char_widgets['gender'].get(),
            'status': self.char_widgets['status'].get(),
            'importance': int(self.char_widgets['importance'].get())
        }

        text_fields = ['appearance', 'personality', 'background', 'abilities',
                      'motivations', 'relationships', 'character_arc', 'voice_style',
                      'quirks', 'combat_style', 'equipment']

        for field in text_fields:
            widget = self.char_widgets[field]
            try:
                char_data[field] = widget.get('1.0', tk.END).strip()
            except Exception:
                # Fallback for Entry widgets
                char_data[field] = widget.get().strip()
        
        if self.current_character_id:
            # Update existing
            self.db.update_character(self.current_character_id, **char_data)
            self.db.update_character(self.current_character_id, name=name, role=role)
            message = f"Character '{name}' updated successfully!"
        else:
            # Add new
            new_id = self.db.add_character(self.current_story_id, name, role, **char_data)
            self.current_character_id = new_id
            message = f"Character '{name}' added successfully!"
        
        self.load_characters()
        self.update_pov_dropdown()
        self.update_status(message)
        messagebox.showinfo("Saved", message)
    
    def delete_character(self):
        """Delete current character"""
        if not self.current_character_id:
            messagebox.showwarning("No Selection", "Please select a character first.")
            return
        
        char = self.db.get_character(self.current_character_id)
        if messagebox.askyesno("Confirm Delete", f"Delete character '{char['name']}'?"):
            self.db.delete_character(self.current_character_id)
            self.current_character_id = None
            self.load_characters()
            self.update_pov_dropdown()
            self.add_character()  # Clear form
            self.update_status("Character deleted")
            try:
                messagebox.showinfo("Deleted", "Character deleted successfully.")
            except Exception:
                pass
    
    def ai_expand_character(self):
        """Use AI to expand character details"""
        if not self.current_character_id:
            messagebox.showwarning("No Selection", "Please select a character first.")
            return
        
        if not self.ai.test_connection():
            messagebox.showerror("AI Not Connected", "Cannot connect to Ollama. Make sure it's running.")
            return
        
        self.update_status("AI expanding character details...")
        self.window.update()
        
        try:
            result = self.world_gen.expand_character_details(
                self.current_story_id,
                self.current_character_id,
                expansion_focus="complete character profile with depth and nuance"
            )
            
            # Show result in dialog
            self.show_ai_result_dialog(
                "AI Character Expansion",
                result['raw_result'],
                "Review the AI suggestions and manually add what you like to the character form."
            )
            
            self.update_status("Character expansion complete")
            
        except Exception as e:
            messagebox.showerror("Error", f"AI generation failed: {str(e)}")
            self.update_status("AI expansion failed")
    
    # ==================== LOCATION MANAGEMENT ====================
    
    def load_locations(self):
        """Load locations for current story"""
        if not self.current_story_id:
            return
        
        self.location_listbox.delete(0, tk.END)
        
        type_filter = self.location_type_filter.get()
        if type_filter == 'All':
            locations = self.db.get_world_locations(self.current_story_id)
        else:
            locations = [loc for loc in self.db.get_world_locations(self.current_story_id)
                        if loc['type'] == type_filter]
        
        self.locations_data = {}
        for loc in locations:
            display_text = f"📍 {loc['name']} ({loc['type']})"
            self.location_listbox.insert(tk.END, display_text)
            self.locations_data[display_text] = loc
    
    def on_location_select(self, event):
        """Handle location selection"""
        selection = self.location_listbox.curselection()
        if not selection:
            return
        
        selected_text = self.location_listbox.get(selection[0])
        loc = self.locations_data.get(selected_text)
        
        if not loc:
            return
        
        self.current_location_id = loc['id']
        
        # Populate form
        self.location_widgets['name'].delete(0, tk.END)
        self.location_widgets['name'].insert(0, loc['name'])
        
        self.location_widgets['type'].set(loc['type'])
        
        text_fields = ['description', 'geography', 'climate', 'population',
                      'government', 'economy', 'culture', 'history',
                      'notable_locations', 'relationships']
        
        for field in text_fields:
            widget = self.location_widgets[field]
            widget.delete('1.0', tk.END)
            if loc[field]:
                widget.insert('1.0', loc[field])
        # Show media (if any) for this location
        try:
            self._display_media_for_entity('location', self.current_location_id)
        except Exception:
            pass
    
    def add_location(self):
        """Clear form for new location"""
        if not self.current_story_id:
            messagebox.showwarning("No Story", "Please select a story first.")
            return
        
        self.current_location_id = None
        self.location_widgets['name'].delete(0, tk.END)
        self.location_widgets['type'].set('')
        
        text_fields = ['description', 'geography', 'climate', 'population',
                      'government', 'economy', 'culture', 'history',
                      'notable_locations', 'relationships']
        
        for field in text_fields:
            self.location_widgets[field].delete('1.0', tk.END)
        
        self.location_widgets['name'].focus()
    
    def save_location(self):
        """Save location (new or update)"""
        if not self.current_story_id:
            messagebox.showwarning("No Story", "Please select a story first.")
            return
        
        name = self.location_widgets['name'].get().strip()
        loc_type = self.location_widgets['type'].get().strip()
        
        if not name or not loc_type:
            messagebox.showerror("Error", "Name and Type are required!")
            return
        
        # Gather all data
        loc_data = {}
        text_fields = ['description', 'geography', 'climate', 'population',
                      'government', 'economy', 'culture', 'history',
                      'notable_locations', 'relationships']
        
        for field in text_fields:
            loc_data[field] = self.location_widgets[field].get('1.0', tk.END).strip()
        
        if self.current_location_id:
            # Update existing
            self.db.update_world_location(self.current_location_id, name=name, type=loc_type, **loc_data)
            message = f"Location '{name}' updated successfully!"
        else:
            # Add new
            new_id = self.db.add_world_location(self.current_story_id, name, loc_type, **loc_data)
            self.current_location_id = new_id
            message = f"Location '{name}' added successfully!"
        
        self.load_locations()
        self.update_status(message)
        messagebox.showinfo("Saved", message)
    
    def delete_location(self):
        """Delete current location"""
        if not self.current_location_id:
            messagebox.showwarning("No Selection", "Please select a location first.")
            return
        
        locations = self.db.get_world_locations(self.current_story_id)
        loc = next((l for l in locations if l['id'] == self.current_location_id), None)
        
        if loc and messagebox.askyesno("Confirm Delete", f"Delete location '{loc['name']}'?"):
            cursor = self.db.conn.cursor()
            cursor.execute('DELETE FROM world_structure WHERE id = ?', (self.current_location_id,))
            self.db.conn.commit()
            
            self.current_location_id = None
            self.load_locations()
            self.add_location()
            self.update_status("Location deleted")
            try:
                messagebox.showinfo("Deleted", "Location deleted successfully.")
            except Exception:
                pass
    
    def ai_expand_location(self):
        """Use AI to expand location details"""
        if not self.current_location_id:
            messagebox.showwarning("No Selection", "Please select a location first.")
            return
        
        if not self.ai.test_connection():
            messagebox.showerror("AI Not Connected", "Cannot connect to Ollama.")
            return
        
        locations = self.db.get_world_locations(self.current_story_id)
        loc = next((l for l in locations if l['id'] == self.current_location_id), None)
        
        if not loc:
            return
        
        self.update_status("AI expanding location details...")
        self.window.update()
        
        try:
            result = self.world_gen.expand_location(
                self.current_story_id,
                loc['name'],
                loc['type'],
                loc['description'] or "A location in the story world",
                expansion_aspects=['geography', 'culture', 'history', 'economy', 'politics', 'notable_locations']
            )
            
            self.show_ai_result_dialog(
                f"AI Location Expansion: {loc['name']}",
                result['raw_result'],
                "Review the AI suggestions and manually add what you like to the location form."
            )
            
            self.update_status("Location expansion complete")
            
        except Exception as e:
            messagebox.showerror("Error", f"AI generation failed: {str(e)}")
            self.update_status("AI expansion failed")
    
    def ai_generate_location(self):
        """Generate a new location with AI"""
        if not self.current_story_id:
            messagebox.showwarning("No Story", "Please select a story first.")
            return
        
        if not self.ai.test_connection():
            messagebox.showerror("AI Not Connected", "Cannot connect to Ollama.")
            return
        
        # Prompt for location concept
        concept = self.prompt_for_input(
            "AI Generate Location",
            "Describe the location you want to generate:",
            "Example: A floating city powered by magic crystals"
        )
        
        if not concept:
            return
        
        self.update_status("AI generating location...")
        self.window.update()
        
        try:
            result = self.world_gen.expand_location(
                self.current_story_id,
                "New Location",
                "Location",
                concept,
                expansion_aspects=['geography', 'culture', 'history', 'economy', 'notable_locations']
            )
            
            self.show_ai_result_dialog(
                "AI Generated Location",
                result['raw_result'],
                "Copy the details you want and manually create the location."
            )
            
            self.update_status("Location generation complete")
            
        except Exception as e:
            messagebox.showerror("Error", f"AI generation failed: {str(e)}")
            self.update_status("Generation failed")
    
    # ==================== BESTIARY MANAGEMENT ====================
    
    def load_creatures(self):
        """Load creatures for current story"""
        if not self.current_story_id:
            return
        
        self.creature_listbox.delete(0, tk.END)
        
        # Get creatures from lore table (we'll use category='Bestiary')
        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT * FROM lore 
            WHERE story_id = ? AND category = 'Bestiary'
            ORDER BY title
        ''', (self.current_story_id,))
        
        creatures = [dict(row) for row in cursor.fetchall()]
        
        self.creatures_data = {}
        for creature in creatures:
            display_text = f"🐉 {creature['title']}"
            self.creature_listbox.insert(tk.END, display_text)
            self.creatures_data[display_text] = creature
    
    def on_creature_select(self, event):
        """Handle creature selection"""
        selection = self.creature_listbox.curselection()
        if not selection:
            return
        
        selected_text = self.creature_listbox.get(selection[0])
        creature = self.creatures_data.get(selected_text)
        
        if not creature:
            return
        
        self.current_creature_id = creature['id']
        
        # Parse content (stored as JSON-like structure)
        import json
        try:
            data = json.loads(creature['content']) if creature['content'] else {}
        except Exception:
            data = {}
        
        # Populate form
        self.creature_widgets['name'].delete(0, tk.END)
        self.creature_widgets['name'].insert(0, creature['title'])
        
        self.creature_widgets['type'].set(data.get('type', ''))
        self.creature_widgets['threat_level'].set(data.get('threat_level', 'Moderate'))
        
        text_fields = ['description', 'habitat', 'behavior', 'abilities',
                      'weaknesses', 'diet', 'lore', 'drops']
        
        for field in text_fields:
            widget = self.creature_widgets[field]
            widget.delete('1.0', tk.END)
            if field in data:
                widget.insert('1.0', data[field])
        # Show media (if any) for this creature
        try:
            self._display_media_for_entity('creature', self.current_creature_id)
        except Exception:
            pass
    
    def add_creature(self):
        """Clear form for new creature"""
        if not self.current_story_id:
            messagebox.showwarning("No Story", "Please select a story first.")
            return
        
        self.current_creature_id = None
        self.creature_widgets['name'].delete(0, tk.END)
        self.creature_widgets['type'].set('')
        self.creature_widgets['threat_level'].set('Moderate')
        
        text_fields = ['description', 'habitat', 'behavior', 'abilities',
                      'weaknesses', 'diet', 'lore', 'drops']
        
        for field in text_fields:
            self.creature_widgets[field].delete('1.0', tk.END)
        
        self.creature_widgets['name'].focus()
    
    def save_creature(self):
        """Save creature (new or update)"""
        if not self.current_story_id:
            messagebox.showwarning("No Story", "Please select a story first.")
            return
        
        name = self.creature_widgets['name'].get().strip()
        if not name:
            messagebox.showerror("Error", "Creature name is required!")
            return
        
        # Gather all data
        import json
        creature_data = {
            'type': self.creature_widgets['type'].get(),
            'threat_level': self.creature_widgets['threat_level'].get()
        }
        
        text_fields = ['description', 'habitat', 'behavior', 'abilities',
                      'weaknesses', 'diet', 'lore', 'drops']
        
        for field in text_fields:
            creature_data[field] = self.creature_widgets[field].get('1.0', tk.END).strip()
        
        content_json = json.dumps(creature_data)
        
        if self.current_creature_id:
            # Update existing
            cursor = self.db.conn.cursor()
            cursor.execute('''
                UPDATE lore SET title = ?, content = ?
                WHERE id = ?
            ''', (name, content_json, self.current_creature_id))
            self.db.conn.commit()
            message = f"Creature '{name}' updated successfully!"
        else:
            # Add new
            new_id = self.db.add_lore(
                self.current_story_id,
                'Bestiary',
                name,
                content_json,
                importance=3
            )
            # db.add_lore returns the new lore id; use as creature id
            self.current_creature_id = new_id
            message = f"Creature '{name}' added successfully!"
        
        self.load_creatures()
        self.update_status(message)
        messagebox.showinfo("Saved", message)
    
    def delete_creature(self):
        """Delete current creature"""
        if not self.current_creature_id:
            messagebox.showwarning("No Selection", "Please select a creature first.")
            return
        
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT title FROM lore WHERE id = ?', (self.current_creature_id,))
        result = cursor.fetchone()
        
        if result and messagebox.askyesno("Confirm Delete", f"Delete creature '{result[0]}'?"):
            cursor.execute('DELETE FROM lore WHERE id = ?', (self.current_creature_id,))
            self.db.conn.commit()
            
            self.current_creature_id = None
            self.load_creatures()
            self.add_creature()
            try:
                messagebox.showinfo("Deleted", "Creature deleted successfully.")
            except Exception:
                pass
            self.update_status("Creature deleted")
    
    def ai_expand_creature(self):
        """Use AI to expand creature details"""
        if not self.current_creature_id:
            messagebox.showwarning("No Selection", "Please select a creature first.")
            return
        
        if not self.ai.test_connection():
            messagebox.showerror("AI Not Connected", "Cannot connect to Ollama.")
            return
        
        creature = self.db.get_lore_entry(self.current_creature_id)
        
        self.update_status("AI expanding creature details...")
        self.window.update()
        
        try:
            result = self.world_gen.expand_creature_details(
                self.current_story_id,
                self.current_creature_id,
                expansion_focus="detailed creature profile with abilities, habitat, and lore"
            )
            
            # Show result in dialog
            self.show_ai_result_dialog(
                "AI Creature Expansion",
                result['raw_result'],
                "Review the AI suggestions and manually add what you like to the creature form."
            )
            
            self.update_status("Creature expansion complete")
            
        except Exception as e:
            messagebox.showerror("Error", f"AI generation failed: {str(e)}")
            self.update_status("AI expansion failed")
    
    # ==================== POWER SYSTEMS, LORE, ORGANIZATIONS ====================
    
    def load_power_systems(self):
        """Load power systems display"""
        if not self.current_story_id:
            return
        # Populate power systems listbox and detail text
        systems = self.db.get_power_systems(self.current_story_id)
        self.power_entries = systems
        self.power_listbox.delete(0, tk.END)
        for sys in systems:
            self.power_listbox.insert(tk.END, sys['name'])

        # If a system is selected, display details, otherwise clear
        if systems:
            self.current_power_id = systems[0]['id']
            self.power_listbox.selection_set(0)
            self.on_power_select(None)
        else:
            self.current_power_id = None
            self.power_systems_text.config(state='normal')
            self.power_systems_text.delete('1.0', tk.END)
            self.power_systems_text.insert('1.0', "No power systems defined yet.\n\nClick '➕ Add System' to create one.")
            self.power_systems_text.config(state='disabled')

        # Configure tags for detailed display if needed
        try:
            self.power_systems_text.tag_config('title', font=('Arial', 14, 'bold'))
            self.power_systems_text.tag_config('subtitle', font=('Arial', 11, 'bold'))
            self.power_systems_text.tag_config('separator', foreground='gray')
        except Exception:
            pass
    
    def load_lore(self):
        """Load lore entries"""
        if not self.current_story_id:
            return
        # Populate lore listbox and set up details
        category_filter = self.lore_category_filter.get()
        if category_filter == 'All':
            lore_entries = self.db.get_lore(self.current_story_id)
        else:
            lore_entries = self.db.get_lore(self.current_story_id, category=category_filter)

        # Exclude bestiary (handled in Bestiary tab)
        lore_entries = [e for e in lore_entries if e.get('category') != 'Bestiary']

        self.lore_entries = lore_entries
        self.lore_listbox.delete(0, tk.END)
        for entry in lore_entries:
            self.lore_listbox.insert(tk.END, f"{entry['title']} ({entry['category']})")

        if lore_entries:
            self.lore_listbox.selection_set(0)
            self.on_lore_select(None)
        else:
            self.current_lore_id = None
            self.lore_text.config(state='normal')
            self.lore_text.delete('1.0', tk.END)
            self.lore_text.insert('1.0', "No lore entries found.\n\nClick '➕ Add' to create one.")
            self.lore_text.config(state='disabled')

        # Configure tags
        try:
            self.lore_text.tag_config('category', font=('Arial', 13, 'bold'))
            self.lore_text.tag_config('title', font=('Arial', 11, 'bold'))
            self.lore_text.tag_config('meta', font=('Arial', 9, 'italic'), foreground='gray')
            self.lore_text.tag_config('content', font=('Arial', 10))
            self.lore_text.tag_config('separator', foreground='gray')
        except Exception:
            pass

    def on_lore_select(self, event):
        """Handle lore list selection and display detail"""
        sel = self.lore_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        entry = self.lore_entries[idx]
        self.current_lore_id = entry['id']
        self.lore_text.config(state='normal')
        self.lore_text.delete('1.0', tk.END)
        if entry.get('timeline_position'):
            self.lore_text.insert(tk.END, f"⏰ {entry['timeline_position']}\n\n", 'meta')
        if entry.get('content'):
            self.lore_text.insert(tk.END, entry['content'])
        self.lore_text.config(state='disabled')

    def on_power_select(self, event):
        """Handle power system selection and display detail"""
        sel = self.power_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        system = self.power_entries[idx]
        self.current_power_id = system['id']
        self.power_systems_text.config(state='normal')
        self.power_systems_text.delete('1.0', tk.END)
        self.power_systems_text.insert(tk.END, f"{system['name']}\n\n", 'title')
        if system.get('description'):
            self.power_systems_text.insert(tk.END, "📋 Description:\n", 'subtitle')
            self.power_systems_text.insert(tk.END, f"{system['description']}\n\n")
        if system.get('rules'):
            self.power_systems_text.insert(tk.END, "⚖️ Rules & Mechanics:\n", 'subtitle')
            self.power_systems_text.insert(tk.END, f"{system['rules']}\n\n")
        if system.get('limitations'):
            self.power_systems_text.insert(tk.END, "🚫 Limitations:\n", 'subtitle')
            self.power_systems_text.insert(tk.END, f"{system['limitations']}\n\n")
        if system.get('acquisition_method'):
            self.power_systems_text.insert(tk.END, "📚 How to Acquire:\n", 'subtitle')
            self.power_systems_text.insert(tk.END, f"{system['acquisition_method']}\n\n")
        if system.get('power_levels'):
            self.power_systems_text.insert(tk.END, "📊 Power Levels:\n", 'subtitle')
            self.power_systems_text.insert(tk.END, f"{system['power_levels']}\n\n")
        if system.get('examples'):
            self.power_systems_text.insert(tk.END, "✨ Examples:\n", 'subtitle')
            self.power_systems_text.insert(tk.END, f"{system['examples']}\n\n")
        self.power_systems_text.config(state='disabled')

    def edit_lore(self, lore_id=None):
        """Open the lore dialog prefilled for editing a lore entry"""
        if lore_id is None:
            return
        # Fetch entry
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT * FROM lore WHERE id = ?', (lore_id,))
        row = cursor.fetchone()
        if not row:
            messagebox.showerror('Error', 'Lore entry not found')
            return
        data = dict(row)
        # Open add_lore dialog prefilled
        def _open_prefilled():
            # Reuse add_lore but prefill fields
            dialog = tk.Toplevel(self.window)
            dialog.title('Edit Lore Entry')
            dialog.geometry('650x650')
            dialog.transient(self.window)
            dialog.grab_set()

            frame = ttk.Frame(dialog, padding=20)
            frame.pack(fill=tk.BOTH, expand=True)

            ttk.Label(frame, text='Edit Lore Entry', font=('Arial', 16, 'bold')).pack(pady=(0,20))

            fields = {}
            ttk.Label(frame, text='Category:', font=('Arial',11,'bold')).pack(anchor='w', pady=(10,5))
            fields['category'] = ttk.Combobox(frame, width=57, values=['History','Culture','Religion','Technology','Magic','Events','Legends','Prophecies','Other'], state='readonly')
            fields['category'].pack(fill=tk.X, pady=(0,10))
            fields['category'].set(data.get('category',''))

            ttk.Label(frame, text='Title:', font=('Arial',11,'bold')).pack(anchor='w', pady=(10,5))
            fields['title'] = ttk.Entry(frame, width=60, font=('Arial',11))
            fields['title'].pack(fill=tk.X, pady=(0,10))
            fields['title'].insert(0, data.get('title',''))

            ttk.Label(frame, text='Content:', font=('Arial',11,'bold')).pack(anchor='w', pady=(10,5))
            content_frame = ttk.Frame(frame)
            content_frame.pack(fill=tk.BOTH, expand=True, pady=(0,10))
            content_scroll = ttk.Scrollbar(content_frame)
            content_scroll.pack(side=tk.RIGHT, fill=tk.Y)
            fields['content'] = tk.Text(content_frame, width=60, height=12, font=('Arial',10), wrap=tk.WORD, yscrollcommand=content_scroll.set)
            fields['content'].pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            content_scroll.config(command=fields['content'].yview)
            fields['content'].insert('1.0', data.get('content',''))

            ttk.Label(frame, text='Timeline Position (optional):', font=('Arial',11,'bold')).pack(anchor='w', pady=(10,5))
            fields['timeline'] = ttk.Entry(frame, width=60)
            fields['timeline'].pack(fill=tk.X, pady=(0,10))
            fields['timeline'].insert(0, data.get('timeline_position',''))

            ttk.Label(frame, text='Importance:', font=('Arial',11,'bold')).pack(anchor='w', pady=(10,5))
            fields['importance'] = ttk.Combobox(frame, width=15, values=['1','2','3','4','5'], state='readonly')
            fields['importance'].pack(anchor='w', pady=(0,10))
            fields['importance'].set(str(data.get('importance',3)))

            def _save():
                category = fields['category'].get().strip()
                title = fields['title'].get().strip()
                content = fields['content'].get('1.0', tk.END).strip()
                if not category or not title or not content:
                    messagebox.showerror('Error','Category, Title, and Content are required!')
                    return
                timeline = fields['timeline'].get().strip()
                importance = int(fields['importance'].get())
                cursor = self.db.conn.cursor()
                cursor.execute('''
                    UPDATE lore SET category = ?, title = ?, content = ?, timeline_position = ?, importance = ? WHERE id = ?
                ''', (category, title, content, timeline, importance, lore_id))
                self.db.conn.commit()
                dialog.destroy()
                self.load_lore()

            button_frame = ttk.Frame(frame)
            button_frame.pack(pady=20)
            ttk.Button(button_frame, text='Save', command=_save, width=20).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text='Cancel', command=dialog.destroy, width=20).pack(side=tk.LEFT, padx=5)

        _open_prefilled()

    def edit_power_system(self, power_id=None):
        """Open the power system dialog prefilled for editing"""
        if power_id is None:
            return
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT * FROM power_systems WHERE id = ?', (power_id,))
        row = cursor.fetchone()
        if not row:
            messagebox.showerror('Error','Power system not found')
            return
        data = dict(row)

        # Build dialog similar to add_power_system but prefilled
        dialog = tk.Toplevel(self.window)
        dialog.title('Edit Power System')
        dialog.geometry('700x800')
        dialog.transient(self.window)
        dialog.grab_set()

        canvas = tk.Canvas(dialog)
        scrollbar = ttk.Scrollbar(dialog, orient='vertical', command=canvas.yview)
        frame = ttk.Frame(canvas, padding=20)
        frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        ttk.Label(frame, text='Edit Power System', font=('Arial',16,'bold')).pack(pady=(0,20))
        fields = {}
        ttk.Label(frame, text='System Name:', font=('Arial',11,'bold')).pack(anchor='w', pady=(10,5))
        fields['name'] = ttk.Entry(frame, width=60, font=('Arial',11))
        fields['name'].pack(fill=tk.X, pady=(0,10))
        fields['name'].insert(0, data.get('name',''))

        text_fields = [
            ('description','Description',5),('rules','Rules & Mechanics',6),('limitations','Limitations & Costs',5),
            ('acquisition_method','How to Acquire/Learn',5),('power_levels','Power Levels/Progression',5),('examples','Example Abilities',6)
        ]
        for field_name,label,height in text_fields:
            ttk.Label(frame, text=f"{label}:", font=('Arial',11,'bold')).pack(anchor='w', pady=(10,5))
            tf = ttk.Frame(frame); tf.pack(fill=tk.X, pady=(0,10))
            ts = ttk.Scrollbar(tf); ts.pack(side=tk.RIGHT, fill=tk.Y)
            fields[field_name] = tk.Text(tf, width=60, height=height, font=('Arial',10), wrap=tk.WORD, yscrollcommand=ts.set)
            fields[field_name].pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            ts.config(command=fields[field_name].yview)
            if data.get(field_name):
                fields[field_name].insert('1.0', data.get(field_name))

        def _save():
            name = fields['name'].get().strip()
            if not name:
                messagebox.showerror('Error','System name is required!')
                return
            desc = fields['description'].get('1.0', tk.END).strip()
            rules = fields['rules'].get('1.0', tk.END).strip()
            limitations = fields['limitations'].get('1.0', tk.END).strip()
            acquisition = fields['acquisition_method'].get('1.0', tk.END).strip()
            power_levels = fields['power_levels'].get('1.0', tk.END).strip()
            examples = fields['examples'].get('1.0', tk.END).strip()

            if power_id:
                # Update existing
                cursor = self.db.conn.cursor()
                cursor.execute('''
                    UPDATE power_systems SET name=?, description=?, rules=?, limitations=?, acquisition_method=?, power_levels=?, examples=?
                    WHERE id=?
                ''', (name, desc, rules, limitations, acquisition, power_levels, examples, power_id))
                self.db.conn.commit()
                messagebox.showinfo("Success", f"Power system '{name}' updated successfully!")
            else:
                self.db.add_power_system(
                    self.current_story_id,
                    name,
                    desc,
                    rules,
                    limitations=limitations,
                    acquisition_method=acquisition,
                    power_levels=power_levels,
                    examples=examples
                )
                messagebox.showinfo("Success", f"Power system '{name}' added successfully!")

            self.load_power_systems()
            dialog.destroy()
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text='Save', command=_save, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text='Cancel', command=dialog.destroy, width=20).pack(side=tk.LEFT, padx=5)

    def delete_lore(self, lore_id=None):
        """Delete a lore entry by id (confirmation)"""
        if not lore_id:
            messagebox.showwarning('No Selection','Select a lore entry first')
            return
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT title FROM lore WHERE id = ?', (lore_id,))
        r = cursor.fetchone()
        title = r[0] if r else 'Unknown'
        if messagebox.askyesno('Confirm Delete', f"Delete lore '{title}'?"):
            cursor.execute('DELETE FROM lore WHERE id = ?', (lore_id,))
            self.db.conn.commit()
            self.load_lore()
            try:
                messagebox.showinfo('Deleted', f"Lore '{title}' deleted successfully.")
            except Exception:
                pass

    def delete_power_system(self, power_id=None):
        """Delete power system by id"""
        if not power_id:
            messagebox.showwarning('No Selection','Select a power system first')
            return
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT name FROM power_systems WHERE id = ?', (power_id,))
        r = cursor.fetchone()
        name = r[0] if r else 'Unknown'
        if messagebox.askyesno('Confirm Delete', f"Delete power system '{name}'?"):
            cursor.execute('DELETE FROM power_systems WHERE id = ?', (power_id,))
            self.db.conn.commit()
            self.load_power_systems()
    
    def load_organizations(self):
        """Load organizations display"""
        if not self.current_story_id:
            return
        
        self.organizations_text.delete('1.0', tk.END)
        
        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT * FROM organizations 
            WHERE story_id = ?
            ORDER BY name
        ''', (self.current_story_id,))
        
        organizations = [dict(row) for row in cursor.fetchall()]
        
        if not organizations:
            self.organizations_text.insert(
                '1.0',
                "No organizations defined yet.\n\n"
                "Click '➕ Add Organization' to create one."
            )
        else:
            for org in organizations:
                self.organizations_text.insert(tk.END, f"{'═'*80}\n", 'separator')
                self.organizations_text.insert(tk.END, f"🏛️ {org['name']}\n", 'title')
                if org['type']:
                    self.organizations_text.insert(tk.END, f"Type: {org['type']}\n", 'meta')
                self.organizations_text.insert(tk.END, f"{'═'*80}\n\n", 'separator')
                
                if org['description']:
                    self.organizations_text.insert(tk.END, f"{org['description']}\n\n")
                
                if org['goals']:
                    self.organizations_text.insert(tk.END, "🎯 Goals:\n", 'subtitle')
                    self.organizations_text.insert(tk.END, f"{org['goals']}\n\n")
                
                if org['structure']:
                    self.organizations_text.insert(tk.END, "📊 Structure:\n", 'subtitle')
                    self.organizations_text.insert(tk.END, f"{org['structure']}\n\n")
                
                if org['members']:
                    self.organizations_text.insert(tk.END, "👥 Notable Members:\n", 'subtitle')
                    self.organizations_text.insert(tk.END, f"{org['members']}\n\n")
                
                self.organizations_text.insert(tk.END, "\n")
        
        self.organizations_text.tag_config('title', font=('Arial', 14, 'bold'))
        self.organizations_text.tag_config('subtitle', font=('Arial', 11, 'bold'))
        self.organizations_text.tag_config('meta', font=('Arial', 10, 'italic'))
        self.organizations_text.tag_config('separator', foreground='gray')
    
    def add_power_system(self):
        """Add or edit a power system. If called directly, creates new entry.
        To edit, call with dialog prefilled via `edit_power_system` which passes `power_id`."""
        # This function will create a new dialog for adding; editing handled below
        if not self.current_story_id:
            messagebox.showwarning("No Story", "Please select a story first.")
            return
        
        dialog = tk.Toplevel(self.window)
        dialog.title("Add Power System")
        dialog.geometry("700x800")
        dialog.transient(self.window)
        dialog.grab_set()
        
        canvas = tk.Canvas(dialog)
        scrollbar = ttk.Scrollbar(dialog, orient='vertical', command=canvas.yview)
        frame = ttk.Frame(canvas, padding=20)
        frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        ttk.Label(frame, text="Add Power System", font=('Arial', 16, 'bold')).pack(pady=(0, 20))
        
        fields = {}
        
        ttk.Label(frame, text="System Name:", font=('Arial', 11, 'bold')).pack(anchor='w', pady=(10, 5))
        fields['name'] = ttk.Entry(frame, width=60, font=('Arial', 11))
        fields['name'].pack(fill=tk.X, pady=(0, 10))
        
        text_fields = [
            ('description', 'Description', 5),
            ('rules', 'Rules & Mechanics', 6),
            ('limitations', 'Limitations & Costs', 5),
            ('acquisition_method', 'How to Acquire/Learn', 5),
            ('power_levels', 'Power Levels/Progression', 5),
            ('examples', 'Example Abilities', 6)
        ]
        
        for field_name, label, height in text_fields:
            ttk.Label(frame, text=f"{label}:", font=('Arial', 11, 'bold')).pack(anchor='w', pady=(10, 5))
            
            text_frame = ttk.Frame(frame)
            text_frame.pack(fill=tk.X, pady=(0, 10))
            
            text_scroll = ttk.Scrollbar(text_frame)
            text_scroll.pack(side=tk.RIGHT, fill=tk.Y)
            
            fields[field_name] = tk.Text(text_frame, width=60, height=height, font=('Arial', 10),
                                         wrap=tk.WORD, yscrollcommand=text_scroll.set)
            fields[field_name].pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            text_scroll.config(command=fields[field_name].yview)
        
        def save(power_id=None):
            name = fields['name'].get().strip()
            if not name:
                messagebox.showerror("Error", "System name is required!")
                return
            desc = fields['description'].get('1.0', tk.END).strip()
            rules = fields['rules'].get('1.0', tk.END).strip()
            limitations = fields['limitations'].get('1.0', tk.END).strip()
            acquisition = fields['acquisition_method'].get('1.0', tk.END).strip()
            power_levels = fields['power_levels'].get('1.0', tk.END).strip()
            examples = fields['examples'].get('1.0', tk.END).strip()

            if power_id:
                # Update existing
                cursor = self.db.conn.cursor()
                cursor.execute('''
                    UPDATE power_systems SET name=?, description=?, rules=?, limitations=?, acquisition_method=?, power_levels=?, examples=?
                    WHERE id=?
                ''', (name, desc, rules, limitations, acquisition, power_levels, examples, power_id))
                self.db.conn.commit()
                messagebox.showinfo("Success", f"Power system '{name}' updated successfully!")
            else:
                self.db.add_power_system(
                    self.current_story_id,
                    name,
                    desc,
                    rules,
                    limitations=limitations,
                    acquisition_method=acquisition,
                    power_levels=power_levels,
                    examples=examples
                )
                messagebox.showinfo("Success", f"Power system '{name}' added successfully!")

            self.load_power_systems()
            dialog.destroy()
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text='Save', command=save, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text='Cancel', command=dialog.destroy, width=20).pack(side=tk.LEFT, padx=5)

    def add_lore(self):
        """Add or edit lore entry. Use `edit_lore(lore_id)` to edit existing entry."""
        if not self.current_story_id:
            messagebox.showwarning("No Story", "Please select a story first.")
            return
        
        dialog = tk.Toplevel(self.window)
        dialog.title("Add Lore Entry")
        dialog.geometry("650x650")
        dialog.transient(self.window)
        dialog.grab_set()
        
        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Add Lore Entry", font=('Arial', 16, 'bold')).pack(pady=(0, 20))
        
        fields = {}
        
        ttk.Label(frame, text="Category:", font=('Arial', 11, 'bold')).pack(anchor='w', pady=(10, 5))
        fields['category'] = ttk.Combobox(
            frame,
            width=57,
            values=['History', 'Culture', 'Religion', 'Technology', 'Magic', 
                    'Events', 'Legends', 'Prophecies', 'Other'],
            state='readonly'
        )
        fields['category'].pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(frame, text="Title:", font=('Arial', 11, 'bold')).pack(anchor='w', pady=(10, 5))
        fields['title'] = ttk.Entry(frame, width=60, font=('Arial', 11))
        fields['title'].pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(frame, text="Content:", font=('Arial', 11, 'bold')).pack(anchor='w', pady=(10, 5))
        
        content_frame = ttk.Frame(frame)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        content_scroll = ttk.Scrollbar(content_frame)
        content_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        fields['content'] = tk.Text(content_frame, width=60, height=12, font=('Arial', 10),
                                    wrap=tk.WORD, yscrollcommand=content_scroll.set)
        fields['content'].pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        content_scroll.config(command=fields['content'].yview)
        
        ttk.Label(frame, text="Timeline Position (optional):", font=('Arial', 11, 'bold')).pack(anchor='w', pady=(10, 5))
        fields['timeline'] = ttk.Entry(frame, width=60)
        fields['timeline'].pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(frame, text="Importance:", font=('Arial', 11, 'bold')).pack(anchor='w', pady=(10, 5))
        fields['importance'] = ttk.Combobox(frame, width=15, values=['1', '2', '3', '4', '5'], state='readonly')
        fields['importance'].set('3')
        fields['importance'].pack(anchor='w', pady=(0, 10))
        
        def save(lore_id=None):
            category = fields['category'].get().strip()
            title = fields['title'].get().strip()
            content = fields['content'].get('1.0', tk.END).strip()

            if not category or not title or not content:
                messagebox.showerror("Error", "Category, Title, and Content are required!")
                return

            timeline = fields['timeline'].get().strip()
            importance = int(fields['importance'].get())

            if lore_id:
                cursor = self.db.conn.cursor()
                cursor.execute('''
                    UPDATE lore SET category = ?, title = ?, content = ?, timeline_position = ?, importance = ?
                    WHERE id = ?
                ''', (category, title, content, timeline, importance, lore_id))
                self.db.conn.commit()
                messagebox.showinfo("Success", f"Lore entry '{title}' updated successfully!")
            else:
                self.db.add_lore(
                    self.current_story_id,
                    category,
                    title,
                    content,
                    timeline_position=timeline,
                    importance=importance
                )
                messagebox.showinfo("Success", f"Lore entry '{title}' added successfully!")

            self.load_lore()
            dialog.destroy()
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Save", command=save, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy, width=20).pack(side=tk.LEFT, padx=5)
    
    def add_organization(self):
        """Add a new organization"""
        if not self.current_story_id:
            messagebox.showwarning("No Story", "Please select a story first.")
            return
        
        dialog = tk.Toplevel(self.window)
        dialog.title("Add Organization")
        dialog.geometry("650x700")
        dialog.transient(self.window)
        dialog.grab_set()
        
        # Scrollable canvas
        canvas = tk.Canvas(dialog)
        scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        frame = ttk.Frame(canvas, padding=20)
        
        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        ttk.Label(frame, text="Add Organization", font=('Arial', 16, 'bold')).pack(pady=(0, 20))
        
        fields = {}
        
        ttk.Label(frame, text="Organization Name:", font=('Arial', 11, 'bold')).pack(anchor='w', pady=(10, 5))
        fields['name'] = ttk.Entry(frame, width=60, font=('Arial', 11))
        fields['name'].pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(frame, text="Type:", font=('Arial', 11, 'bold')).pack(anchor='w', pady=(10, 5))
        fields['type'] = ttk.Combobox(
            frame,
            width=57,
            values=['Guild', 'Kingdom', 'Empire', 'Church', 'Military', 'Academy',
                    'Merchant Group', 'Secret Society', 'Clan', 'Other'],
            state='readonly'
        )
        fields['type'].pack(fill=tk.X, pady=(0, 10))
        
        text_fields = [
            ('description', 'Description', 5),
            ('goals', 'Goals & Purpose', 4),
            ('structure', 'Structure & Hierarchy', 4),
            ('members', 'Notable Members', 4),
            ('resources', 'Resources & Power', 4),
            ('relationships', 'Relationships with Others', 4)
        ]
        
        for field_name, label, height in text_fields:
            ttk.Label(frame, text=f"{label}:", font=('Arial', 11, 'bold')).pack(anchor='w', pady=(10, 5))
            
            text_frame = ttk.Frame(frame)
            text_frame.pack(fill=tk.X, pady=(0, 10))
            
            text_scroll = ttk.Scrollbar(text_frame)
            text_scroll.pack(side=tk.RIGHT, fill=tk.Y)
            
            fields[field_name] = tk.Text(text_frame, width=60, height=height, font=('Arial', 10),
                                         wrap=tk.WORD, yscrollcommand=text_scroll.set)
            fields[field_name].pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            text_scroll.config(command=fields[field_name].yview)
        
        def save():
            name = fields['name'].get().strip()
            if not name:
                messagebox.showerror("Error", "Organization name is required!")
                return
            
            cursor = self.db.conn.cursor()
            cursor.execute('''
                INSERT INTO organizations (
                    story_id, name, type, description, goals, structure,
                    members, resources, relationships
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                self.current_story_id,
                name,
                fields['type'].get(),
                fields['description'].get('1.0', tk.END).strip(),
                fields['goals'].get('1.0', tk.END).strip(),
                fields['structure'].get('1.0', tk.END).strip(),
                fields['members'].get('1.0', tk.END).strip(),
                fields['resources'].get('1.0', tk.END).strip(),
                fields['relationships'].get('1.0', tk.END).strip()
            ))
            self.db.conn.commit()
            
            self.load_organizations()
            dialog.destroy()
            messagebox.showinfo("Success", f"Organization '{name}' added successfully!")
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Save", command=save, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy, width=20).pack(side=tk.LEFT, padx=5)
    
    def ai_generate_power_system(self):
        """Generate a power system with AI"""
        if not self.current_story_id:
            messagebox.showwarning("No Story", "Please select a story first.")
            return
        
        if not self.ai.test_connection():
            messagebox.showerror("AI Not Connected", "Cannot connect to Ollama.")
            return
        
        concept = self.prompt_for_input(
            "AI Generate Power System",
            "Describe the power system concept:",
            "Example: Magic based on emotions and willpower"
        )
        
        if not concept:
            return
        
        self.update_status("AI generating power system...")
        self.window.update()
        
        try:
            result = self.world_gen.generate_power_system(self.current_story_id, concept)
            
            self.show_ai_result_dialog(
                "AI Generated Power System",
                result['raw_result'],
                "Review and manually add this power system using 'Add Power System'."
            )
            
            self.update_status("Power system generation complete")
            
        except Exception as e:
            messagebox.showerror("Error", f"AI generation failed: {str(e)}")
            self.update_status("Generation failed")
    
    def ai_generate_lore(self):
        """Generate lore with AI"""
        if not self.current_story_id:
            messagebox.showwarning("No Story", "Please select a story first.")
            return
        
        if not self.ai.test_connection():
            messagebox.showerror("AI Not Connected", "Cannot connect to Ollama.")
            return
        
        # Category selection
        dialog = tk.Toplevel(self.window)
        dialog.title("AI Generate Lore")
        dialog.geometry("550x350")
        dialog.transient(self.window)
        dialog.grab_set()
        
        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="AI Generate Lore", font=('Arial', 16, 'bold')).pack(pady=(0, 20))
        
        ttk.Label(frame, text="What lore topic should AI generate?", font=('Arial', 11, 'bold')).pack(pady=(10, 5))
        ttk.Label(
            frame,
            text="Example: 'The Great War 500 years ago'",
            font=('Arial', 9, 'italic'),
            foreground='gray'
        ).pack()
        
        topic_frame = ttk.Frame(frame)
        topic_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        topic_scroll = ttk.Scrollbar(topic_frame)
        topic_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        topic_text = tk.Text(topic_frame, width=50, height=6, font=('Arial', 10),
                            wrap=tk.WORD, yscrollcommand=topic_scroll.set)
        topic_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        topic_scroll.config(command=topic_text.yview)
        
        ttk.Label(frame, text="Category:", font=('Arial', 11, 'bold')).pack(anchor='w', pady=(10, 5))
        category_combo = ttk.Combobox(
            frame,
            width=25,
            values=['History', 'Culture', 'Religion', 'Technology', 'Magic', 
                    'Events', 'Legends', 'Prophecies', 'Other'],
            state='readonly'
        )
        category_combo.set('History')
        category_combo.pack(anchor='w', pady=(0, 10))
        
        def generate():
            topic = topic_text.get('1.0', tk.END).strip()
            if not topic:
                messagebox.showerror("Error", "Please describe the lore topic.")
                return
            
            category = category_combo.get()
            dialog.destroy()
            
            self.update_status("AI generating lore...")
            self.window.update()
            
            try:
                result = self.world_gen.generate_lore(self.current_story_id, topic, category)
                
                self.show_ai_result_dialog(
                    "AI Generated Lore",
                    result['raw_result'],
                    "Review and manually add this lore using 'Add Lore Entry'."
                )
                
                self.update_status("Lore generation complete")
                
            except Exception as e:
                messagebox.showerror("Error", f"AI generation failed: {str(e)}")
                self.update_status("Generation failed")
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Generate", command=generate, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy, width=20).pack(side=tk.LEFT, padx=5)
    
    # ==================== PROGRESSION ====================
    
    def load_progression(self):
        # Load arcs for selector
        # If no story selected, ensure fields are cleared and return
        try:
            if not self.current_story_id:
                # Clear selector and fields
                try:
                    self.progression_widgets['arc_selector']['values'] = []
                    self.progression_widgets['arc_selector'].set("")
                except Exception:
                    pass
                self.current_arc_id = None
                for field in ['arc_name', 'arc_number', 'current_plot_points', 'completed_plot_points', 'character_development',
                              'foreshadowing', 'unresolved_threads', 'next_major_events', 'pacing_notes']:
                    try:
                        if field in ['arc_name', 'arc_number']:
                            self.progression_widgets[field].delete(0, tk.END)
                        else:
                            self.progression_widgets[field].delete('1.0', tk.END)
                    except Exception:
                        pass
                return

            arcs = self.db.get_arcs(self.current_story_id) or []
            arc_names = [f"Arc {arc.get('arc_number')}: {arc.get('arc_name')}" for arc in arcs]

            # If no explicit arcs exist, try to infer arc entries from arc_progression records
            if not arcs:
                try:
                    cursor = self.db.conn.cursor()
                    cursor.execute('SELECT DISTINCT arc_id, progression_data FROM arc_progression WHERE story_id = ?', (self.current_story_id,))
                    rows = cursor.fetchall()
                    inferred = []
                    import json
                    for r in rows:
                        try:
                            prog = json.loads(r[1]) if r[1] else {}
                            name = prog.get('arc_name') or f"Unnamed Arc {r[0]}"
                            number = prog.get('arc_number') or r[0] or 0
                            inferred.append({'id': r[0], 'arc_number': number, 'arc_name': name})
                        except Exception:
                            inferred.append({'id': r[0], 'arc_number': r[0] or 0, 'arc_name': f"Arc {r[0]}"})
                    if inferred:
                        arcs = inferred
                        arc_names = [f"Arc {a.get('arc_number')}: {a.get('arc_name')}" for a in arcs]
                except Exception:
                    pass

            # Populate selector values
            try:
                self.progression_widgets['arc_selector']['values'] = arc_names
            except Exception:
                pass

            if arcs:
                # Select first arc by default and load its progression
                try:
                    self.progression_widgets['arc_selector'].set(arc_names[0])
                except Exception:
                    pass
                self.current_arc_id = arcs[0].get('id')
                self.load_arc_progression()
            else:
                # Clear selector and clear fields when there are no arcs/progressions
                try:
                    self.progression_widgets['arc_selector'].set("")
                except Exception:
                    pass
                self.current_arc_id = None
                # Clear progression fields
                for field in ['arc_name', 'arc_number', 'current_plot_points', 'completed_plot_points', 'character_development',
                              'foreshadowing', 'unresolved_threads', 'next_major_events', 'pacing_notes']:
                    try:
                        if field in ['arc_name', 'arc_number']:
                            self.progression_widgets[field].delete(0, tk.END)
                        else:
                            self.progression_widgets[field].delete('1.0', tk.END)
                    except Exception:
                        pass
        except Exception as e:
            # Safely handle errors while trying to load progression
            try:
                print('Error loading progression:', e)
            except Exception:
                pass

    def load_arc_progression(self):
        if not self.current_story_id or not hasattr(self, 'current_arc_id') or not self.current_arc_id:
            return
        progression_data = self.db.get_arc_progression(self.current_story_id, self.current_arc_id)
        if not progression_data:
            # Clear fields
            self.progression_widgets['arc_name'].delete(0, tk.END)
            self.progression_widgets['arc_number'].delete(0, tk.END)
            for field in ['current_plot_points', 'completed_plot_points', 'character_development',
                          'foreshadowing', 'unresolved_threads', 'next_major_events', 'pacing_notes']:
                self.progression_widgets[field].delete('1.0', tk.END)
            return
        # Assume progression_data is a JSON string
        import json
        progression = json.loads(progression_data)
        self.progression_widgets['arc_name'].delete(0, tk.END)
        self.progression_widgets['arc_name'].insert(0, progression.get('arc_name', ""))
        self.progression_widgets['arc_number'].delete(0, tk.END)
        self.progression_widgets['arc_number'].insert(0, str(progression.get('arc_number', "")))
        for field in ['current_plot_points', 'completed_plot_points', 'character_development',
                      'foreshadowing', 'unresolved_threads', 'next_major_events', 'pacing_notes']:
            self.progression_widgets[field].delete('1.0', tk.END)
            self.progression_widgets[field].insert('1.0', progression.get(field, ""))

    def on_arc_selected(self, event=None):
        selected = self.progression_widgets['arc_selector'].get()
        arcs = self.db.get_arcs(self.current_story_id)
        for arc in arcs:
            arc_label = f"Arc {arc['arc_number']}: {arc['arc_name']}"
            if arc_label == selected:
                self.current_arc_id = arc['id']
                break
        self.load_arc_progression()
    def save_progression(self):
        if not self.current_story_id or not hasattr(self, 'current_arc_id') or not self.current_arc_id:
            return
        import json
        data = {
            'arc_name': self.progression_widgets['arc_name'].get(),
            'arc_number': int(self.progression_widgets['arc_number'].get()) if self.progression_widgets['arc_number'].get().strip() else None
        }
        text_fields = ['current_plot_points', 'completed_plot_points', 'character_development',
                      'foreshadowing', 'unresolved_threads', 'next_major_events', 'pacing_notes']
        for field in text_fields:
            data[field] = self.progression_widgets[field].get('1.0', tk.END).strip()
        progression_json = json.dumps(data)
        # Update arc metadata (name/number) in story_arcs table so selector labels stay in sync
        try:
            self.db.update_arc(self.current_arc_id, arc_name=data.get('arc_name'), arc_number=data.get('arc_number'))
        except Exception:
            # If update fails, continue to save progression data but log status
            pass

        # Save progression JSON into arc_progression table
        try:
            self.db.save_arc_progression(self.current_story_id, self.current_arc_id, progression_json)
            self.update_status("Arc progression data saved")
            try:
                messagebox.showinfo('Saved', 'Arc progression saved successfully.')
            except Exception:
                pass
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save progression data: {e}")
            return

        # Reload arcs/selector so any updated name/number are reflected
        self.load_progression()
        # Re-select the arc we just saved
        if self.current_arc_id:
            arcs = self.db.get_arcs(self.current_story_id)
            for arc in arcs:
                if arc['id'] == self.current_arc_id:
                    label = f"Arc {arc['arc_number']}: {arc['arc_name']}"
                    try:
                        self.progression_widgets['arc_selector'].set(label)
                    except Exception:
                        pass
                    break
    
    def create_arc_dialog(self):
        """Dialog to create a new arc and add to DB"""
        if not self.current_story_id:
            messagebox.showwarning("No Story", "Please select a story first.")
            return

        dialog = tk.Toplevel(self.window)
        dialog.title("Add Arc")
        dialog.geometry("480x220")
        dialog.transient(self.window)
        dialog.grab_set()

        frm = ttk.Frame(dialog, padding=12)
        frm.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frm, text="Arc Number:", font=('Arial', 11, 'bold')).grid(row=0, column=0, sticky='w', pady=6)
        arc_number_entry = ttk.Entry(frm, width=10)
        arc_number_entry.grid(row=0, column=1, sticky='w', pady=6)

        ttk.Label(frm, text="Arc Name:", font=('Arial', 11, 'bold')).grid(row=1, column=0, sticky='w', pady=6)
        arc_name_entry = ttk.Entry(frm, width=40)
        arc_name_entry.grid(row=1, column=1, sticky='w', pady=6)

        ttk.Label(frm, text="Synopsis (optional):", font=('Arial', 11, 'bold')).grid(row=2, column=0, sticky='nw', pady=6)
        synopsis_text = tk.Text(frm, width=40, height=5)
        synopsis_text.grid(row=2, column=1, pady=6)

        def do_add():
            num = arc_number_entry.get().strip()
            name = arc_name_entry.get().strip()
            syn = synopsis_text.get('1.0', tk.END).strip()
            if not name or not num:
                messagebox.showerror("Error", "Arc number and name are required.")
                return
            try:
                arc_id = self.db.add_arc(self.current_story_id, int(num), name, synopsis=syn)
                self.load_progression()  # refresh selector
                # select the newly added arc
                arcs = self.db.get_arcs(self.current_story_id)
                for arc in arcs:
                    if arc['id'] == arc_id:
                        label = f"Arc {arc['arc_number']}: {arc['arc_name']}"
                        self.progression_widgets['arc_selector'].set(label)
                        self.current_arc_id = arc_id
                        self.load_arc_progression()
                        break
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("DB Error", f"Failed to add arc: {e}")

        btns = ttk.Frame(frm)
        btns.grid(row=3, column=0, columnspan=2, pady=10)
        ttk.Button(btns, text="Add Arc", command=do_add).pack(side=tk.LEFT, padx=6)
        ttk.Button(btns, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=6)

    # Backwards-compatible alias used by progression tab button
    def add_arc_dialog(self):
        return self.create_arc_dialog()

    def delete_arc(self):
        """Delete the currently selected arc."""
        try:
            arc_id = getattr(self, 'current_arc_id', None)
            if not arc_id:
                # Try to parse from combobox selection
                sel = self.progression_widgets.get('arc_selector')
                if sel:
                    label = sel.get()
                    # Expect format: 'Arc {number}: {name}'
                    arcs = self.db.get_arcs(self.current_story_id) if self.current_story_id else []
                    for arc in arcs:
                        lbl = f"Arc {arc['arc_number']}: {arc['arc_name']}"
                        if lbl == label:
                            arc_id = arc['id']
                            break

            if not arc_id:
                messagebox.showwarning('No Arc Selected', 'Please select an arc to delete.')
                return

            confirm = messagebox.askyesno('Confirm Delete', 'Are you sure you want to delete this arc and its progression data?')
            if not confirm:
                return

            # Delete progression first, then arc
            try:
                if self.current_story_id:
                    self.db.delete_arc_progression(self.current_story_id, arc_id)
            except Exception:
                pass

            self.db.delete_arc(arc_id)
            self.update_status('Arc deleted')
            # Refresh UI
            self.current_arc_id = None
            self.load_progression()
            # Clear fields
            for key in ['arc_name', 'arc_number']:
                w = self.progression_widgets.get(key)
                if isinstance(w, ttk.Entry):
                    try:
                        w.delete(0, tk.END)
                    except Exception:
                        pass

        except Exception as e:
            messagebox.showerror('Delete Error', f'Failed to delete arc: {e}')
    
    def create_main_content(self, parent):
        """Create main content area with tabs"""
        content_frame = ttk.Frame(parent)
        parent.add(content_frame, weight=1)
        
        # Create notebook with tabs
        self.notebook = ttk.Notebook(content_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create all tabs
        self.create_overview_tab()
        self.create_characters_tab()
        self.create_world_tab()
        self.create_bestiary_tab()  # NEW
        self.create_lore_tab()
        self.create_progression_tab()
        self.create_chapter_generator_tab()
        self.create_chapters_list_tab()
    
    def create_status_bar(self):
        """Create bottom status bar"""
        status_frame = ttk.Frame(self.window)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_bar = ttk.Label(
            status_frame,
            text="Ready | Click 'New Story' to begin",
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding=(5, 2)
        )
        self.status_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # AI status indicator
        self.ai_status_label = ttk.Label(
            status_frame,
            text="AI: " + ("🟢 Connected" if self.ai.test_connection() else "🔴 Disconnected"),
            relief=tk.SUNKEN,
            padding=(5, 2)
        )
        self.ai_status_label.pack(side=tk.RIGHT)
    
    def create_overview_tab(self):
        """Story overview and settings tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📋 Overview")
        
        # Scrollable canvas
        canvas = tk.Canvas(tab)
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Content
        content = ttk.Frame(scrollable_frame, padding=30)
        content.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header = ttk.Label(
            content,
            text="Story Overview & Settings",
            font=('Arial', 16, 'bold')
        )
        header.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky='w')
        
        row = 1
        
        # Title
        ttk.Label(content, text="Story Title:", font=('Arial', 11, 'bold')).grid(
            row=row, column=0, sticky='w', pady=8
        )
        self.overview_title = ttk.Entry(content, width=70, font=('Arial', 12))
        self.overview_title.grid(row=row, column=1, sticky='ew', pady=8, padx=(15, 0))
        row += 1
        
        # Synopsis
        ttk.Label(content, text="Synopsis:", font=('Arial', 11, 'bold')).grid(
            row=row, column=0, sticky='nw', pady=8
        )
        synopsis_frame = ttk.Frame(content)
        synopsis_frame.grid(row=row, column=1, sticky='ew', pady=8, padx=(15, 0))
        
        synopsis_scroll = ttk.Scrollbar(synopsis_frame)
        synopsis_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.overview_synopsis = tk.Text(
            synopsis_frame,
            width=70,
            height=6,
            font=('Arial', 11),
            wrap=tk.WORD,
            yscrollcommand=synopsis_scroll.set
        )
        self.overview_synopsis.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        synopsis_scroll.config(command=self.overview_synopsis.yview)
        row += 1
        
        # Genre
        ttk.Label(content, text="Genre:", font=('Arial', 11, 'bold')).grid(
            row=row, column=0, sticky='w', pady=8
        )
        self.overview_genre = ttk.Entry(content, width=70, font=('Arial', 11))
        self.overview_genre.grid(row=row, column=1, sticky='ew', pady=8, padx=(15, 0))
        self.overview_genre.insert(0, "Light Novel / Fantasy")
        row += 1
        
        # Themes
        ttk.Label(content, text="Themes:", font=('Arial', 11, 'bold')).grid(
            row=row, column=0, sticky='w', pady=8
        )
        self.overview_themes = ttk.Entry(content, width=70, font=('Arial', 11))
        self.overview_themes.grid(row=row, column=1, sticky='ew', pady=8, padx=(15, 0))
        row += 1
        
        # Tone
        ttk.Label(content, text="Tone:", font=('Arial', 11, 'bold')).grid(
            row=row, column=0, sticky='w', pady=8
        )
        self.overview_tone = ttk.Entry(content, width=70, font=('Arial', 11))
        self.overview_tone.grid(row=row, column=1, sticky='ew', pady=8, padx=(15, 0))
        row += 1
        
        # Writing Style
        ttk.Label(content, text="Writing Style:", font=('Arial', 11, 'bold')).grid(
            row=row, column=0, sticky='w', pady=8
        )
        self.overview_style = ttk.Entry(content, width=70, font=('Arial', 11))
        self.overview_style.grid(row=row, column=1, sticky='ew', pady=8, padx=(15, 0))
        self.overview_style.insert(0, "ReZero/Fate-inspired - Internal monologue, detailed sensory descriptions")
        row += 1
        
        # Target Length
        ttk.Label(content, text="Target Length:", font=('Arial', 11, 'bold')).grid(
            row=row, column=0, sticky='w', pady=8
        )
        length_frame = ttk.Frame(content)
        length_frame.grid(row=row, column=1, sticky='w', pady=8, padx=(15, 0))
        
        self.overview_target_length = ttk.Combobox(
            length_frame,
            width=20,
            values=['Short (10-20 chapters)', 'Medium (20-50 chapters)', 
                    'Long (50-100 chapters)', 'Epic (100+ chapters)'],
            state='readonly'
        )
        self.overview_target_length.set('Medium (20-50 chapters)')
        self.overview_target_length.pack(side=tk.LEFT)
        row += 1
        
        # Buttons
        button_frame = ttk.Frame(content)
        button_frame.grid(row=row, column=0, columnspan=2, pady=30)
        
        ttk.Button(
            button_frame,
            text="💾 Save Story Information",
            command=self.save_overview,
            width=25
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="🎨 Generate World from Synopsis",
            command=self.generate_from_synopsis,
            width=30
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="📊 View Story Statistics",
            command=self.show_story_stats,
            width=25
        ).pack(side=tk.LEFT, padx=5)
        
        content.columnconfigure(1, weight=1)
    
    def create_characters_tab(self):
        """Characters management tab with enhanced UI"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="👤 Characters")
        
        # Split into list and details
        paned = ttk.PanedWindow(tab, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left: Character list
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)
        
        # Header with filter
        header_frame = ttk.Frame(left_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(
            header_frame,
            text="Characters",
            font=('Arial', 13, 'bold')
        ).pack(side=tk.LEFT)
        
        # Filter by role
        ttk.Label(header_frame, text="Filter:").pack(side=tk.LEFT, padx=(20, 5))
        self.char_role_filter = ttk.Combobox(
            header_frame,
            width=15,
            values=['All', 'Protagonist', 'Major Character', 'Supporting Character', 
                    'Minor Character', 'Antagonist'],
            state='readonly'
        )
        self.char_role_filter.set('All')
        self.char_role_filter.pack(side=tk.LEFT, padx=5)
        self.char_role_filter.bind('<<ComboboxSelected>>', lambda e: self.load_characters())
        
        # Action buttons
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(
            button_frame,
            text="➕ Add Character",
            command=self.add_character
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            button_frame,
            text="🎨 AI Expand",
            command=self.ai_expand_character
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            button_frame,
            text="🗑️ Delete",
            command=self.delete_character
        ).pack(side=tk.LEFT, padx=2)
        
        # Character list
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        char_scrollbar = ttk.Scrollbar(list_frame)
        char_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.char_listbox = tk.Listbox(
            list_frame,
            yscrollcommand=char_scrollbar.set,
            font=('Arial', 11),
            selectmode=tk.SINGLE
        )
        self.char_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        char_scrollbar.config(command=self.char_listbox.yview)
        
        self.char_listbox.bind('<<ListboxSelect>>', self.on_character_select)
        self.char_listbox.bind('<Double-Button-1>', lambda e: self.notebook.select(0))
        
        # Right: Character details
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=2)
        
        # Scrollable details
        canvas = tk.Canvas(right_frame)
        scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=canvas.yview)
        self.char_details_frame = ttk.Frame(canvas)
        
        self.char_details_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.char_details_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Use focused mousewheel binding for this canvas region
        try:
            self._bind_mousewheel_widget(canvas)
        except Exception:
            pass
        
        self.setup_character_details_form()
    
    def setup_character_details_form(self):
        """Setup enhanced character details form"""
        frame = self.char_details_frame
        self.char_widgets = {}
        
        # Header
        header = ttk.Label(
            frame,
            text="Character Details",
            font=('Arial', 14, 'bold')
        )
        header.grid(row=0, column=0, columnspan=2, pady=(10, 20), sticky='w', padx=15)
        
        row = 1
        
        # Name
        ttk.Label(frame, text="Name:", font=('Arial', 11, 'bold')).grid(
            row=row, column=0, sticky='w', padx=15, pady=6
        )
        self.char_widgets['name'] = ttk.Entry(frame, width=50, font=('Arial', 12))
        self.char_widgets['name'].grid(row=row, column=1, sticky='ew', padx=15, pady=6)
        row += 1
        
        # Role
        ttk.Label(frame, text="Role:", font=('Arial', 11, 'bold')).grid(
            row=row, column=0, sticky='w', padx=15, pady=6
        )
        self.char_widgets['role'] = ttk.Combobox(
            frame,
            width=48,
            values=['Protagonist', 'Deuteragonist', 'Major Character',
                    'Supporting Character', 'Minor Character', 'Antagonist',
                    'Love Interest', 'Mentor', 'Rival'],
            state='readonly'
        )
        self.char_widgets['role'].grid(row=row, column=1, sticky='ew', padx=15, pady=6)
        row += 1
        
        # Age and Gender row
        ttk.Label(frame, text="Age & Gender:", font=('Arial', 11, 'bold')).grid(
            row=row, column=0, sticky='w', padx=15, pady=6
        )
        age_gender_frame = ttk.Frame(frame)
        age_gender_frame.grid(row=row, column=1, sticky='ew', padx=15, pady=6)
        
        self.char_widgets['age'] = ttk.Entry(age_gender_frame, width=10)
        self.char_widgets['age'].pack(side=tk.LEFT)
        
        ttk.Label(age_gender_frame, text="Gender:").pack(side=tk.LEFT, padx=(15, 5))
        self.char_widgets['gender'] = ttk.Combobox(
            age_gender_frame,
            width=15,
            values=['Male', 'Female', 'Non-binary', 'Other'],
            state='readonly'
        )
        self.char_widgets['gender'].pack(side=tk.LEFT)
        row += 1
        
        # Importance slider
        ttk.Label(frame, text="Importance:", font=('Arial', 11, 'bold')).grid(
            row=row, column=0, sticky='w', padx=15, pady=6
        )
        importance_frame = ttk.Frame(frame)
        importance_frame.grid(row=row, column=1, sticky='ew', padx=15, pady=6)
        
        self.char_widgets['importance'] = tk.Scale(
            importance_frame,
            from_=1, to=5,
            orient=tk.HORIZONTAL,
            length=250,
            tickinterval=1
        )
        self.char_widgets['importance'].pack(side=tk.LEFT)
        self.char_widgets['importance'].set(3)
        
        ttk.Label(importance_frame, text="(1=Minor, 5=Critical)").pack(side=tk.LEFT, padx=10)
        row += 1
        
        # Status
        ttk.Label(frame, text="Status:", font=('Arial', 11, 'bold')).grid(
            row=row, column=0, sticky='w', padx=15, pady=6
        )
        self.char_widgets['status'] = ttk.Combobox(
            frame,
            width=48,
            values=['Alive', 'Deceased', 'Unknown', 'MIA'],
            state='readonly'
        )
        self.char_widgets['status'].set('Alive')
        self.char_widgets['status'].grid(row=row, column=1, sticky='ew', padx=15, pady=6)
        row += 1
        
        # Separator
        ttk.Separator(frame, orient=tk.HORIZONTAL).grid(
            row=row, column=0, columnspan=2, sticky='ew', padx=15, pady=15
        )
        row += 1

        # Create the larger text fields for detailed character attributes
        text_fields = [
            ('appearance', 'Physical Appearance', 4),
            ('personality', 'Personality Traits', 4),
            ('background', 'Background Story', 6),
            ('motivations', 'Goals & Motivations', 4),
            ('abilities', 'Abilities & Powers', 4),
            ('combat_style', 'Combat Style', 3),
            ('equipment', 'Equipment & Belongings', 3),
            ('relationships', 'Relationships', 3),
            ('character_arc', 'Character Development Arc', 4),
            ('voice_style', 'Voice & Speech Pattern', 3),
            ('quirks', 'Quirks & Mannerisms', 3)
        ]

        for key, label, height in text_fields:
            ttk.Label(frame, text=label+':', font=('Arial', 11, 'bold')).grid(
                row=row, column=0, sticky='nw', padx=15, pady=(6, 4)
            )
            tf = ttk.Frame(frame)
            tf.grid(row=row, column=1, sticky='ew', padx=15, pady=(6, 4))
            sc = ttk.Scrollbar(tf)
            sc.pack(side=tk.RIGHT, fill=tk.Y)
            txt = tk.Text(tf, width=70, height=height, wrap=tk.WORD, yscrollcommand=sc.set)
            txt.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            sc.config(command=txt.yview)
            self.char_widgets[key] = txt
            row += 1

        # Action buttons for character form
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=12, padx=15, sticky='e')

        try:
            save_btn = tk.Button(btn_frame, text="💾 Save Character", command=self.save_character,
                                 bg='#9B111E', fg='white', activebackground='#2F3E9E')
        except Exception:
            save_btn = ttk.Button(btn_frame, text="💾 Save Character", command=self.save_character)

        save_btn.pack(side=tk.RIGHT, padx=6)
        ttk.Button(btn_frame, text="🗑️ Delete", command=self.delete_character).pack(side=tk.RIGHT, padx=6)

        # after creating form columns
        frame.columnconfigure(0, weight=0)
        frame.columnconfigure(1, weight=1)  # content column expands

    def create_world_tab(self):
        """World builder tab with locations list and details form"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="🌍 World")

        paned = ttk.PanedWindow(tab, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left: Locations list and controls
        left_frame = ttk.Frame(paned, width=300)
        paned.add(left_frame, weight=1)

        header = ttk.Frame(left_frame)
        header.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(header, text="Locations", font=('Arial', 13, 'bold')).pack(side=tk.LEFT)

        ttk.Button(left_frame, text="➕ Add Location", command=self.add_location).pack(fill=tk.X, padx=8, pady=(6, 8))

        filter_frame = ttk.Frame(left_frame)
        filter_frame.pack(fill=tk.X, padx=8)
        ttk.Label(filter_frame, text="Type:").pack(side=tk.LEFT)
        self.location_type_filter = ttk.Combobox(filter_frame, width=18, values=['All', 'City', 'Town', 'Region', 'Country', 'Dungeon', 'Other'], state='readonly')
        self.location_type_filter.set('All')
        self.location_type_filter.pack(side=tk.LEFT, padx=(6, 0))
        self.location_type_filter.bind('<<ComboboxSelected>>', lambda e: self.load_locations())

        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=(8, 8))
        scroll = ttk.Scrollbar(list_frame)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.location_listbox = tk.Listbox(list_frame, yscrollcommand=scroll.set, font=('Arial', 11))
        self.location_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.config(command=self.location_listbox.yview)
        self.location_listbox.bind('<<ListboxSelect>>', self.on_location_select)

        # Right: Location detail form
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=3)

        canvas = tk.Canvas(right_frame)
        scrollbar = ttk.Scrollbar(right_frame, orient='vertical', command=canvas.yview)
        form_frame = ttk.Frame(canvas)
        form_frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=form_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.location_widgets = {}

        ttk.Label(form_frame, text="Location Name:", font=('Arial', 11, 'bold')).grid(row=0, column=0, sticky='w', padx=10, pady=(10, 6))
        self.location_widgets['name'] = ttk.Entry(form_frame, width=60)
        self.location_widgets['name'].grid(row=0, column=1, sticky='ew', padx=10, pady=(10, 6))

        ttk.Label(form_frame, text="Type:", font=('Arial', 11, 'bold')).grid(row=1, column=0, sticky='w', padx=10, pady=(0, 6))
        self.location_widgets['type'] = ttk.Combobox(form_frame, width=30, values=['City', 'Town', 'Region', 'Country', 'Dungeon', 'Other'], state='readonly')
        self.location_widgets['type'].grid(row=1, column=1, sticky='w', padx=10, pady=(0, 6))

        # Large text fields used elsewhere
        text_fields = [
            ('description', 'Description', 6),
            ('geography', 'Geography', 4),
            ('climate', 'Climate', 3),
            ('population', 'Population', 3),
            ('government', 'Government', 3),
            ('economy', 'Economy', 3),
            ('culture', 'Culture', 4),
            ('history', 'History', 5),
            ('notable_locations', 'Notable Locations', 4),
            ('relationships', 'Relationships', 3)
        ]

        r = 2
        for key, label, h in text_fields:
            ttk.Label(form_frame, text=label+":", font=('Arial', 11, 'bold')).grid(row=r, column=0, sticky='nw', padx=10, pady=(8, 4))
            tf = ttk.Frame(form_frame)
            tf.grid(row=r, column=1, sticky='ew', padx=10, pady=(8, 4))
            sc = ttk.Scrollbar(tf)
            sc.pack(side=tk.RIGHT, fill=tk.Y)
            txt = tk.Text(tf, width=80, height=h, wrap=tk.WORD, yscrollcommand=sc.set)
            txt.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            sc.config(command=txt.yview)
            self.location_widgets[key] = txt
            r += 1

        # Action buttons
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=r, column=0, columnspan=2, pady=12)
        ttk.Button(btn_frame, text="💾 Save Location", command=self.save_location).pack(side=tk.LEFT, padx=6)
        ttk.Button(btn_frame, text="🗑️ Delete", command=self.delete_location).pack(side=tk.LEFT, padx=6)

        form_frame.columnconfigure(0, weight=0)
        form_frame.columnconfigure(1, weight=1)  # content column expands

        # Load initial data
        self.load_locations()

    def create_bestiary_tab(self):
        """Bestiary tab: list of creatures and a details pane"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="🐉 Bestiary")

        paned = ttk.PanedWindow(tab, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        left = ttk.Frame(paned, width=300)
        paned.add(left, weight=1)

        header = ttk.Frame(left)
        header.pack(fill=tk.X, pady=(0, 6))
        ttk.Label(header, text="Creatures", font=('Arial', 13, 'bold')).pack(side=tk.LEFT)

        ttk.Button(left, text="➕ Add Creature", command=self.add_creature).pack(fill=tk.X, padx=8, pady=(6, 6))

        list_frame = ttk.Frame(left)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=(6, 8))
        cs = ttk.Scrollbar(list_frame)
        cs.pack(side=tk.RIGHT, fill=tk.Y)
        self.creature_listbox = tk.Listbox(list_frame, yscrollcommand=cs.set, font=('Arial', 11))
        self.creature_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        cs.config(command=self.creature_listbox.yview)
        self.creature_listbox.bind('<<ListboxSelect>>', self.on_creature_select)

        right = ttk.Frame(paned)
        paned.add(right, weight=3)

        # Detail form (scrollable)
        canvas = tk.Canvas(right)
        scrollbar = ttk.Scrollbar(right, orient='vertical', command=canvas.yview)
        frame = ttk.Frame(canvas)
        frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.creature_widgets = {}

        ttk.Label(frame, text="Name:", font=('Arial', 11, 'bold')).grid(row=0, column=0, sticky='w', padx=10, pady=(10, 6))
        self.creature_widgets['name'] = ttk.Entry(frame, width=60)
        self.creature_widgets['name'].grid(row=0, column=1, sticky='ew', padx=10, pady=(10, 6))

        ttk.Label(frame, text="Type:", font=('Arial', 11, 'bold')).grid(row=1, column=0, sticky='w', padx=10, pady=(0, 6))
        self.creature_widgets['type'] = ttk.Entry(frame, width=30)
        self.creature_widgets['type'].grid(row=1, column=1, sticky='w', padx=10, pady=(0, 6))

        ttk.Label(frame, text="Threat Level:", font=('Arial', 11, 'bold')).grid(row=2, column=0, sticky='w', padx=10, pady=(0, 6))
        self.creature_widgets['threat_level'] = ttk.Combobox(frame, width=20, values=['Low', 'Moderate', 'High', 'Extreme'], state='readonly')
        self.creature_widgets['threat_level'].grid(row=2, column=1, sticky='w', padx=10, pady=(0, 6))

        text_keys = ['description', 'habitat', 'behavior', 'abilities', 'weaknesses', 'diet', 'lore', 'drops']
        r = 3
        for key in text_keys:
            ttk.Label(frame, text=f"{key.replace('_', ' ').title()}:", font=('Arial', 11, 'bold')).grid(row=r, column=0, sticky='nw', padx=10, pady=(8, 4))
            tf = ttk.Frame(frame)
            tf.grid(row=r, column=1, sticky='ew', padx=10, pady=(8, 4))
            sc = ttk.Scrollbar(tf)
            sc.pack(side=tk.RIGHT, fill=tk.Y)
            txt = tk.Text(tf, width=80, height=4, wrap=tk.WORD, yscrollcommand=sc.set)
            txt.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            sc.config(command=txt.yview)
            self.creature_widgets[key] = txt
            r += 1

        frame.columnconfigure(1, weight=1)

        # Action buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=r, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="💾 Save Creature", command=self.save_creature).pack(side=tk.LEFT, padx=6)
        ttk.Button(btn_frame, text="🗑️ Delete", command=self.delete_creature).pack(side=tk.LEFT, padx=6)

        # Load initial data
        self.load_creatures()

    def create_lore_tab(self):
        """Lore & powers tab (list and content display)"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📚 Lore & Powers")

        paned = ttk.PanedWindow(tab, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left: Lore list + controls
        left = ttk.Frame(paned, width=320)
        paned.add(left, weight=1)

        header = ttk.Frame(left)
        header.pack(fill=tk.X)
        ttk.Label(header, text="Lore Entries", font=('Arial', 14, 'bold')).pack(side=tk.LEFT)

        ttk.Label(header, text="Category:").pack(side=tk.LEFT, padx=(10,4))
        self.lore_category_filter = ttk.Combobox(header, width=14, values=['All', 'History', 'Culture', 'Religion', 'Technology', 'Magic', 'Events', 'Legends', 'Prophecies', 'Other'], state='readonly')
        self.lore_category_filter.set('All')
        self.lore_category_filter.pack(side=tk.LEFT)
        self.lore_category_filter.bind('<<ComboboxSelected>>', lambda e: self.load_lore())

        btns = ttk.Frame(left)
        btns.pack(fill=tk.X, pady=(8,4))
        ttk.Button(btns, text='➕ Add', command=self.add_lore).pack(side=tk.LEFT, padx=4)
        ttk.Button(btns, text='✏️ Edit', command=lambda: self.edit_lore(getattr(self, 'current_lore_id', None))).pack(side=tk.LEFT, padx=4)
        ttk.Button(btns, text='🗑️ Delete', command=lambda: self.delete_lore(getattr(self, 'current_lore_id', None))).pack(side=tk.LEFT, padx=4)

        list_frame = ttk.Frame(left)
        list_frame.pack(fill=tk.BOTH, expand=True)
        lb_scroll = ttk.Scrollbar(list_frame)
        lb_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.lore_listbox = tk.Listbox(list_frame, yscrollcommand=lb_scroll.set, font=('Arial', 11))
        self.lore_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        lb_scroll.config(command=self.lore_listbox.yview)
        self.lore_listbox.bind('<<ListboxSelect>>', self.on_lore_select)

        # Right: Details (Lore display on top, Power Systems below)
        right = ttk.Frame(paned)
        paned.add(right, weight=3)

        # Lore detail area
        lore_frame = ttk.LabelFrame(right, text='Lore Detail', padding=8)
        lore_frame.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        lore_scroll = ttk.Scrollbar(lore_frame)
        lore_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.lore_text = tk.Text(lore_frame, wrap=tk.WORD, yscrollcommand=lore_scroll.set, font=('Arial', 10), state='normal')
        self.lore_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        lore_scroll.config(command=self.lore_text.yview)

        # Power systems area
        ps_frame = ttk.LabelFrame(right, text='Power Systems', padding=8)
        ps_frame.pack(fill=tk.BOTH, expand=True, padx=6, pady=(0,6))

        ps_btns = ttk.Frame(ps_frame)
        ps_btns.pack(fill=tk.X)
        ttk.Button(ps_btns, text='➕ Add System', command=self.add_power_system).pack(side=tk.LEFT, padx=4)
        ttk.Button(ps_btns, text='✏️ Edit System', command=lambda: self.edit_power_system(getattr(self, 'current_power_id', None))).pack(side=tk.LEFT, padx=4)
        ttk.Button(ps_btns, text='🗑️ Delete System', command=lambda: self.delete_power_system(getattr(self, 'current_power_id', None))).pack(side=tk.LEFT, padx=4)

        ps_list_frame = ttk.Frame(ps_frame)
        ps_list_frame.pack(fill=tk.BOTH, expand=True, pady=(6,0))
        ps_scroll = ttk.Scrollbar(ps_list_frame)
        ps_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.power_listbox = tk.Listbox(ps_list_frame, yscrollcommand=ps_scroll.set, font=('Arial', 11))
        self.power_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ps_scroll.config(command=self.power_listbox.yview)
        self.power_listbox.bind('<<ListboxSelect>>', self.on_power_select)

        self.power_systems_text = tk.Text(ps_list_frame, height=10, wrap=tk.WORD, state='disabled', font=('Arial', 10))

        # Initial load
        self.load_lore()
        self.load_power_systems()
    
    def create_progression_tab(self):
        """Progression tracking per story arc"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📈 Progression")

        # Scrollable area
        canvas = tk.Canvas(tab)
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Container for progression widgets
        content = ttk.Frame(scroll_frame, padding=20)
        content.pack(fill=tk.BOTH, expand=True)

        self.progression_widgets = {}

        # Arc selector
        ttk.Label(content, text="Select Arc:", font=('Arial', 11, 'bold')).grid(row=0, column=0, sticky='w')
        self.progression_widgets['arc_selector'] = ttk.Combobox(content, width=50, state='readonly')
        self.progression_widgets['arc_selector'].grid(row=0, column=1, sticky='w', padx=(10, 0))
        self.progression_widgets['arc_selector'].bind('<<ComboboxSelected>>', self.on_arc_selected)

        # After creating arc selector
        arc_controls = ttk.Frame(content)
        arc_controls.grid(row=0, column=2, sticky='w', padx=(10,0))
        ttk.Button(arc_controls, text="➕ Add Arc", command=self.add_arc_dialog, width=12).pack(side=tk.LEFT, padx=3)
        ttk.Button(arc_controls, text="🗑️ Delete Arc", command=self.delete_arc, width=12).pack(side=tk.LEFT, padx=3)

        # Arc name & number
        ttk.Label(content, text="Arc Name:", font=('Arial', 11, 'bold')).grid(row=1, column=0, sticky='w', pady=(10, 5))
        self.progression_widgets['arc_name'] = ttk.Entry(content, width=60)
        self.progression_widgets['arc_name'].grid(row=1, column=1, sticky='w', padx=(10, 0), pady=(10, 5))

        ttk.Label(content, text="Arc Number:", font=('Arial', 11, 'bold')).grid(row=2, column=0, sticky='w', pady=(0, 10))
        self.progression_widgets['arc_number'] = ttk.Entry(content, width=10)
        self.progression_widgets['arc_number'].grid(row=2, column=1, sticky='w', padx=(10, 0), pady=(0, 10))

        # Progression text fields
        text_fields = [
            ('current_plot_points', 'Current Plot Points', 6,
             "What's happening now? Active storylines, conflicts, immediate goals..."),
            ('completed_plot_points', 'Completed Plot Points', 6,
             "What has been resolved? Major events that have concluded..."),
            ('character_development', 'Character Development Notes', 7,
             "How are characters changing? Growth, relationships, realizations..."),
            ('foreshadowing', 'Active Foreshadowing', 6,
             "Hints and setup for future events, mysteries to be revealed..."),
            ('unresolved_threads', 'Unresolved Plot Threads', 6,
             "Open questions, unfinished business, mysteries to address..."),
            ('next_major_events', 'Planned Major Events', 6,
             "What's coming next? Major plot points, confrontations, revelations..."),
            ('pacing_notes', 'Pacing & Structure Notes', 5,
             "Notes on story rhythm, when to speed up/slow down...")
        ]

        row = 3
        for field, label, height, placeholder in text_fields:
            ttk.Label(content, text=label, font=('Arial', 12, 'bold')).grid(row=row, column=0, columnspan=2, pady=(15, 5), sticky='w')
            row += 1

            ttk.Label(content, text=placeholder, font=('Arial', 9, 'italic'), foreground='gray').grid(
                row=row, column=0, columnspan=2, pady=(0, 5), sticky='w')
            row += 1

            text_frame = ttk.Frame(content)
            text_frame.grid(row=row, column=0, columnspan=2, sticky='ew', pady=(0, 10))

            text_scroll = ttk.Scrollbar(text_frame)
            text_scroll.pack(side=tk.RIGHT, fill=tk.Y)

            self.progression_widgets[field] = tk.Text(
                text_frame,
                width=100,
                height=height,
                font=('Arial', 10),
                wrap=tk.WORD,
                yscrollcommand=text_scroll.set
            )
            self.progression_widgets[field].pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            text_scroll.config(command=self.progression_widgets[field].yview)

            row += 1

        # Action buttons
        button_frame = ttk.Frame(content)
        button_frame.grid(row=row, column=0, columnspan=2, pady=25)

        ttk.Button(button_frame, text="💾 Save Progression Data", command=self.save_progression, width=25).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="📊 View Timeline", command=self.show_timeline, width=20).pack(side=tk.LEFT, padx=5)

        content.columnconfigure(1, weight=1)

        # Populate arcs for current story
        self.load_progression()

    def create_chapter_generator_tab(self):
        """Enhanced chapter generation tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="🎨 Generate Chapter")
        
        # Split view
        paned = ttk.PanedWindow(tab, orient=tk.VERTICAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top: Generation settings
        top_frame = ttk.Frame(paned)
        paned.add(top_frame, weight=1)
        
        settings_frame = ttk.LabelFrame(top_frame, text="Chapter Generation Settings", padding=20)
        settings_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a grid layout
        row = 0
        
        # Chapter number
        ttk.Label(
            settings_frame,
            text="Chapter Number:",
            font=('Arial', 11, 'bold')
        ).grid(row=row, column=0, sticky='w', pady=8)
        
        chapter_frame = ttk.Frame(settings_frame)
        chapter_frame.grid(row=row, column=1, sticky='w', pady=8, padx=(10, 0))
        
        self.gen_chapter_number = ttk.Entry(chapter_frame, width=10, font=('Arial', 11))
        self.gen_chapter_number.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            chapter_frame,
            text="Auto (Next)",
            command=self.set_next_chapter_number,
            width=12
        ).pack(side=tk.LEFT)
        row += 1
        
        # Chapter title
        ttk.Label(
            settings_frame,
            text="Chapter Title:",
            font=('Arial', 11, 'bold')
        ).grid(row=row, column=0, sticky='w', pady=8)
        
        ttk.Label(
            settings_frame,
            text="(Optional - leave blank for 'Chapter X')",
            font=('Arial', 9, 'italic'),
            foreground='gray'
        ).grid(row=row, column=2, sticky='w', padx=(10, 0))
        
        self.gen_chapter_title = ttk.Entry(settings_frame, width=50, font=('Arial', 11))
        self.gen_chapter_title.grid(row=row, column=1, sticky='ew', pady=8, padx=(10, 0))
        row += 1
        
        # POV Character
        ttk.Label(
            settings_frame,
            text="POV Character:",
            font=('Arial', 11, 'bold')
        ).grid(row=row, column=0, sticky='w', pady=8)
        
        self.gen_pov_character = ttk.Combobox(settings_frame, width=48)
        self.gen_pov_character.grid(row=row, column=1, sticky='ew', pady=8, padx=(10, 0))
        row += 1
        
        # Plot directive
        ttk.Label(
            settings_frame,
            text="Plot Directive:",
            font=('Arial', 11, 'bold')
        ).grid(row=row, column=0, sticky='nw', pady=8)
        
        ttk.Label(
            settings_frame,
            text="What should happen in this chapter? Be specific!",
            font=('Arial', 9, 'italic'),
            foreground='gray'
        ).grid(row=row+1, column=0, sticky='nw', pady=0)
        
        plot_frame = ttk.Frame(settings_frame)
        plot_frame.grid(row=row, column=1, rowspan=2, sticky='ew', pady=8, padx=(10, 0))
        
        plot_scroll = ttk.Scrollbar(plot_frame)
        plot_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.gen_plot_directive = tk.Text(
            plot_frame,
            width=50,
            height=6,
            font=('Arial', 10),
            wrap=tk.WORD,
            yscrollcommand=plot_scroll.set
        )
        self.gen_plot_directive.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        plot_scroll.config(command=self.gen_plot_directive.yview)
        row += 2
        
        # Previous chapter summary
        ttk.Label(
            settings_frame,
            text="Previous Chapter Summary:",
            font=('Arial', 11, 'bold')
        ).grid(row=row, column=0, sticky='nw', pady=8)
        
        ttk.Label(
            settings_frame,
            text="(Optional - helps with continuity)",
            font=('Arial', 9, 'italic'),
            foreground='gray'
        ).grid(row=row+1, column=0, sticky='nw', pady=0)
        
        prev_frame = ttk.Frame(settings_frame)
        prev_frame.grid(row=row, column=1, rowspan=2, sticky='ew', pady=8, padx=(10, 0))
        
        prev_scroll = ttk.Scrollbar(prev_frame)
        prev_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.gen_previous_summary = tk.Text(
            prev_frame,
            width=50,
            height=4,
            font=('Arial', 10),
            wrap=tk.WORD,
            yscrollcommand=prev_scroll.set
        )
        self.gen_previous_summary.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        prev_scroll.config(command=self.gen_previous_summary.yview)
        row += 2
        
        # AI Parameters
        params_frame = ttk.LabelFrame(settings_frame, text="AI Generation Parameters", padding=15)
        params_frame.grid(row=row, column=0, columnspan=3, sticky='ew', pady=15)
        
        param_row = 0
        
        # Temperature
        ttk.Label(
            params_frame,
            text="Creativity Level (Temperature):",
            font=('Arial', 10, 'bold')
        ).grid(row=param_row, column=0, sticky='w', padx=5)
        
        temp_frame = ttk.Frame(params_frame)
        temp_frame.grid(row=param_row, column=1, sticky='ew', padx=5)
        
        self.gen_temperature = tk.Scale(
            temp_frame,
            from_=0.5, to=1.0,
            orient=tk.HORIZONTAL,
            resolution=0.05,
            length=250,
            tickinterval=0.1
        )
        self.gen_temperature.set(0.85)
        self.gen_temperature.pack(side=tk.LEFT)
        
        ttk.Label(
            temp_frame,
            text="Lower = More focused | Higher = More creative",
            font=('Arial', 9, 'italic')
        ).pack(side=tk.LEFT, padx=10)
        param_row += 1
        
        # Max words
        ttk.Label(
            params_frame,
            text="Target Word Count:",
            font=('Arial', 10, 'bold')
        ).grid(row=param_row, column=0, sticky='w', padx=5, pady=10)
        
        words_frame = ttk.Frame(params_frame)
        words_frame.grid(row=param_row, column=1, sticky='w', padx=5, pady=10)
        
        self.gen_max_words = ttk.Combobox(
            words_frame,
            width=15,
            values=['2000', '2500', '3000', '3500', '4000', '5000'],
            state='readonly'
        )
        self.gen_max_words.set('3000')
        self.gen_max_words.pack(side=tk.LEFT)
        
        ttk.Label(
            words_frame,
            text="words",
            font=('Arial', 10)
        ).pack(side=tk.LEFT, padx=5)
        
        row += 1
        
        # Action buttons
        button_frame = ttk.Frame(settings_frame)
        button_frame.grid(row=row, column=0, columnspan=3, pady=20)
        
        self.generate_btn = ttk.Button(
            button_frame,
            text="🎨 Generate Chapter",
            command=self.generate_chapter,
            width=25
        )
        self.generate_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="👁️ Preview Prompt",
            command=self.view_generation_prompt,
            width=20
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="📋 Load Previous Chapter",
            command=self.load_previous_chapter_summary,
            width=25
        ).pack(side=tk.LEFT, padx=5)
        
        settings_frame.columnconfigure(1, weight=1)
        
        # Bottom: Generated chapter display
        bottom_frame = ttk.Frame(paned)
        paned.add(bottom_frame, weight=3)
        
        output_frame = ttk.LabelFrame(bottom_frame, text="Generated Chapter", padding=10)
        output_frame.pack(fill=tk.BOTH, expand=True)
        
        # Progress bar
        self.gen_progress = ttk.Progressbar(output_frame, mode='indeterminate')
        self.gen_progress.pack(fill=tk.X, pady=(0, 10))
        
        # Status label
        self.gen_status_label = ttk.Label(
            output_frame,
            text="Ready to generate",
            font=('Arial', 10, 'italic')
        )
        self.gen_status_label.pack(pady=5)
        
        # Output text
        text_frame = ttk.Frame(output_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        text_scroll = ttk.Scrollbar(text_frame)
        text_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.gen_output = tk.Text(
            text_frame,
            yscrollcommand=text_scroll.set,
            font=('Georgia', 11),
            wrap=tk.WORD,
            padx=20,
            pady=15
        )
        self.gen_output.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        text_scroll.config(command=self.gen_output.yview)
        
        # Output action buttons
        output_button_frame = ttk.Frame(output_frame)
        output_button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(
            output_button_frame,
            text="💾 Save Chapter",
            command=self.save_generated_chapter,
            width=18
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            output_button_frame,
            text="🔄 Regenerate",
            command=self.generate_chapter,
            width=18
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            output_button_frame,
            text="📋 Copy to Clipboard",
            command=self.copy_chapter_to_clipboard,
            width=20
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            output_button_frame,
            text="📄 Export as TXT",
            command=self.export_chapter_txt,
            width=18
        ).pack(side=tk.LEFT, padx=5)

    # ----------------- Export / Clipboard Helpers -----------------
    def copy_chapter_to_clipboard(self):
        """Copy currently displayed/generated chapter to clipboard."""
        try:
            text = ''
            # Prefer generated output if visible
            if hasattr(self, 'gen_output') and self.gen_output.get('1.0', tk.END).strip():
                text = self.gen_output.get('1.0', tk.END).strip()
            # Otherwise use chapter viewer
            if not text and hasattr(self, 'chapter_viewer'):
                text = self.chapter_viewer.get('1.0', tk.END).strip()

            if not text:
                messagebox.showwarning('No Content', 'No chapter content available to copy.')
                return

            self.window.clipboard_clear()
            self.window.clipboard_append(text)
            self.update_status('Chapter copied to clipboard')
            messagebox.showinfo('Copied', 'Chapter text copied to clipboard.')
        except Exception as e:
            messagebox.showerror('Error', f'Failed to copy to clipboard: {e}')

    def export_chapter_txt(self):
        """Export current generated chapter to a TXT file."""
        # Reuse export_chapter behavior
        return self.export_chapter()

    def export_chapter(self):
        """Export generated chapter or current viewer content to a .txt file."""
        if not self.current_story_id:
            messagebox.showwarning('No Story', 'Please select a story first.')
            return

        # Determine content to export
        content = ''
        filename_default = 'chapter.txt'
        if hasattr(self, 'gen_output') and self.gen_output.get('1.0', tk.END).strip():
            content = self.gen_output.get('1.0', tk.END).strip()
            chapter_num = self.gen_chapter_number.get().strip() if hasattr(self, 'gen_chapter_number') else ''
            if chapter_num:
                filename_default = f"Chapter_{chapter_num}.txt"
        elif hasattr(self, 'chapter_viewer') and self.chapter_viewer.get('1.0', tk.END).strip():
            content = self.chapter_viewer.get('1.0', tk.END).strip()
            filename_default = 'Chapter.txt'
        else:
            messagebox.showwarning('No Content', 'No chapter content available to export.')
            return

        story = self.db.get_story(self.current_story_id) if self.current_story_id else None
        title = story.get('title', 'story') if story else 'story'
        suggested = f"{title}_{filename_default}".replace(' ', '_')

        path = filedialog.asksaveasfilename(defaultextension='.txt', initialfile=suggested, filetypes=[('Text files','*.txt')])
        if not path:
            return

        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            messagebox.showinfo('Exported', f'Chapter exported to:\n{path}')
            self.update_status(f'Exported chapter to {os.path.basename(path)}')
        except Exception as e:
            messagebox.showerror('Export Error', f'Failed to export chapter: {e}')

    def export_selected_chapter(self):
        """Export the chapter currently shown in the viewer to a TXT file."""
        # If viewer has content, export it; otherwise fall back to selection
        if hasattr(self, 'chapter_viewer') and self.chapter_viewer.get('1.0', tk.END).strip():
            return self.export_chapter()

        # If no content in viewer, try to get selected tree item
        try:
            sel = self.chapters_tree.selection()
            if not sel:
                messagebox.showwarning('No Selection', 'Select a chapter first.')
                return
            item = sel[0]
            vals = self.chapters_tree.item(item).get('values', [])
            # First column is chapter number
            chapter_num = vals[0] if vals else ''
            chapter = None
            if chapter_num and self.current_story_id:
                chapter = self.db.get_chapter(self.current_story_id, int(chapter_num))
            if chapter and chapter.get('content'):
                # Temporarily set viewer content and export
                self.chapter_viewer.delete('1.0', tk.END)
                self.chapter_viewer.insert('1.0', chapter['content'])
                return self.export_chapter()
            else:
                messagebox.showwarning('No Content', 'Selected chapter has no content to export.')
        except Exception as e:
            messagebox.showerror('Error', f'Failed to export selected chapter: {e}')

    def export_all_chapters(self):
        """Export all chapters for the current story into separate TXT files in a chosen folder."""
        if not self.current_story_id:
            messagebox.showwarning('No Story', 'Please select a story first.')
            return

        folder = filedialog.askdirectory()
        if not folder:
            return

        try:
            chapters = self.db.get_all_chapters(self.current_story_id)
            if not chapters:
                messagebox.showinfo('No Chapters', 'No chapters to export for this story.')
                return
            for ch in chapters:
                num = ch.get('chapter_number', '0')
                title = ch.get('title') or f'Chapter_{num}'
                safe_title = f"{num:03d}_{title}".replace(' ', '_')
                path = os.path.join(folder, f"{safe_title}.txt")
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(ch.get('content') or '')

            messagebox.showinfo('Export Complete', f'Exported {len(chapters)} chapters to:\n{folder}')
            self.update_status(f'Exported {len(chapters)} chapters')
        except Exception as e:
            messagebox.showerror('Export Error', f'Failed to export all chapters: {e}')
    
    def create_chapters_list_tab(self):
        """Enhanced chapters list tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📚 Chapters List")
        
        # Top controls
        control_frame = ttk.Frame(tab)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(
            control_frame,
            text="All Chapters",
            font=('Arial', 14, 'bold')
        ).pack(side=tk.LEFT, padx=5)
        
        # Filter by status
        ttk.Label(control_frame, text="Status:").pack(side=tk.LEFT, padx=(30, 5))
        self.chapter_status_filter = ttk.Combobox(
            control_frame,
            width=12,
            values=['All', 'draft', 'complete', 'revised'],
            state='readonly'
        )
        self.chapter_status_filter.set('All')
        self.chapter_status_filter.pack(side=tk.LEFT, padx=5)
        self.chapter_status_filter.bind('<<ComboboxSelected>>', lambda e: self.load_chapters_list())
        
        ttk.Button(
            control_frame,
            text="🔄 Refresh",
            command=self.load_chapters_list,
            width=12
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            control_frame,
            text="📊 Statistics",
            command=self.show_chapter_stats,
            width=15
        ).pack(side=tk.RIGHT, padx=5)
        
        # Chapters tree view
        tree_frame = ttk.Frame(tab)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Treeview with scrollbar
        tree_scroll = ttk.Scrollbar(tree_frame)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        columns = ('Chapter', 'Title', 'Words', 'POV', 'Status', 'Date')
        self.chapters_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show='tree headings',
            height=12,
            yscrollcommand=tree_scroll.set
        )
        
        self.chapters_tree.heading('#0', text='ID')
        self.chapters_tree.heading('Chapter', text='Chapter #')
        self.chapters_tree.heading('Title', text='Title')
        self.chapters_tree.heading('Words', text='Word Count')
        self.chapters_tree.heading('POV', text='POV')
        self.chapters_tree.heading('Status', text='Status')
        self.chapters_tree.heading('Date', text='Created')
        
        self.chapters_tree.column('#0', width=50)
        self.chapters_tree.column('Chapter', width=80)
        self.chapters_tree.column('Title', width=350)
        self.chapters_tree.column('Words', width=100)
        self.chapters_tree.column('POV', width=150)
        self.chapters_tree.column('Status', width=100)
        self.chapters_tree.column('Date', width=120)
        
        self.chapters_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.config(command=self.chapters_tree.yview)
        
        self.chapters_tree.bind('<Double-1>', self.view_chapter_from_list)
        self.chapters_tree.bind('<<TreeviewSelect>>', self.on_chapter_tree_select)
        
        # Chapter viewer/editor
        viewer_frame = ttk.LabelFrame(tab, text="Chapter Content", padding=10)
        viewer_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        viewer_scroll = ttk.Scrollbar(viewer_frame)
        viewer_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.chapter_viewer = tk.Text(
            viewer_frame,
            yscrollcommand=viewer_scroll.set,
            font=('Georgia', 11),
            wrap=tk.WORD,
            padx=20,
            pady=15
        )
        self.chapter_viewer.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        viewer_scroll.config(command=self.chapter_viewer.yview)
        
        # Viewer action buttons
        viewer_button_frame = ttk.Frame(viewer_frame)
        viewer_button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(
            viewer_button_frame,
            text="✏️ Edit Chapter",
            command=self.edit_selected_chapter,
            width=18
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            viewer_button_frame,
            text="🗑️ Delete Chapter",
            command=self.delete_selected_chapter,
            width=18
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            viewer_button_frame,
            text="📄 Export Chapter",
            command=self.export_selected_chapter,
            width=18
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            viewer_button_frame,
            text="✅ Mark as Complete",
            command=self.mark_chapter_complete,
            width=20
        ).pack(side=tk.LEFT, padx=5)
    
    # ==================== THEME MANAGEMENT ====================
    
    def apply_theme(self):
        """Apply current theme to all widgets with comprehensive styling"""
        theme = self.theme_manager.get_theme()
        
        # Configure main window
        self.window.configure(bg=theme['bg'])
        
        # Configure ttk styles
        style = ttk.Style(self.window)
        try:
            style.theme_use('clam')  # 'clam' or 'alt' often looks cleaner
        except Exception:
            pass

        # Configure global fonts and padding
        default_font = ('Segoe UI', 10)  # or 'Arial' depending on platform
        self.window.option_add("*Font", default_font)
        style.configure('TButton', padding=(8,6), relief='flat', background='#2b7cff', foreground='white')
        style.map('TButton',
                  background=[('active', '#1155cc')],
                  foreground=[('disabled', 'gray')])
        # Notebook tab padding
        style.configure('TNotebook.Tab', padding=[12, 8])
        
        # ===== FRAMES =====
        style.configure('TFrame', background=theme['frame_bg'])
        style.configure('TLabelframe', 
                       background=theme['labelframe_bg'],
                       foreground=theme['labelframe_fg'],
                       bordercolor=theme['labelframe_border'],
                       relief='solid')
        style.configure('TLabelframe.Label',
                       background=theme['labelframe_bg'],
                       foreground=theme['labelframe_fg'],
                       font=('Arial', 10, 'bold'))
        
        # ===== LABELS =====
        style.configure('TLabel',
                       background=theme['frame_bg'],
                       foreground=theme['fg'])
        
        # ===== BUTTONS =====
        style.configure('TButton',
                       background=theme['button_bg'],
                       foreground=theme['button_fg'],
                       bordercolor=theme['button_border'],
                       lightcolor=theme['button_bg'],
                       darkcolor=theme['button_border'],
                       borderwidth=1,
                       focuscolor=theme['focus_border'],
                       relief='raised',
                       padding=(10, 5))
        
        style.map('TButton',
                 background=[('active', theme['button_hover_bg']),
                           ('pressed', theme['button_active_bg']),
                           ('disabled', theme['disabled_bg'])],
                 foreground=[('disabled', theme['disabled_fg'])],
                 bordercolor=[('focus', theme['focus_border'])])
        
        # ===== ENTRIES =====
        style.configure('TEntry',
                       fieldbackground=theme['input_bg'],
                       foreground=theme['input_fg'],
                       bordercolor=theme['input_border'],
                       lightcolor=theme['input_bg'],
                       darkcolor=theme['input_border'],
                       insertcolor=theme['text_cursor'],
                       borderwidth=1,
                       relief='solid')
        
        style.map('TEntry',
                 bordercolor=[('focus', theme['input_focus_border'])],
                 lightcolor=[('focus', theme['accent_light'])])
        
        # ===== COMBOBOX =====
        style.configure('TCombobox',
                       fieldbackground=theme['input_bg'],
                       foreground=theme['input_fg'],
                       background=theme['input_bg'],
                       bordercolor=theme['input_border'],
                       arrowcolor=theme['fg'],
                       borderwidth=1,
                       relief='solid')
        
        style.map('TCombobox',
                 fieldbackground=[('readonly', theme['input_bg'])],
                 selectbackground=[('readonly', theme['input_bg'])],
                 selectforeground=[('readonly', theme['input_fg'])],
                 bordercolor=[('focus', theme['input_focus_border'])])
        
        # ===== NOTEBOOK (TABS) =====
        style.configure('TNotebook',
                       background=theme['bg'],
                       borderwidth=0,
                       tabmargins=[2, 5, 2, 0])
        
        style.configure('TNotebook.Tab',
                       background=theme['tab_bg'],
                       foreground=theme['tab_fg'],
                       padding=[20, 10],
                       borderwidth=1,
                       focuscolor='')
        
        style.map('TNotebook.Tab',
                 background=[('selected', theme['tab_selected_bg']),
                           ('active', theme['tab_hover_bg'])],
                 foreground=[('selected', theme['tab_selected_fg']),
                           ('active', theme['fg'])],
                 expand=[('selected', [1, 1, 1, 0])])
        
        # ===== PROGRESSBAR =====
        style.configure('TProgressbar',
                       background=theme['accent'],
                       troughcolor=theme['tertiary_bg'],
                       bordercolor=theme['border'],
                       lightcolor=theme['accent'],
                       darkcolor=theme['accent'])
        
        # ===== SEPARATOR =====
        style.configure('TSeparator',
                       background=theme['separator'])
        
        # ===== SCROLLBAR =====
        style.configure('TScrollbar',
                       background=theme['scrollbar_bg'],
                       troughcolor=theme['scrollbar_bg'],
                       bordercolor=theme['border'],
                       arrowcolor=theme['fg'])
        
        style.map('TScrollbar',
                 background=[('active', theme['scrollbar_active'])],
                 arrowcolor=[('active', theme['fg'])])
        
        # ===== TREEVIEW =====
        style.configure('Treeview',
                       background=theme['list_bg'],
                       foreground=theme['list_fg'],
                       fieldbackground=theme['list_bg'],
                       borderwidth=1,
                       relief='solid')
        
        style.map('Treeview',
                 background=[('selected', theme['list_select_bg'])],
                 foreground=[('selected', theme['list_select_fg'])])
        
        style.configure('Treeview.Heading',
                       background=theme['header_bg'],
                       foreground=theme['header_fg'],
                       borderwidth=1,
                       relief='raised')
        
        style.map('Treeview.Heading',
                 background=[('active', theme['hover_bg'])])
        
        # ===== PANEDWINDOW =====
        style.configure('TPanedwindow',
                       background=theme['bg'])
        style.configure('Sash',
                       sashthickness=6,
                       sashrelief='flat',
                       background=theme['separator'])
        
        # ===== TEXT WIDGETS =====
        text_widgets = []
        
        # Collect all text widgets
        if hasattr(self, 'overview_synopsis'):
            text_widgets.append(self.overview_synopsis)
        if hasattr(self, 'gen_plot_directive'):
            text_widgets.append(self.gen_plot_directive)
        if hasattr(self, 'gen_previous_summary'):
            text_widgets.append(self.gen_previous_summary)
        if hasattr(self, 'gen_output'):
            text_widgets.append(self.gen_output)
        if hasattr(self, 'chapter_viewer'):
            text_widgets.append(self.chapter_viewer)
        if hasattr(self, 'power_systems_text'):
            text_widgets.append(self.power_systems_text)
        if hasattr(self, 'lore_text'):
            text_widgets.append(self.lore_text)
        if hasattr(self, 'organizations_text'):
            text_widgets.append(self.organizations_text)
        
        for widget in text_widgets:
            try:
                widget.configure(
                    bg=theme['text_bg'],
                    fg=theme['text_fg'],
                    insertbackground=theme['text_cursor'],
                    selectbackground=theme['text_selection_bg'],
                    selectforeground=theme['text_selection_fg'],
                    borderwidth=1,
                    relief='solid'
                )
            except Exception:
                pass
        
        # Character form text widgets
        if hasattr(self, 'char_widgets'):
            for widget in self.char_widgets.values():
                if isinstance(widget, tk.Text):
                    try:
                        widget.configure(
                            bg=theme['text_bg'],
                            fg=theme['text_fg'],
                            insertbackground=theme['text_cursor'],
                            selectbackground=theme['text_selection_bg'],
                            selectforeground=theme['text_selection_fg']
                        )
                    except Exception:
                        pass
        
        # Location form text widgets
        if hasattr(self, 'location_widgets'):
            for widget in self.location_widgets.values():
                if isinstance(widget, tk.Text):
                    try:
                        widget.configure(
                            bg=theme['text_bg'],
                            fg=theme['text_fg'],
                            insertbackground=theme['text_cursor'],
                            selectbackground=theme['text_selection_bg'],
                            selectforeground=theme['text_selection_fg']
                        )
                    except Exception:
                        pass
        
        # Creature form text widgets
        if hasattr(self, 'creature_widgets'):
            for widget in self.creature_widgets.values():
                if isinstance(widget, tk.Text):
                    try:
                        widget.configure(
                            bg=theme['text_bg'],
                            fg=theme['text_fg'],
                            insertbackground=theme['text_cursor'],
                            selectbackground=theme['text_selection_bg'],
                            selectforeground=theme['text_selection_fg']
                        )
                    except Exception:
                        pass
        
        # Progression form text widgets
        if hasattr(self, 'progression_widgets'):
            for widget in self.progression_widgets.values():
                if isinstance(widget, tk.Text):
                    try:
                        widget.configure(
                            bg=theme['text_bg'],
                            fg=theme['text_fg'],
                            insertbackground=theme['text_cursor'],
                            selectbackground=theme['text_selection_bg'],
                            selectforeground=theme['text_selection_fg']
                        )
                    except Exception:
                        pass
        
        # ===== LISTBOX WIDGETS =====
        listbox_widgets = []
        
        if hasattr(self, 'story_listbox'):
            listbox_widgets.append(self.story_listbox)
        if hasattr(self, 'char_listbox'):
            listbox_widgets.append(self.char_listbox)
        if hasattr(self, 'location_listbox'):
            listbox_widgets.append(self.location_listbox)
        if hasattr(self, 'creature_listbox'):
            listbox_widgets.append(self.creature_listbox)
        
        for widget in listbox_widgets:
            try:
                widget.configure(
                    bg=theme['list_bg'],
                    fg=theme['list_fg'],
                    selectbackground=theme['list_select_bg'],
                    selectforeground=theme['list_select_fg'],
                    borderwidth=1,
                    relief='solid',
                    highlightthickness=0
                )
            except Exception:
                pass
        
        # ===== ENTRY WIDGETS =====
        entry_widgets = []
        
        if hasattr(self, 'overview_title'):
            entry_widgets.append(self.overview_title)
        if hasattr(self, 'overview_genre'):
            entry_widgets.append(self.overview_genre)
        if hasattr(self, 'overview_themes'):
            entry_widgets.append(self.overview_themes)
        if hasattr(self, 'overview_tone'):
            entry_widgets.append(self.overview_tone)
        if hasattr(self, 'overview_style'):
            entry_widgets.append(self.overview_style)
        if hasattr(self, 'gen_chapter_number'):
            entry_widgets.append(self.gen_chapter_number)
        if hasattr(self, 'gen_chapter_title'):
            entry_widgets.append(self.gen_chapter_title)
        if hasattr(self, 'story_search'):
            entry_widgets.append(self.story_search)
        
        for widget in entry_widgets:
            try:
                widget.configure(
                    background=theme['input_bg'],
                    foreground=theme['input_fg']
                )
            except Exception:
                pass
        
        # ===== STATUS BAR =====
        if hasattr(self, 'status_bar'):
            self.status_bar.configure(
                background=theme['statusbar_bg'],
                foreground=theme['statusbar_fg']
            )
        
        if hasattr(self, 'ai_status_label'):
            self.ai_status_label.configure(
                background=theme['statusbar_bg'],
                foreground=theme['statusbar_fg']
            )
        
        # ===== CANVAS WIDGETS =====
        canvas_widgets = []
        for widget in self.window.winfo_children():
            self._apply_theme_recursive(widget, theme)
        
        # Force update
        self.window.update_idletasks()
        
        # Update status message
        theme_name = self.theme_manager.current_theme.capitalize()
        self.update_status(f"{theme_name} theme applied successfully")
    
    def _apply_theme_recursive(self, widget, theme):
        """Recursively apply theme to all child widgets"""
        try:
            widget_class = widget.winfo_class()
            
            # Canvas
            if widget_class == 'Canvas':
                widget.configure(bg=theme['bg'], highlightthickness=0)
            
            # Frame
            elif widget_class == 'Frame':
                widget.configure(bg=theme['frame_bg'])
            
            # Label
            elif widget_class == 'Label':
                widget.configure(bg=theme['frame_bg'], fg=theme['fg'])
            
            # Entry
            elif widget_class == 'Entry':
                widget.configure(bg=theme['input_bg'], fg=theme['input_fg'],
                               insertbackground=theme['text_cursor'])
            
            # Text
            elif widget_class == 'Text':
                widget.configure(
                    bg=theme['text_bg'],
                    fg=theme['text_fg'],
                    insertbackground=theme['text_cursor'],
                    selectbackground=theme['text_selection_bg'],
                    selectforeground=theme['text_selection_fg']
                )
            
            # Listbox
            elif widget_class == 'Listbox':
                widget.configure(
                    bg=theme['list_bg'],
                    fg=theme['list_fg'],
                    selectbackground=theme['list_select_bg'],
                    selectforeground=theme['list_select_fg']
                )
            
            # Scale
            elif widget_class == 'Scale':
                widget.configure(
                    bg=theme['frame_bg'],
                    fg=theme['fg'],
                    troughcolor=theme['tertiary_bg'],
                    activebackground=theme['accent']
                )
            
            # Recurse through children
            for child in widget.winfo_children():
                self._apply_theme_recursive(child, theme)
        
        except Exception:
            pass
    
    def toggle_theme(self):
        """Toggle between light and dark theme"""
        self.theme_manager.toggle_theme()
        self.apply_theme()
    
    def set_theme(self, theme_name):
        """Set specific theme"""
        self.theme_manager.set_theme(theme_name)
        self.apply_theme()
    
    # ==================== STORY MANAGEMENT ====================
    
    def load_stories(self):
        """Load all stories into the listbox"""
        self.story_listbox.delete(0, tk.END)
        stories = self.db.get_all_stories()
        
        self.stories_data = {}
        for story in stories:
            display_text = f"{story['title']}"
            self.story_listbox.insert(tk.END, display_text)
            self.stories_data[display_text] = story
    
    def filter_stories(self, event=None):
        """Filter stories based on search"""
        search_term = self.story_search.get().lower()
        self.story_listbox.delete(0, tk.END)
        
        for display_text, story in self.stories_data.items():
            if search_term in display_text.lower():
                self.story_listbox.insert(tk.END, display_text)
    
    def on_story_select(self, event):
        """Handle story selection"""
        selection = self.story_listbox.curselection()
        if not selection:
            return
        
        selected_text = self.story_listbox.get(selection[0])
        story = self.stories_data.get(selected_text)
        
        if not story:
            return
        
        self.current_story_id = story['id']
        self.load_story_data(story['id'])
        
        # Update sidebar info
        self.story_title_label.config(text=story['title'])
        
        stats_text = f"Chapters: {story['current_chapter']}\n"
        stats_text += f"Genre: {story['genre'] or 'Not set'}\n"
        stats_text += f"Status: {story['status']}"
        self.story_stats_label.config(text=stats_text)
        
        self.update_status(f"Loaded: {story['title']}")
    
    def load_story_data(self, story_id):
        """Load all data for a story into the UI"""
        story = self.db.get_story(story_id)
        
        # Load overview
        self.overview_title.delete(0, tk.END)
        self.overview_title.insert(0, story['title'])
        
        self.overview_synopsis.delete('1.0', tk.END)
        self.overview_synopsis.insert('1.0', story['synopsis'] or '')
        
        self.overview_genre.delete(0, tk.END)
        self.overview_genre.insert(0, story['genre'] or 'Light Novel / Fantasy')
        
        self.overview_themes.delete(0, tk.END)
        self.overview_themes.insert(0, story['themes'] or '')
        
        self.overview_tone.delete(0, tk.END)
        self.overview_tone.insert(0, story['tone'] or '')
        
        self.overview_style.delete(0, tk.END)
        self.overview_style.insert(0, story['writing_style'] or 'ReZero/Fate-inspired')
        
        # Load all data
        self.load_characters()
        self.load_locations()
        self.load_creatures()
        self.load_power_systems()
        self.load_lore()
        self.load_organizations()
        self.load_progression()
        self.load_chapters_list()
        
        # Update POV character dropdown
        self.update_pov_dropdown()
    
    def update_pov_dropdown(self):
        """Update POV character dropdown with current characters"""
        if not self.current_story_id:
            return
        
        characters = self.db.get_characters(self.current_story_id)
        char_names = [c['name'] for c in characters]
        self.gen_pov_character['values'] = char_names
        
        # Set default to protagonist if exists
        protagonists = [c['name'] for c in characters if c['role'] == 'Protagonist']
        if protagonists:
            self.gen_pov_character.set(protagonists[0])
    
    def new_story(self):
        """Create a new story"""
        dialog = tk.Toplevel(self.window)
        dialog.title("Create New Story")
        dialog.geometry("600x500")
        dialog.transient(self.window)
        dialog.grab_set()
        
        # Apply theme to dialog
        theme = self.theme_manager.get_theme()
        dialog.configure(bg=theme['bg'])
        
        frame = ttk.Frame(dialog, padding=30)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(
            frame,
            text="Create New Light Novel",
            font=('Arial', 16, 'bold')
        ).pack(pady=(0, 20))
        
        # Title
        ttk.Label(frame, text="Story Title:", font=('Arial', 11, 'bold')).pack(anchor='w', pady=(10, 5))
        title_entry = ttk.Entry(frame, width=60, font=('Arial', 11))
        title_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Synopsis
        ttk.Label(frame, text="Synopsis:", font=('Arial', 11, 'bold')).pack(anchor='w', pady=(10, 5))
        ttk.Label(
            frame,
            text="Brief description of your story (helps AI generate world structure)",
            font=('Arial', 9, 'italic'),
            foreground='gray'
        ).pack(anchor='w')
        
        synopsis_frame = ttk.Frame(frame)
        synopsis_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 10))
        
        synopsis_scroll = ttk.Scrollbar(synopsis_frame)
        synopsis_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        synopsis_text = tk.Text(
            synopsis_frame,
            width=60,
            height=8,
            font=('Arial', 10),
            wrap=tk.WORD,
            yscrollcommand=synopsis_scroll.set
        )
        synopsis_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        synopsis_scroll.config(command=synopsis_text.yview)
        row += 1
        
        # Genre
        ttk.Label(frame, text="Genre:", font=('Arial', 11, 'bold')).pack(anchor='w', pady=(10, 5))
        genre_entry = ttk.Entry(frame, width=60, font=('Arial', 11))
        genre_entry.insert(0, "Light Novel / Fantasy")
        genre_entry.pack(fill=tk.X, pady=(0, 10))
        
        def create():
            title = title_entry.get().strip()
            if not title:
                messagebox.showerror("Error", "Story title is required!")
                return
            
            synopsis = synopsis_text.get('1.0', tk.END).strip()
            genre = genre_entry.get().strip()
            
            story_id = self.db.create_story(
                title=title,
                synopsis=synopsis,
                genre=genre,
                writing_style="ReZero/Fate-inspired - Deep internal monologue, detailed sensory descriptions"
            )
            
            self.load_stories()
            dialog.destroy()

            # Select the newly created story and switch to Overview tab so the
            # user can use the save/edit/delete controls there.
            try:
                self.current_story_id = story_id
                self.load_story_data(story_id)
                try:
                    self.notebook.select(0)
                except Exception:
                    pass
                self.update_status(f"Created story: {title}")
            except Exception:
                pass

            messagebox.showinfo(
                "Success",
                f"Story '{title}' created successfully!\n\n"
                "You can now:\n"
                "• Add characters\n"
                "• Build the world\n"
                "• Create lore and power systems\n"
                "• Generate chapters"
            )
            
            # Ask if they want AI to analyze synopsis
            if synopsis and messagebox.askyesno(
                "AI World Generation",
                "Would you like AI to analyze your synopsis and suggest:\n"
                "• Key characters\n"
                "• World locations\n"
                "• Power systems\n"
                "• Story arcs\n\n"
                "This may take 1-2 minutes."
            ):
                self.current_story_id = story_id
                self.load_story_data(story_id)
                self.generate_from_synopsis()
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=20)
        
        ttk.Button(
            button_frame,
            text="Create Story",
            command=create,
            width=20
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Cancel",
            command=dialog.destroy,
            width=20
        ).pack(side=tk.LEFT, padx=5)
        
        title_entry.focus()
    
    def select_story(self):
        """Prompt user to select a story"""
        if self.story_listbox.size() == 0:
            messagebox.showinfo(
                "No Stories",
                "No stories available. Create a new story first."
            )
            return
        
        # Switch to first tab to show story info
        self.notebook.select(0)
    
    def save_all(self):
        """Save all current changes"""
        if not self.current_story_id:
            messagebox.showwarning("No Story", "Please select a story first.")
            return
        
        try:
            # Save overview
            self.save_overview()
            
            # Save progression if changed
            self.save_progression()
            
            messagebox.showinfo("Saved", "All changes saved successfully!")
        except Exception as e:
            messagebox.showerror("Save Error", f"Error saving: {str(e)}")
    
    def save_overview(self):
        """Save story overview"""
        if not self.current_story_id:
            return
        
        self.db.update_story(
            self.current_story_id,
            title=self.overview_title.get(),
            synopsis=self.overview_synopsis.get('1.0', tk.END).strip(),
            genre=self.overview_genre.get(),
            themes=self.overview_themes.get(),
            tone=self.overview_tone.get(),
            writing_style=self.overview_style.get()
        )
        
        self.load_stories()
        self.update_status("Story information saved")
    
    def delete_current_story(self):
        """Delete the currently selected story"""
        if not self.current_story_id:
            messagebox.showwarning("No Selection", "Please select a story first.")
            return
        
        story = self.db.get_story(self.current_story_id)
        
        if messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete '{story['title']}'?\n\n"
            "This will delete:\n"
            "• All characters\n"
            "• All locations\n"
            "• All lore\n"
            "• All chapters\n\n"
            "This cannot be undone!"
        ):
            self.db.delete_story(self.current_story_id)
            self.current_story_id = None
            self.load_stories()
            
            # Clear all fields
            self.story_title_label.config(text="No story selected")
            self.story_stats_label.config(text="")
            
            messagebox.showinfo("Deleted", "Story deleted successfully.")
    
    # ==================== CHARACTER MANAGEMENT ====================
    
    def load_characters(self):
        """Load characters for current story"""
        if not self.current_story_id:
            return
        
        self.char_listbox.delete(0, tk.END)
        
        role_filter = self.char_role_filter.get()
        if role_filter == 'All':
            characters = self.db.get_characters(self.current_story_id)
        else:
            characters = self.db.get_characters(self.current_story_id, role=role_filter)
        
        self.characters_data = {}
        for char in characters:
            # Use emoji indicators
            role_emoji = {
                'Protagonist': '⭐',
                'Deuteragonist': '🌟',
                'Major Character': '●',
                'Supporting Character': '○',
                'Minor Character': '·',
                'Antagonist': '⚔️',
                'Love Interest': '💕',
                'Mentor': '📚',
                'Rival': '⚡'
            }.get(char['role'], '●')
            
            display_text = f"{role_emoji} {char['name']} - {char['role']}"
            self.char_listbox.insert(tk.END, display_text)
            self.characters_data[display_text] = char
    
    def on_character_select(self, event):
        """Handle character selection"""
        selection = self.char_listbox.curselection()
        if not selection:
            return
        
        selected_text = self.char_listbox.get(selection[0])
        char = self.characters_data.get(selected_text)
        
        if not char:
            return
        
        self.current_character_id = char['id']
        
        # Populate form
        self.char_widgets['name'].delete(0, tk.END)
        self.char_widgets['name'].insert(0, char['name'])
        
        self.char_widgets['role'].set(char['role'])
        
        self.char_widgets['age'].delete(0, tk.END)
        if char['age']:
            self.char_widgets['age'].insert(0, str(char['age']))
        
        self.char_widgets['gender'].set(char['gender'] or '')
        self.char_widgets['status'].set(char['status'] or 'Alive')
        
        # Text fields
        text_fields = ['appearance', 'personality', 'background', 'abilities',
                      'motivations', 'relationships', 'character_arc', 'voice_style',
                      'quirks', 'combat_style', 'equipment']
        
        for field in text_fields:
            widget = self.char_widgets[field]
            widget.delete('1.0', tk.END)
            if char[field]:
                widget.insert('1.0', char[field])
        
        self.char_widgets['importance'].set(char['importance'])
    
    def add_character(self):
        """Clear form for new character"""
        if not self.current_story_id:
            messagebox.showwarning("No Story", "Please select a story first.")
            return
        
        self.current_character_id = None
        
        # Clear all fields
        self.char_widgets['name'].delete(0, tk.END)
        self.char_widgets['role'].set('')
        self.char_widgets['age'].delete(0, tk.END)
        self.char_widgets['gender'].set('')
        self.char_widgets['status'].set('Alive')
        
        text_fields = ['appearance', 'personality', 'background', 'abilities',
                      'motivations', 'relationships', 'character_arc', 'voice_style',
                      'quirks', 'combat_style', 'equipment']
        
        for field in text_fields:
            self.char_widgets[field].delete('1.0', tk.END)
        
        self.char_widgets['importance'].set(3)
        self.char_widgets['name'].focus()
    
    def save_character(self):
        """Save character (new or update)"""
        if not self.current_story_id:
            messagebox.showwarning("No Story", "Please select a story first.")
            return
        # Gather data from the character form widgets
        name = self.char_widgets['name'].get().strip()
        role = self.char_widgets['role'].get().strip()
        if not name or not role:
            messagebox.showerror("Error", "Name and Role are required!")
            return

        char_data = {
            'age': int(self.char_widgets['age'].get()) if self.char_widgets['age'].get().strip() else None,
            'gender': self.char_widgets['gender'].get(),
            'status': self.char_widgets['status'].get(),
            'importance': int(self.char_widgets['importance'].get())
        }

        text_fields = ['appearance', 'personality', 'background', 'abilities',
                      'motivations', 'relationships', 'character_arc', 'voice_style',
                      'quirks', 'combat_style', 'equipment']

        for field in text_fields:
            widget = self.char_widgets[field]
            try:
                char_data[field] = widget.get('1.0', tk.END).strip()
            except Exception:
                # Fallback for Entry widgets
                char_data[field] = widget.get().strip()
        
        if self.current_character_id:
            # Update existing
            self.db.update_character(self.current_character_id, **char_data)
            self.db.update_character(self.current_character_id, name=name, role=role)
            message = f"Character '{name}' updated successfully!"
        else:
            # Add new
            self.db.add_character(self.current_story_id, name, role, **char_data)
            message = f"Character '{name}' added successfully!"
        
        self.load_characters()
        self.update_pov_dropdown()
        self.update_status(message)
        messagebox.showinfo("Saved", message)
    
    def delete_character(self):
        """Delete current character"""
        if not self.current_character_id:
            messagebox.showwarning("No Selection", "Please select a character first.")
            return
        
        char = self.db.get_character(self.current_character_id)
        if messagebox.askyesno("Confirm Delete", f"Delete character '{char['name']}'?"):
            self.db.delete_character(self.current_character_id)
            self.current_character_id = None
            self.load_characters()
            self.update_pov_dropdown()
            self.add_character()  # Clear form
            self.update_status("Character deleted")
    
    def ai_expand_character(self):
        """Use AI to expand character details"""
        if not self.current_character_id:
            messagebox.showwarning("No Selection", "Please select a character first.")
            return
        
        if not self.ai.test_connection():
            messagebox.showerror("AI Not Connected", "Cannot connect to Ollama. Make sure it's running.")
            return
        
        self.update_status("AI expanding character details...")
        self.window.update()
        
        try:
            result = self.world_gen.expand_character_details(
                self.current_story_id,
                self.current_character_id,
                expansion_focus="complete character profile with depth and nuance"
            )
            
            # Show result in dialog
            self.show_ai_result_dialog(
                "AI Character Expansion",
                result['raw_result'],
                "Review the AI suggestions and manually add what you like to the character form."
            )
            
            self.update_status("Character expansion complete")
            
        except Exception as e:
            messagebox.showerror("Error", f"AI generation failed: {str(e)}")
            self.update_status("AI expansion failed")
    
    # ==================== LOCATION MANAGEMENT ====================
    
    def load_locations(self):
        """Load locations for current story"""
        if not self.current_story_id:
            return
        
        self.location_listbox.delete(0, tk.END)
        
        type_filter = self.location_type_filter.get()
        if type_filter == 'All':
            locations = self.db.get_world_locations(self.current_story_id)
        else:
            locations = [loc for loc in self.db.get_world_locations(self.current_story_id)
                        if loc['type'] == type_filter]
        
        self.locations_data = {}
        for loc in locations:
            display_text = f"📍 {loc['name']} ({loc['type']})"
            self.location_listbox.insert(tk.END, display_text)
            self.locations_data[display_text] = loc
    
    def on_location_select(self, event):
        """Handle location selection"""
        selection = self.location_listbox.curselection()
        if not selection:
            return
        
        selected_text = self.location_listbox.get(selection[0])
        loc = self.locations_data.get(selected_text)
        
        if not loc:
            return
        
        self.current_location_id = loc['id']
        
        # Populate form
        self.location_widgets['name'].delete(0, tk.END)
        self.location_widgets['name'].insert(0, loc['name'])
        
        self.location_widgets['type'].set(loc['type'])
        
        text_fields = ['description', 'geography', 'climate', 'population',
                      'government', 'economy', 'culture', 'history',
                      'notable_locations', 'relationships']
        
        for field in text_fields:
            widget = self.location_widgets[field]
            widget.delete('1.0', tk.END)
            if loc[field]:
                widget.insert('1.0', loc[field])
    
    def add_location(self):
        """Clear form for new location"""
        if not self.current_story_id:
            messagebox.showwarning("No Story", "Please select a story first.")
            return
        
        self.current_location_id = None
        self.location_widgets['name'].delete(0, tk.END)
        self.location_widgets['type'].set('')
        
        text_fields = ['description', 'geography', 'climate', 'population',
                      'government', 'economy', 'culture', 'history',
                      'notable_locations', 'relationships']
        
        for field in text_fields:
            self.location_widgets[field].delete('1.0', tk.END)
        
        self.location_widgets['name'].focus()
    
    def save_location(self):
        """Save location (new or update)"""
        if not self.current_story_id:
            messagebox.showwarning("No Story", "Please select a story first.")
            return
        
        name = self.location_widgets['name'].get().strip()
        loc_type = self.location_widgets['type'].get().strip()
        
        if not name or not loc_type:
            messagebox.showerror("Error", "Name and Type are required!")
            return
        
        # Gather all data
        loc_data = {}
        text_fields = ['description', 'geography', 'climate', 'population',
                      'government', 'economy', 'culture', 'history',
                      'notable_locations', 'relationships']
        
        for field in text_fields:
            loc_data[field] = self.location_widgets[field].get('1.0', tk.END).strip()
        
        if self.current_location_id:
            # Update existing
            self.db.update_world_location(self.current_location_id, name=name, type=loc_type, **loc_data)
            message = f"Location '{name}' updated successfully!"
        else:
            # Add new
            self.db.add_world_location(self.current_story_id, name, loc_type, **loc_data)
            message = f"Location '{name}' added successfully!"
        
        self.load_locations()
        self.update_status(message)
        messagebox.showinfo("Saved", message)
    
    def delete_location(self):
        """Delete current location"""
        if not self.current_location_id:
            messagebox.showwarning("No Selection", "Please select a location first.")
            return
        
        locations = self.db.get_world_locations(self.current_story_id)
        loc = next((l for l in locations if l['id'] == self.current_location_id), None)
        
        if loc and messagebox.askyesno("Confirm Delete", f"Delete location '{loc['name']}'?"):
            cursor = self.db.conn.cursor()
            cursor.execute('DELETE FROM world_structure WHERE id = ?', (self.current_location_id,))
            self.db.conn.commit()
            
            self.current_location_id = None
            self.load_locations()
            self.add_location()
            self.update_status("Location deleted")
    
    def ai_expand_location(self):
        """Use AI to expand location details"""
        if not self.current_location_id:
            messagebox.showwarning("No Selection", "Please select a location first.")
            return
        
        if not self.ai.test_connection():
            messagebox.showerror("AI Not Connected", "Cannot connect to Ollama.")
            return
        
        locations = self.db.get_world_locations(self.current_story_id)
        loc = next((l for l in locations if l['id'] == self.current_location_id), None)
        
        if not loc:
            return
        
        self.update_status("AI expanding location details...")
        self.window.update()
        
        try:
            result = self.world_gen.expand_location(
                self.current_story_id,
                loc['name'],
                loc['type'],
                loc['description'] or "A location in the story world",
                expansion_aspects=['geography', 'culture', 'history', 'economy', 'politics', 'notable_locations']
            )
            
            self.show_ai_result_dialog(
                f"AI Location Expansion: {loc['name']}",
                result['raw_result'],
                "Review the AI suggestions and manually add what you like to the location form."
            )
            
            self.update_status("Location expansion complete")
            
        except Exception as e:
            messagebox.showerror("Error", f"AI generation failed: {str(e)}")
            self.update_status("AI expansion failed")
    
    def ai_generate_location(self):
        """Generate a new location with AI"""
        if not self.current_story_id:
            messagebox.showwarning("No Story", "Please select a story first.")
            return
        
        if not self.ai.test_connection():
            messagebox.showerror("AI Not Connected", "Cannot connect to Ollama.")
            return
        
        # Prompt for location concept
        concept = self.prompt_for_input(
            "AI Generate Location",
            "Describe the location you want to generate:",
            "Example: A floating city powered by magic crystals"
        )
        
        if not concept:
            return
        
        self.update_status("AI generating location...")
        self.window.update()
        
        try:
            result = self.world_gen.expand_location(
                self.current_story_id,
                "New Location",
                "Location",
                concept,
                expansion_aspects=['geography', 'culture', 'history', 'economy', 'notable_locations']
            )
            
            self.show_ai_result_dialog(
                "AI Generated Location",
                result['raw_result'],
                "Copy the details you want and manually create the location."
            )
            
            self.update_status("Location generation complete")
            
        except Exception as e:
            messagebox.showerror("Error", f"AI generation failed: {str(e)}")
            self.update_status("Generation failed")
    
    # ==================== BESTIARY MANAGEMENT ====================
    
    def load_creatures(self):
        """Load creatures for current story"""
        if not self.current_story_id:
            return
        
        self.creature_listbox.delete(0, tk.END)
        
        # Get creatures from lore table (we'll use category='Bestiary')
        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT * FROM lore 
            WHERE story_id = ? AND category = 'Bestiary'
            ORDER BY title
        ''', (self.current_story_id,))
        
        creatures = [dict(row) for row in cursor.fetchall()]
        
        self.creatures_data = {}
        for creature in creatures:
            display_text = f"🐉 {creature['title']}"
            self.creature_listbox.insert(tk.END, display_text)
            self.creatures_data[display_text] = creature
    
    def on_creature_select(self, event):
        """Handle creature selection"""
        selection = self.creature_listbox.curselection()
        if not selection:
            return
        
        selected_text = self.creature_listbox.get(selection[0])
        creature = self.creatures_data.get(selected_text)
        
        if not creature:
            return
        
        self.current_creature_id = creature['id']
        
        # Parse content (stored as JSON-like structure)
        import json
        try:
            data = json.loads(creature['content']) if creature['content'] else {}
        except Exception:
            data = {}
        
        # Populate form
        self.creature_widgets['name'].delete(0, tk.END)
        self.creature_widgets['name'].insert(0, creature['title'])
        
        self.creature_widgets['type'].set(data.get('type', ''))
        self.creature_widgets['threat_level'].set(data.get('threat_level', 'Moderate'))
        
        text_fields = ['description', 'habitat', 'behavior', 'abilities',
                      'weaknesses', 'diet', 'lore', 'drops']
        
        for field in text_fields:
            widget = self.creature_widgets[field]
            widget.delete('1.0', tk.END)
            if field in data:
                widget.insert('1.0', data[field])
    
    def add_creature(self):
        """Clear form for new creature"""
        if not self.current_story_id:
            messagebox.showwarning("No Story", "Please select a story first.")
            return
        
        self.current_creature_id = None
        self.creature_widgets['name'].delete(0, tk.END)
        self.creature_widgets['type'].set('')
        self.creature_widgets['threat_level'].set('Moderate')
        
        text_fields = ['description', 'habitat', 'behavior', 'abilities',
                      'weaknesses', 'diet', 'lore', 'drops']
        
        for field in text_fields:
            self.creature_widgets[field].delete('1.0', tk.END)
        
        self.creature_widgets['name'].focus()
    
    def save_creature(self):
        """Save creature (new or update)"""
        if not self.current_story_id:
            messagebox.showwarning("No Story", "Please select a story first.")
            return
        
        name = self.creature_widgets['name'].get().strip()
        if not name:
            messagebox.showerror("Error", "Creature name is required!")
            return
        
        # Gather all data
        import json
        creature_data = {
            'type': self.creature_widgets['type'].get(),
            'threat_level': self.creature_widgets['threat_level'].get()
        }
        
        text_fields = ['description', 'habitat', 'behavior', 'abilities',
                      'weaknesses', 'diet', 'lore', 'drops']
        
        for field in text_fields:
            creature_data[field] = self.creature_widgets[field].get('1.0', tk.END).strip()
        
        content_json = json.dumps(creature_data)
        
        if self.current_creature_id:
            # Update existing
            cursor = self.db.conn.cursor()
            cursor.execute('''
                UPDATE lore SET title = ?, content = ?
                WHERE id = ?
            ''', (name, content_json, self.current_creature_id))
            self.db.conn.commit()
            message = f"Creature '{name}' updated successfully!"
        else:
            # Add new
            self.db.add_lore(
                self.current_story_id,
                'Bestiary',
                name,
                content_json,
                importance=3
            )
            message = f"Creature '{name}' added successfully!"
        
        self.load_creatures()
        self.update_status(message)
        messagebox.showinfo("Saved", message)
    
    def delete_creature(self):
        """Delete current creature"""
        if not self.current_creature_id:
            messagebox.showwarning("No Selection", "Please select a creature first.")
            return
        
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT title FROM lore WHERE id = ?', (self.current_creature_id,))
        result = cursor.fetchone()
        
        if result and messagebox.askyesno("Confirm Delete", f"Delete creature '{result[0]}'?"):
            cursor.execute('DELETE FROM lore WHERE id = ?', (self.current_creature_id,))
            self.db.conn.commit()
            
            self.current_creature_id = None
            self.load_creatures()
            self.add_creature()
            self.update_status("Creature deleted")
    
    def ai_expand_creature(self):
        """Use AI to expand creature details"""
        if not self.current_creature_id:
            messagebox.showwarning("No Selection", "Please select a creature first.")
            return
        
        if not self.ai.test_connection():
            messagebox.showerror("AI Not Connected", "Cannot connect to Ollama.")
            return
        
        creature = self.db.get_lore_entry(self.current_creature_id)
        
        self.update_status("AI expanding creature details...")
        self.window.update()
        
        try:
            result = self.world_gen.expand_creature_details(
                self.current_story_id,
                self.current_creature_id,
                expansion_focus="detailed creature profile with abilities, habitat, and lore"
            )
            
            # Show result in dialog
            self.show_ai_result_dialog(
                "AI Creature Expansion",
                result['raw_result'],
                "Review the AI suggestions and manually add what you like to the creature form."
            )
            
            self.update_status("Creature expansion complete")
            
        except Exception as e:
            messagebox.showerror("Error", f"AI generation failed: {str(e)}")
            self.update_status("AI expansion failed")
    
    # ==================== POWER SYSTEMS, LORE, ORGANIZATIONS ====================
    
    def load_power_systems(self):
        """Load power systems display"""
        if not self.current_story_id:
            return
        # Populate power systems listbox and detail text
        systems = self.db.get_power_systems(self.current_story_id)
        self.power_entries = systems
        self.power_listbox.delete(0, tk.END)
        for sys in systems:
            self.power_listbox.insert(tk.END, sys['name'])

        # If a system is selected, display details, otherwise clear
        if systems:
            self.current_power_id = systems[0]['id']
            self.power_listbox.selection_set(0)
            self.on_power_select(None)
        else:
            self.current_power_id = None
            self.power_systems_text.config(state='normal')
            self.power_systems_text.delete('1.0', tk.END)
            self.power_systems_text.insert('1.0', "No power systems defined yet.\n\nClick '➕ Add System' to create one.")
            self.power_systems_text.config(state='disabled')

        # Configure tags for detailed display if needed
        try:
            self.power_systems_text.tag_config('title', font=('Arial', 14, 'bold'))
            self.power_systems_text.tag_config('subtitle', font=('Arial', 11, 'bold'))
            self.power_systems_text.tag_config('separator', foreground='gray')
        except Exception:
            pass
    
    def load_lore(self):
        """Load lore entries"""
        if not self.current_story_id:
            return
        # Populate lore listbox and set up details
        category_filter = self.lore_category_filter.get()
        if category_filter == 'All':
            lore_entries = self.db.get_lore(self.current_story_id)
        else:
            lore_entries = self.db.get_lore(self.current_story_id, category=category_filter)

        # Exclude bestiary (handled in Bestiary tab)
        lore_entries = [e for e in lore_entries if e.get('category') != 'Bestiary']

        self.lore_entries = lore_entries
        self.lore_listbox.delete(0, tk.END)
        for entry in lore_entries:
            self.lore_listbox.insert(tk.END, f"{entry['title']} ({entry['category']})")

        if lore_entries:
            self.lore_listbox.selection_set(0)
            self.on_lore_select(None)
        else:
            self.current_lore_id = None
            self.lore_text.config(state='normal')
            self.lore_text.delete('1.0', tk.END)
            self.lore_text.insert('1.0', "No lore entries found.\n\nClick '➕ Add' to create one.")
            self.lore_text.config(state='disabled')

        # Configure tags
        try:
            self.lore_text.tag_config('category', font=('Arial', 13, 'bold'))
            self.lore_text.tag_config('title', font=('Arial', 11, 'bold'))
            self.lore_text.tag_config('meta', font=('Arial', 9, 'italic'), foreground='gray')
            self.lore_text.tag_config('content', font=('Arial', 10))
            self.lore_text.tag_config('separator', foreground='gray')
        except Exception:
            pass

    def on_lore_select(self, event):
        """Handle lore list selection and display detail"""
        sel = self.lore_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        entry = self.lore_entries[idx]
        self.current_lore_id = entry['id']
        self.lore_text.config(state='normal')
        self.lore_text.delete('1.0', tk.END)
        if entry.get('timeline_position'):
            self.lore_text.insert(tk.END, f"⏰ {entry['timeline_position']}\n\n", 'meta')
        if entry.get('content'):
            self.lore_text.insert(tk.END, entry['content'])
        self.lore_text.config(state='disabled')

    def on_power_select(self, event):
        """Handle power system selection and display detail"""
        sel = self.power_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        system = self.power_entries[idx]
        self.current_power_id = system['id']
        self.power_systems_text.config(state='normal')
        self.power_systems_text.delete('1.0', tk.END)
        self.power_systems_text.insert(tk.END, f"{system['name']}\n\n", 'title')
        if system.get('description'):
            self.power_systems_text.insert(tk.END, "📋 Description:\n", 'subtitle')
            self.power_systems_text.insert(tk.END, f"{system['description']}\n\n")
        if system.get('rules'):
            self.power_systems_text.insert(tk.END, "⚖️ Rules & Mechanics:\n", 'subtitle')
            self.power_systems_text.insert(tk.END, f"{system['rules']}\n\n")
        if system.get('limitations'):
            self.power_systems_text.insert(tk.END, "🚫 Limitations:\n", 'subtitle')
            self.power_systems_text.insert(tk.END, f"{system['limitations']}\n\n")
        if system.get('acquisition_method'):
            self.power_systems_text.insert(tk.END, "📚 How to Acquire:\n", 'subtitle')
            self.power_systems_text.insert(tk.END, f"{system['acquisition_method']}\n\n")
        if system.get('power_levels'):
            self.power_systems_text.insert(tk.END, "📊 Power Levels:\n", 'subtitle')
            self.power_systems_text.insert(tk.END, f"{system['power_levels']}\n\n")
        if system.get('examples'):
            self.power_systems_text.insert(tk.END, "✨ Examples:\n", 'subtitle')
            self.power_systems_text.insert(tk.END, f"{system['examples']}\n\n")
        self.power_systems_text.config(state='disabled')

    def edit_lore(self, lore_id=None):
        """Open the lore dialog prefilled for editing a lore entry"""
        if lore_id is None:
            return
        # Fetch entry
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT * FROM lore WHERE id = ?', (lore_id,))
        row = cursor.fetchone()
        if not row:
            messagebox.showerror('Error', 'Lore entry not found')
            return
        data = dict(row)
        # Open add_lore dialog prefilled
        def _open_prefilled():
            # Reuse add_lore but prefill fields
            dialog = tk.Toplevel(self.window)
            dialog.title('Edit Lore Entry')
            dialog.geometry('650x650')
            dialog.transient(self.window)
            dialog.grab_set()

            frame = ttk.Frame(dialog, padding=20)
            frame.pack(fill=tk.BOTH, expand=True)

            ttk.Label(frame, text='Edit Lore Entry', font=('Arial', 16, 'bold')).pack(pady=(0,20))

            fields = {}
            ttk.Label(frame, text='Category:', font=('Arial',11,'bold')).pack(anchor='w', pady=(10,5))
            fields['category'] = ttk.Combobox(frame, width=57, values=['History','Culture','Religion','Technology','Magic','Events','Legends','Prophecies','Other'], state='readonly')
            fields['category'].pack(fill=tk.X, pady=(0,10))
            fields['category'].set(data.get('category',''))

            ttk.Label(frame, text='Title:', font=('Arial',11,'bold')).pack(anchor='w', pady=(10,5))
            fields['title'] = ttk.Entry(frame, width=60, font=('Arial',11))
            fields['title'].pack(fill=tk.X, pady=(0,10))
            fields['title'].insert(0, data.get('title',''))

            ttk.Label(frame, text='Content:', font=('Arial',11,'bold')).pack(anchor='w', pady=(10,5))
            content_frame = ttk.Frame(frame)
            content_frame.pack(fill=tk.BOTH, expand=True, pady=(0,10))
            content_scroll = ttk.Scrollbar(content_frame)
            content_scroll.pack(side=tk.RIGHT, fill=tk.Y)
            fields['content'] = tk.Text(content_frame, width=60, height=12, font=('Arial',10), wrap=tk.WORD, yscrollcommand=content_scroll.set)
            fields['content'].pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            content_scroll.config(command=fields['content'].yview)
            fields['content'].insert('1.0', data.get('content',''))

            ttk.Label(frame, text='Timeline Position (optional):', font=('Arial',11,'bold')).pack(anchor='w', pady=(10,5))
            fields['timeline'] = ttk.Entry(frame, width=60)
            fields['timeline'].pack(fill=tk.X, pady=(0,10))
            fields['timeline'].insert(0, data.get('timeline_position',''))

            ttk.Label(frame, text='Importance:', font=('Arial',11,'bold')).pack(anchor='w', pady=(10,5))
            fields['importance'] = ttk.Combobox(frame, width=15, values=['1','2','3','4','5'], state='readonly')
            fields['importance'].pack(anchor='w', pady=(0,10))
            fields['importance'].set(str(data.get('importance',3)))

            def _save():
                category = fields['category'].get().strip()
                title = fields['title'].get().strip()
                content = fields['content'].get('1.0', tk.END).strip()
                if not category or not title or not content:
                    messagebox.showerror('Error','Category, Title, and Content are required!')
                    return
                timeline = fields['timeline'].get().strip()
                importance = int(fields['importance'].get())
                cursor = self.db.conn.cursor()
                cursor.execute('''
                    UPDATE lore SET category = ?, title = ?, content = ?, timeline_position = ?, importance = ? WHERE id = ?
                ''', (category, title, content, timeline, importance, lore_id))
                self.db.conn.commit()
                dialog.destroy()
                self.load_lore()

            button_frame = ttk.Frame(frame)
            button_frame.pack(pady=20)
            ttk.Button(button_frame, text='Save', command=_save, width=20).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text='Cancel', command=dialog.destroy, width=20).pack(side=tk.LEFT, padx=5)

        _open_prefilled()

    def edit_power_system(self, power_id=None):
        """Open the power system dialog prefilled for editing"""
        if power_id is None:
            return
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT * FROM power_systems WHERE id = ?', (power_id,))
        row = cursor.fetchone()
        if not row:
            messagebox.showerror('Error','Power system not found')
            return
        data = dict(row)

        # Build dialog similar to add_power_system but prefilled
        dialog = tk.Toplevel(self.window)
        dialog.title('Edit Power System')
        dialog.geometry('700x800')
        dialog.transient(self.window)
        dialog.grab_set()

        canvas = tk.Canvas(dialog)
        scrollbar = ttk.Scrollbar(dialog, orient='vertical', command=canvas.yview)
        frame = ttk.Frame(canvas, padding=20)
        frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        ttk.Label(frame, text='Edit Power System', font=('Arial',16,'bold')).pack(pady=(0,20))
        fields = {}
        ttk.Label(frame, text='System Name:', font=('Arial',11,'bold')).pack(anchor='w', pady=(10,5))
        fields['name'] = ttk.Entry(frame, width=60, font=('Arial',11))
        fields['name'].pack(fill=tk.X, pady=(0,10))
        fields['name'].insert(0, data.get('name',''))

        text_fields = [
            ('description','Description',5),('rules','Rules & Mechanics',6),('limitations','Limitations & Costs',5),
            ('acquisition_method','How to Acquire/Learn',5),('power_levels','Power Levels/Progression',5),('examples','Example Abilities',6)
        ]
        for field_name,label,height in text_fields:
            ttk.Label(frame, text=f"{label}:", font=('Arial',11,'bold')).pack(anchor='w', pady=(10,5))
            tf = ttk.Frame(frame); tf.pack(fill=tk.X, pady=(0,10))
            ts = ttk.Scrollbar(tf); ts.pack(side=tk.RIGHT, fill=tk.Y)
            fields[field_name] = tk.Text(tf, width=60, height=height, font=('Arial',10), wrap=tk.WORD, yscrollcommand=ts.set)
            fields[field_name].pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            ts.config(command=fields[field_name].yview)
            if data.get(field_name):
                fields[field_name].insert('1.0', data.get(field_name))

        def _save():
            name = fields['name'].get().strip()
            if not name:
                messagebox.showerror('Error','System name is required!')
                return
            cursor = self.db.conn.cursor()
            cursor.execute('''
                UPDATE power_systems SET name=?, description=?, rules=?, limitations=?, acquisition_method=?, power_levels=?, examples=?
                WHERE id=?
            ''', (
                fields['name'].get().strip(),
                fields['description'].get('1.0', tk.END).strip(),
                fields['rules'].get('1.0', tk.END).strip(),
                fields['limitations'].get('1.0', tk.END).strip(),
                fields['acquisition_method'].get('1.0', tk.END).strip(),
                fields['power_levels'].get('1.0', tk.END).strip(),
                fields['examples'].get('1.0', tk.END).strip(),
                power_id
            ))
            self.db.conn.commit()
            dialog.destroy()
            self.load_power_systems()

        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=20)
        ttk.Button(button_frame, text='Save', command=_save, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text='Cancel', command=dialog.destroy, width=20).pack(side=tk.LEFT, padx=5)

    def delete_lore(self, lore_id=None):
        """Delete a lore entry by id (confirmation)"""
        if not lore_id:
            messagebox.showwarning('No Selection','Select a lore entry first')
            return
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT title FROM lore WHERE id = ?', (lore_id,))
        r = cursor.fetchone()
        title = r[0] if r else 'Unknown'
        if messagebox.askyesno('Confirm Delete', f"Delete lore '{title}'?"):
            cursor.execute('DELETE FROM lore WHERE id = ?', (lore_id,))
            self.db.conn.commit()
            self.load_lore()

    def delete_power_system(self, power_id=None):
        """Delete power system by id"""
        if not power_id:
            messagebox.showwarning('No Selection','Select a power system first')
            return
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT name FROM power_systems WHERE id = ?', (power_id,))
        r = cursor.fetchone()
        name = r[0] if r else 'Unknown'
        if messagebox.askyesno('Confirm Delete', f"Delete power system '{name}'?"):
            cursor.execute('DELETE FROM power_systems WHERE id = ?', (power_id,))
            self.db.conn.commit()
            self.load_power_systems()
    
    def load_organizations(self):
        """Load organizations display"""
        if not self.current_story_id:
            return
        
        self.organizations_text.delete('1.0', tk.END)
        
        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT * FROM organizations 
            WHERE story_id = ?
            ORDER BY name
        ''', (self.current_story_id,))
        
        organizations = [dict(row) for row in cursor.fetchall()]
        
        if not organizations:
            self.organizations_text.insert(
                '1.0',
                "No organizations defined yet.\n\n"
                "Click '➕ Add Organization' to create one."
            )
        else:
            for org in organizations:
                self.organizations_text.insert(tk.END, f"{'═'*80}\n", 'separator')
                self.organizations_text.insert(tk.END, f"🏛️ {org['name']}\n", 'title')
                if org['type']:
                    self.organizations_text.insert(tk.END, f"Type: {org['type']}\n", 'meta')
                self.organizations_text.insert(tk.END, f"{'═'*80}\n\n", 'separator')
                
                if org['description']:
                    self.organizations_text.insert(tk.END, f"{org['description']}\n\n")
                
                if org['goals']:
                    self.organizations_text.insert(tk.END, "🎯 Goals:\n", 'subtitle')
                    self.organizations_text.insert(tk.END, f"{org['goals']}\n\n")
                
                if org['structure']:
                    self.organizations_text.insert(tk.END, "📊 Structure:\n", 'subtitle')
                    self.organizations_text.insert(tk.END, f"{org['structure']}\n\n")
                
                if org['members']:
                    self.organizations_text.insert(tk.END, "👥 Notable Members:\n", 'subtitle')
                    self.organizations_text.insert(tk.END, f"{org['members']}\n\n")
                
                self.organizations_text.insert(tk.END, "\n")
        
        self.organizations_text.tag_config('title', font=('Arial', 14, 'bold'))
        self.organizations_text.tag_config('subtitle', font=('Arial', 11, 'bold'))
        self.organizations_text.tag_config('meta', font=('Arial', 10, 'italic'))
        self.organizations_text.tag_config('separator', foreground='gray')
    
    def add_power_system(self):
        """Add or edit a power system. If called directly, creates new entry.
        To edit, call with dialog prefilled via `edit_power_system` which passes `power_id`."""
        # This function will create a new dialog for adding; editing handled below
        if not self.current_story_id:
            messagebox.showwarning("No Story", "Please select a story first.")
            return
        
        dialog = tk.Toplevel(self.window)
        dialog.title("Add Power System")
        dialog.geometry("700x800")
        dialog.transient(self.window)
        dialog.grab_set()
        
        canvas = tk.Canvas(dialog)
        scrollbar = ttk.Scrollbar(dialog, orient='vertical', command=canvas.yview)
        frame = ttk.Frame(canvas, padding=20)
        
        frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        ttk.Label(frame, text="Add Power System", font=('Arial', 16, 'bold')).pack(pady=(0, 20))
        
        fields = {}
        
        ttk.Label(frame, text="System Name:", font=('Arial', 11, 'bold')).pack(anchor='w', pady=(10, 5))
        fields['name'] = ttk.Entry(frame, width=60, font=('Arial', 11))
        fields['name'].pack(fill=tk.X, pady=(0, 10))
        
        text_fields = [
            ('description', 'Description', 5),
            ('rules', 'Rules & Mechanics', 6),
            ('limitations', 'Limitations & Costs', 5),
            ('acquisition_method', 'How to Acquire/Learn', 5),
            ('power_levels', 'Power Levels/Progression', 5),
            ('examples', 'Example Abilities', 6)
        ]
        
        for field_name, label, height in text_fields:
            ttk.Label(frame, text=f"{label}:", font=('Arial', 11, 'bold')).pack(anchor='w', pady=(10, 5))
            
            text_frame = ttk.Frame(frame)
            text_frame.pack(fill=tk.X, pady=(0, 10))
            
            text_scroll = ttk.Scrollbar(text_frame)
            text_scroll.pack(side=tk.RIGHT, fill=tk.Y)
            
            fields[field_name] = tk.Text(text_frame, width=60, height=height, font=('Arial', 10),
                                         wrap=tk.WORD, yscrollcommand=text_scroll.set)
            fields[field_name].pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            text_scroll.config(command=fields[field_name].yview)
        
        def save(power_id=None):
            name = fields['name'].get().strip()
            if not name:
                messagebox.showerror("Error", "System name is required!")
                return
            desc = fields['description'].get('1.0', tk.END).strip()
            rules = fields['rules'].get('1.0', tk.END).strip()
            limitations = fields['limitations'].get('1.0', tk.END).strip()
            acquisition = fields['acquisition_method'].get('1.0', tk.END).strip()
            power_levels = fields['power_levels'].get('1.0', tk.END).strip()
            examples = fields['examples'].get('1.0', tk.END).strip()

            if power_id:
                # Update existing
                cursor = self.db.conn.cursor()
                cursor.execute('''
                    UPDATE power_systems SET name=?, description=?, rules=?, limitations=?, acquisition_method=?, power_levels=?, examples=?
                    WHERE id=?
                ''', (name, desc, rules, limitations, acquisition, power_levels, examples, power_id))
                self.db.conn.commit()
                messagebox.showinfo("Success", f"Power system '{name}' updated successfully!")
            else:
                self.db.add_power_system(
                    self.current_story_id,
                    name,
                    desc,
                    rules,
                    limitations=limitations,
                    acquisition_method=acquisition,
                    power_levels=power_levels,
                    examples=examples
                )
                messagebox.showinfo("Success", f"Power system '{name}' added successfully!")

            self.load_power_systems()
            dialog.destroy()
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Save", command=save, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy, width=20).pack(side=tk.LEFT, padx=5)
    
    def add_lore(self):
        """Add or edit lore entry. Use `edit_lore(lore_id)` to edit existing entry."""
        if not self.current_story_id:
            messagebox.showwarning("No Story", "Please select a story first.")
            return
        
        dialog = tk.Toplevel(self.window)
        dialog.title("Add Lore Entry")
        dialog.geometry("650x650")
        dialog.transient(self.window)
        dialog.grab_set()
        
        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Add Lore Entry", font=('Arial', 16, 'bold')).pack(pady=(0, 20))
        
        fields = {}
        
        ttk.Label(frame, text="Category:", font=('Arial', 11, 'bold')).pack(anchor='w', pady=(10, 5))
        fields['category'] = ttk.Combobox(
            frame,
            width=57,
            values=['History', 'Culture', 'Religion', 'Technology', 'Magic', 
                    'Events', 'Legends', 'Prophecies', 'Other'],
            state='readonly'
        )
        fields['category'].pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(frame, text="Title:", font=('Arial', 11, 'bold')).pack(anchor='w', pady=(10, 5))
        fields['title'] = ttk.Entry(frame, width=60, font=('Arial', 11))
        fields['title'].pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(frame, text="Content:", font=('Arial', 11, 'bold')).pack(anchor='w', pady=(10, 5))
        
        content_frame = ttk.Frame(frame)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        content_scroll = ttk.Scrollbar(content_frame)
        content_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        fields['content'] = tk.Text(content_frame, width=60, height=12, font=('Arial', 10),
                                    wrap=tk.WORD, yscrollcommand=content_scroll.set)
        fields['content'].pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        content_scroll.config(command=fields['content'].yview)
        
        ttk.Label(frame, text="Timeline Position (optional):", font=('Arial', 11, 'bold')).pack(anchor='w', pady=(10, 5))
        fields['timeline'] = ttk.Entry(frame, width=60)
        fields['timeline'].pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(frame, text="Importance:", font=('Arial', 11, 'bold')).pack(anchor='w', pady=(10, 5))
        fields['importance'] = ttk.Combobox(frame, width=15, values=['1', '2', '3', '4', '5'], state='readonly')
        fields['importance'].set('3')
        fields['importance'].pack(anchor='w', pady=(0, 10))
        
        def save(lore_id=None):
            category = fields['category'].get().strip()
            title = fields['title'].get().strip()
            content = fields['content'].get('1.0', tk.END).strip()

            if not category or not title or not content:
                messagebox.showerror("Error", "Category, Title, and Content are required!")
                return

            timeline = fields['timeline'].get().strip()
            importance = int(fields['importance'].get())

            if lore_id:
                cursor = self.db.conn.cursor()
                cursor.execute('''
                    UPDATE lore SET category = ?, title = ?, content = ?, timeline_position = ?, importance = ?
                    WHERE id = ?
                ''', (category, title, content, timeline, importance, lore_id))
                self.db.conn.commit()
                messagebox.showinfo("Success", f"Lore entry '{title}' updated successfully!")
            else:
                self.db.add_lore(
                    self.current_story_id,
                    category,
                    title,
                    content,
                    timeline_position=timeline,
                    importance=importance
                )
                messagebox.showinfo("Success", f"Lore entry '{title}' added successfully!")

            self.load_lore()
            dialog.destroy()
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Save", command=save, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy, width=20).pack(side=tk.LEFT, padx=5)
    
    def add_organization(self):
        """Add a new organization"""
        if not self.current_story_id:
            messagebox.showwarning("No Story", "Please select a story first.")
            return
        
        dialog = tk.Toplevel(self.window)
        dialog.title("Add Organization")
        dialog.geometry("650x700")
        dialog.transient(self.window)
        dialog.grab_set()
        
        # Scrollable canvas
        canvas = tk.Canvas(dialog)
        scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        frame = ttk.Frame(canvas, padding=20)
        
        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        ttk.Label(frame, text="Add Organization", font=('Arial', 16, 'bold')).pack(pady=(0, 20))
        
        fields = {}
        
        ttk.Label(frame, text="Organization Name:", font=('Arial', 11, 'bold')).pack(anchor='w', pady=(10, 5))
        fields['name'] = ttk.Entry(frame, width=60, font=('Arial', 11))
        fields['name'].pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(frame, text="Type:", font=('Arial', 11, 'bold')).pack(anchor='w', pady=(10, 5))
        fields['type'] = ttk.Combobox(
            frame,
            width=57,
            values=['Guild', 'Kingdom', 'Empire', 'Church', 'Military', 'Academy',
                    'Merchant Group', 'Secret Society', 'Clan', 'Other'],
            state='readonly'
        )
        fields['type'].pack(fill=tk.X, pady=(0, 10))
        
        text_fields = [
            ('description', 'Description', 5),
            ('goals', 'Goals & Purpose', 4),
            ('structure', 'Structure & Hierarchy', 4),
            ('members', 'Notable Members', 4),
            ('resources', 'Resources & Power', 4),
            ('relationships', 'Relationships with Others', 4)
        ]
        
        for field_name, label, height in text_fields:
            ttk.Label(frame, text=f"{label}:", font=('Arial', 11, 'bold')).pack(anchor='w', pady=(10, 5))
            
            text_frame = ttk.Frame(frame)
            text_frame.pack(fill=tk.X, pady=(0, 10))
            
            text_scroll = ttk.Scrollbar(text_frame)
            text_scroll.pack(side=tk.RIGHT, fill=tk.Y)
            
            fields[field_name] = tk.Text(text_frame, width=60, height=height, font=('Arial', 10),
                                         wrap=tk.WORD, yscrollcommand=text_scroll.set)
            fields[field_name].pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            text_scroll.config(command=fields[field_name].yview)
        
        def save():
            name = fields['name'].get().strip()
            if not name:
                messagebox.showerror("Error", "Organization name is required!")
                return
            
            cursor = self.db.conn.cursor()
            cursor.execute('''
                INSERT INTO organizations (
                    story_id, name, type, description, goals, structure,
                    members, resources, relationships
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                self.current_story_id,
                name,
                fields['type'].get(),
                fields['description'].get('1.0', tk.END).strip(),
                fields['goals'].get('1.0', tk.END).strip(),
                fields['structure'].get('1.0', tk.END).strip(),
                fields['members'].get('1.0', tk.END).strip(),
                fields['resources'].get('1.0', tk.END).strip(),
                fields['relationships'].get('1.0', tk.END).strip()
            ))
            self.db.conn.commit()
            
            self.load_organizations()
            dialog.destroy()
            messagebox.showinfo("Success", f"Organization '{name}' added successfully!")
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Save", command=save, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy, width=20).pack(side=tk.LEFT, padx=5)
    
    def ai_generate_power_system(self):
        """Generate a power system with AI"""
        if not self.current_story_id:
            messagebox.showwarning("No Story", "Please select a story first.")
            return
        
        if not self.ai.test_connection():
            messagebox.showerror("AI Not Connected", "Cannot connect to Ollama.")
            return
        
        concept = self.prompt_for_input(
            "AI Generate Power System",
            "Describe the power system concept:",
            "Example: Magic based on emotions and willpower"
        )
        
        if not concept:
            return
        
        self.update_status("AI generating power system...")
        self.window.update()
        
        try:
            result = self.world_gen.generate_power_system(self.current_story_id, concept)
            
            self.show_ai_result_dialog(
                "AI Generated Power System",
                result['raw_result'],
                "Review and manually add this power system using 'Add Power System'."
            )
            
            self.update_status("Power system generation complete")
            
        except Exception as e:
            messagebox.showerror("Error", f"AI generation failed: {str(e)}")
            self.update_status("Generation failed")
    
    def ai_generate_lore(self):
        """Generate lore with AI"""
        if not self.current_story_id:
            messagebox.showwarning("No Story", "Please select a story first.")
            return
        
        if not self.ai.test_connection():
            messagebox.showerror("AI Not Connected", "Cannot connect to Ollama.")
            return
        
        # Category selection
        dialog = tk.Toplevel(self.window)
        dialog.title("AI Generate Lore")
        dialog.geometry("550x350")
        dialog.transient(self.window)
        dialog.grab_set()
        
        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="AI Generate Lore", font=('Arial', 16, 'bold')).pack(pady=(0, 20))
        
        ttk.Label(frame, text="What lore topic should AI generate?", font=('Arial', 11, 'bold')).pack(pady=(10, 5))
        ttk.Label(
            frame,
            text="Example: 'The Great War 500 years ago'",
            font=('Arial', 9, 'italic'),
            foreground='gray'
        ).pack()
        
        topic_frame = ttk.Frame(frame)
        topic_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        topic_scroll = ttk.Scrollbar(topic_frame)
        topic_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        topic_text = tk.Text(topic_frame, width=50, height=6, font=('Arial', 10),
                            wrap=tk.WORD, yscrollcommand=topic_scroll.set)
        topic_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        topic_scroll.config(command=topic_text.yview)
        
        ttk.Label(frame, text="Category:", font=('Arial', 11, 'bold')).pack(anchor='w', pady=(10, 5))
        category_combo = ttk.Combobox(
            frame,
            width=25,
            values=['History', 'Culture', 'Religion', 'Technology', 'Magic', 
                    'Events', 'Legends', 'Prophecies', 'Other'],
            state='readonly'
        )
        category_combo.set('History')
        category_combo.pack(anchor='w', pady=(0, 10))
        
        def generate():
            topic = topic_text.get('1.0', tk.END).strip()
            if not topic:
                messagebox.showerror("Error", "Please describe the lore topic.")
                return
            
            category = category_combo.get()
            dialog.destroy()
            
            self.update_status("AI generating lore...")
            self.window.update()
            
            try:
                result = self.world_gen.generate_lore(self.current_story_id, topic, category)
                
                self.show_ai_result_dialog(
                    "AI Generated Lore",
                    result['raw_result'],
                    "Review and manually add this lore using 'Add Lore Entry'."
                )
                
                self.update_status("Lore generation complete")
                
            except Exception as e:
                messagebox.showerror("Error", f"AI generation failed: {str(e)}")
                self.update_status("Generation failed")
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Generate", command=generate, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy, width=20).pack(side=tk.LEFT, padx=5)
    
    # ==================== PROGRESSION ====================
    
    def load_progression(self):
    # Load arcs for selector
        arcs = self.db.get_arcs(self.current_story_id)
        arc_names = [f"Arc {arc['arc_number']}: {arc['arc_name']}" for arc in arcs]
        # Populate selector values
        self.progression_widgets['arc_selector']['values'] = arc_names
        if arcs:
            # Select first arc by default and load its progression
            self.progression_widgets['arc_selector'].set(arc_names[0])
            self.current_arc_id = arcs[0]['id']
            self.load_arc_progression()
        else:
            # Clear selector and clear fields when there are no arcs
            try:
                self.progression_widgets['arc_selector'].set("")
            except Exception:
                pass
            self.current_arc_id = None
            # Clear progression fields
            self.progression_widgets['arc_name'].delete(0, tk.END)
            self.progression_widgets['arc_number'].delete(0, tk.END)
            for field in ['current_plot_points', 'completed_plot_points', 'character_development',
                          'foreshadowing', 'unresolved_threads', 'next_major_events', 'pacing_notes']:
                try:
                    self.progression_widgets[field].delete('1.0', tk.END)
                except Exception:
                    pass

    def load_arc_progression(self):
        if not self.current_story_id or not hasattr(self, 'current_arc_id') or not self.current_arc_id:
            return
        progression_data = self.db.get_arc_progression(self.current_story_id, self.current_arc_id)
        if not progression_data:
            # Clear fields
            self.progression_widgets['arc_name'].delete(0, tk.END)
            self.progression_widgets['arc_number'].delete(0, tk.END)
            for field in ['current_plot_points', 'completed_plot_points', 'character_development',
                          'foreshadowing', 'unresolved_threads', 'next_major_events', 'pacing_notes']:
                self.progression_widgets[field].delete('1.0', tk.END)
            return
        # Assume progression_data is a JSON string
        import json
        progression = json.loads(progression_data)
        self.progression_widgets['arc_name'].delete(0, tk.END)
        self.progression_widgets['arc_name'].insert(0, progression.get('arc_name', ""))
        self.progression_widgets['arc_number'].delete(0, tk.END)
        self.progression_widgets['arc_number'].insert(0, str(progression.get('arc_number', "")))
        for field in ['current_plot_points', 'completed_plot_points', 'character_development',
                      'foreshadowing', 'unresolved_threads', 'next_major_events', 'pacing_notes']:
            self.progression_widgets[field].delete('1.0', tk.END)
            self.progression_widgets[field].insert('1.0', progression.get(field, ""))

    def on_arc_selected(self, event=None):
        selected = self.progression_widgets['arc_selector'].get()
        arcs = self.db.get_arcs(self.current_story_id)
        for arc in arcs:
            arc_label = f"Arc {arc['arc_number']}: {arc['arc_name']}"
            if arc_label == selected:
                self.current_arc_id = arc['id']
                break
        self.load_arc_progression()
    def save_progression(self):
        if not self.current_story_id or not hasattr(self, 'current_arc_id') or not self.current_arc_id:
            return
        import json
        data = {
            'arc_name': self.progression_widgets['arc_name'].get(),
            'arc_number': int(self.progression_widgets['arc_number'].get()) if self.progression_widgets['arc_number'].get().strip() else None
        }
        text_fields = ['current_plot_points', 'completed_plot_points', 'character_development',
                      'foreshadowing', 'unresolved_threads', 'next_major_events', 'pacing_notes']
        for field in text_fields:
            data[field] = self.progression_widgets[field].get('1.0', tk.END).strip()
        progression_json = json.dumps(data)
        # Update arc metadata (name/number) in story_arcs table so selector labels stay in sync
        try:
            self.db.update_arc(self.current_arc_id, arc_name=data.get('arc_name'), arc_number=data.get('arc_number'))
        except Exception:
            # If update fails, continue to save progression data but log status
            pass

        # Save progression JSON into arc_progression table
        try:
            self.db.save_arc_progression(self.current_story_id, self.current_arc_id, progression_json)
            self.update_status("Arc progression data saved")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save progression data: {e}")
            return

        # Reload arcs/selector so any updated name/number are reflected
        self.load_progression()
        # Re-select the arc we just saved
        if self.current_arc_id:
            arcs = self.db.get_arcs(self.current_story_id)
            for arc in arcs:
                if arc['id'] == self.current_arc_id:
                    label = f"Arc {arc['arc_number']}: {arc['arc_name']}"
                    try:
                        self.progression_widgets['arc_selector'].set(label)
                    except Exception:
                        pass
                    break
    
    def create_arc_dialog(self):
        """Dialog to create a new arc and add to DB"""
        if not self.current_story_id:
            messagebox.showwarning("No Story", "Please select a story first.")
            return

        dialog = tk.Toplevel(self.window)
        dialog.title("Add Arc")
        dialog.geometry("480x220")
        dialog.transient(self.window)
        dialog.grab_set()

        frm = ttk.Frame(dialog, padding=12)
        frm.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frm, text="Arc Number:", font=('Arial', 11, 'bold')).grid(row=0, column=0, sticky='w', pady=6)
        arc_number_entry = ttk.Entry(frm, width=10)
        arc_number_entry.grid(row=0, column=1, sticky='w', pady=6)

        ttk.Label(frm, text="Arc Name:", font=('Arial', 11, 'bold')).grid(row=1, column=0, sticky='w', pady=6)
        arc_name_entry = ttk.Entry(frm, width=40)
        arc_name_entry.grid(row=1, column=1, sticky='w', pady=6)

        ttk.Label(frm, text="Synopsis (optional):", font=('Arial', 11, 'bold')).grid(row=2, column=0, sticky='nw', pady=6)
        synopsis_text = tk.Text(frm, width=40, height=5)
        synopsis_text.grid(row=2, column=1, pady=6)

        def do_add():
            num = arc_number_entry.get().strip()
            name = arc_name_entry.get().strip()
            syn = synopsis_text.get('1.0', tk.END).strip()
            if not name or not num:
                messagebox.showerror("Error", "Arc number and name are required.")
                return
            try:
                arc_id = self.db.add_arc(self.current_story_id, int(num), name, synopsis=syn)
                self.load_progression()  # refresh selector
                # select the newly added arc
                arcs = self.db.get_arcs(self.current_story_id)
                for arc in arcs:
                    if arc['id'] == arc_id:
                        label = f"Arc {arc['arc_number']}: {arc['arc_name']}"
                        self.progression_widgets['arc_selector'].set(label)
                        self.current_arc_id = arc_id
                        self.load_arc_progression()
                        break
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("DB Error", f"Failed to add arc: {e}")

        btns = ttk.Frame(frm)
        btns.grid(row=3, column=0, columnspan=2, pady=10)
        ttk.Button(btns, text="Add Arc", command=do_add).pack(side=tk.LEFT, padx=5)
        ttk.Button(btns, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)