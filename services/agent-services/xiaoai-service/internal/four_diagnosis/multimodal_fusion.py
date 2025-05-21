import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Tuple, Optional, Union

class ModalityEncoder(nn.Module):
    """各个模态数据的特征编码器基类"""
    
    def __init__(self, input_dim: int, hidden_dim: int, output_dim: int):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, output_dim)
        )
    
    def forward(self, x):
        return self.encoder(x)


class TongueImageEncoder(ModalityEncoder):
    """舌象图像编码器"""
    
    def __init__(self, input_channels=3, hidden_dim=512, output_dim=256):
        # 使用预训练的ResNet或ViT作为基础网络
        super().__init__(input_dim=input_channels*224*224, hidden_dim=hidden_dim, output_dim=output_dim)
        
        # 替换基础编码器为CNN架构
        self.cnn = nn.Sequential(
            nn.Conv2d(input_channels, 32, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.Conv2d(32, 64, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.Conv2d(64, 128, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d(output_size=(7, 7))
        )
        
        self.fc = nn.Sequential(
            nn.Flatten(),
            nn.Linear(128 * 7 * 7, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, output_dim)
        )
    
    def forward(self, x):
        # x形状: [batch_size, channels, height, width]
        x = self.cnn(x)
        return self.fc(x)


class VoiceEncoder(ModalityEncoder):
    """声音特征编码器"""
    
    def __init__(self, input_dim=128, hidden_dim=256, output_dim=256):
        super().__init__(input_dim=input_dim, hidden_dim=hidden_dim, output_dim=output_dim)
        
        # 针对音频序列的RNN编码器
        self.rnn = nn.GRU(
            input_size=input_dim, 
            hidden_size=hidden_dim // 2,
            num_layers=2,
            batch_first=True,
            bidirectional=True
        )
        
        self.fc = nn.Linear(hidden_dim, output_dim)
    
    def forward(self, x, lengths=None):
        # x形状: [batch_size, seq_len, features]
        if lengths is not None:
            # 使用PackedSequence处理变长序列
            packed = nn.utils.rnn.pack_padded_sequence(
                x, lengths, batch_first=True, enforce_sorted=False
            )
            output, hidden = self.rnn(packed)
            output, _ = nn.utils.rnn.pad_packed_sequence(output, batch_first=True)
        else:
            output, hidden = self.rnn(x)
        
        # 取最后一个时间步的隐藏状态
        last_hidden = hidden[-2:].transpose(0, 1).contiguous().view(-1, self.rnn.hidden_size * 2)
        return self.fc(last_hidden)


class PulseEncoder(ModalityEncoder):
    """脉象特征编码器"""
    
    def __init__(self, input_dim=128, hidden_dim=256, output_dim=256):
        super().__init__(input_dim=input_dim, hidden_dim=hidden_dim, output_dim=output_dim)
        
        # 针对脉诊信号的1D-CNN编码器
        self.conv_layers = nn.Sequential(
            nn.Conv1d(input_dim, 64, kernel_size=5, stride=1, padding=2),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.MaxPool1d(kernel_size=2, stride=2),
            
            nn.Conv1d(64, 128, kernel_size=5, stride=1, padding=2),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.MaxPool1d(kernel_size=2, stride=2),
            
            nn.Conv1d(128, 256, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.AdaptiveAvgPool1d(output_size=1)
        )
        
        self.fc = nn.Linear(256, output_dim)
    
    def forward(self, x):
        # x形状: [batch_size, features, time_steps]
        x = self.conv_layers(x)
        x = x.squeeze(-1)  # 去除最后一个维度
        return self.fc(x)


class InquiryEncoder(ModalityEncoder):
    """问诊信息编码器"""
    
    def __init__(self, vocab_size=10000, embedding_dim=128, hidden_dim=256, output_dim=256):
        super().__init__(input_dim=embedding_dim, hidden_dim=hidden_dim, output_dim=output_dim)
        
        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        
        # 使用Transformer编码器
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=embedding_dim,
            nhead=8,
            dim_feedforward=hidden_dim,
            dropout=0.1
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=4)
        
        self.fc = nn.Linear(embedding_dim, output_dim)
    
    def forward(self, x, attention_mask=None):
        # x形状: [batch_size, seq_len]
        x = self.embedding(x)  # [batch_size, seq_len, embedding_dim]
        
        # 转置为Transformer期望的形状 [seq_len, batch_size, embedding_dim]
        x = x.transpose(0, 1)
        
        if attention_mask is not None:
            # 创建适用于Transformer的注意力掩码
            attention_mask = attention_mask.float().masked_fill(
                attention_mask == 0, float('-inf')
            ).masked_fill(attention_mask == 1, float(0.0))
        
        output = self.transformer(x, src_key_padding_mask=attention_mask)
        
        # 使用[CLS]标记的输出（第一个位置）
        cls_output = output[0]  # [batch_size, embedding_dim]
        
        return self.fc(cls_output)


class CrossModalAttention(nn.Module):
    """跨模态注意力机制"""
    
    def __init__(self, dim: int, num_heads: int = 8):
        super().__init__()
        self.dim = dim
        self.num_heads = num_heads
        self.head_dim = dim // num_heads
        assert self.head_dim * num_heads == dim, "dim must be divisible by num_heads"
        
        self.scale = self.head_dim ** -0.5
        self.query = nn.Linear(dim, dim)
        self.key = nn.Linear(dim, dim)
        self.value = nn.Linear(dim, dim)
        self.output_proj = nn.Linear(dim, dim)
        
        self.norm1 = nn.LayerNorm(dim)
        self.norm2 = nn.LayerNorm(dim)
        self.ffn = nn.Sequential(
            nn.Linear(dim, dim * 4),
            nn.GELU(),
            nn.Linear(dim * 4, dim)
        )
    
    def forward(self, query_modal, context_modals):
        """
        跨模态注意力计算
        
        Args:
            query_modal: 查询模态特征 [batch_size, query_dim]
            context_modals: 上下文模态特征列表 List[[batch_size, context_dim], ...]
        
        Returns:
            融合后的特征 [batch_size, dim]
        """
        batch_size = query_modal.shape[0]
        
        # 残差连接起点
        residual = query_modal
        
        # 自注意力计算
        q = self.query(query_modal)
        
        # 连接所有上下文模态特征
        context_concat = torch.cat(context_modals, dim=0)  # [num_modals * batch_size, dim]
        
        k = self.key(context_concat)
        v = self.value(context_concat)
        
        # 重塑为多头形式
        q = q.view(batch_size, 1, self.num_heads, self.head_dim).transpose(1, 2)  # [batch_size, num_heads, 1, head_dim]
        k = k.view(-1, 1, self.num_heads, self.head_dim).transpose(1, 2)  # [num_modals*batch_size, num_heads, 1, head_dim]
        v = v.view(-1, 1, self.num_heads, self.head_dim).transpose(1, 2)  # [num_modals*batch_size, num_heads, 1, head_dim]
        
        # 计算注意力分数
        attn = torch.matmul(q, k.transpose(-2, -1)) * self.scale  # [batch_size, num_heads, 1, num_modals*batch_size]
        
        # 应用softmax
        attn = F.softmax(attn, dim=-1)
        
        # 应用注意力权重
        out = torch.matmul(attn, v)  # [batch_size, num_heads, 1, head_dim]
        out = out.transpose(1, 2).reshape(batch_size, self.dim)  # [batch_size, dim]
        
        # 第一个残差连接
        out = self.output_proj(out)
        out = self.norm1(out + residual)
        
        # 前馈网络
        residual = out
        out = self.ffn(out)
        out = self.norm2(out + residual)
        
        return out


class MultimodalFusionModule(nn.Module):
    """多模态特征融合模块"""
    
    def __init__(self, feature_dim: int = 256, num_tcm_features: int = 64):
        super().__init__()
        
        # 各模态编码器
        self.tongue_encoder = TongueImageEncoder(output_dim=feature_dim)
        self.voice_encoder = VoiceEncoder(output_dim=feature_dim)
        self.pulse_encoder = PulseEncoder(output_dim=feature_dim)
        self.inquiry_encoder = InquiryEncoder(output_dim=feature_dim)
        
        # 跨模态注意力层 - 每个模态作为查询的融合层
        self.tongue_fusion = CrossModalAttention(feature_dim)
        self.voice_fusion = CrossModalAttention(feature_dim)
        self.pulse_fusion = CrossModalAttention(feature_dim)
        self.inquiry_fusion = CrossModalAttention(feature_dim)
        
        # 全局融合层
        self.global_fusion = nn.MultiheadAttention(
            embed_dim=feature_dim,
            num_heads=8,
            dropout=0.1
        )
        
        # 输出映射层 - 映射到中医特征空间
        self.tcm_mapping = nn.Sequential(
            nn.Linear(feature_dim, feature_dim),
            nn.LayerNorm(feature_dim),
            nn.ReLU(),
            nn.Linear(feature_dim, num_tcm_features)
        )
        
        # 体质分类器
        self.constitution_classifier = nn.Linear(num_tcm_features, 9)  # 9种体质类型
        
    def encode_modalities(self, 
                         tongue_data=None, 
                         voice_data=None, 
                         pulse_data=None, 
                         inquiry_data=None,
                         voice_lengths=None,
                         inquiry_mask=None):
        """编码各个模态数据"""
        features = {}
        available_modalities = []
        
        if tongue_data is not None:
            features['tongue'] = self.tongue_encoder(tongue_data)
            available_modalities.append(features['tongue'])
            
        if voice_data is not None:
            features['voice'] = self.voice_encoder(voice_data, voice_lengths)
            available_modalities.append(features['voice'])
            
        if pulse_data is not None:
            features['pulse'] = self.pulse_encoder(pulse_data)
            available_modalities.append(features['pulse'])
            
        if inquiry_data is not None:
            features['inquiry'] = self.inquiry_encoder(inquiry_data, inquiry_mask)
            available_modalities.append(features['inquiry'])
            
        return features, available_modalities
    
    def modality_fusion(self, features, available_modalities):
        """对每个模态应用跨模态注意力融合"""
        fusion_features = {}
        
        if 'tongue' in features:
            # 获取除舌象外的其他模态特征作为上下文
            context = [f for k, f in features.items() if k != 'tongue']
            fusion_features['tongue'] = self.tongue_fusion(features['tongue'], context)
            
        if 'voice' in features:
            context = [f for k, f in features.items() if k != 'voice']
            fusion_features['voice'] = self.voice_fusion(features['voice'], context)
            
        if 'pulse' in features:
            context = [f for k, f in features.items() if k != 'pulse']
            fusion_features['pulse'] = self.pulse_fusion(features['pulse'], context)
            
        if 'inquiry' in features:
            context = [f for k, f in features.items() if k != 'inquiry']
            fusion_features['inquiry'] = self.inquiry_fusion(features['inquiry'], context)
        
        return fusion_features
    
    def global_feature_fusion(self, fusion_features):
        """全局特征融合"""
        # 将所有融合特征堆叠为序列
        modal_sequence = torch.stack(list(fusion_features.values()), dim=0)  # [num_modals, batch_size, dim]
        
        # 应用自注意力机制
        attn_output, _ = self.global_fusion(
            modal_sequence, modal_sequence, modal_sequence
        )
        
        # 取平均值作为全局融合特征
        global_feature = attn_output.mean(dim=0)  # [batch_size, dim]
        return global_feature
    
    def forward(self, 
               tongue_data=None, 
               voice_data=None, 
               pulse_data=None, 
               inquiry_data=None,
               voice_lengths=None, 
               inquiry_mask=None):
        """前向传播，融合多模态数据"""
        # 1. 编码各模态数据
        features, available_modalities = self.encode_modalities(
            tongue_data, voice_data, pulse_data, inquiry_data,
            voice_lengths, inquiry_mask
        )
        
        if len(available_modalities) == 0:
            raise ValueError("至少需要一种模态数据进行分析")
            
        # 2. 模态间跨模态融合
        if len(available_modalities) > 1:
            fusion_features = self.modality_fusion(features, available_modalities)
            # 3. 全局特征融合
            global_feature = self.global_feature_fusion(fusion_features)
        else:
            # 只有一种模态时，直接使用该模态特征
            global_feature = next(iter(features.values()))
        
        # 4. 映射到中医特征空间
        tcm_features = self.tcm_mapping(global_feature)
        
        # 5. 预测体质分类
        constitution_logits = self.constitution_classifier(tcm_features)
        
        return {
            'tcm_features': tcm_features,
            'constitution_logits': constitution_logits,
            'modality_features': features,
            'fusion_features': fusion_features if len(available_modalities) > 1 else features
        }
        
    def predict_constitution(self, 
                            tongue_data=None, 
                            voice_data=None, 
                            pulse_data=None, 
                            inquiry_data=None,
                            voice_lengths=None, 
                            inquiry_mask=None):
        """预测用户体质类型"""
        
        with torch.no_grad():
            outputs = self.forward(
                tongue_data, voice_data, pulse_data, inquiry_data,
                voice_lengths, inquiry_mask
            )
            
            constitution_probs = F.softmax(outputs['constitution_logits'], dim=1)
            
            return {
                'constitution_probs': constitution_probs,
                'tcm_features': outputs['tcm_features']
            }


# 设备端轻量级模型
class MultimodalLiteModule(nn.Module):
    """设备端轻量级多模态融合模型"""
    
    def __init__(self, feature_dim: int = 128, num_tcm_features: int = 32):
        super().__init__()
        
        # 轻量级特征提取器
        self.tongue_encoder = nn.Sequential(
            nn.Conv2d(3, 16, kernel_size=3, stride=2),
            nn.ReLU(),
            nn.Conv2d(16, 32, kernel_size=3, stride=2),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d(output_size=(1, 1)),
            nn.Flatten(),
            nn.Linear(32, feature_dim)
        )
        
        self.voice_encoder = nn.Sequential(
            nn.Linear(40, 64),  # MFCC特征
            nn.ReLU(),
            nn.Linear(64, feature_dim)
        )
        
        self.pulse_encoder = nn.Sequential(
            nn.Linear(20, 64),  # 脉诊特征
            nn.ReLU(),
            nn.Linear(64, feature_dim)
        )
        
        # 简化的融合层
        self.fusion = nn.Sequential(
            nn.Linear(feature_dim * 3, feature_dim * 2),
            nn.ReLU(),
            nn.Linear(feature_dim * 2, num_tcm_features)
        )
        
        # 体质预测器
        self.constitution_predictor = nn.Linear(num_tcm_features, 9)
    
    def forward(self, tongue_data=None, voice_data=None, pulse_data=None):
        features = []
        
        if tongue_data is not None:
            tongue_features = self.tongue_encoder(tongue_data)
            features.append(tongue_features)
            
        if voice_data is not None:
            voice_features = self.voice_encoder(voice_data)
            features.append(voice_features)
            
        if pulse_data is not None:
            pulse_features = self.pulse_encoder(pulse_data)
            features.append(pulse_features)
            
        if not features:
            raise ValueError("至少需要一种模态数据进行分析")
            
        # 简单拼接并处理
        if len(features) == 1:
            combined = features[0]
        else:
            combined = torch.cat(features, dim=1)
            
        tcm_features = self.fusion(combined)
        constitution_logits = self.constitution_predictor(tcm_features)
        
        return {
            'tcm_features': tcm_features,
            'constitution_logits': constitution_logits
        } 