"""Custom exceptions for AquilaTrace platform."""


class AquilaTraceException(Exception):
    """Base exception for AquilaTrace."""
    pass


class ConfigurationError(AquilaTraceException):
    """Raised when configuration is invalid."""
    pass


class DataError(AquilaTraceException):
    """Raised when data processing fails."""
    pass


class ModelError(AquilaTraceException):
    """Raised when model operations fail."""
    pass


class GraphError(AquilaTraceException):
    """Raised when graph operations fail."""
    pass


class NLPError(AquilaTraceException):
    """Raised when NLP operations fail."""
    pass


class BlockchainError(AquilaTraceException):
    """Raised when blockchain analysis fails."""
    pass


class DatabaseError(AquilaTraceException):
    """Raised when database operations fail."""
    pass
