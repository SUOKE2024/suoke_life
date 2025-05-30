import grpc

# 导入生成的gRPC模块
# 注意:需要先使用protoc生成Python代码
# 这里假设已经生成并放置在正确位置
from app.api.grpc.generated import knowledge_pb2, knowledge_pb2_grpc
from app.core.logger import get_logger
from app.services.knowledge_service import KnowledgeService

logger = get_logger()


class MedKnowledgeServicer(knowledge_pb2_grpc.MedKnowledgeServiceServicer):
    """中医知识gRPC服务实现"""

    def __init__(self, knowledge_service: KnowledgeService):
        self.service = knowledge_service

    def GetConstitutionInfo(self, request, context):
        """获取中医体质信息"""
        try:
            # 优先使用ID查询
            if request.constitution_id:
                constitution = self.service.get_constitution_by_id(request.constitution_id)
            # 如果没有ID,尝试使用名称查询
            elif request.constitution_name:
                # 这需要在repository中添加按名称查询的方法
                constitutions = self.service.search_knowledge(
                    request.constitution_name, "Constitution", 1, 0
                )
                if constitutions.total > 0:
                    constitution_id = constitutions.data[0].id
                    constitution = self.service.get_constitution_by_id(constitution_id)
                else:
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details(f"找不到名为'{request.constitution_name}'的体质")
                    return knowledge_pb2.ConstitutionResponse()
            else:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("请提供体质ID或名称")
                return knowledge_pb2.ConstitutionResponse()

            if not constitution:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"找不到ID为'{request.constitution_id}'的体质")
                return knowledge_pb2.ConstitutionResponse()

            # 将模型转换为protobuf消息
            constitution_info = knowledge_pb2.ConstitutionInfo(
                id=constitution.id,
                name=constitution.name,
                description=constitution.description,
                characteristics=constitution.characteristics,
                symptoms=constitution.symptoms,
                preventions=constitution.preventions,
                food_recommendations=constitution.food_recommendations,
                food_avoidances=constitution.food_avoidances,
                prevalence=constitution.prevalence,
            )

            return knowledge_pb2.ConstitutionResponse(constitution=constitution_info)
        except Exception as e:
            logger.error(f"GetConstitutionInfo错误: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"服务器内部错误: {e!s}")
            return knowledge_pb2.ConstitutionResponse()

    def GetSymptomInfo(self, request, context):
        """获取症状信息"""
        try:
            # 优先使用ID查询
            if request.symptom_id:
                symptom = self.service.get_symptom_by_id(request.symptom_id)
            # 如果没有ID,尝试使用名称查询
            elif request.symptom_name:
                symptoms = self.service.search_knowledge(request.symptom_name, "Symptom", 1, 0)
                if symptoms.total > 0:
                    symptom_id = symptoms.data[0].id
                    symptom = self.service.get_symptom_by_id(symptom_id)
                else:
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details(f"找不到名为'{request.symptom_name}'的症状")
                    return knowledge_pb2.SymptomResponse()
            else:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("请提供症状ID或名称")
                return knowledge_pb2.SymptomResponse()

            if not symptom:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"找不到ID为'{request.symptom_id}'的症状")
                return knowledge_pb2.SymptomResponse()

            # 将模型转换为protobuf消息
            symptom_info = knowledge_pb2.SymptomInfo(
                id=symptom.id,
                name=symptom.name,
                description=symptom.description,
                related_syndromes=symptom.related_syndromes,
                related_diseases=symptom.related_diseases,
                related_constitutions=symptom.related_constitutions,
                western_medicine_explanation=symptom.western_medicine_explanation,
            )

            return knowledge_pb2.SymptomResponse(symptom=symptom_info)
        except Exception as e:
            logger.error(f"GetSymptomInfo错误: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"服务器内部错误: {e!s}")
            return knowledge_pb2.SymptomResponse()

    def GetAcupointInfo(self, request, context):
        """获取穴位信息"""
        try:
            # 优先使用ID查询
            if request.acupoint_id:
                acupoint = self.service.get_acupoint_by_id(request.acupoint_id)
            # 如果没有ID,尝试使用名称查询
            elif request.acupoint_name:
                acupoints = self.service.search_knowledge(request.acupoint_name, "Acupoint", 1, 0)
                if acupoints.total > 0:
                    acupoint_id = acupoints.data[0].id
                    acupoint = self.service.get_acupoint_by_id(acupoint_id)
                else:
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details(f"找不到名为'{request.acupoint_name}'的穴位")
                    return knowledge_pb2.AcupointResponse()
            else:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("请提供穴位ID或名称")
                return knowledge_pb2.AcupointResponse()

            if not acupoint:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"找不到ID为'{request.acupoint_id}'的穴位")
                return knowledge_pb2.AcupointResponse()

            # 将模型转换为protobuf消息
            acupoint_info = knowledge_pb2.AcupointInfo(
                id=acupoint.id,
                name=acupoint.name,
                pinyin=acupoint.pinyin,
                meridian=acupoint.meridian,
                location=acupoint.location,
                functions=acupoint.functions,
                indications=acupoint.indications,
                manipulation=acupoint.manipulation,
                cautions=acupoint.cautions,
            )

            return knowledge_pb2.AcupointResponse(acupoint=acupoint_info)
        except Exception as e:
            logger.error(f"GetAcupointInfo错误: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"服务器内部错误: {e!s}")
            return knowledge_pb2.AcupointResponse()

    def GetHerbalInfo(self, request, context):
        """获取中药信息"""
        try:
            # 优先使用ID查询
            if request.herbal_id:
                herb = self.service.get_herb_by_id(request.herbal_id)
            # 如果没有ID,尝试使用名称查询
            elif request.herbal_name:
                herbs = self.service.search_knowledge(request.herbal_name, "Herb", 1, 0)
                if herbs.total > 0:
                    herb_id = herbs.data[0].id
                    herb = self.service.get_herb_by_id(herb_id)
                else:
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details(f"找不到名为'{request.herbal_name}'的中药")
                    return knowledge_pb2.HerbalResponse()
            else:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("请提供中药ID或名称")
                return knowledge_pb2.HerbalResponse()

            if not herb:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"找不到ID为'{request.herbal_id}'的中药")
                return knowledge_pb2.HerbalResponse()

            # 将模型转换为protobuf消息
            herbal_info = knowledge_pb2.HerbalInfo(
                id=herb.id,
                name=herb.name,
                pinyin=herb.pinyin,
                category=herb.category,
                nature=herb.nature,
                flavor=herb.flavor,
                meridian_tropism=herb.meridian_tropism,
                efficacy=herb.efficacy,
                indications=herb.indications,
                dosage=herb.dosage,
                cautions=herb.cautions,
                common_pairs=herb.common_pairs,
                modern_research=herb.modern_research,
            )

            return knowledge_pb2.HerbalResponse(herbal=herbal_info)
        except Exception as e:
            logger.error(f"GetHerbalInfo错误: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"服务器内部错误: {e!s}")
            return knowledge_pb2.HerbalResponse()

    def GetRecommendationsByConstitution(self, request, context):
        """通过体质查找推荐方案"""
        try:
            if not request.constitution_id:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("请提供体质ID")
                return knowledge_pb2.RecommendationResponse()

            # 获取推荐
            types = list(request.recommendation_types) if request.recommendation_types else None
            result = self.service.get_recommendations_by_constitution(
                request.constitution_id, types
            )

            if result.total == 0:
                return knowledge_pb2.RecommendationResponse(recommendations=[])

            # 转换为protobuf消息
            recommendations = []
            for rec in result.data:
                recommendation = knowledge_pb2.Recommendation(
                    id=rec.id,
                    type=rec.type,
                    title=rec.title,
                    description=rec.description,
                    relevance_score=rec.relevance_score,
                    evidence=rec.evidence,
                )
                recommendations.append(recommendation)

            return knowledge_pb2.RecommendationResponse(recommendations=recommendations)
        except Exception as e:
            logger.error(f"GetRecommendationsByConstitution错误: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"服务器内部错误: {e!s}")
            return knowledge_pb2.RecommendationResponse()

    def SearchKnowledge(self, request, context):
        """按关键字搜索知识库"""
        try:
            if not request.query:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("请提供搜索关键词")
                return knowledge_pb2.SearchResponse()

            # 设置默认值
            limit = request.limit if request.limit > 0 else 10
            offset = request.offset if request.offset >= 0 else 0
            entity_type = request.entity_type if request.entity_type else None

            # 搜索知识库
            result = self.service.search_knowledge(request.query, entity_type, limit, offset)

            # 转换为protobuf消息
            results = []
            for item in result.data:
                entity = knowledge_pb2.KnowledgeEntity(
                    id=item.id,
                    name=item.name,
                    entity_type=item.entity_type,
                    brief=item.brief,
                    relevance_score=item.relevance_score,
                )
                results.append(entity)

            return knowledge_pb2.SearchResponse(results=results, total_count=result.total)
        except Exception as e:
            logger.error(f"SearchKnowledge错误: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"服务器内部错误: {e!s}")
            return knowledge_pb2.SearchResponse()

    def GetSyndromePathways(self, request, context):
        """获取中医辨证路径"""
        try:
            # 优先使用ID查询
            if request.syndrome_id:
                result = self.service.get_syndrome_pathways(request.syndrome_id)
            # 如果没有ID,尝试使用名称查询
            elif request.syndrome_name:
                syndromes = self.service.search_knowledge(request.syndrome_name, "Syndrome", 1, 0)
                if syndromes.total > 0:
                    syndrome_id = syndromes.data[0].id
                    result = self.service.get_syndrome_pathways(syndrome_id)
                else:
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details(f"找不到名为'{request.syndrome_name}'的证型")
                    return knowledge_pb2.SyndromePathwaysResponse()
            else:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("请提供证型ID或名称")
                return knowledge_pb2.SyndromePathwaysResponse()

            if not result.syndrome:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"找不到ID为'{request.syndrome_id}'的证型")
                return knowledge_pb2.SyndromePathwaysResponse()

            # 转换症状信息
            syndrome_info = knowledge_pb2.SyndromeInfo(
                id=result.syndrome.id,
                name=result.syndrome.name,
                description=result.syndrome.description,
                key_symptoms=result.syndrome.key_symptoms,
                tongue_features=result.syndrome.tongue_features,
                pulse_features=result.syndrome.pulse_features,
            )

            # 转换路径信息
            pathways = []
            for pathway in result.pathways:
                diagnosis_steps = []

                for step in pathway.steps:
                    evidence = []
                    for ev in step.evidence:
                        evidence_item = knowledge_pb2.DiagnosisEvidence(
                            type=ev.type, description=ev.description, weight=ev.weight
                        )
                        evidence.append(evidence_item)

                    step_info = knowledge_pb2.DiagnosisStep(
                        step_number=step.step_number,
                        description=step.description,
                        evidence=evidence,
                        differential_points=step.differential_points,
                    )
                    diagnosis_steps.append(step_info)

                pathway_info = knowledge_pb2.DiagnosisPathway(
                    id=pathway.id,
                    name=pathway.name,
                    description=pathway.description,
                    steps=diagnosis_steps,
                )
                pathways.append(pathway_info)

            return knowledge_pb2.SyndromePathwaysResponse(syndrome=syndrome_info, pathways=pathways)
        except Exception as e:
            logger.error(f"GetSyndromePathways错误: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"服务器内部错误: {e!s}")
            return knowledge_pb2.SyndromePathwaysResponse()
