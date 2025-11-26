import json


class PromptTemplates:
    """Templates for generating different types of content"""
    
    @staticmethod
    def chapter_generation_prompt(
        story_info: dict,
        characters: list,
        world_info: list,
        power_systems: list,
        lore: list,
        progression: dict,
        chapter_number: int,
        plot_directive: str,
        previous_chapter_summary: str = "",
        target_word_count: int | None = None,
    ) -> str:
        """
        Construct comprehensive chapter generation prompt
        """
        
        # Format character information
        char_section = "=== CHARACTERS ===\n\n"
        
        # Separate by importance
        protagonists = [c for c in characters if c['role'].lower() in ['protagonist', 'main character']]
        major_chars = [c for c in characters if c['importance'] >= 3 and c['role'].lower() not in ['protagonist', 'main character']]
        supporting = [c for c in characters if c['importance'] < 3]
        
        if protagonists:
            char_section += "PROTAGONIST(S):\n"
            for char in protagonists:
                char_section += f"\n• {char['name']} ({char['age']}, {char['gender']})\n"
                if char['appearance']:
                    char_section += f"  Appearance: {char['appearance']}\n"
                if char['personality']:
                    char_section += f"  Personality: {char['personality']}\n"
                if char['abilities']:
                    char_section += f"  Abilities: {char['abilities']}\n"
                if char['background']:
                    char_section += f"  Background: {char['background']}\n"
                if char['motivations']:
                    char_section += f"  Motivations: {char['motivations']}\n"
                if char['voice_style']:
                    char_section += f"  Speech Style: {char['voice_style']}\n"
                if char['character_arc']:
                    char_section += f"  Character Arc: {char['character_arc']}\n"
        
        if major_chars:
            char_section += "\nMAJOR CHARACTERS:\n"
            for char in major_chars:
                char_section += f"\n• {char['name']} - {char['role']}\n"
                if char['personality']:
                    char_section += f"  Personality: {char['personality']}\n"
                if char['relationships']:
                    char_section += f"  Relationships: {char['relationships']}\n"
                if char['abilities']:
                    char_section += f"  Abilities: {char['abilities']}\n"
        
        if supporting:
            char_section += "\nSUPPORTING CHARACTERS:\n"
            for char in supporting:
                char_section += f"• {char['name']} - {char['role']}"
                if char['personality']:
                    char_section += f": {char['personality'][:100]}"
                char_section += "\n"
        
        # Format world information
        world_section = "\n=== WORLD SETTING ===\n\n"
        if world_info:
            for location in world_info:
                world_section += f"• {location['name']} ({location['type']})\n"
                if location['description']:
                    world_section += f"  {location['description']}\n"
                if location['culture']:
                    world_section += f"  Culture: {location['culture']}\n"
        
        # Format power systems
        power_section = "\n=== POWER SYSTEMS ===\n\n"
        if power_systems:
            for system in power_systems:
                power_section += f"• {system['name']}\n"
                if system['description']:
                    power_section += f"  {system['description']}\n"
                if system['rules']:
                    power_section += f"  Rules: {system['rules']}\n"
                if system['limitations']:
                    power_section += f"  Limitations: {system['limitations']}\n"
        
        # Format relevant lore
        lore_section = "\n=== RELEVANT LORE ===\n\n"
        if lore:
            for entry in lore[:5]:  # Top 5 most relevant
                lore_section += f"• {entry['title']} ({entry['category']})\n"
                if entry['content']:
                    lore_section += f"  {entry['content'][:200]}...\n"
        
        # Format story progression
        progression_section = "\n=== STORY PROGRESSION ===\n\n"
        if progression:
            progression_section += "Current Arc Progression:\n"
            # If progression is JSON object from arc_progression table, include it
            # progression may be a dict already, otherwise parse JSON
            if isinstance(progression, str):
                try:
                    progression = json.loads(progression)
                except:
                    pass
            if isinstance(progression, dict):
                for k, v in progression.items():
                    progression_section += f"- {k}: {v}\n\n"
        
        # Previous chapter context
        previous_section = ""
        if previous_chapter_summary:
            previous_section = f"\n=== PREVIOUS CHAPTER SUMMARY ===\n\n{previous_chapter_summary}\n"
        
        # Story style guidelines
        style_section = f"""
=== WRITING STYLE GUIDELINES ===

Genre: {story_info.get('genre', 'Light Novel')}
Tone: {story_info.get('tone', 'Varied based on scene')}
Style: {story_info.get('writing_style', 'ReZero/Fate-inspired')}
Themes: {story_info.get('themes', '')}

Style Requirements:
- Use first-person or close third-person perspective for deep character interiority
- Include internal monologue and character thoughts
- Balance description, action, and dialogue naturally
- Use sensory details to immerse the reader
- Employ strategic pacing - slow for emotional moments, fast for action
- Include scene transitions with "◇◇◇" or similar markers
- Write dialogue that reflects each character's unique voice
- Show character emotions through actions and reactions, not just statements
- Build tension progressively within the chapter
- End with a hook or emotional beat that compels reading the next chapter
"""
        
        # Main generation instruction
        # If caller provided a target word count, use it. Otherwise fall back
        # to the original guidance range.
        word_instruction = (
            f"7. Target length: approximately {target_word_count} words"
            if target_word_count else
            "7. Ranges between 2500-4000 words"
        )

        main_instruction = f"""
=== CHAPTER {chapter_number} GENERATION TASK ===

Title: {story_info.get('title', 'Untitled')}
Chapter: {chapter_number}

PLOT DIRECTIVE FOR THIS CHAPTER:
{plot_directive}

INSTRUCTIONS:
Write a complete Chapter {chapter_number} that:
1. Follows the plot directive naturally
2. Stays true to all established characters, world rules, and lore
3. Maintains consistency with previous events
4. Develops characters and relationships meaningfully
5. Advances the overall story arc
        6. Creates an engaging, immersive reading experience
        {word_instruction}
8. Includes proper scene breaks and pacing
9. Ends with a compelling hook or resolution

Begin writing Chapter {chapter_number} now:
"""
        
        # Combine all sections
        full_prompt = (
            char_section +
            world_section +
            power_section +
            lore_section +
            progression_section +
            previous_section +
            style_section +
            main_instruction
        )
        
        return full_prompt
    
    @staticmethod
    def world_generation_prompt(
        story_info: dict,
        existing_world: list,
        generation_focus: str,
        specific_request: str
    ) -> str:
        """
        Construct world generation/expansion prompt
        """
        
        existing_section = ""
        if existing_world:
            existing_section = "\n=== EXISTING WORLD ELEMENTS ===\n\n"
            for location in existing_world:
                existing_section += f"• {location['name']} ({location['type']}): {location['description'][:150]}\n"
        
        prompt = f"""
=== WORLD BUILDING TASK ===

Story: {story_info.get('title', 'Untitled')}
Genre: {story_info.get('genre', 'Light Novel')}
Themes: {story_info.get('themes', '')}
{existing_section}

GENERATION FOCUS: {generation_focus}

SPECIFIC REQUEST:
{specific_request}

INSTRUCTIONS:
Generate detailed world-building information that:
1. Fits seamlessly with the existing world elements
2. Feels authentic and internally consistent
3. Has depth and interesting details
4. Considers practical implications (economy, society, culture)
5. Avoids generic fantasy clichés
6. Provides hooks for story potential
7. Is organized clearly with headers

Format your response with clear sections for each element you create.
Include practical details that make the world feel real and lived-in.

Generate the requested world details now:
"""
        
        return prompt
    
    @staticmethod
    def character_expansion_prompt(
        character_name: str,
        basic_info: dict,
        story_context: dict,
        expansion_focus: str
    ) -> str:
        """
        Construct character detail expansion prompt
        """
        
        prompt = f"""
=== CHARACTER DEVELOPMENT TASK ===

Character: {character_name}
Role: {basic_info.get('role', 'Unknown')}
Story: {story_context.get('title', 'Untitled')}

EXISTING INFORMATION:
"""
        
        if basic_info.get('age'):
            prompt += f"Age: {basic_info['age']}\n"
        if basic_info.get('gender'):
            prompt += f"Gender: {basic_info['gender']}\n"
        if basic_info.get('personality'):
            prompt += f"Personality: {basic_info['personality']}\n"
        if basic_info.get('background'):
            prompt += f"Background: {basic_info['background']}\n"
        if basic_info.get('abilities'):
            prompt += f"Abilities: {basic_info['abilities']}\n"
        
        prompt += f"""

EXPANSION FOCUS: {expansion_focus}

INSTRUCTIONS:
Expand this character's details with depth and nuance:
1. Create realistic motivations and conflicts
2. Develop their voice and mannerisms
3. Establish meaningful relationships
4. Plan character growth potential
5. Consider their role in the story
6. Add unique quirks and traits
7. Ensure they feel like a real person

Provide detailed character information now:
"""
        
        return prompt
    
    @staticmethod
    def synopsis_to_structure_prompt(synopsis: str, genre: str) -> str:
        """
        Convert story synopsis to structured world/character suggestions
        """
        
        prompt = f"""
=== STORY STRUCTURE ANALYSIS ===

Genre: {genre}

Synopsis:
{synopsis}

TASK:
Analyze this synopsis and suggest:

1. KEY CHARACTERS needed:
   - Protagonist(s) with brief descriptions
   - Major supporting characters
   - Potential antagonists

2. WORLD LOCATIONS required:
   - Primary setting(s)
   - Important secondary locations
   - Brief description of each

3. POWER SYSTEMS (if applicable):
   - Magic/ability systems needed
   - Rules and limitations
   - How they serve the story

4. KEY LORE ELEMENTS:
   - Historical events that matter
   - Cultural/social structures
   - Important background information

5. STORY ARCS suggested:
   - Major plot arcs (3-5)
   - Character development arcs
   - Potential chapter breakdown

Format your response clearly with headers for each section.
Focus on what's essential for this story to work well.

Provide your analysis:
"""
        
        return prompt