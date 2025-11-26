"""
Enhanced Theme Manager for Light/Dark Mode with full UI theming
Provides comprehensive color schemes for the entire application
"""

import json
import os

class ThemeManager:
    """Manages application themes with comprehensive color schemes"""
    
    def __init__(self, config_path="theme_config.json"):
        self.config_path = config_path
        self.current_theme = self._load_saved_theme()
        
        self.themes = {
            'light': {
                # Main backgrounds
                'bg': '#F5F5F5',
                'fg': '#1A1A1A',
                'secondary_bg': '#FFFFFF',
                'tertiary_bg': '#E8E8E8',
                
                # Input fields
                'input_bg': '#FFFFFF',
                'input_fg': '#000000',
                'input_border': '#CCCCCC',
                'input_focus_border': '#0078D7',
                
                # Buttons
                'button_bg': '#FFFFFF',
                'button_fg': '#000000',
                'button_hover_bg': '#E8E8E8',
                'button_active_bg': '#D0D0D0',
                'button_border': '#ADADAD',
                
                # Primary/accent buttons
                'primary_button_bg': '#0078D7',
                'primary_button_fg': '#FFFFFF',
                'primary_button_hover': '#005A9E',
                
                # Text widgets
                'text_bg': '#FFFFFF',
                'text_fg': '#000000',
                'text_selection_bg': '#0078D7',
                'text_selection_fg': '#FFFFFF',
                'text_cursor': '#000000',
                
                # Listbox/Treeview
                'list_bg': '#FFFFFF',
                'list_fg': '#000000',
                'list_select_bg': '#0078D7',
                'list_select_fg': '#FFFFFF',
                'list_hover_bg': '#E5F3FF',
                
                # Frames and containers
                'frame_bg': '#F5F5F5',
                'labelframe_bg': '#FFFFFF',
                'labelframe_fg': '#1A1A1A',
                'labelframe_border': '#CCCCCC',
                
                # Sidebar
                'sidebar_bg': '#E8E8E8',
                'sidebar_fg': '#1A1A1A',
                
                # Status bar
                'statusbar_bg': '#F0F0F0',
                'statusbar_fg': '#333333',
                
                # Notebook tabs
                'tab_bg': '#E8E8E8',
                'tab_fg': '#000000',
                'tab_selected_bg': '#0078D7',
                'tab_selected_fg': '#FFFFFF',
                'tab_hover_bg': '#D0D0D0',
                
                # Scrollbars
                'scrollbar_bg': '#F0F0F0',
                'scrollbar_fg': '#C0C0C0',
                'scrollbar_active': '#A0A0A0',
                
                # Borders
                'border': '#CCCCCC',
                'focus_border': '#0078D7',
                
                # Accent colors
                'accent': '#0078D7',
                'accent_light': '#E5F3FF',
                'success': '#28A745',
                'warning': '#FFC107',
                'error': '#DC3545',
                'info': '#17A2B8',
                
                # Headers
                'header_bg': '#FFFFFF',
                'header_fg': '#1A1A1A',
                
                # Separator
                'separator': '#CCCCCC',
                
                # Disabled state
                'disabled_bg': '#F0F0F0',
                'disabled_fg': '#A0A0A0',
                
                # Hover states
                'hover_bg': '#E8E8E8',
                
                # Placeholder text
                'placeholder_fg': '#888888',
                
                # Menu
                'menu_bg': '#FFFFFF',
                'menu_fg': '#000000',
                'menu_highlight_bg': '#0078D7',
                'menu_highlight_fg': '#FFFFFF',
                
                # Tooltips
                'tooltip_bg': '#FFFFCC',
                'tooltip_fg': '#000000',
                
                # Canvas
                'canvas_bg': '#FFFFFF'
            },
            'dark': {
                # Main backgrounds
                'bg': '#1E1E1E',
                'fg': '#E0E0E0',
                'secondary_bg': '#252525',
                'tertiary_bg': '#2D2D2D',
                
                # Input fields
                'input_bg': '#2D2D2D',
                'input_fg': '#E0E0E0',
                'input_border': '#404040',
                'input_focus_border': '#4A9EFF',
                
                # Buttons
                'button_bg': '#2D2D2D',
                'button_fg': '#E0E0E0',
                'button_hover_bg': '#3D3D3D',
                'button_active_bg': '#4D4D4D',
                'button_border': '#404040',
                
                # Primary/accent buttons
                'primary_button_bg': '#4A9EFF',
                'primary_button_fg': '#FFFFFF',
                'primary_button_hover': '#357ABD',
                
                # Text widgets
                'text_bg': '#252525',
                'text_fg': '#E0E0E0',
                'text_selection_bg': '#4A9EFF',
                'text_selection_fg': '#FFFFFF',
                'text_cursor': '#E0E0E0',
                
                # Listbox/Treeview
                'list_bg': '#252525',
                'list_fg': '#E0E0E0',
                'list_select_bg': '#4A9EFF',
                'list_select_fg': '#FFFFFF',
                'list_hover_bg': '#2D3E50',
                
                # Frames and containers
                'frame_bg': '#1E1E1E',
                'labelframe_bg': '#252525',
                'labelframe_fg': '#E0E0E0',
                'labelframe_border': '#404040',
                
                # Sidebar
                'sidebar_bg': '#181818',
                'sidebar_fg': '#E0E0E0',
                
                # Status bar
                'statusbar_bg': '#252525',
                'statusbar_fg': '#B0B0B0',
                
                # Notebook tabs
                'tab_bg': '#2D2D2D',
                'tab_fg': '#B0B0B0',
                'tab_selected_bg': '#4A9EFF',
                'tab_selected_fg': '#FFFFFF',
                'tab_hover_bg': '#3D3D3D',
                
                # Scrollbars
                'scrollbar_bg': '#2D2D2D',
                'scrollbar_fg': '#404040',
                'scrollbar_active': '#606060',
                
                # Borders
                'border': '#404040',
                'focus_border': '#4A9EFF',
                
                # Accent colors
                'accent': '#4A9EFF',
                'accent_light': '#2D3E50',
                'success': '#5CB85C',
                'warning': '#F0AD4E',
                'error': '#D9534F',
                'info': '#5BC0DE',
                
                # Headers
                'header_bg': '#252525',
                'header_fg': '#FFFFFF',
                
                # Separator
                'separator': '#404040',
                
                # Disabled state
                'disabled_bg': '#2D2D2D',
                'disabled_fg': '#606060',
                
                # Hover states
                'hover_bg': '#2D2D2D',
                
                # Placeholder text
                'placeholder_fg': '#707070',
                
                # Menu
                'menu_bg': '#252525',
                'menu_fg': '#E0E0E0',
                'menu_highlight_bg': '#4A9EFF',
                'menu_highlight_fg': '#FFFFFF',
                
                # Tooltips
                'tooltip_bg': '#3D3D3D',
                'tooltip_fg': '#E0E0E0',
                
                # Canvas
                'canvas_bg': '#1E1E1E'
            }
        }
    
    def _load_saved_theme(self):
        """Load previously saved theme preference"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    data = json.load(f)
                    return data.get('theme', 'light')
        except:
            pass
        return 'light'
    
    def _save_theme(self):
        """Save current theme preference"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump({'theme': self.current_theme}, f)
        except:
            pass
    
    def get_theme(self, theme_name=None):
        """Get theme colors dictionary"""
        if theme_name is None:
            theme_name = self.current_theme
        return self.themes.get(theme_name, self.themes['light'])
    
    def toggle_theme(self):
        """Toggle between light and dark theme"""
        self.current_theme = 'dark' if self.current_theme == 'light' else 'light'
        self._save_theme()
        return self.current_theme
    
    def set_theme(self, theme_name):
        """Set specific theme"""
        if theme_name in self.themes:
            self.current_theme = theme_name
            self._save_theme()
            return True
        return False
    
    def get_color(self, color_key, theme_name=None):
        """Get specific color from theme"""
        theme = self.get_theme(theme_name)
        return theme.get(color_key, '#000000')
    
    def get_available_themes(self):
        """Get list of available theme names"""
        return list(self.themes.keys())
    
    def add_custom_theme(self, name, colors):
        """Add a custom theme"""
        base = self.themes['light'].copy()
        base.update(colors)
        self.themes[name] = base
    
    def export_theme(self, theme_name, filepath):
        """Export theme to JSON file"""
        theme = self.get_theme(theme_name)
        with open(filepath, 'w') as f:
            json.dump(theme, f, indent=2)
    
    def import_theme(self, name, filepath):
        """Import theme from JSON file"""
        with open(filepath, 'r') as f:
            colors = json.load(f)
        self.add_custom_theme(name, colors)