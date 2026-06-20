import keyword
import re
from collections import defaultdict
from datetime import datetime, timezone

UTC = timezone.utc


def utcnow() -> datetime:
    return datetime.now(tz=UTC)


class VariableNameManager:
    """Manages Python variable lifecycle using an optimized dual-dictionary architecture.

    Provides O(1) execution speeds, multi-mode underscore contraction,
    and full bidirectional tracing via an inverse history map.
    """

    _STRICT_INVALID = re.compile(r'\W', flags=re.ASCII)
    _CONTRACT_INVALID = re.compile(r'\W+', flags=re.ASCII)

    def __init__(self, contract_underscores: bool = True) -> None:
        """Initializes the manager.

        Args:
            contract_underscores: If True (default), compresses sequential invalid characters into a single underscore.
        """
        self.contract_underscores = contract_underscores

        # Chronological forward tracking: { base_name : [variants] }
        self._variables_history: dict[str, list[str]] = defaultdict(list)

        # Bulletproof collision safety & tracing: { generated_name : raw_input }
        self._inverse_history: dict[str, str] = {}

    def make_valid(self, s: str) -> str:
        """Converts an input string into a unique variable name with O(1) efficiency."""
        base = self._get_base_identifier(s)
        existing_variants = self._variables_history[base]

        # Shortcut: Use the chronological list length as the starting suffix index
        suffix_index = len(existing_variants)
        candidate = base if suffix_index == 0 else f"{base}_{suffix_index}"

        # Inverse history lookup guarantees absolute protection against cross-key collisions
        while candidate in self._inverse_history:
            suffix_index += 1
            candidate = f"{base}_{suffix_index}"

        # Commit to both tracking histories
        existing_variants.append(candidate)
        self._inverse_history[candidate] = s

        return candidate

    def _get_base_identifier(self, s: str) -> str:
        """Applies core Python syntax restrictions and underscore normalization rules."""
        if not s or s.isspace():
            return '_'

        regex_pattern = self._CONTRACT_INVALID if self.contract_underscores else self._STRICT_INVALID
        s = regex_pattern.sub('_', s)

        if s.isdigit():
            s = '_' + s

        if keyword.iskeyword(s) or s in ('None', 'True', 'False'):
            s += '_'

        return s

    @property
    def forward_history(self) -> dict[str, list[str]]:
        """Returns a copy of the chronological variant tracking mapping."""
        return {k: v.copy() for k, v in self._variables_history.items()}

    @property
    def inverse_history(self) -> dict[str, str]:
        """Returns a copy of the generated_name -> raw_input tracing dictionary."""
        return self._inverse_history.copy()

    def reset(self) -> None:
        """Clears all tracking histories for a brand new lifecycle."""
        self._variables_history.clear()
        self._inverse_history.clear()
