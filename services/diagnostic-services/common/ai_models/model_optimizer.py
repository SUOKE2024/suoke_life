"""
AI模型优化器 - 提升五诊服务模型精度
支持模型训练、调优、压缩和部署优化
"""

import asyncio
import logging
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib
import json
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
import time
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ModelConfig:
    """模型配置"""
    model_name: str
    model_type: str  # 'classification', 'regression', 'multimodal'
    input_shape: Tuple[int, ...]
    num_classes: int
    learning_rate: float = 0.001
    batch_size: int = 32
    epochs: int = 100
    early_stopping_patience: int = 10
    dropout_rate: float = 0.3
    l2_regularization: float = 0.01

@dataclass
class OptimizationResult:
    """优化结果"""
    model_name: str
    original_accuracy: float
    optimized_accuracy: float
    improvement: float
    training_time: float
    model_size_mb: float
    inference_time_ms: float

class TCMDataset(Dataset):
    """中医数据集"""
    
    def __init__(self, features: np.ndarray, labels: np.ndarray, transform=None):
        self.features = torch.FloatTensor(features)
        self.labels = torch.LongTensor(labels)
        self.transform = transform
    
    def __len__(self):
        return len(self.features)
    
    def __getitem__(self, idx):
        feature = self.features[idx]
        label = self.labels[idx]
        
        if self.transform:
            feature = self.transform(feature)
        
        return feature, label

class EnhancedTCMModel(nn.Module):
    """增强的中医诊断模型"""
    
    def __init__(self, config: ModelConfig):
        super().__init__()
        self.config = config
        
        # 特征提取层
        self.feature_extractor = nn.Sequential(
            nn.Linear(config.input_shape[0], 512),
            nn.BatchNorm1d(512),
            nn.ReLU(),
            nn.Dropout(config.dropout_rate),
            
            nn.Linear(512, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Dropout(config.dropout_rate),
            
            nn.Linear(256, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(config.dropout_rate)
        )
        
        # 注意力机制
        self.attention = nn.MultiheadAttention(
            embed_dim=128,
            num_heads=8,
            dropout=config.dropout_rate
        )
        
        # 分类器
        self.classifier = nn.Sequential(
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(config.dropout_rate),
            nn.Linear(64, config.num_classes)
        )
        
        # 权重初始化
        self._initialize_weights()
    
    def _initialize_weights(self):
        """权重初始化"""
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.BatchNorm1d):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)
    
    def forward(self, x):
        # 特征提取
        features = self.feature_extractor(x)
        
        # 注意力机制 (需要调整维度)
        features_reshaped = features.unsqueeze(0)  # (1, batch_size, 128)
        attended_features, _ = self.attention(
            features_reshaped, features_reshaped, features_reshaped
        )
        attended_features = attended_features.squeeze(0)  # (batch_size, 128)
        
        # 分类
        output = self.classifier(attended_features)
        return output

