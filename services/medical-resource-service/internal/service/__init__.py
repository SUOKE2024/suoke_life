"""
医疗资源服务模块
"""

from .wellness_tourism_service import WellnessTourismService
from .enhanced_food_agriculture_service import EnhancedFoodAgricultureService
from .famous_doctor_service import FamousDoctorService
from .intelligent_appointment_service import IntelligentAppointmentService

__all__ = [
    "WellnessTourismService",
    "EnhancedFoodAgricultureService", 
    "FamousDoctorService",
    "IntelligentAppointmentService"
] 