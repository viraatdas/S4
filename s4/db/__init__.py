"""Database module for S4 SaaS."""

from s4.db.tenant_manager import TenantManager

__all__ = ["TenantManager"]

# Global instance of tenant manager
tenant_manager = TenantManager() 