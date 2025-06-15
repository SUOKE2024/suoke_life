"""
API接口测试

测试REST API的各个端点。
"""

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


class TestHealthAPI:
    """健康检查API测试"""

    def test_health_check(self, client: TestClient):
        """测试健康检查端点"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "listen-service"
        assert "timestamp" in data
        assert "version" in data

    def test_root_endpoint(self, client: TestClient):
        """测试根端点"""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["service"] == "listen-service"
        assert data["status"] == "running"
        assert data["docs"] == "/docs"


class TestAudioUploadAPI:
    """音频上传API测试"""

    def test_upload_audio_success(self, client: TestClient, sample_audio_file: Path):
        """测试成功上传音频文件"""
        with open(sample_audio_file, "rb") as f:
            response = client.post(
                "/api/v1/audio/upload",
                files={"file": ("test_audio.wav", f, "audio/wav")},
                headers={"Authorization": "Bearer test_token"}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert "request_id" in data
        assert "file_path" in data
        assert data["status"] == "uploaded"
        assert "validation" in data

    def test_upload_audio_no_file(self, client: TestClient):
        """测试上传空文件"""
        response = client.post(
            "/api/v1/audio/upload",
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 422  # Unprocessable Entity

    def test_upload_audio_invalid_format(self, client: TestClient, temp_dir: Path):
        """测试上传不支持的文件格式"""
        # 创建一个文本文件
        text_file = temp_dir / "test.txt"
        text_file.write_text("This is not an audio file")
        
        with open(text_file, "rb") as f:
            response = client.post(
                "/api/v1/audio/upload",
                files={"file": ("test.txt", f, "text/plain")},
                headers={"Authorization": "Bearer test_token"}
            )
        
        assert response.status_code == 400


class TestAudioAnalysisAPI:
    """音频分析API测试"""

    def test_analyze_audio_basic(self, client: TestClient, sample_request_data: dict):
        """测试基础音频分析"""
        response = client.post(
            "/api/v1/audio/analyze",
            json=sample_request_data,
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "request_id" in data
        assert "audio_features" in data
        assert "processing_time" in data
        assert data["analysis_type"] == "basic"

    def test_analyze_audio_comprehensive(self, client: TestClient, sample_request_data: dict):
        """测试综合音频分析"""
        sample_request_data["analysis_type"] = "comprehensive"
        
        response = client.post(
            "/api/v1/audio/analyze",
            json=sample_request_data,
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "audio_features" in data
        assert "tcm_features" in data
        assert data["analysis_type"] == "comprehensive"

    def test_analyze_audio_invalid_file(self, client: TestClient, mock_user_id: str):
        """测试分析不存在的文件"""
        request_data = {
            "file_path": "/nonexistent/file.wav",
            "analysis_type": "basic",
            "user_id": mock_user_id,
            "language": "zh-CN"
        }
        
        response = client.post(
            "/api/v1/audio/analyze",
            json=request_data,
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 500

    def test_analyze_audio_invalid_type(self, client: TestClient, sample_request_data: dict):
        """测试无效的分析类型"""
        sample_request_data["analysis_type"] = "invalid_type"
        
        response = client.post(
            "/api/v1/audio/analyze",
            json=sample_request_data,
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 500


class TestTCMDiagnosisAPI:
    """中医诊断API测试"""

    def test_tcm_diagnose_success(self, client: TestClient, sample_tcm_request_data: dict):
        """测试成功的中医诊断"""
        response = client.post(
            "/api/v1/tcm/diagnose",
            json=sample_tcm_request_data,
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "request_id" in data
        assert "constitution_type" in data
        assert "emotion_state" in data
        assert "voice_features" in data
        assert "diagnosis_result" in data
        assert "recommendations" in data
        assert "confidence_score" in data

    def test_tcm_diagnose_invalid_constitution(self, client: TestClient, sample_tcm_request_data: dict):
        """测试无效的体质类型"""
        sample_tcm_request_data["constitution_type"] = "invalid_constitution"
        
        response = client.post(
            "/api/v1/tcm/diagnose",
            json=sample_tcm_request_data,
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 500


class TestBatchAnalysisAPI:
    """批量分析API测试"""

    def test_batch_analyze_success(self, client: TestClient, sample_audio_files: list[Path], mock_user_id: str):
        """测试成功的批量分析"""
        request_data = {
            "file_paths": [str(f) for f in sample_audio_files],
            "analysis_type": "basic",
            "user_id": mock_user_id
        }
        
        response = client.post(
            "/api/v1/audio/batch-analyze",
            json=request_data,
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "request_id" in data
        assert data["status"] == "processing"
        assert data["total_files"] == len(sample_audio_files)
        assert data["completed_files"] == 0
        assert data["failed_files"] == 0

    def test_batch_analyze_too_many_files(self, client: TestClient, mock_user_id: str):
        """测试批量分析文件数量超限"""
        request_data = {
            "file_paths": [f"/fake/file_{i}.wav" for i in range(15)],  # 超过10个文件
            "analysis_type": "basic",
            "user_id": mock_user_id
        }
        
        response = client.post(
            "/api/v1/audio/batch-analyze",
            json=request_data,
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 400


class TestStatusAPI:
    """状态查询API测试"""

    def test_get_analysis_status_not_found(self, client: TestClient):
        """测试查询不存在的分析状态"""
        response = client.get("/api/v1/analysis/status/nonexistent_id")
        assert response.status_code == 404

    def test_get_cache_stats(self, client: TestClient):
        """测试获取缓存统计"""
        response = client.get(
            "/api/v1/cache/stats",
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "type" in data
        assert "requests" in data or "size" in data

    def test_get_performance_stats(self, client: TestClient):
        """测试获取性能统计"""
        response = client.get(
            "/api/v1/performance/stats",
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "total_functions_monitored" in data
        assert "total_function_calls" in data

    def test_clear_cache(self, client: TestClient):
        """测试清空缓存"""
        response = client.delete(
            "/api/v1/cache/clear",
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data


class TestAuthenticationAPI:
    """认证API测试"""

    def test_missing_authorization_header(self, client: TestClient, sample_request_data: dict):
        """测试缺少认证头"""
        response = client.post(
            "/api/v1/audio/analyze",
            json=sample_request_data
        )
        
        assert response.status_code == 403  # Forbidden

    def test_invalid_authorization_header(self, client: TestClient, sample_request_data: dict):
        """测试无效的认证头"""
        response = client.post(
            "/api/v1/audio/analyze",
            json=sample_request_data,
            headers={"Authorization": "Invalid token"}
        )
        
        assert response.status_code == 403  # Forbidden


class TestErrorHandling:
    """错误处理测试"""

    def test_404_error(self, client: TestClient):
        """测试404错误"""
        response = client.get("/nonexistent/endpoint")
        assert response.status_code == 404

    def test_method_not_allowed(self, client: TestClient):
        """测试方法不允许错误"""
        response = client.put("/health")
        assert response.status_code == 405

    def test_request_validation_error(self, client: TestClient):
        """测试请求验证错误"""
        response = client.post(
            "/api/v1/audio/analyze",
            json={"invalid": "data"},
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 422


@pytest.mark.integration
class TestAPIIntegration:
    """API集成测试"""

    def test_full_audio_analysis_workflow(self, client: TestClient, sample_audio_file: Path):
        """测试完整的音频分析工作流"""
        # 1. 上传文件
        with open(sample_audio_file, "rb") as f:
            upload_response = client.post(
                "/api/v1/audio/upload",
                files={"file": ("test_audio.wav", f, "audio/wav")},
                headers={"Authorization": "Bearer test_token"}
            )
        
        assert upload_response.status_code == 200
        upload_data = upload_response.json()
        uploaded_file_path = upload_data["file_path"]
        
        # 2. 分析音频
        analysis_request = {
            "file_path": uploaded_file_path,
            "analysis_type": "comprehensive",
            "user_id": "test_user",
            "language": "zh-CN"
        }
        
        analysis_response = client.post(
            "/api/v1/audio/analyze",
            json=analysis_request,
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert analysis_response.status_code == 200
        analysis_data = analysis_response.json()
        assert "audio_features" in analysis_data
        assert "tcm_features" in analysis_data
        
        # 3. 中医诊断
        tcm_request = {
            "file_path": uploaded_file_path,
            "user_id": "test_user",
            "constitution_type": "平和质",
            "symptoms": ["咳嗽"],
            "context": {"age": 30, "gender": "male"}
        }
        
        tcm_response = client.post(
            "/api/v1/tcm/diagnose",
            json=tcm_request,
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert tcm_response.status_code == 200
        tcm_data = tcm_response.json()
        assert "diagnosis_result" in tcm_data
        assert "recommendations" in tcm_data

    def test_cache_functionality(self, client: TestClient, sample_request_data: dict):
        """测试缓存功能"""
        # 第一次请求
        response1 = client.post(
            "/api/v1/audio/analyze",
            json=sample_request_data,
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response1.status_code == 200
        
        # 第二次相同请求（应该使用缓存）
        response2 = client.post(
            "/api/v1/audio/analyze",
            json=sample_request_data,
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response2.status_code == 200
        
        # 验证结果一致
        data1 = response1.json()
        data2 = response2.json()
        assert data1["audio_features"] == data2["audio_features"] 