from dataclasses import dataclass
from typing import Callable, Dict, Any

@dataclass
class Tool:
    """A tool is a function, it's parameters, optionally properties, validator to validate input params, and explainer to describe output and potential errors"""
    name: str
    description: str
    properties: Dict[str, Any]
    function: Callable[..., Any]
    parameters: Dict[str, Any]
    validator: Callable[..., Any]
    explainer: Callable[..., Any]