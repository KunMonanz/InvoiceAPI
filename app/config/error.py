class ConfigError(Exception):
    """Base class for configuration errors."""

    pass


class MissingEnvVarError(ConfigError):
    """Raised when a required environment variable is missing."""

    def __init__(self, var_name: str):
        self.var_name = var_name
        super().__init__(f"Missing required environment variable: {var_name}")
