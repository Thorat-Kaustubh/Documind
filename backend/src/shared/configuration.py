from dataclasses import dataclass, field

@dataclass
class AIConfig:
    # Tier 1: Core Reasoning (Groq)
    core_model: str = field(
        default="llama-3.3-70b-versatile",
        metadata={"description": "The 'Architect': Ultra-fast synthesis and complex reasoning (Primary)."}
    )
    
    # Tier 2: Fast Processing (Groq)
    fast_model: str = field(
        default="llama-3.1-8b-instant",
        metadata={"description": "The 'Shredder': Sub-300ms summarization and fallback layer."}
    )
    
    # Tier 3-5: Flash Intelligence (Gemini Stable)
    grounding_model: str = field(
        default="gemini-2.5-flash",
        metadata={"description": "The 'Pulse Tracker': Fact-checking and grounding (STABLE)."}
    )
    
    research_model: str = field(
        default="gemini-2.5-flash", 
        metadata={"description": "The 'Investigator': Deep intelligence layer (STABLE)."}
    )

    chat_model: str = field(
        default="gemini-2.5-flash",
        metadata={"description": "The 'Master Bot': High-context memory-rich conversations (STABLE)."}
    )

config = AIConfig()
