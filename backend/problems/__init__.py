from .calculus import DerivativePowerRule, DerivativeProductRule

_ALL_TYPES = [DerivativePowerRule(), DerivativeProductRule()]

REGISTRY = {pt.id: pt for pt in _ALL_TYPES}
