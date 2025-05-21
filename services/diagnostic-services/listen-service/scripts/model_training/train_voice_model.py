#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
语音特征分析模型训练脚本
"""
import os
import sys
import argparse
import logging
import json
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import matplotlib.pyplot as plt
import librosa
import soundfile as sf
import yaml
from tqdm import tqdm

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 添加项目根目录到Python路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)
from internal.audio.voice_feature_extractor import VoiceFeatureExtractor

class VoiceFeatureDataset(Dataset):
    """语音特征数据集"""
    
    def __init__(self, audio_files, labels, feature_extractor, transform=None):
        """
        初始化数据集
        
        Args:
            audio_files: 音频文件路径列表
            labels: 对应的标签列表
            feature_extractor: 特征提取器
            transform: 数据增强转换
        """
        self.audio_files = audio_files
        self.labels = labels
        self.feature_extractor = feature_extractor
        self.transform = transform
        
        # 缓存特征，避免重复计算
        self.features_cache = {}
    
    def __len__(self):
        return len(self.audio_files)
    
    def __getitem__(self, idx):
        audio_file = self.audio_files[idx]
        label = self.labels[idx]
        
        # 尝试从缓存获取特征
        if audio_file in self.features_cache:
            features = self.features_cache[audio_file]
        else:
            # 加载音频
            audio, sr = librosa.load(audio_file, sr=16000, mono=True)
            
            # 提取特征
            features = self.feature_extractor.extract_features(audio, sr)
            
            # 转换特征格式
            features_vector = []
            for feature_name, value in features.items():
                if isinstance(value, (int, float)):
                    features_vector.append(value)
                elif isinstance(value, (list, np.ndarray)) and len(value) > 0:
                    # 如果是数组，取平均值、最大值、最小值等统计特征
                    value_array = np.array(value)
                    features_vector.extend([
                        np.mean(value_array),
                        np.std(value_array),
                        np.max(value_array),
                        np.min(value_array)
                    ])
            
            features = np.array(features_vector, dtype=np.float32)
            
            # 应用数据增强
            if self.transform:
                features = self.transform(features)
            
            # 存入缓存
            self.features_cache[audio_file] = features
        
        return features, label

class VoiceAnalysisModel(nn.Module):
    """语音分析模型"""
    
    def __init__(self, input_dim, hidden_dims, output_dim, dropout_rate=0.3):
        """
        初始化模型
        
        Args:
            input_dim: 输入特征维度
            hidden_dims: 隐藏层维度列表
            output_dim: 输出维度
            dropout_rate: Dropout率
        """
        super(VoiceAnalysisModel, self).__init__()
        
        layers = []
        prev_dim = input_dim
        
        # 构建隐藏层
        for hidden_dim in hidden_dims:
            layers.append(nn.Linear(prev_dim, hidden_dim))
            layers.append(nn.BatchNorm1d(hidden_dim))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(dropout_rate))
            prev_dim = hidden_dim
        
        # 输出层
        layers.append(nn.Linear(prev_dim, output_dim))
        
        self.model = nn.Sequential(*layers)
    
    def forward(self, x):
        """前向传播"""
        return self.model(x)

def train_model(args):
    """
    训练模型
    
    Args:
        args: 命令行参数
    """
    # 加载配置
    with open(args.config, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 初始化特征提取器
    feature_extractor = VoiceFeatureExtractor()
    
    # 加载数据集
    logger.info(f"加载数据集: {args.data_dir}")
    data = []
    
    # 遍历数据目录下的每个子目录（每个类别一个子目录）
    for label_dir in os.listdir(args.data_dir):
        label_path = os.path.join(args.data_dir, label_dir)
        if not os.path.isdir(label_path):
            continue
        
        # 获取标签序号
        try:
            label = int(label_dir.split('_')[0])
        except ValueError:
            logger.warning(f"跳过无效标签目录: {label_dir}")
            continue
        
        # 遍历该类别下的所有音频文件
        for audio_file in os.listdir(label_path):
            if not audio_file.endswith(('.wav', '.mp3', '.flac')):
                continue
            
            data.append({
                'file_path': os.path.join(label_path, audio_file),
                'label': label
            })
    
    # 检查数据集大小
    if len(data) == 0:
        logger.error("数据集为空，请检查数据路径")
        return
    
    # 转换为DataFrame
    df = pd.DataFrame(data)
    
    # 拆分训练集和测试集
    train_df, test_df = train_test_split(
        df, test_size=args.test_size, random_state=42, stratify=df['label']
    )
    
    logger.info(f"训练集大小: {len(train_df)}, 测试集大小: {len(test_df)}")
    
    # 创建数据集
    train_dataset = VoiceFeatureDataset(
        train_df['file_path'].tolist(),
        train_df['label'].tolist(),
        feature_extractor
    )
    
    test_dataset = VoiceFeatureDataset(
        test_df['file_path'].tolist(),
        test_df['label'].tolist(),
        feature_extractor
    )
    
    # 检查特征维度
    sample_features, _ = train_dataset[0]
    input_dim = len(sample_features)
    logger.info(f"特征维度: {input_dim}")
    
    # 创建数据加载器
    train_loader = DataLoader(
        train_dataset,
        batch_size=args.batch_size,
        shuffle=True,
        num_workers=args.num_workers
    )
    
    test_loader = DataLoader(
        test_dataset,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=args.num_workers
    )
    
    # 计算类别数
    num_classes = len(df['label'].unique())
    
    # 创建模型
    model = VoiceAnalysisModel(
        input_dim=input_dim,
        hidden_dims=args.hidden_dims,
        output_dim=num_classes
    )
    
    # 如果指定了GPU，则使用GPU
    device = torch.device(args.device if torch.cuda.is_available() else "cpu")
    model = model.to(device)
    logger.info(f"使用设备: {device}")
    
    # 定义损失函数和优化器
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=args.learning_rate)
    
    # 学习率调度器
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, 'min', patience=5, factor=0.5, verbose=True
    )
    
    # 训练模型
    logger.info("开始训练模型...")
    train_losses = []
    val_losses = []
    best_val_loss = float('inf')
    
    for epoch in range(args.epochs):
        # 训练阶段
        model.train()
        epoch_loss = 0
        
        with tqdm(train_loader, desc=f"Epoch {epoch+1}/{args.epochs}") as pbar:
            for features, labels in pbar:
                features = features.to(device)
                labels = labels.to(device)
                
                # 前向传播
                outputs = model(features)
                loss = criterion(outputs, labels)
                
                # 反向传播和优化
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                
                # 更新进度条
                epoch_loss += loss.item()
                pbar.set_postfix({'loss': loss.item()})
        
        avg_train_loss = epoch_loss / len(train_loader)
        train_losses.append(avg_train_loss)
        
        # 验证阶段
        model.eval()
        val_loss = 0
        predictions = []
        ground_truth = []
        
        with torch.no_grad():
            for features, labels in test_loader:
                features = features.to(device)
                labels = labels.to(device)
                
                # 前向传播
                outputs = model(features)
                loss = criterion(outputs, labels)
                
                # 计算损失
                val_loss += loss.item()
                
                # 保存预测结果和真实标签
                _, predicted = torch.max(outputs, 1)
                predictions.extend(predicted.cpu().numpy())
                ground_truth.extend(labels.cpu().numpy())
        
        avg_val_loss = val_loss / len(test_loader)
        val_losses.append(avg_val_loss)
        
        # 计算评估指标
        accuracy = accuracy_score(ground_truth, predictions)
        precision, recall, f1, _ = precision_recall_fscore_support(
            ground_truth, predictions, average='weighted'
        )
        
        logger.info(
            f"Epoch {epoch+1}/{args.epochs} - "
            f"Train Loss: {avg_train_loss:.4f}, "
            f"Val Loss: {avg_val_loss:.4f}, "
            f"Accuracy: {accuracy:.4f}, "
            f"F1: {f1:.4f}"
        )
        
        # 更新学习率
        scheduler.step(avg_val_loss)
        
        # 保存最佳模型
        if avg_val_loss < best_val_loss:
            best_val_loss = avg_val_loss
            torch.save(model.state_dict(), os.path.join(args.output_dir, 'best_model.pth'))
            logger.info(f"保存最佳模型，验证损失: {best_val_loss:.4f}")
    
    # 保存最终模型
    torch.save(model.state_dict(), os.path.join(args.output_dir, 'final_model.pth'))
    
    # 保存完整模型（含架构）
    torch.save(model, os.path.join(args.output_dir, 'full_model.pth'))
    
    # 保存模型配置
    model_config = {
        'input_dim': input_dim,
        'hidden_dims': args.hidden_dims,
        'output_dim': num_classes,
        'feature_names': list(feature_extractor.get_feature_names()),
        'class_mapping': {i: label for i, label in enumerate(sorted(df['label'].unique()))}
    }
    
    with open(os.path.join(args.output_dir, 'model_config.json'), 'w', encoding='utf-8') as f:
        json.dump(model_config, f, ensure_ascii=False, indent=2)
    
    # 绘制训练过程
    plt.figure(figsize=(10, 5))
    plt.plot(train_losses, label='Training Loss')
    plt.plot(val_losses, label='Validation Loss')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.title('Training and Validation Loss')
    plt.legend()
    plt.savefig(os.path.join(args.output_dir, 'training_loss.png'))
    
    logger.info(f"模型训练完成，保存在: {args.output_dir}")

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='语音分析模型训练')
    parser.add_argument('--data_dir', type=str, required=True, help='数据集目录')
    parser.add_argument('--config', type=str, required=True, help='配置文件路径')
    parser.add_argument('--output_dir', type=str, required=True, help='输出目录')
    parser.add_argument('--batch_size', type=int, default=32, help='批次大小')
    parser.add_argument('--epochs', type=int, default=50, help='训练轮数')
    parser.add_argument('--learning_rate', type=float, default=0.001, help='学习率')
    parser.add_argument('--hidden_dims', type=int, nargs='+', default=[128, 64], help='隐藏层维度')
    parser.add_argument('--test_size', type=float, default=0.2, help='测试集比例')
    parser.add_argument('--device', type=str, default='cuda:0', help='设备')
    parser.add_argument('--num_workers', type=int, default=4, help='数据加载线程数')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    
    # 创建输出目录
    os.makedirs(args.output_dir, exist_ok=True)
    
    # 训练模型
    train_model(args) 