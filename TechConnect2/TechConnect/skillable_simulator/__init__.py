"""
Skillable Gen AI Lab Instructions Generator Simulator

This module demonstrates how the Skillable Gen AI agent consumes TechConnect
context blocks to automatically generate lab instructions, deployment scripts,
and training materials.

Module Structure:
  - generator.py: Core lab instruction generation logic
  - simulator.py: End-to-end simulator and workflow orchestration
  - test_simulator.py: Comprehensive test suite

Key Classes:
  - XMLParser: Parses XML-formatted content from context blocks
  - LabInstructionGenerator: Generates lab guides, scripts, and reports
  - SkillableSimulator: Orchestrates complete lab generation workflow
"""

__version__ = "1.0.0"
__author__ = "Skillable Gen AI Lab Generator"

from .generator import LabInstructionGenerator, XMLParser
from .simulator import SkillableSimulator

__all__ = [
    "LabInstructionGenerator",
    "XMLParser",
    "SkillableSimulator"
]
