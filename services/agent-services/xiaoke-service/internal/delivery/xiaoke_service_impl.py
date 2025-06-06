"""
xiaoke_service_impl - 索克生活项目模块
"""

from api.grpc import xiaoke_service_pb2, xiaoke_service_pb2_grpc
from datetime import datetime
from google.protobuf.timestamp_pb2 import Timestamp
from internal.inventory.product_manager import ProductManager
from internal.observability.metrics import measure_time, metrics
from internal.repository.subscription_repository import SubscriptionRepository
from internal.scheduler.resource_manager import ResourceManager
import grpc
import logging

#!/usr/bin/env python

"""
小克服务(XiaoKeService)的gRPC实现
"""




logger = logging.getLogger(__name__)


class XiaoKeServiceServicer(xiaoke_service_pb2_grpc.XiaoKeServiceServicer):
    """小克服务gRPC实现"""

    def __init__(self):
        """初始化服务实现"""
        # 初始化依赖管理器
        self.resource_manager = ResourceManager()
        self.product_manager = ProductManager()
        self.subscription_repo = SubscriptionRepository()
        logger.info("小克服务实现已初始化")

    @measure_time("ScheduleMedicalResource")
    def ScheduleMedicalResource(self, request, context):
        """处理医疗资源调度请求"""
        logger.info(
            f"接收到医疗资源调度请求: user_id={request.user_id}, resource_type={request.resource_type}"
        )

        try:
            # 处理请求
            scheduled_resources = self.resource_manager.schedule_resources(
                user_id=request.user_id,
                resource_type=request.resource_type,
                constitution_type=request.constitution_type,
                location=request.location,
                requirements=list(request.requirements),
                page_size=request.page_size,
                page_number=request.page_number,
            )

            # 构建响应
            resources = []
            for resource in scheduled_resources["resources"]:
                resources.append(
                    xiaoke_service_pb2.MedicalResource(
                        resource_id=resource["id"],
                        name=resource["name"],
                        type=resource["type"],
                        location=resource["location"],
                        rating=resource["rating"],
                        description=resource["description"],
                        price=resource["price"],
                        available_times=resource["available_times"],
                        specialties=resource["specialties"],
                        metadata=resource["metadata"],
                    )
                )

            # 记录资源数量指标
            metrics.record_resource_count(
                resource_type=request.resource_type,
                count=scheduled_resources["total_count"],
            )

            return xiaoke_service_pb2.MedicalResourceResponse(
                request_id=scheduled_resources["request_id"],
                resources=resources,
                total_count=scheduled_resources["total_count"],
                page_count=scheduled_resources["page_count"],
            )

        except Exception as e:
            logger.error(f"医疗资源调度失败: {e!s}", exc_info=True)
            metrics.record_request("ScheduleMedicalResource", status="error")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"医疗资源调度处理失败: {e!s}")
            return xiaoke_service_pb2.MedicalResourceResponse()

    @measure_time("ManageAppointment")
    def ManageAppointment(self, request, context):
        """处理预约管理请求"""
        logger.info(
            f"接收到预约管理请求: user_id={request.user_id}, doctor_id={request.doctor_id}"
        )

        try:
            # 处理预约请求
            appointment_result = self.resource_manager.manage_appointment(
                user_id=request.user_id,
                doctor_id=request.doctor_id,
                appointment_type=request.appointment_type,
                preferred_time=request.preferred_time,
                symptoms=request.symptoms,
                constitution_type=request.constitution_type,
                metadata=dict(request.metadata),
            )

            # 添加资源记录指标
            if appointment_result["status"] == "CONFIRMED":
                metrics.record_resource_count("active_appointments", 1)

            return xiaoke_service_pb2.AppointmentResponse(
                appointment_id=appointment_result["appointment_id"],
                status=appointment_result["status"],
                confirmed_time=appointment_result["confirmed_time"],
                doctor_name=appointment_result["doctor_name"],
                location=appointment_result["location"],
                meeting_link=appointment_result.get("meeting_link", ""),
                metadata=appointment_result.get("metadata", {}),
            )

        except Exception as e:
            logger.error(f"预约管理失败: {e!s}", exc_info=True)
            metrics.record_request("ManageAppointment", status="error")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"预约管理处理失败: {e!s}")
            return xiaoke_service_pb2.AppointmentResponse()

    @measure_time("CustomizeProduct")
    def CustomizeProduct(self, request, context):
        """处理农产品定制请求"""
        logger.info(
            f"接收到农产品定制请求: user_id={request.user_id}, constitution_type={request.constitution_type}"
        )

        try:
            # 处理定制请求
            customization_result = self.product_manager.customize_products(
                user_id=request.user_id,
                constitution_type=request.constitution_type,
                health_conditions=list(request.health_conditions),
                preferences=list(request.preferences),
                season=request.season,
                packaging_preference=request.packaging_preference,
                quantity=request.quantity,
                need_delivery=request.need_delivery,
                delivery_address=request.delivery_address,
            )

            # 构建定制产品列表
            customized_products = []
            for product in customization_result["products"]:
                customized_products.append(
                    xiaoke_service_pb2.CustomizedProduct(
                        product_id=product["id"],
                        name=product["name"],
                        description=product["description"],
                        origin=product["origin"],
                        producer=product["producer"],
                        price=product["price"],
                        quantity=product["quantity"],
                        image_url=product["image_url"],
                        constitution_benefit=product["constitution_benefit"],
                        health_benefits=product["health_benefits"],
                        harvesting_date=product["harvesting_date"],
                    )
                )

                # 记录产品推荐指标
                metrics.record_product_recommendation(
                    constitution_type=request.constitution_type,
                    category=product.get("category", "unknown"),
                )

            return xiaoke_service_pb2.ProductCustomizationResponse(
                customization_id=customization_result["customization_id"],
                products=customized_products,
                total_price=customization_result["total_price"],
                delivery_estimate=customization_result["delivery_estimate"],
                metadata=customization_result.get("metadata", {}),
                payment_link=customization_result.get("payment_link", ""),
            )

        except Exception as e:
            logger.error(f"农产品定制失败: {e!s}", exc_info=True)
            metrics.record_request("CustomizeProduct", status="error")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"农产品定制处理失败: {e!s}")
            return xiaoke_service_pb2.ProductCustomizationResponse()

    @measure_time("TraceProduct")
    def TraceProduct(self, request, context):
        """处理农产品溯源请求"""
        logger.info(f"接收到农产品溯源请求: product_id={request.product_id}")

        try:
            # 处理溯源请求
            trace_result = self.product_manager.trace_product(
                product_id=request.product_id,
                batch_id=request.batch_id,
                trace_token=request.trace_token,
            )

            # 构建溯源记录
            trace_records = []
            for record in trace_result["trace_records"]:
                timestamp = Timestamp()
                timestamp.FromDatetime(datetime.fromisoformat(record["timestamp"]))

                trace_records.append(
                    xiaoke_service_pb2.TraceRecord(
                        stage_name=record["stage_name"],
                        location=record["location"],
                        timestamp=timestamp,
                        operator=record["operator"],
                        details=record["details"],
                        verification_hash=record["verification_hash"],
                    )
                )

            # 记录区块链服务调用指标
            if trace_result["verified"]:
                metrics.record_erp_api_call("blockchain_verify", "success")

            return xiaoke_service_pb2.ProductTraceResponse(
                product_name=trace_result["product_name"],
                trace_records=trace_records,
                blockchain_verification_url=trace_result["blockchain_verification_url"],
                verified=trace_result["verified"],
                qr_code_url=trace_result["qr_code_url"],
            )

        except Exception as e:
            logger.error(f"农产品溯源失败: {e!s}", exc_info=True)
            metrics.record_request("TraceProduct", status="error")
            metrics.record_erp_api_call("blockchain_verify", "failure")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"农产品溯源处理失败: {e!s}")
            return xiaoke_service_pb2.ProductTraceResponse()

    @measure_time("ProcessPayment")
    def ProcessPayment(self, request, context):
        """处理支付请求"""
        logger.info(
            f"接收到支付处理请求: user_id={request.user_id}, order_id={request.order_id}"
        )

        try:
            # 处理支付请求
            payment_result = self.product_manager.process_payment(
                user_id=request.user_id,
                order_id=request.order_id,
                payment_method=request.payment_method,
                amount=request.amount,
                currency=request.currency,
                metadata=dict(request.metadata),
            )

            # 构建时间戳
            timestamp = Timestamp()
            timestamp.FromDatetime(datetime.fromisoformat(payment_result["timestamp"]))

            # 记录支付指标
            metrics.record_payment(
                payment_method=request.payment_method, status=payment_result["status"]
            )

            return xiaoke_service_pb2.PaymentResponse(
                payment_id=payment_result["payment_id"],
                status=payment_result["status"],
                transaction_id=payment_result["transaction_id"],
                timestamp=timestamp,
                payment_url=payment_result["payment_url"],
                receipt_url=payment_result["receipt_url"],
            )

        except Exception as e:
            logger.error(f"支付处理失败: {e!s}", exc_info=True)
            metrics.record_request("ProcessPayment", status="error")
            metrics.record_payment(
                payment_method=request.payment_method, status="FAILED"
            )
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"支付处理失败: {e!s}")
            return xiaoke_service_pb2.PaymentResponse()

    @measure_time("ManageSubscription")
    def ManageSubscription(self, request, context):
        """处理订阅管理请求"""
        logger.info(
            f"接收到订阅管理请求: user_id={request.user_id}, action={request.action}"
        )

        try:
            # 处理订阅请求
            subscription_result = self.subscription_repo.manage_subscription(
                user_id=request.user_id,
                action=request.action,
                subscription_id=request.subscription_id,
                plan_id=request.plan_id,
                payment_method=request.payment_method,
                billing_cycle=request.billing_cycle,
                metadata=dict(request.metadata),
            )

            # 构建时间戳
            start_date = Timestamp()
            start_date.FromDatetime(
                datetime.fromisoformat(subscription_result["start_date"])
            )

            end_date = Timestamp()
            end_date.FromDatetime(
                datetime.fromisoformat(subscription_result["end_date"])
            )

            # 记录订阅指标
            metrics.record_db_operation(
                database="postgres",
                operation=f"subscription_{request.action.lower()}",
                status="success",
            )

            return xiaoke_service_pb2.SubscriptionResponse(
                subscription_id=subscription_result["subscription_id"],
                status=subscription_result["status"],
                start_date=start_date,
                end_date=end_date,
                plan_name=subscription_result["plan_name"],
                amount=subscription_result["amount"],
                next_billing_date=subscription_result["next_billing_date"],
                included_services=subscription_result["included_services"],
                metadata=subscription_result.get("metadata", {}),
            )

        except Exception as e:
            logger.error(f"订阅管理失败: {e!s}", exc_info=True)
            metrics.record_request("ManageSubscription", status="error")
            metrics.record_db_operation(
                database="postgres",
                operation=f"subscription_{request.action.lower()}",
                status="failure",
            )
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"订阅管理处理失败: {e!s}")
            return xiaoke_service_pb2.SubscriptionResponse()

    @measure_time("RecommendProducts")
    def RecommendProducts(self, request, context):
        """处理商品推荐请求"""
        logger.info(
            f"接收到商品推荐请求: user_id={request.user_id}, constitution_type={request.constitution_type}"
        )

        try:
            # 处理推荐请求
            recommendation_result = self.product_manager.recommend_products(
                user_id=request.user_id,
                constitution_type=request.constitution_type,
                season=request.season,
                health_conditions=list(request.health_conditions),
                preferences=list(request.preferences),
                max_results=request.max_results,
            )

            # 构建推荐商品列表
            seasonal_products = []
            for product in recommendation_result["seasonal_products"]:
                seasonal_products.append(
                    xiaoke_service_pb2.RecommendedProduct(
                        product_id=product["id"],
                        name=product["name"],
                        description=product["description"],
                        category=product["category"],
                        price=product["price"],
                        recommendation_score=product["recommendation_score"],
                        image_url=product["image_url"],
                        health_benefits=product["health_benefits"],
                        recommendation_reason=product["recommendation_reason"],
                    )
                )
                metrics.record_product_recommendation(
                    constitution_type=request.constitution_type,
                    category=product.get("category", "seasonal"),
                )

            constitution_specific_products = []
            for product in recommendation_result["constitution_specific_products"]:
                constitution_specific_products.append(
                    xiaoke_service_pb2.RecommendedProduct(
                        product_id=product["id"],
                        name=product["name"],
                        description=product["description"],
                        category=product["category"],
                        price=product["price"],
                        recommendation_score=product["recommendation_score"],
                        image_url=product["image_url"],
                        health_benefits=product["health_benefits"],
                        recommendation_reason=product["recommendation_reason"],
                    )
                )
                metrics.record_product_recommendation(
                    constitution_type=request.constitution_type,
                    category=product.get("category", "constitution"),
                )

            personalized_products = []
            for product in recommendation_result["personalized_products"]:
                personalized_products.append(
                    xiaoke_service_pb2.RecommendedProduct(
                        product_id=product["id"],
                        name=product["name"],
                        description=product["description"],
                        category=product["category"],
                        price=product["price"],
                        recommendation_score=product["recommendation_score"],
                        image_url=product["image_url"],
                        health_benefits=product["health_benefits"],
                        recommendation_reason=product["recommendation_reason"],
                    )
                )
                metrics.record_product_recommendation(
                    constitution_type=request.constitution_type,
                    category=product.get("category", "personalized"),
                )

            return xiaoke_service_pb2.ProductRecommendationResponse(
                seasonal_products=seasonal_products,
                constitution_specific_products=constitution_specific_products,
                personalized_products=personalized_products,
                recommendation_explanation=recommendation_result.get(
                    "recommendation_explanation", {}
                ),
            )

        except Exception as e:
            logger.error(f"商品推荐失败: {e!s}", exc_info=True)
            metrics.record_request("RecommendProducts", status="error")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"商品推荐处理失败: {e!s}")
            return xiaoke_service_pb2.ProductRecommendationResponse()
