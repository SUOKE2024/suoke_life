"""
EdgeAIInference.test - 索克生活项目模块
"""

from pathlib import Path
import pytest
import sys

# 添加项目路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

# 导入EdgeAI推理模块
from core.ai.EdgeAIInference import (
    EdgeAIInference,
    create_model_config,
    create_inference_request,
    ModelType,
    DeviceType
)

class TestEdgeAIInference:
    """边缘AI推理框架测试"""
    
    @pytest.mark.asyncio
    async def test_framework_initialization(self):
        """测试框架初始化"""
        framework = EdgeAIInference()
        await framework.initialize()
        assert framework.is_initialized is True
        assert len(framework.device_info) > 0
        
    @pytest.mark.asyncio
    async def test_model_loading(self):
        """测试模型加载"""
        framework = EdgeAIInference()
        await framework.initialize()
        
        # 创建模型配置
        config = create_model_config(
            model_id="test_model",
            model_path="/path/to/model.onnx",
            model_type="onnx",
            device_type="cpu"
        )
        
        # 加载模型
        await framework.load_model(config)
        assert "test_model" in framework.loaded_models
        
    @pytest.mark.asyncio
    async def test_inference_execution(self):
        """测试推理执行"""
        framework = EdgeAIInference()
        await framework.initialize()
        
        # 加载模型
        config = create_model_config(
            model_id="test_model",
            model_path="/path/to/model.onnx"
        )
        await framework.load_model(config)
        
        # 创建推理请求
        request = create_inference_request(
            request_id="test_request",
            model_id="test_model",
            input_data={"image": "test_data"}
        )
        
        # 执行推理
        result = await framework.inference(request)
        assert result.request_id == "test_request"
        assert result.model_id == "test_model"
        assert result.confidence > 0
        
    @pytest.mark.asyncio
    async def test_batch_inference(self):
        """测试批量推理"""
        framework = EdgeAIInference()
        await framework.initialize()
        
        # 加载模型
        config = create_model_config(
            model_id="test_model",
            model_path="/path/to/model.onnx"
        )
        await framework.load_model(config)
        
        # 创建多个推理请求
        requests = [
            create_inference_request(
                request_id=f"test_request_{i}",
                model_id="test_model",
                input_data={"image": f"test_data_{i}"}
            )
            for i in range(3)
        ]
        
        # 执行批量推理
        results = []
        for request in requests:
            result = await framework.inference(request)
            results.append(result)
        
        assert len(results) == 3
        for i, result in enumerate(results):
            assert result.request_id == f"test_request_{i}"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
