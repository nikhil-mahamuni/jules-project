class PranaliError(Exception):
    """Base class for all exceptions in Pranali."""
    pass

class ConfigError(PranaliError):
    """Raised when there is an issue with the configuration."""
    pass

class ProviderCapabilityError(PranaliError):
    """Raised when an LLM provider does not support a required capability."""
    pass

class LLMRouterError(PranaliError):
    """Raised when the LLM router cannot find a suitable provider."""
    pass
