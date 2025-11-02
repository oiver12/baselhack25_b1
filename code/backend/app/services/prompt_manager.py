"""
Prompt management system for loading and formatting prompts from JSON
"""
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class PromptManager:
    """Manages prompts loaded from JSON with safe formatting and defaults"""
    
    def __init__(self, prompts_file: Optional[Path] = None):
        """
        Initialize prompt manager
        
        Args:
            prompts_file: Path to prompts.json file. If None, uses default location.
        """
        if prompts_file is None:
            # Default to prompts.json in backend root
            prompts_file = Path(__file__).parent.parent.parent / "prompts.json"
        
        self.prompts_file = Path(prompts_file)
        self._prompts: Dict[str, Any] = {}
        self._defaults = self._get_default_prompts()
        self._load_prompts()
    
    def _get_default_prompts(self) -> Dict[str, Any]:
        """Fallback defaults if JSON file is missing or corrupted"""
        return {
            "two_word_label": {
                "default": {
                    "system": "Summarize in exactly 2 words, no punctuation.",
                    "user_template": "{text}"
                },
                "with_existing": {
                    "system": "Summarize in exactly 2 words, no punctuation. Make sure your label is distinct from existing labels - use different words, not numbered variants.",
                    "user_template": "Generate a 2-word label. Existing labels: {existing_labels_str}. Make sure your label is distinct - use different words entirely, NOT numbered variants.\n\nMessages to summarize:\n{text}"
                },
                "retry": {
                    "system": "Generate a 2-word label that is COMPLETELY DIFFERENT from existing labels. Use different words, NOT numbered variants or slight variations.",
                    "user_template": "Generate a 2-word label. Your previous attempt was too similar to existing labels.\n\nEXISTING LABELS: {existing_labels_str}\n\nCRITICAL: Your label must use DIFFERENT WORDS entirely, not numbered variants. Make it semantically distinct.\n\nMessages to summarize:\n{text}"
                },
                "hard_retry": {
                    "system": "CRITICAL: You MUST generate a completely different 2-word label. Use DIFFERENT WORDS entirely, NOT numbered variants (e.g., not 'AI' and 'AI 2'). The label must be semantically distinct with different concepts.",
                    "user_template": "URGENT: The previous attempt generated a label too similar to existing ones. Generate a COMPLETELY DIFFERENT 2-word label.\n\nEXISTING LABELS TO AVOID: {existing_labels_str}\n\nYour label must use different words and concepts entirely. Examples of BAD pairs: ('Room selection', 'Room selection 2') or ('AI', 'AI system'). Examples of GOOD pairs: ('Room selection', 'Workspace setup') or ('AI', 'Machine learning').\n\nMessages to summarize:\n{text}"
                }
            },
            "classify_message": {
                "system": "Classify as 'positive', 'neutral', or 'negative' only."
            },
            "best_message": {
                "system": "You evaluate helpfulness.",
                "user_template": "Select the best, clearest, most helpful message. Return only that text:\n{messages_list}"
            },
            "noble_message": {
                "system": "You evaluate messages for their nobility, clarity, and representativeness. A noble message is well-articulated, constructive, thoughtful, and best represents the core perspective of the cluster.",
                "user_template": "From the following messages in this cluster (labeled '{cluster_label}'), select the single most noble, clear, and representative message. Return only that exact message text, nothing else:\n\n{messages_list}"
            },
            "expert_expertise": {
                "system": "You analyze a person's messages to identify their area of expertise. Based on the messages they wrote, determine what domain, topic, or area they are expert in.",
                "user_template": "Based on the following messages written by this person in the cluster '{cluster_label}', identify their area of expertise. Generate exactly 3 concise bullet points describing what domain or topic they are expert in. Each bullet point should be a single line starting with '- '.\n\nMessages:\n{messages_list}\n\nRespond with exactly 3 bullet points, one per line, nothing else:"
            },
            "bullet_summary": {
                "system": "You are a skilled summarizer. Summarize in exactly 3 bullet points, one per line, with no introduction or extra commentary. The bullet points should be how we can solve the problem",
                "user_template": "Summarize the following messages as 3 concise bullet points. Also add a approval rating for each bullet point from 0 to 1. Each bullet point should be clear and distinct. Also respond with 2 pros and 2 cons for each bullet point. Respond in this exact JSON format (no extra commentary): {{\n  \"summary\": \"Summary of all the messages (approx 40 words)\",\n  \"description\": \"Description of the problem (approx 100 words)\",\n  \"points\": [\n    {{\n      \"title\": \"First bullet point\",\n      \"pros\": [\"Pro 1\", \"Pro 2\"],\n      \"cons\": [\"Con 1\", \"Con 2\"],\n      \"approval_rating\": 0.5\n    }},\n    {{\n      \"title\": \"Second bullet point\",\n      \"pros\": [\"Pro 1\", \"Pro 2\"],\n      \"cons\": [\"Con 1\", \"Con 2\"],\n      \"approval_rating\": 0.5\n    }},\n    {{\n      \"title\": \"Third bullet point\",\n      \"pros\": [\"Pro 1\", \"Pro 2\"],\n      \"cons\": [\"Con 1\", \"Con 2\"],\n      \"approval_rating\": 0.5\n    }}\n  ]\n}}\nThe question to this conversation is: {question}\n{messages_list}"
            }
        }
    
    def _load_prompts(self) -> None:
        """Load prompts from JSON file with fallback to defaults"""
        try:
            if self.prompts_file.exists():
                with open(self.prompts_file, 'r', encoding='utf-8') as f:
                    self._prompts = json.load(f)
                logger.info(f"Loaded prompts from {self.prompts_file}")
            else:
                logger.warning(
                    f"Prompts file not found at {self.prompts_file}, using defaults. "
                    f"To customize prompts, create prompts.json in the backend root."
                )
                self._prompts = self._defaults.copy()
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Failed to load prompts from {self.prompts_file}: {e}. Using defaults.")
            self._prompts = self._defaults.copy()
    
    def get(self, *keys: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get prompt value by nested keys
        
        Args:
            *keys: Nested keys to traverse (e.g., 'two_word_label', 'default', 'system')
            default: Default value if key path doesn't exist
            
        Returns:
            Prompt string or default/None
        """
        current = self._prompts
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                # Try defaults as fallback
                current = self._defaults
                for k in keys:
                    if isinstance(current, dict) and k in current:
                        current = current[k]
                    else:
                        logger.warning(f"Prompt key path not found: {' -> '.join(keys)}")
                        return default
                break
        
        return current if isinstance(current, str) else default
    
    def format_template(self, *keys: str, **kwargs: Any) -> str:
        """
        Get and format template string with safe error handling
        
        Args:
            *keys: Nested keys to prompt template
            **kwargs: Format arguments for template
            
        Returns:
            Formatted string, or unformatted template if formatting fails
        """
        template = self.get(*keys)
        if template is None:
            logger.error(f"Template not found: {' -> '.join(keys)}")
            return ""
        
        try:
            return template.format(**kwargs)
        except (KeyError, ValueError) as e:
            logger.warning(
                f"Template formatting failed for {' -> '.join(keys)}: {e}. "
                f"Returning unformatted template."
            )
            return template
    
    def reload(self) -> None:
        """Reload prompts from file (useful for hot-reloading in development)"""
        self._load_prompts()


# Global instance - will be initialized with path from config
_prompt_manager: Optional[PromptManager] = None


def get_prompt_manager() -> PromptManager:
    """Get global prompt manager instance"""
    global _prompt_manager
    if _prompt_manager is None:
        from app.config import settings
        prompts_path = getattr(settings, 'PROMPTS_FILE_PATH', None)
        prompt_file = Path(prompts_path) if prompts_path else None
        _prompt_manager = PromptManager(prompt_file)
    return _prompt_manager