class ModelOptimizer:
    """模型优化器"""
    
    def __init__(self, base_path: str = "models"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"使用设备: {self.device}")
    
    async def optimize_model(
        self,
        config: ModelConfig,
        train_data: Tuple[np.ndarray, np.ndarray],
        val_data: Tuple[np.ndarray, np.ndarray],
        test_data: Tuple[np.ndarray, np.ndarray]
    ) -> OptimizationResult:
        """优化模型"""
        logger.info(f"开始优化模型: {config.model_name}")
        start_time = time.time()
        
        # 创建数据集
        train_dataset = TCMDataset(train_data[0], train_data[1])
        val_dataset = TCMDataset(val_data[0], val_data[1])
        test_dataset = TCMDataset(test_data[0], test_data[1])
        
        train_loader = DataLoader(train_dataset, batch_size=config.batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=config.batch_size, shuffle=False)
        test_loader = DataLoader(test_dataset, batch_size=config.batch_size, shuffle=False)
        
        # 创建模型
        model = EnhancedTCMModel(config).to(self.device)
        
        # 损失函数和优化器
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.AdamW(
            model.parameters(),
            lr=config.learning_rate,
            weight_decay=config.l2_regularization
        )
        
        # 学习率调度器
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(
            optimizer, mode='min', factor=0.5, patience=5, verbose=True
        )
        
        # 训练模型
        best_val_loss = float('inf')
        patience_counter = 0
        train_losses = []
        val_losses = []
        
        for epoch in range(config.epochs):
            # 训练阶段
            model.train()
            train_loss = 0.0
            for batch_features, batch_labels in train_loader:
                batch_features = batch_features.to(self.device)
                batch_labels = batch_labels.to(self.device)
                
                optimizer.zero_grad()
                outputs = model(batch_features)
                loss = criterion(outputs, batch_labels)
                loss.backward()
                
                # 梯度裁剪
                torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
                
                optimizer.step()
                train_loss += loss.item()
            
            # 验证阶段
            model.eval()
            val_loss = 0.0
            with torch.no_grad():
                for batch_features, batch_labels in val_loader:
                    batch_features = batch_features.to(self.device)
                    batch_labels = batch_labels.to(self.device)
                    
                    outputs = model(batch_features)
                    loss = criterion(outputs, batch_labels)
                    val_loss += loss.item()
            
            train_loss /= len(train_loader)
            val_loss /= len(val_loader)
            
            train_losses.append(train_loss)
            val_losses.append(val_loss)
            
            # 学习率调度
            scheduler.step(val_loss)
            
            # 早停检查
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
                # 保存最佳模型
                torch.save(model.state_dict(), self.base_path / f"{config.model_name}_best.pth")
            else:
                patience_counter += 1
                if patience_counter >= config.early_stopping_patience:
                    logger.info(f"早停触发，epoch: {epoch}")
                    break
            
            if epoch % 10 == 0:
                logger.info(f"Epoch {epoch}: train_loss={train_loss:.4f}, val_loss={val_loss:.4f}")
        
        # 加载最佳模型
        model.load_state_dict(torch.load(self.base_path / f"{config.model_name}_best.pth"))
        
        # 测试模型
        test_accuracy = await self._evaluate_model(model, test_loader)
        
        # 计算模型大小
        model_size = self._get_model_size(model)
        
        # 测试推理时间
        inference_time = await self._measure_inference_time(model, test_data[0][:100])
        
        training_time = time.time() - start_time
        
        # 保存优化后的模型
        await self._save_optimized_model(model, config)
        
        result = OptimizationResult(
            model_name=config.model_name,
            original_accuracy=0.75,  # 假设原始精度
            optimized_accuracy=test_accuracy,
            improvement=test_accuracy - 0.75,
            training_time=training_time,
            model_size_mb=model_size,
            inference_time_ms=inference_time
        )
        
        logger.info(f"模型优化完成: {config.model_name}, 精度提升: {result.improvement:.3f}")
        return result
    
    async def _evaluate_model(self, model: nn.Module, test_loader: DataLoader) -> float:
        """评估模型"""
        model.eval()
        correct = 0
        total = 0
        
        with torch.no_grad():
            for batch_features, batch_labels in test_loader:
                batch_features = batch_features.to(self.device)
                batch_labels = batch_labels.to(self.device)
                
                outputs = model(batch_features)
                _, predicted = torch.max(outputs.data, 1)
                total += batch_labels.size(0)
                correct += (predicted == batch_labels).sum().item()
        
        accuracy = correct / total
        return accuracy
    
    def _get_model_size(self, model: nn.Module) -> float:
        """获取模型大小(MB)"""
        param_size = 0
        for param in model.parameters():
            param_size += param.nelement() * param.element_size()
        
        buffer_size = 0
        for buffer in model.buffers():
            buffer_size += buffer.nelement() * buffer.element_size()
        
        size_mb = (param_size + buffer_size) / 1024 / 1024
        return size_mb
    
    async def _measure_inference_time(self, model: nn.Module, sample_data: np.ndarray) -> float:
        """测量推理时间(ms)"""
        model.eval()
        sample_tensor = torch.FloatTensor(sample_data).to(self.device)
        
        # 预热
        with torch.no_grad():
            for _ in range(10):
                _ = model(sample_tensor)
        
        # 测量时间
        start_time = time.time()
        with torch.no_grad():
            for _ in range(100):
                _ = model(sample_tensor)
        
        avg_time_ms = (time.time() - start_time) * 1000 / 100
        return avg_time_ms
    
    async def _save_optimized_model(self, model: nn.Module, config: ModelConfig):
        """保存优化后的模型"""
        model_path = self.base_path / f"{config.model_name}_optimized.pth"
        torch.save({
            'model_state_dict': model.state_dict(),
            'config': config,
            'timestamp': datetime.now().isoformat()
        }, model_path)
        
        # 保存ONNX格式用于部署
        try:
            dummy_input = torch.randn(1, config.input_shape[0]).to(self.device)
            onnx_path = self.base_path / f"{config.model_name}_optimized.onnx"
            torch.onnx.export(
                model, dummy_input, onnx_path,
                export_params=True,
                opset_version=11,
                do_constant_folding=True,
                input_names=['input'],
                output_names=['output']
            )
            logger.info(f"ONNX模型已保存: {onnx_path}")
        except Exception as e:
            logger.warning(f"ONNX导出失败: {e}")

