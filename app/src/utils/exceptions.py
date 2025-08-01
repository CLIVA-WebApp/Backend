class AuthenticationException(Exception):
    """Raised when authentication fails"""
    pass

class DatabaseException(Exception):
    """Raised when database operations fail"""
    pass

class ValidationException(Exception):
    """Raised when data validation fails"""
    pass

class NotFoundException(Exception):
    """Raised when requested resource is not found"""
    pass

class GeocodingException(Exception):
    """Raised when geocoding operations fail"""
    pass