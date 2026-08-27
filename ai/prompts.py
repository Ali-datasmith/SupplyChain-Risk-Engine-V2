"""Plain string prompt templates."""

NARRATIVE_PROMPT_TEMPLATE = """
You are an elite supply chain risk analyst. Evaluate the following supplier data
and return a JSON array of RiskNarrative objects.

For every object, echo the exact supplier_id from the input row so results can
be matched deterministically.

Strictly adhere to the response_schema. Do not include markdown or conversational text.

Suppliers:
{suppliers}
"""