class DataAugmentator:
    """数据增强器"""
    
    @staticmethod
    def augment_audio_features(features: np.ndarray, noise_factor: float = 0.01) -> np.ndarray:
        """音频特征增强"""
        # 添加噪声
        noise = np.random.normal(0, noise_factor, features.shape)
        augmented = features + noise
        
        # 时间拉伸模拟
        stretch_factor = np.random.uniform(0.9, 1.1)
        if stretch_factor != 1.0:
            indices = np.linspace(0, len(features) - 1, int(len(features) * stretch_factor))
            augmented = np.interp(np.arange(len(features)), indices, augmented[indices.astype(int)])
        
        return augmented
    
    @staticmethod
    def augment_image_features(features: np.ndarray, rotation_range: float = 10) -> np.ndarray:
        """图像特征增强"""
        # 模拟旋转和缩放
        rotation = np.random.uniform(-rotation_range, rotation_range)
        scale = np.random.uniform(0.9, 1.1)
        
        # 简单的特征变换
        augmented = features * scale
        augmented = np.roll(augmented, int(rotation))
        
        return augmented
    
    @staticmethod
    def augment_sensor_data(data: np.ndarray, jitter_std: float = 0.01) -> np.ndarray:
        """传感器数据增强"""
        # 添加抖动
        jitter = np.random.normal(0, jitter_std, data.shape)
        augmented = data + jitter
        
        # 模拟传感器漂移
        drift = np.random.uniform(-0.05, 0.05)
        augmented = augmented + drift
        
        return augmented

class ModelEnsemble:
    """模型集成"""
    
    def __init__(self, models: List[nn.Module], weights: Optional[List[float]] = None):
        self.models = models
        self.weights = weights or [1.0 / len(models)] * len(models)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    def predict(self, x: torch.Tensor) -> torch.Tensor:
        """集成预测"""
        predictions = []
        
        for model, weight in zip(self.models, self.weights):
            model.eval()
            with torch.no_grad():
                pred = model(x)
                predictions.append(pred * weight)
        
        # 加权平均
        ensemble_pred = torch.stack(predictions).sum(dim=0)
        return ensemble_pred

async def optimize_all_models():
    """优化所有诊断模型"""
    optimizer = ModelOptimizer()
    
    # 模型配置
    configs = [
        ModelConfig(
            model_name="listen_service_voice_analysis",
            model_type="classification",
            input_shape=(128,),  # MFCC特征
            num_classes=10,  # 声音类型
            learning_rate=0.001,
            batch_size=32,
            epochs=100
        ),
        ModelConfig(
            model_name="look_service_face_analysis",
            model_type="classification",
            input_shape=(512,),  # 面部特征
            num_classes=9,   # 体质类型
            learning_rate=0.0005,
            batch_size=16,
            epochs=150
        ),
        ModelConfig(
            model_name="inquiry_service_symptom_extraction",
            model_type="classification",
            input_shape=(256,),  # 文本特征
            num_classes=20,  # 症状类型
            learning_rate=0.002,
            batch_size=64,
            epochs=80
        ),
        ModelConfig(
            model_name="palpation_service_pulse_analysis",
            model_type="classification",
            input_shape=(64,),   # 脉象特征
            num_classes=28,  # 脉象类型
            learning_rate=0.001,
            batch_size=32,
            epochs=120
        )
    ]
    
    results = []
    
    for config in configs:
        # 生成模拟数据
        train_data = (
            np.random.randn(1000, config.input_shape[0]),
            np.random.randint(0, config.num_classes, 1000)
        )
        val_data = (
            np.random.randn(200, config.input_shape[0]),
            np.random.randint(0, config.num_classes, 200)
        )
        test_data = (
            np.random.randn(200, config.input_shape[0]),
            np.random.randint(0, config.num_classes, 200)
        )
        
        try:
            result = await optimizer.optimize_model(config, train_data, val_data, test_data)
            results.append(result)
        except Exception as e:
            logger.error(f"优化模型 {config.model_name} 失败: {e}")
    
    return results

if __name__ == "__main__":
    # 运行模型优化
    results = asyncio.run(optimize_all_models())
    
    # 输出结果
    print("\n=== 模型优化结果 ===")
    total_improvement = 0
    for result in results:
        print(f"模型: {result.model_name}")
        print(f"  原始精度: {result.original_accuracy:.3f}")
        print(f"  优化精度: {result.optimized_accuracy:.3f}")
        print(f"  精度提升: {result.improvement:.3f}")
        print(f"  训练时间: {result.training_time:.1f}s")
        print(f"  模型大小: {result.model_size_mb:.1f}MB")
        print(f"  推理时间: {result.inference_time_ms:.1f}ms")
        print()
        total_improvement += result.improvement
    
    print(f"总体精度提升: {total_improvement:.3f}")
    print("模型优化完成！") 