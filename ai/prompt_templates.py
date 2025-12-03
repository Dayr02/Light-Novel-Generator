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
        Construct optimized chapter generation prompt with token efficiency
        """

        # ===== SMART CHARACTER FILTERING =====
        # Only include full details for highly important characters
        protagonists = [c for c in characters if c['role'].lower() in ['protagonist', 'main character', 'deuteragonist']]
        major_chars = [c for c in characters if c['importance'] >= 4 and c not in protagonists]
        supporting = [c for c in characters if 2 <= c['importance'] < 4]
        minor = [c for c in characters if c['importance'] < 2]

        char_section = "=== KEY CHARACTERS ===\n\n"

        # Protagonists - FULL details
        if protagonists:
            char_section += "PROTAGONIST(S):\n"
            for char in protagonists[:2]:  # Max 2 protagonists with full details
                char_section += f"\n• {char['name']} ({char.get('age', '?')}, {char.get('gender', '?')})\n"
                if char.get('appearance'): char_section += f"  Appearance: {char['appearance'][:200]}\n"
                if char.get('personality'): char_section += f"  Personality: {char['personality'][:250]}\n"
                if char.get('abilities'): char_section += f"  Abilities: {char['abilities'][:200]}\n"
                if char.get('motivations'): char_section += f"  Motivations: {char['motivations'][:200]}\n"
                if char.get('voice_style'): char_section += f"  Voice: {char['voice_style'][:150]}\n"
                if char.get('character_arc'): char_section += f"  Arc: {char['character_arc'][:200]}\n"

        # Major characters - CONDENSED details
        if major_chars:
            char_section += "\nMAJOR CHARACTERS:\n"
            for char in major_chars[:4]:  # Max 4 major chars
                char_section += f"• {char['name']} ({char['role']})"
                if char.get('personality'): char_section += f" - {char['personality'][:120]}"
                if char.get('abilities'): char_section += f" | Powers: {char['abilities'][:100]}"
                char_section += "\n"

        # Supporting - NAME AND ROLE ONLY
        if supporting:
            char_section += "\nSUPPORTING: "
            char_section += ", ".join([f"{c['name']} ({c['role']})" for c in supporting[:6]])
            char_section += "\n"

        # Skip minor characters entirely to save tokens

        # ===== WORLD INFO - CONDENSED =====
        world_section = "\n=== SETTING ===\n"
        if world_info:
            for loc in world_info[:5]:  # Max 5 locations
                world_section += f"• {loc['name']} ({loc['type']})"
                if loc.get('description'): world_section += f": {loc['description'][:150]}"
                world_section += "\n"

        # ===== POWER SYSTEMS - ESSENTIAL ONLY =====
        power_section = "\n=== POWERS ===\n"
        if power_systems:
            for sys in power_systems[:3]:  # Max 3 systems
                power_section += f"• {sys['name']}: {sys.get('description', '')[:120]}\n"
                if sys.get('rules'): power_section += f"  Rules: {sys['rules'][:150]}\n"
                if sys.get('limitations'): power_section += f"  Limits: {sys['limitations'][:100]}\n"

        # ===== LORE - TOP 3 ONLY =====
        lore_section = "\n=== KEY LORE ===\n"
        if lore:
            for entry in lore[:3]:
                lore_section += f"• {entry['title']}: {entry.get('content', '')[:180]}\n"

        # ===== PROGRESSION - CONCISE =====
        progression_section = "\n=== STORY PROGRESS ===\n"
        if progression:
            if isinstance(progression, str):
                try:
                    progression = json.loads(progression)
                except:
                    pass
                
            if isinstance(progression, dict):
                # Only include most relevant fields
                if progression.get('current_plot_points'):
                    progression_section += f"Current: {progression['current_plot_points'][:250]}\n"
                if progression.get('foreshadowing'):
                    progression_section += f"Foreshadowing: {progression['foreshadowing'][:200]}\n"
                if progression.get('unresolved_threads'):
                    progression_section += f"Unresolved: {progression['unresolved_threads'][:200]}\n"

        # ===== PREVIOUS CHAPTER - BRIEF =====
        previous_section = ""
        if previous_chapter_summary:
            previous_section = f"\n=== PREVIOUS CHAPTER ===\n{previous_chapter_summary[:500]}\n"

        # ===== WRITING GUIDELINES - STREAMLINED =====
        style_section = f"""
    === STYLE ===
    Genre: {story_info.get('genre', 'Light Novel')} | Tone: {story_info.get('tone', 'Varied')}
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

        # ===== GENERATION INSTRUCTION - CLEAR AND DIRECT =====
        word_target = target_word_count if target_word_count else 3500

        main_instruction = f"""
    === WRITE CHAPTER {chapter_number} ===

    Story: {story_info.get('title', 'Untitled')}

    PLOT DIRECTIVE:
    {plot_directive}

    INSTRUCTIONS:
    1. Write a COMPLETE {word_target}-word chapter
    2. Follow the plot directive naturally
    3. Stay true to character voices and world rules
    4. Include internal thoughts and sensory details
    5. Create emotional engagement
    6. Build to a compelling chapter ending
    7. Use scene breaks (◇◇◇) appropriately
    8. DO NOT stop early - write the FULL target length

    Begin Chapter {chapter_number}:
    """

        # ===== COMBINE SECTIONS =====
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
    @staticmethod
    def world_generation_prompt(
        story_info: dict,
        existing_world: list,
        generation_focus: str = "World Building",
        specific_request: str = "Generate comprehensive world-building details"
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
    @staticmethod
    def character_expansion_prompt(
        character_name: str,
        basic_info: dict,
        story_context: dict,
        expansion_focus: str = "complete profile"
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