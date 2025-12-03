from ai.ollama_client import OllamaClient
from ai.prompt_templates import PromptTemplates
from database.db_manager import DatabaseManager
import json
import re

class WorldGenerator:
    """Handles AI-powered world generation and expansion"""
    
    def __init__(self, db_manager: DatabaseManager, ai_client: OllamaClient):
        self.db = db_manager
        self.ai = ai_client
        self.templates = PromptTemplates()
    
    def generate_from_synopsis(self, story_id: int, synopsis: str, genre: str) -> dict:
        """
        Generate world structure suggestions from story synopsis
        Returns structured data that can be added to database
        """
        
        prompt = self.templates.synopsis_to_structure_prompt(synopsis, genre)
        
        print("Analyzing synopsis and generating world structure...")
        result = self.ai.generate_world_details(prompt, temperature=0.7, max_tokens=3000)
        
        # Save generation history
        self.db.save_world_generation(
            story_id=story_id,
            prompt=prompt,
            result=result,
            elements_generated={'type': 'synopsis_analysis'}
        )
        
        return {
            'raw_result': result,
            'suggestions': self._parse_structure_suggestions(result)
        }
    
    def expand_location(self, story_id: int, location_name: str, 
                       location_type: str, basic_description: str,
                       expansion_aspects: list = None) -> dict:
        """
        Generate detailed information for a world location
        
        expansion_aspects: list of aspects to focus on, e.g.,
            ['geography', 'culture', 'history', 'economy', 'notable_locations']
        """
        
        if expansion_aspects is None:
            expansion_aspects = ['geography', 'culture', 'history', 'politics', 'economy']
        
        story = self.db.get_story(story_id)
        existing_world = self.db.get_world_locations(story_id)
        
        specific_request = f"""
Create comprehensive details for: {location_name} ({location_type})
Basic Description: {basic_description}

Focus on these aspects: {', '.join(expansion_aspects)}

Provide rich, specific details that make this location feel real and unique.
Consider how it fits into the broader world and story.
"""
        
        prompt = self.templates.world_generation_prompt(
            story_info=story,
            existing_world=existing_world,
            generation_focus="Location Details",
            specific_request=specific_request
        )
        
        print(f"Generating detailed information for {location_name}...")
        result = self.ai.generate_world_details(prompt, temperature=0.7, max_tokens=2500)
        
        # Save generation history
        self.db.save_world_generation(
            story_id=story_id,
            prompt=prompt,
            result=result,
            elements_generated={'type': 'location_expansion', 'location': location_name}
        )
        
        # Parse result into structured data
        parsed_data = self._parse_location_details(result)
        
        return {
            'raw_result': result,
            'parsed_data': parsed_data
        }
    
    def generate_power_system(self, story_id: int, system_concept: str) -> dict:
        """
        Generate a complete magic/power system
        """
        
        story = self.db.get_story(story_id)
        existing_world = self.db.get_world_locations(story_id)
        existing_systems = self.db.get_power_systems(story_id)
        
        existing_systems_text = ""
        if existing_systems:
            existing_systems_text = "Existing Power Systems:\n"
            for sys in existing_systems:
                existing_systems_text += f"• {sys['name']}: {sys['description'][:100]}\n"
        
        specific_request = f"""
Create a detailed power/magic system based on: {system_concept}

{existing_systems_text}

Include:
1. System Name and Core Concept
2. How it works (mechanics)
3. Rules and limitations (very important!)
4. How people acquire/learn this power
5. Power levels or progression
6. Examples of abilities/techniques
7. Weaknesses and costs
8. How it affects society/culture

Make it unique, balanced, and story-appropriate.
Ensure it has clear limitations to prevent it from solving all problems easily.
"""
        
        prompt = self.templates.world_generation_prompt(
            story_info=story,
            existing_world=existing_world,
            generation_focus="Power System",
            specific_request=specific_request
        )
        
        print(f"Generating power system: {system_concept}...")
        result = self.ai.generate_world_details(prompt, temperature=0.75, max_tokens=2500)
        
        # Save generation history
        self.db.save_world_generation(
            story_id=story_id,
            prompt=prompt,
            result=result,
            elements_generated={'type': 'power_system', 'concept': system_concept}
        )
        
        parsed_data = self._parse_power_system(result)
        
        return {
            'raw_result': result,
            'parsed_data': parsed_data
        }
    
    def generate_lore(self, story_id: int, lore_topic: str, 
                     category: str = "History") -> dict:
        """
        Generate historical/cultural lore
        """
        
        story = self.db.get_story(story_id)
        existing_world = self.db.get_world_locations(story_id)
        existing_lore = self.db.get_lore(story_id)
        
        existing_lore_text = ""
        if existing_lore:
            existing_lore_text = "Existing Lore:\n"
            for lore in existing_lore[:5]:
                existing_lore_text += f"• {lore['title']}: {lore['content'][:100]}\n"
        
        specific_request = f"""
Create detailed lore about: {lore_topic}
Category: {category}

{existing_lore_text}

Provide:
1. The core information/event
2. Historical context and timeline
3. Key figures involved
4. Impact on the world/society
5. Modern-day relevance
6. Connections to other lore elements
7. Story hooks this creates

Make it compelling and useful for storytelling.
"""
        
        prompt = self.templates.world_generation_prompt(
            story_info=story,
            existing_world=existing_world,
            generation_focus="Lore",
            specific_request=specific_request
        )
        
        print(f"Generating lore: {lore_topic}...")
        result = self.ai.generate_world_details(prompt, temperature=0.7, max_tokens=2000)
        
        # Save generation history
        self.db.save_world_generation(
            story_id=story_id,
            prompt=prompt,
            result=result,
            elements_generated={'type': 'lore', 'topic': lore_topic}
        )
        
        return {
            'raw_result': result,
            'category': category,
            'topic': lore_topic
        }
    
    def expand_character_details(self, story_id: int, character_id: int,
                                 expansion_focus: str = "complete profile") -> dict:
        """
        Use AI to expand character details
        """
        
        character = self.db.get_character(character_id)
        story = self.db.get_story(story_id)
        
        prompt = self.templates.character_expansion_prompt(
            character_name=character['name'],
            basic_info=character,
            story_context=story,
            expansion_focus=expansion_focus
        )
        
        print(f"Expanding character details for {character['name']}...")
        result = self.ai.expand_character(prompt, temperature=0.75)
        
        return {
            'raw_result': result,
            'character_name': character['name'],
            'parsed_suggestions': self._parse_character_expansion(result)
        }
    
    def expand_creature_details(self, story_id: int, creature_id: int,
                               expansion_focus: str = "complete bestiary entry") -> dict:
        """
        Use AI to expand creature/bestiary details
        """
        
        creature = self.db.get_creature(creature_id)
        story = self.db.get_story(story_id)
        
        prompt = self.templates.character_expansion_prompt(
            character_name=creature['name'],
            basic_info=creature,
            story_context=story,
            expansion_focus=expansion_focus
        )
        
        print(f"Expanding creature details for {creature['name']}...")
        result = self.ai.expand_character(prompt, temperature=0.75)
        
        return {
            'raw_result': result,
            'creature_name': creature['name'],
            'parsed_suggestions': self._parse_character_expansion(result)
        }
    
    # Helper parsing methods
    
    def _parse_structure_suggestions(self, text: str) -> dict:
        """Parse AI suggestions into structured format"""
        # This is a simple parser - can be enhanced
        return {
            'characters': self._extract_section(text, 'CHARACTERS'),
            'locations': self._extract_section(text, 'LOCATIONS'),
            'power_systems': self._extract_section(text, 'POWER'),
            'lore': self._extract_section(text, 'LORE'),
            'arcs': self._extract_section(text, 'ARCS')
        }
    
    def _parse_location_details(self, text: str) -> dict:
        """Parse location details into structured format"""
        return {
            'geography': self._extract_section(text, 'GEOGRAPHY'),
            'culture': self._extract_section(text, 'CULTURE'),
            'history': self._extract_section(text, 'HISTORY'),
            'economy': self._extract_section(text, 'ECONOMY'),
            'politics': self._extract_section(text, 'POLITICS'),
            'notable_locations': self._extract_section(text, 'NOTABLE')
        }
    
    def _parse_power_system(self, text: str) -> dict:
        """Parse power system details"""
        return {
            'name': self._extract_field(text, 'name', 'System Name'),
            'description': self._extract_section(text, 'CONCEPT', 'DESCRIPTION'),
            'rules': self._extract_section(text, 'RULES', 'MECHANICS'),
            'limitations': self._extract_section(text, 'LIMITATIONS', 'WEAKNESSES'),
            'acquisition': self._extract_section(text, 'ACQUISITION', 'LEARN'),
            'examples': self._extract_section(text, 'EXAMPLES', 'ABILITIES')
        }
    
    def _parse_character_expansion(self, text: str) -> dict:
        """Parse character expansion suggestions"""
        return {
            'personality': self._extract_section(text, 'PERSONALITY'),
            'background': self._extract_section(text, 'BACKGROUND'),
            'motivations': self._extract_section(text, 'MOTIVATIONS'),
            'relationships': self._extract_section(text, 'RELATIONSHIPS'),
            'voice': self._extract_section(text, 'VOICE', 'SPEECH'),
            'development': self._extract_section(text, 'DEVELOPMENT', 'GROWTH')
        }
    
    def _extract_section(self, text: str, *keywords) -> str:
        """Extract text section based on headers"""
        for keyword in keywords:
            pattern = rf'{keyword}[:\s]+(.*?)(?=\n\n[A-Z]|$)'
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()
        return ""
    
    def _extract_field(self, text: str, *keywords) -> str:
        """Extract specific field value"""
        for keyword in keywords:
            pattern = rf'{keyword}[:\s]+([^\n]+)'
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return ""