"""
Element extraction strategies for AI-powered selector healing.
"""

from .base_strategy import ExtractionStrategy
from .form_context_strategy import FormContextStrategy
from .same_type_strategy import SameTypeStrategy
from .strategy_selector import StrategySelector
from .visual_strategy import VisualStrategy

__all__ = [
    "ExtractionStrategy",
    "SameTypeStrategy",
    "FormContextStrategy",
    "VisualStrategy",
    "StrategySelector",
]
