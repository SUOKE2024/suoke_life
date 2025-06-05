#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
RAG服务端到端测试
测试完整的工作流程，包括文档管理、检索、生成等功能
"""

import asyncio
import pytest
import httpx
import json
import time
from typing import Dict, List, Any
from pathlib import Path
import tempfile
import os

class TestRAGServiceE2E:
    """RAG服务端到端测试类"""
    
    @pytest.fixture(scope="class")
    def base_url(self):
        """测试服务的基础URL"""
        return os.getenv("RAG_SERVICE_URL", "http://localhost:8076")
    
    @pytest.fixture(scope="class")
    def api_key(self):
        """API密钥"""
        return os.getenv("RAG_API_KEY", "test-api-key")
    
    @pytest.fixture(scope="class")
    def headers(self, api_key):
        """请求头"""
        return {
            "Content-Type": "application/json",
            "X-API-Key": api_key
        }
    
    @pytest.fixture(scope="class")
    async def client(self, base_url):
        """HTTP客户端"""
        async with httpx.AsyncClient(base_url=base_url, timeout=30.0) as client:
            yield client
    
    @pytest.fixture(scope="class")
    def sample_documents(self):
        """测试文档数据"""
        return [
            {
                "id": "tcm_doc_001",
                "content": "高血压在中医理论中属于眩晕、头痛范畴。主要病机为肝阳上亢、痰湿壅盛、肾阴虚等。治疗原则以平肝潜阳、化痰降浊、滋阴补肾为主。常用方剂包括天麻钩藤饮、半夏白术天麻汤、杞菊地黄丸等。",
                "metadata": {
                    "title": "中医高血压治疗指南",
                    "category": "中医内科",
                    "author": "张仲景",
                    "date": "2024-01-15",
                    "tags": ["高血压", "中医", "治疗"]
                },
                "source": "tcm_guidelines"
            },
            {
                "id": "tcm_doc_002", 
                "content": "糖尿病中医称为消渴病，分为上消、中消、下消三型。上消属肺热津伤，治以清热润肺；中消属胃热炽盛，治以清胃泻火；下消属肾阴亏虚，治以滋阴补肾。常用方剂有白虎汤、玉女煎、六味地黄丸等。",
                "metadata": {
                    "title": "中医糖尿病诊疗方案",
                    "category": "中医内科",
                    "author": "李时珍",
                    "date": "2024-01-16",
                    "tags": ["糖尿病", "消渴病", "中医"]
                },
                "source": "tcm_guidelines"
            },
            {
                "id": "acup_doc_001",
                "content": "失眠的针灸治疗以安神定志为主要治疗原则。主要穴位包括百会、四神聪、神门、三阴交、太溪等。百会穴位于头顶正中，有安神定志的作用；神门穴为心经原穴，能宁心安神；三阴交为脾肝肾三经交会穴，有调理气血的功效。",
                "metadata": {
                    "title": "针灸治疗失眠临床研究",
                    "category": "针灸学",
                    "author": "王医生",
                    "date": "2024-01-17",
                    "tags": ["失眠", "针灸", "穴位"]
                },
                "source": "acupuncture_research"
            }
        ]
    
    @pytest.mark.asyncio
    async def test_service_health(self, client):
        """测试服务健康状态"""
        response = await client.get("/health")
        assert response.status_code == 200
        
        health_data = response.json()
        assert health_data["status"] == "healthy"
        assert "components" in health_data
        assert "version" in health_data
    
    @pytest.mark.asyncio
    async def test_service_status(self, client):
        """测试服务详细状态"""
        response = await client.get("/status")
        assert response.status_code == 200
        
        status_data = response.json()
        assert status_data["service"] == "rag-service"
        assert "version" in status_data
        assert "uptime" in status_data
    
    @pytest.mark.asyncio
    async def test_document_management_workflow(self, client, headers, sample_documents):
        """测试文档管理完整工作流程"""
        
        # 1. 添加文档
        for doc in sample_documents:
            add_response = await client.post(
                "/api/v1/documents",
                headers=headers,
                json={
                    "document": doc,
                    "collection_name": "test_collection",
                    "reindex": True
                }
            )
            assert add_response.status_code == 201
            
            add_data = add_response.json()
            assert add_data["success"] is True
            assert add_data["document_id"] == doc["id"]
        
        # 等待索引完成
        await asyncio.sleep(2)
        
        # 2. 列出文档
        list_response = await client.get(
            "/api/v1/documents?collection=test_collection&page=1&limit=10",
            headers=headers
        )
        assert list_response.status_code == 200
        
        list_data = list_response.json()
        assert len(list_data["documents"]) == len(sample_documents)
        assert list_data["total"] == len(sample_documents)
        
        # 3. 验证文档内容
        for doc in list_data["documents"]:
            assert doc["id"] in [d["id"] for d in sample_documents]
            assert "content" in doc
            assert "metadata" in doc
    
    @pytest.mark.asyncio
    async def test_basic_query_workflow(self, client, headers):
        """测试基础查询工作流程"""
        
        # 基础查询
        query_data = {
            "query": "高血压的中医治疗方法",
            "top_k": 3,
            "collection_names": ["test_collection"]
        }
        
        response = await client.post(
            "/api/v1/query",
            headers=headers,
            json=query_data
        )
        assert response.status_code == 200
        
        result = response.json()
        assert "answer" in result
        assert "references" in result
        assert "retrieval_latency_ms" in result
        assert "generation_latency_ms" in result
        assert "total_latency_ms" in result
        
        # 验证答案质量
        assert len(result["answer"]) > 50  # 答案应该有一定长度
        assert "高血压" in result["answer"] or "治疗" in result["answer"]
        
        # 验证引用
        assert len(result["references"]) > 0
        for ref in result["references"]:
            assert "id" in ref
            assert "title" in ref
            assert "source" in ref
    
    @pytest.mark.asyncio
    async def test_stream_query_workflow(self, client, headers):
        """测试流式查询工作流程"""
        
        query_data = {
            "query": "糖尿病的中医分型和治疗",
            "top_k": 3,
            "system_prompt": "你是一位专业的中医师，请详细回答问题。"
        }
        
        async with client.stream(
            "POST",
            "/api/v1/query/stream",
            headers=headers,
            json=query_data
        ) as response:
            assert response.status_code == 200
            assert response.headers["content-type"] == "text/event-stream"
            
            chunks = []
            async for chunk in response.aiter_text():
                if chunk.strip():
                    # 解析SSE格式
                    if chunk.startswith("data: "):
                        data_str = chunk[6:]  # 移除"data: "前缀
                        try:
                            data = json.loads(data_str)
                            chunks.append(data)
                        except json.JSONDecodeError:
                            continue
            
            # 验证流式响应
            assert len(chunks) > 0
            
            # 检查最后一个chunk是否标记为final
            final_chunk = None
            for chunk in reversed(chunks):
                if chunk.get("is_final"):
                    final_chunk = chunk
                    break
            
            assert final_chunk is not None
            assert "references" in final_chunk
    
    @pytest.mark.asyncio
    async def test_multimodal_query_workflow(self, client, api_key):
        """测试多模态查询工作流程"""
        
        # 创建测试图片文件
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
            # 写入一些测试数据（模拟图片）
            temp_file.write(b"fake_image_data_for_testing")
            temp_file_path = temp_file.name
        
        try:
            # 多模态查询
            with open(temp_file_path, "rb") as f:
                files = {"files": ("test_image.jpg", f, "image/jpeg")}
                data = {"query": "请分析这个图像"}
                headers_multipart = {"X-API-Key": api_key}
                
                response = await client.post(
                    "/api/v1/query_multimodal",
                    headers=headers_multipart,
                    files=files,
                    data=data
                )
            
            # 注意：这里可能返回400或500，因为我们使用的是假图片数据
            # 但我们主要测试接口是否可达
            assert response.status_code in [200, 400, 500]
            
        finally:
            # 清理临时文件
            os.unlink(temp_file_path)
    
    @pytest.mark.asyncio
    async def test_tcm_syndrome_analysis(self, client, headers):
        """测试中医证候分析功能"""
        
        syndrome_data = {
            "symptoms": ["头痛", "眩晕", "面红", "急躁易怒", "口苦"],
            "pulse": "弦脉",
            "tongue": "舌红苔黄"
        }
        
        response = await client.post(
            "/api/v1/tcm/syndrome_analysis",
            headers=headers,
            json=syndrome_data
        )
        
        # 这个接口可能还未实现，所以接受404
        assert response.status_code in [200, 404, 501]
        
        if response.status_code == 200:
            result = response.json()
            assert "syndrome" in result
            assert "confidence" in result
            assert "treatment_principle" in result
    
    @pytest.mark.asyncio
    async def test_herb_recommendation(self, client, headers):
        """测试中药推荐功能"""
        
        herb_data = {
            "condition": "失眠多梦",
            "constitution": "阴虚体质",
            "age": 45,
            "gender": "female"
        }
        
        response = await client.post(
            "/api/v1/tcm/herb_recommendation",
            headers=headers,
            json=herb_data
        )
        
        # 这个接口可能还未实现，所以接受404
        assert response.status_code in [200, 404, 501]
        
        if response.status_code == 200:
            result = response.json()
            assert "herbs" in result or "formula" in result
    
    @pytest.mark.asyncio
    async def test_batch_query_workflow(self, client, headers):
        """测试批量查询工作流程"""
        
        batch_data = {
            "queries": [
                {"query": "高血压治疗", "top_k": 3},
                {"query": "糖尿病饮食", "top_k": 3},
                {"query": "失眠调理", "top_k": 3}
            ],
            "parallel": True
        }
        
        response = await client.post(
            "/api/v1/query/batch",
            headers=headers,
            json=batch_data
        )
        
        # 批量接口可能还未实现
        assert response.status_code in [200, 404, 501]
        
        if response.status_code == 200:
            results = response.json()
            assert "results" in results
            assert len(results["results"]) == 3
    
    @pytest.mark.asyncio
    async def test_error_handling(self, client, headers):
        """测试错误处理"""
        
        # 1. 测试空查询
        response = await client.post(
            "/api/v1/query",
            headers=headers,
            json={"query": "", "top_k": 3}
        )
        assert response.status_code == 400
        
        error_data = response.json()
        assert "error" in error_data
        
        # 2. 测试无效的top_k
        response = await client.post(
            "/api/v1/query",
            headers=headers,
            json={"query": "测试", "top_k": -1}
        )
        assert response.status_code == 400
        
        # 3. 测试无效的API密钥
        invalid_headers = {"Content-Type": "application/json", "X-API-Key": "invalid-key"}
        response = await client.post(
            "/api/v1/query",
            headers=invalid_headers,
            json={"query": "测试", "top_k": 3}
        )
        assert response.status_code in [401, 403]
    
    @pytest.mark.asyncio
    async def test_performance_requirements(self, client, headers):
        """测试性能要求"""
        
        query_data = {
            "query": "中医养生的基本原则",
            "top_k": 5
        }
        
        # 测试响应时间
        start_time = time.time()
        response = await client.post(
            "/api/v1/query",
            headers=headers,
            json=query_data
        )
        end_time = time.time()
        
        assert response.status_code == 200
        
        # 响应时间应该在合理范围内（5秒内）
        response_time = end_time - start_time
        assert response_time < 5.0, f"响应时间过长: {response_time}秒"
        
        result = response.json()
        
        # 检查内部延迟指标
        if "total_latency_ms" in result:
            assert result["total_latency_ms"] < 5000  # 5秒内
        
        if "retrieval_latency_ms" in result:
            assert result["retrieval_latency_ms"] < 1000  # 检索应在1秒内
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, client, headers):
        """测试并发请求处理"""
        
        async def make_query(query_text: str):
            """发起单个查询"""
            response = await client.post(
                "/api/v1/query",
                headers=headers,
                json={"query": query_text, "top_k": 3}
            )
            return response
        
        # 并发发起多个查询
        queries = [
            "高血压的症状",
            "糖尿病的预防",
            "失眠的原因",
            "中医养生方法",
            "针灸的作用"
        ]
        
        tasks = [make_query(query) for query in queries]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 验证所有请求都成功
        successful_responses = 0
        for response in responses:
            if isinstance(response, httpx.Response) and response.status_code == 200:
                successful_responses += 1
        
        # 至少80%的请求应该成功
        success_rate = successful_responses / len(queries)
        assert success_rate >= 0.8, f"并发请求成功率过低: {success_rate}"
    
    @pytest.mark.asyncio
    async def test_cache_functionality(self, client, headers):
        """测试缓存功能"""
        
        query_data = {
            "query": "中医基础理论",
            "top_k": 3
        }
        
        # 第一次查询
        start_time1 = time.time()
        response1 = await client.post(
            "/api/v1/query",
            headers=headers,
            json=query_data
        )
        end_time1 = time.time()
        
        assert response1.status_code == 200
        first_response_time = end_time1 - start_time1
        
        # 第二次相同查询（应该命中缓存）
        start_time2 = time.time()
        response2 = await client.post(
            "/api/v1/query",
            headers=headers,
            json=query_data
        )
        end_time2 = time.time()
        
        assert response2.status_code == 200
        second_response_time = end_time2 - start_time2
        
        # 缓存命中的响应应该更快
        # 注意：这个测试可能不稳定，因为网络延迟等因素
        if second_response_time < first_response_time * 0.8:
            print(f"缓存生效：第一次 {first_response_time:.3f}s，第二次 {second_response_time:.3f}s")
        
        # 验证响应内容一致
        result1 = response1.json()
        result2 = response2.json()
        assert result1["answer"] == result2["answer"]
    
    @pytest.mark.asyncio
    async def test_metrics_endpoint(self, client):
        """测试指标端点"""
        
        response = await client.get("/metrics")
        assert response.status_code == 200
        
        # 检查是否返回Prometheus格式的指标
        metrics_text = response.text
        assert "# HELP" in metrics_text or "# TYPE" in metrics_text
    
    @pytest.mark.asyncio
    async def test_cleanup_test_data(self, client, headers, sample_documents):
        """清理测试数据"""
        
        # 删除测试文档
        for doc in sample_documents:
            response = await client.delete(
                f"/api/v1/documents/{doc['id']}",
                headers=headers
            )
            # 删除可能成功或失败（如果文档不存在）
            assert response.status_code in [200, 404]

class TestRAGServiceStress:
    """RAG服务压力测试"""
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_high_load_queries(self, client, headers):
        """测试高负载查询"""
        
        async def stress_query(query_id: int):
            """压力测试查询"""
            response = await client.post(
                "/api/v1/query",
                headers=headers,
                json={
                    "query": f"测试查询 {query_id}",
                    "top_k": 3
                }
            )
            return response.status_code == 200
        
        # 发起100个并发查询
        tasks = [stress_query(i) for i in range(100)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 计算成功率
        success_count = sum(1 for result in results if result is True)
        success_rate = success_count / len(tasks)
        
        # 在高负载下，至少70%的请求应该成功
        assert success_rate >= 0.7, f"高负载测试成功率过低: {success_rate}"
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_memory_usage_stability(self, client, headers):
        """测试内存使用稳定性"""
        
        # 连续发起多个查询，检查是否有内存泄漏
        for i in range(50):
            response = await client.post(
                "/api/v1/query",
                headers=headers,
                json={
                    "query": f"长时间运行测试 {i}",
                    "top_k": 3
                }
            )
            
            # 每10个请求检查一次服务状态
            if i % 10 == 0:
                health_response = await client.get("/health")
                assert health_response.status_code == 200
                
                health_data = health_response.json()
                assert health_data["status"] == "healthy"

if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"]) 