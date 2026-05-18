"""Datacentric-ядро контекста проекта: доменные модели, AI-bundle и генерация XML по схемам."""

from app.project_context.ai_bundle import (
    InvestmentProjectNarratives,
    InvestmentProjectPackage,
    build_investment_project_ai_context,
)
from app.project_context.domain_models import DesignAssignmentDraft
from app.project_context.package_template import default_investment_project_package
from app.project_context.xml_design_assignment import build_minstroy_design_assignment_xml

__all__ = [
    "DesignAssignmentDraft",
    "InvestmentProjectNarratives",
    "InvestmentProjectPackage",
    "build_investment_project_ai_context",
    "build_minstroy_design_assignment_xml",
    "default_investment_project_package",
]
