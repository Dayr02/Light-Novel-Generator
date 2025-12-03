"""
Configuration management for Light Novel Generator
"""

import json
import os
from pathlib import Path

class Config:
    """Application configuration manager"""
    
    DEFAULT_CONFIG = {
        # AI Settings
        'ai': {
            'model': 'llama3.1:8b',
            'base_url': 'http://localhost:11434',
            'default_temperature': 0.85,
            'default_max_tokens': 4500,
            'timeout': 300
        },
        
        # Generation Defaults
        'generation': {
            'default_word_count': 5000,
            'min_word_count': 3000,
            'max_word_count': 8000,
            'chapter_temperature': 0.85,
            'world_temperature': 0.7,
            'character_temperature': 0.75
        },
        
        # UI Settings
        'ui': {
            'theme': 'light',
            'font_family': 'Arial',
            'font_size': 11,
            'window_width': 1500,
            'window_height': 900,
            'sidebar_width': 280
        },
        
        # Database Settings
        'database': {
            'path': 'data/lightnovel.db',
            'backup_on_exit': False,
            'auto_save_interval': 300  # seconds
        },
        
        # Export Settings
        'export': {
            'default_format': 'txt',
            'include_metadata': True,
            'chapter_separator': '=' * 80
        },
        
        # Writing Style Presets
        'style_presets': {
            'rezero': {
                'name': 'ReZero Style',
                'description': 'Deep psychological exploration, time loop tension, emotional intensity',
                'temperature': 0.85,
                'style_notes': 'Focus on internal monologue, suffering and growth, detailed emotional reactions'
            },
            'fate': {
                'name': 'Fate Style',
                'description': 'Epic battles, heroic ideals, complex magic systems',
                'temperature': 0.8,
                'style_notes': 'Noble phantasms, servant dynamics, philosophical conflict, grand scale'
            },
            'isekai': {
                'name': 'Classic Isekai',
                'description': 'Power fantasy, game mechanics, adventure focus',
                'temperature': 0.8,
                'style_notes': 'World building, skill acquisition, world exploration, lighter tone'
            },
            'dark_fantasy': {
                'name': 'Dark Fantasy',
                'description': 'Gritty realism, moral ambiguity, high stakes, tactical/intense combat',
                'temperature': 0.8,
                'style_notes': 'Consequences matter, complex villains, mature themes'
            }
        }
    }
    
    def __init__(self, config_path="config.json"):
        self.config_path = config_path
        self.config = self.load_config()
    
    def load_config(self):
        """Load configuration from file or create default"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # Merge with defaults to handle missing keys
                    return self._merge_configs(self.DEFAULT_CONFIG, loaded)
            except Exception as e:
                print(f"Error loading config: {e}. Using defaults.")
                return self.DEFAULT_CONFIG.copy()
        else:
            self.save_config(self.DEFAULT_CONFIG)
            return self.DEFAULT_CONFIG.copy()
    
    def _merge_configs(self, default, loaded):
        """Recursively merge loaded config with defaults"""
        result = default.copy()
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        return result
    
    def save_config(self, config=None):
        """Save configuration to file"""
        if config is None:
            config = self.config
        
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, *keys, default=None):
        """Get a configuration value by key path"""
        value = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value
    
    def set(self, *keys, value):
        """Set a configuration value by key path"""
        config = self.config
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        config[keys[-1]] = value
        self.save_config()
    
    # Convenience properties
    @property
    def ai_model(self):
        return self.get('ai', 'model', default='llama3.1:8b')
    
    @property
    def ai_base_url(self):
        return self.get('ai', 'base_url', default='http://localhost:11434')
    
    @property
    def default_temperature(self):
        return self.get('generation', 'chapter_temperature', default=0.85)
    
    @property
    def default_word_count(self):
        return self.get('generation', 'default_word_count', default=3000)
    
    @property
    def theme(self):
        return self.get('ui', 'theme', default='light')
    
    @theme.setter
    def theme(self, value):
        self.set('ui', 'theme', value=value)
    
    @property
    def database_path(self):
        return self.get('database', 'path', default='data/lightnovel.db')
    
    def get_style_preset(self, preset_name):
        """Get a writing style preset"""
        return self.get('style_presets', preset_name, default=None)
    
    def get_all_style_presets(self):
        """Get all style preset names"""
        return list(self.get('style_presets', default={}).keys())


# Global config instance
_config = None

def get_config():
    """Get the global config instance"""
    global _config
    if _config is None:
        _config = Config()
    return _config