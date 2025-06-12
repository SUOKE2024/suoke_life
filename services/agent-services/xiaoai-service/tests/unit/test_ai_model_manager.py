"""
AI模型管理器单元测试
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timezone

from xiaoai.core.ai_model_manager import (
    AIModelManager,
    ModelInstance,
    ModelConfig,
    ModelType,
    ModelStatus,
    ModelError,
    ModelNotFoundError
)


class TestModelInstance:
    """模型实例测试类"""
    
    @pytest.fixture
    def model_config(self):
        """创建模型配置"""
        return ModelConfig(
            name="test_model",
            model_type=ModelType.TRANSFORMER,
            model_path="bert-base-chinese",
            task="classification",
            device="cpu",
            max_length=128,
            batch_size=4
        )
    
    @pytest.fixture
    def model_instance(self, model_config):
        """创建模型实例"""
        return ModelInstance(model_config)
    
    def test_model_instance_initialization(self, model_instance, model_config):
        """测试模型实例初始化"""
        assert model_instance.config==model_config
        assert model_instance.status==ModelStatus.UNLOADED
        assert model_instance.model is None
        assert model_instance.tokenizer is None
        assert model_instance.metrics.model_name=="test_model"
        assert model_instance.metrics.total_calls==0
    
    @pytest.mark.asyncio
    async def test_load_transformer_model(self, model_instance):
        """测试加载Transformer模型"""
        with patch('xiaoai.core.ai_model_manager.AutoTokenizer') as mock_tokenizer, \
             patch('xiaoai.core.ai_model_manager.AutoModelForSequenceClassification') as mock_model:
            
            mock_tokenizer.from_pretrained.return_value = Mock()
            mock_model.from_pretrained.return_value = Mock()
            
            await model_instance.load()
            
            assert model_instance.status==ModelStatus.LOADED
            assert model_instance.model is not None
            assert model_instance.tokenizer is not None
            assert model_instance.load_time is not None
            assert model_instance.last_used is not None
    
    @pytest.mark.asyncio
    async def test_load_model_error(self, model_instance):
        """测试模型加载错误"""
        with patch('xiaoai.core.ai_model_manager.AutoTokenizer') as mock_tokenizer:
            mock_tokenizer.from_pretrained.side_effect = Exception("模型文件不存在")
            
            with pytest.raises(ModelError):
                await model_instance.load()
            
            assert model_instance.status==ModelStatus.ERROR
    
    @pytest.mark.asyncio
    async def test_predict_transformer(self, model_instance):
        """测试Transformer模型预测"""
        # 模拟加载成功
        with patch('xiaoai.core.ai_model_manager.AutoTokenizer') as mock_tokenizer, \
             patch('xiaoai.core.ai_model_manager.AutoModelForSequenceClassification') as mock_model:
            
            # 设置模拟对象
            mock_tokenizer_instance = Mock()
            mock_model_instance = Mock()
            
            mock_tokenizer.from_pretrained.return_value = mock_tokenizer_instance
            mock_model.from_pretrained.return_value = mock_model_instance
            
            # 模拟分词结果
            mock_tokenizer_instance.return_value = {
                'input_ids': Mock(),
                'attention_mask': Mock()
            }
            
            # 模拟模型输出
            mock_output = Mock()
            mock_output.logits = Mock()
            mock_model_instance.return_value = mock_output
            
            await model_instance.load()
            
            # 测试预测
            result = await model_instance.predict("测试文本")
            
            assert result is not None
            assert model_instance.metrics.total_calls==1
            assert model_instance.metrics.total_time_ms > 0
    
    @pytest.mark.asyncio
    async def test_predict_without_load(self, model_instance):
        """测试未加载模型时的预测"""
        with patch.object(model_instance, 'load') as mock_load:
            mock_load.return_value = None
            model_instance.status = ModelStatus.LOADED
            model_instance.model = Mock()
            model_instance.tokenizer = Mock()
            
            # 模拟预测方法
            with patch.object(model_instance, '_predict_internal') as mock_predict:
                mock_predict.return_value = "预测结果"
                
                result = await model_instance.predict("测试输入")
                
                mock_load.assert_called_once()
                assert result=="预测结果"
    
    def test_unload_model(self, model_instance):
        """测试卸载模型"""
        # 模拟已加载的模型
        model_instance.model = Mock()
        model_instance.tokenizer = Mock()
        model_instance.status = ModelStatus.LOADED
        
        with patch('torch.cuda.is_available', return_value=False):
            model_instance.unload()
            
            assert model_instance.status==ModelStatus.UNLOADED
            assert model_instance.model is None
            assert model_instance.tokenizer is None
    
    def test_get_memory_usage(self, model_instance):
        """测试获取内存使用量"""
        # 测试未加载模型
        assert model_instance.get_memory_usage()==0.0
        
        # 测试已加载模型
        mock_model = Mock()
        mock_model.get_memory_footprint.return_value = 1024 * 1024 * 100  # 100MB
        model_instance.model = mock_model
        
        memory_usage = model_instance.get_memory_usage()
        assert memory_usage==100.0
    
    def test_update_metrics(self, model_instance):
        """测试更新性能指标"""
        # 测试成功调用
        model_instance._update_metrics(100, success=True)
        
        assert model_instance.metrics.total_calls==1
        assert model_instance.metrics.total_time_ms==100
        assert model_instance.metrics.avg_time_ms==100.0
        assert model_instance.metrics.error_count==0
        
        # 测试失败调用
        model_instance._update_metrics(0, success=False)
        
        assert model_instance.metrics.total_calls==2
        assert model_instance.metrics.error_count==1


class TestAIModelManager:
    """AI模型管理器测试类"""
    
    @pytest.fixture
    async def model_manager(self):
        """创建模型管理器实例"""
        manager = AIModelManager()
        
        # 模拟初始化过程
        with patch.object(manager, '_load_model_configs') as mock_load_configs, \
             patch('asyncio.create_task') as mock_create_task:
            
            mock_load_configs.return_value = None
            mock_create_task.return_value = Mock()
            
            await manager.initialize()
            
        yield manager
        
        # 清理
        if manager.auto_unload_task:
            manager.auto_unload_task.cancel()
    
    @pytest.mark.asyncio
    async def test_model_manager_initialization(self, model_manager):
        """测试模型管理器初始化"""
        assert model_manager.models is not None
        assert model_manager.cache_manager is not None
        assert model_manager.executor is not None
    
    @pytest.mark.asyncio
    async def test_load_model_configs(self, model_manager):
        """测试加载模型配置"""
        await model_manager._load_model_configs()
        
        # 检查是否加载了预定义的模型
        expected_models = [
            "tcm_syndrome_classifier",
            "constitution_analyzer", 
            "symptom_extractor"
        ]
        
        for model_name in expected_models:
            assert model_name in model_manager.models
            assert isinstance(model_manager.models[model_name], ModelInstance)
    
    @pytest.mark.asyncio
    async def test_get_model_success(self, model_manager):
        """测试成功获取模型"""
        # 添加测试模型
        test_config = ModelConfig(
            name="test_model",
            model_type=ModelType.TRANSFORMER,
            model_path="test_path",
            task="test_task"
        )
        test_instance = ModelInstance(test_config)
        test_instance.status = ModelStatus.LOADED
        model_manager.models["test_model"] = test_instance
        
        result = await model_manager.get_model("test_model")
        
        assert result==test_instance
    
    @pytest.mark.asyncio
    async def test_get_model_not_found(self, model_manager):
        """测试获取不存在的模型"""
        with pytest.raises(ModelNotFoundError):
            await model_manager.get_model("nonexistent_model")
    
    @pytest.mark.asyncio
    async def test_get_model_auto_load(self, model_manager):
        """测试自动加载模型"""
        # 创建未加载的模型实例
        test_config = ModelConfig(
            name="test_model",
            model_type=ModelType.TRANSFORMER,
            model_path="test_path",
            task="test_task"
        )
        test_instance = ModelInstance(test_config)
        test_instance.status = ModelStatus.UNLOADED
        
        with patch.object(test_instance, 'load') as mock_load:
            mock_load.return_value = None
            test_instance.status = ModelStatus.LOADED
            
            model_manager.models["test_model"] = test_instance
            
            result = await model_manager.get_model("test_model")
            
            mock_load.assert_called_once()
            assert result==test_instance
    
    @pytest.mark.asyncio
    async def test_predict_with_cache(self, model_manager):
        """测试带缓存的预测"""
        # 模拟缓存管理器
        mock_cache_manager = AsyncMock()
        mock_cache_manager.get.return_value = "cached_result"
        model_manager.cache_manager = mock_cache_manager
        
        result = await model_manager.predict("test_model", "test_input", use_cache=True)
        
        assert result=="cached_result"
        mock_cache_manager.get.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_predict_without_cache(self, model_manager):
        """测试不使用缓存的预测"""
        # 创建模拟模型实例
        mock_instance = AsyncMock()
        mock_instance.predict.return_value = "prediction_result"
        
        with patch.object(model_manager, 'get_model') as mock_get_model:
            mock_get_model.return_value = mock_instance
            
            result = await model_manager.predict("test_model", "test_input", use_cache=False)
            
            assert result=="prediction_result"
            mock_instance.predict.assert_called_once_with("test_input")
    
    @pytest.mark.asyncio
    async def test_batch_predict(self, model_manager):
        """测试批量预测"""
        # 创建模拟模型实例
        mock_instance = AsyncMock()
        mock_instance.config.batch_size = 2
        mock_instance.predict.side_effect = [
            ["result1", "result2"],
            ["result3"]
        ]
        
        with patch.object(model_manager, 'get_model') as mock_get_model:
            mock_get_model.return_value = mock_instance
            
            inputs = ["input1", "input2", "input3"]
            results = await model_manager.batch_predict("test_model", inputs)
            
            assert results==["result1", "result2", "result3"]
            assert mock_instance.predict.call_count==2
    
    @pytest.mark.asyncio
    async def test_preload_models(self, model_manager):
        """测试预加载模型"""
        # 创建模拟模型实例
        mock_instance1 = AsyncMock()
        mock_instance2 = AsyncMock()
        
        model_manager.models = {
            "model1": mock_instance1,
            "model2": mock_instance2,
            "model3": AsyncMock()  # 不在预加载列表中
        }
        
        await model_manager.preload_models(["model1", "model2"])
        
        mock_instance1.load.assert_called_once()
        mock_instance2.load.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_unload_model(self, model_manager):
        """测试卸载单个模型"""
        mock_instance = Mock()
        model_manager.models["test_model"] = mock_instance
        
        await model_manager.unload_model("test_model")
        
        mock_instance.unload.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_unload_all_models(self, model_manager):
        """测试卸载所有模型"""
        mock_instance1 = Mock()
        mock_instance2 = Mock()
        
        model_manager.models = {
            "model1": mock_instance1,
            "model2": mock_instance2
        }
        
        await model_manager.unload_all_models()
        
        mock_instance1.unload.assert_called_once()
        mock_instance2.unload.assert_called_once()
    
    def test_generate_cache_key(self, model_manager):
        """测试生成缓存键"""
        key1 = model_manager._generate_cache_key("model1", "input1", {"param": "value"})
        key2 = model_manager._generate_cache_key("model1", "input1", {"param": "value"})
        key3 = model_manager._generate_cache_key("model1", "input2", {"param": "value"})
        
        # 相同输入应该生成相同的键
        assert key1==key2
        
        # 不同输入应该生成不同的键
        assert key1!=key3
        
        # 键应该是32位的十六进制字符串
        assert len(key1)==32
        assert all(c in "0123456789abcdef" for c in key1)
    
    def test_get_model_metrics(self, model_manager):
        """测试获取模型指标"""
        mock_instance = Mock()
        mock_metrics = Mock()
        mock_instance.metrics = mock_metrics
        
        model_manager.models["test_model"] = mock_instance
        
        result = model_manager.get_model_metrics("test_model")
        assert result==mock_metrics
        
        # 测试不存在的模型
        result = model_manager.get_model_metrics("nonexistent")
        assert result is None
    
    def test_get_all_metrics(self, model_manager):
        """测试获取所有模型指标"""
        mock_instance1 = Mock()
        mock_instance2 = Mock()
        mock_metrics1 = Mock()
        mock_metrics2 = Mock()
        
        mock_instance1.metrics = mock_metrics1
        mock_instance2.metrics = mock_metrics2
        
        model_manager.models = {
            "model1": mock_instance1,
            "model2": mock_instance2
        }
        
        result = model_manager.get_all_metrics()
        
        assert result=={
            "model1": mock_metrics1,
            "model2": mock_metrics2
        }
    
    @pytest.mark.asyncio
    async def test_health_check(self, model_manager):
        """测试健康检查"""
        # 创建模拟模型实例
        mock_instance1 = Mock()
        mock_instance1.status = ModelStatus.LOADED
        mock_instance1.get_memory_usage.return_value = 100.0
        mock_instance1.metrics.total_calls = 10
        mock_instance1.metrics.avg_time_ms = 50.0
        mock_instance1.metrics.error_count = 0
        
        mock_instance2 = Mock()
        mock_instance2.status = ModelStatus.UNLOADED
        mock_instance2.get_memory_usage.return_value = 0.0
        mock_instance2.metrics.total_calls = 0
        mock_instance2.metrics.avg_time_ms = 0.0
        mock_instance2.metrics.error_count = 0
        
        model_manager.models = {
            "model1": mock_instance1,
            "model2": mock_instance2
        }
        
        health_status = await model_manager.health_check()
        
        assert health_status["total_models"]==2
        assert health_status["loaded_models"]==1
        assert health_status["total_memory_mb"]==100.0
        assert "model1" in health_status["models"]
        assert "model2" in health_status["models"]
        
        # 检查模型状态
        assert health_status["models"]["model1"]["status"]=="loaded"
        assert health_status["models"]["model2"]["status"]=="unloaded"
    
    @pytest.mark.asyncio
    async def test_close(self, model_manager):
        """测试关闭模型管理器"""
        # 模拟自动卸载任务
        mock_task = Mock()
        model_manager.auto_unload_task = mock_task
        
        # 模拟模型实例
        mock_instance = Mock()
        model_manager.models["test_model"] = mock_instance
        
        with patch.object(model_manager, 'unload_all_models') as mock_unload_all:
            mock_unload_all.return_value = None
            
            await model_manager.close()
            
            mock_task.cancel.assert_called_once()
            mock_unload_all.assert_called_once()


@pytest.mark.asyncio
async def test_get_model_manager_singleton():
    """测试全局模型管理器单例"""
    with patch('xiaoai.core.ai_model_manager.AIModelManager') as mock_manager_class:
        mock_manager = AsyncMock()
        mock_manager_class.return_value = mock_manager
        
        # 重置全局变量
        import xiaoai.core.ai_model_manager
        xiaoai.core.ai_model_manager._model_manager = None
        
        # 第一次调用应该创建新实例
        from xiaoai.core.ai_model_manager import get_model_manager
        manager1 = await get_model_manager()
        
        # 第二次调用应该返回相同实例
        manager2 = await get_model_manager()
        
        assert manager1==manager2
        mock_manager.initialize.assert_called_once()


@pytest.mark.asyncio
async def test_predict_convenience_function():
    """测试便捷预测函数"""
    with patch('xiaoai.core.ai_model_manager.get_model_manager') as mock_get_manager:
        mock_manager = AsyncMock()
        mock_manager.predict.return_value = "prediction_result"
        mock_get_manager.return_value = mock_manager
        
        from xiaoai.core.ai_model_manager import predict
        result = await predict("test_model", "test_input", param="value")
        
        assert result=="prediction_result"
        mock_manager.predict.assert_called_once_with("test_model", "test_input", param="value")


@pytest.mark.asyncio
async def test_batch_predict_convenience_function():
    """测试便捷批量预测函数"""
    with patch('xiaoai.core.ai_model_manager.get_model_manager') as mock_get_manager:
        mock_manager = AsyncMock()
        mock_manager.batch_predict.return_value = ["result1", "result2"]
        mock_get_manager.return_value = mock_manager
        
        from xiaoai.core.ai_model_manager import batch_predict
        result = await batch_predict("test_model", ["input1", "input2"])
        
        assert result==["result1", "result2"]
        mock_manager.batch_predict.assert_called_once_with("test_model", ["input1", "input2"])


class TestModelConfig:
    """模型配置测试类"""
    
    def test_model_config_creation(self):
        """测试模型配置创建"""
        config = ModelConfig(
            name="test_model",
            model_type=ModelType.TRANSFORMER,
            model_path="/path/to/model",
            task="classification"
        )
        
        assert config.name=="test_model"
        assert config.model_type==ModelType.TRANSFORMER
        assert config.model_path=="/path/to/model"
        assert config.task=="classification"
        assert config.device=="cpu"  # 默认值
        assert config.max_length==512  # 默认值
        assert config.batch_size==1  # 默认值
    
    def test_model_config_with_custom_values(self):
        """测试自定义值的模型配置"""
        config = ModelConfig(
            name="custom_model",
            model_type=ModelType.ONNX,
            model_path="/custom/path",
            task="embedding",
            device="cuda",
            max_length=256,
            batch_size=8,
            cache_size=2000,
            warmup_samples=10
        )
        
        assert config.device=="cuda"
        assert config.max_length==256
        assert config.batch_size==8
        assert config.cache_size==2000
        assert config.warmup_samples==10