from .auth import router as auth_router
from .camera import router as camera_router
from .customer import router as customer_router
from .mall import router as mall_router
from .analytics import router as analytics_router


__all__ = ["auth_router", "camera_router", "customer_router", "mall_router", "analytics_router"]