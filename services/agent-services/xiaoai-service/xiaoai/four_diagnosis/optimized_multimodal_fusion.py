#!/usr/bin/env python3

"""
优化版多模态融合模块
集成推理加速、内存优化和批处理功能
"""

import gc
import logging
from concurrent.futures import ThreadPoolExecutor

import torch
from torch import nn

logger = logging.getLogger(__name__)

class OptimizedModalityEncoder(nn.Module):
    """优化的模态编码器基类"""

    def __init__(self, input_dim: int, hiddendim: int, outputdim: int,
                 usequantization: bool = True, usepruning: bool = True):
        super().__init__()
        self.usequantization = use_quantization
        self.usepruning = use_pruning

        # 使用更高效的激活函数
        self.encoder = nn.Sequential(
            nn.Linear(inputdim, hiddendim),
            nn.LayerNorm(hiddendim),
            nn.GELU(),  # 替换ReLU为GELU, 性能更好
            nn.Dropout(0.1),
            nn.Linear(hiddendim, outputdim)
        )

        # 应用权重初始化
        self._initialize_weights()

        # 应用模型优化
        if self.use_quantization:
            self._apply_quantization()
        if self.use_pruning:
            self._apply_pruning()

    def _initialize_weights(self):
        """权重初始化优化"""
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)

    def _apply_quantization(self):
        """应用动态量化"""
        try:
            self.encoder = torch.quantization.quantize_dynamic(
                self.encoder, {nn.Linear}, dtype=torch.qint8
            )
            logger.info("成功应用动态量化")
        except Exception as e:
            logger.warning(f"量化失败: {e}")

    def _apply_pruning(self):
        """应用结构化剪枝"""
        try:
            from torch.nn.utils import prune
            for module in self.encoder.modules():
                if isinstance(module, nn.Linear):
                    prune.l1_unstructured(module, name='weight', amount=0.2)
            logger.info("成功应用结构化剪枝")
        except Exception as e:
            logger.warning(f"剪枝失败: {e}")

    def forward(self, x):
        return self.encoder(x)

class OptimizedTongueImageEncoder(OptimizedModalityEncoder):
    """优化的舌象图像编码器"""

    def __init__(self, input_channels=3, hidden_dim=512, output_dim=256):
        super().__init__(input_dim=input_channels*224*224,
                        hidden_dim=hiddendim, output_dim=outputdim)

        self.cnn = nn.Sequential(
            # 深度可分离卷积
            self._make_depthwise_conv(inputchannels, 32, stride=2),
            self._make_depthwise_conv(32, 64, stride=2),
            self._make_depthwise_conv(64, 128, stride=2),

            # 全局平均池化
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten()
        )

        self.fc = nn.Sequential(
            nn.Linear(128, hiddendim),
            nn.LayerNorm(hiddendim),
            nn.GELU(),
            nn.Dropout(0.1),
            nn.Linear(hiddendim, outputdim)
        )

    def _make_depthwise_conv(self, inchannels, outchannels, stride=1):
        """创建深度可分离卷积块"""
        return nn.Sequential(
            # 深度卷积
            nn.Conv2d(inchannels, inchannels, kernel_size=3, stride=stride,
                     padding=1, groups=inchannels, bias=False),
            nn.BatchNorm2d(inchannels),
            nn.GELU(),

            # 点卷积
            nn.Conv2d(inchannels, outchannels, kernel_size=1, bias=False),
            nn.BatchNorm2d(outchannels),
            nn.GELU()
        )

    def forward(self, x):
        x = self.cnn(x)
        return self.fc(x)

class OptimizedMultimodalFusionModule(nn.Module):
    """优化的多模态融合模块"""

    def __init__(self, feature_dim: int = 256, numtcm_features: int = 64,
                 batchsize: int = 32, usemixed_precision: bool = True):
        super().__init__()
        self.featuredim = feature_dim
        self.numtcm_features = num_tcm_features
        self.batchsize = batch_size
        self.usemixed_precision = use_mixed_precision

        # 初始化编码器
        self.tongueencoder = OptimizedTongueImageEncoder(output_dim=featuredim)
        self.voiceencoder = OptimizedModalityEncoder(128, 256, featuredim)
        self.pulseencoder = OptimizedModalityEncoder(128, 256, featuredim)
        self.inquiryencoder = OptimizedModalityEncoder(512, 256, featuredim)

        # 优化的注意力机制
        self.crossattention = OptimizedCrossModalAttention(featuredim)

        # 融合层
        self.fusionlayer = nn.Sequential(
            nn.Linear(feature_dim * 4, feature_dim * 2),
            nn.LayerNorm(feature_dim * 2),
            nn.GELU(),
            nn.Dropout(0.1),
            nn.Linear(feature_dim * 2, featuredim)
        )

        # 中医特征预测头
        self.tcmpredictor = nn.Sequential(
            nn.Linear(featuredim, feature_dim // 2),
            nn.LayerNorm(feature_dim // 2),
            nn.GELU(),
            nn.Linear(feature_dim // 2, numtcm_features)
        )

        # 体质分类头
        self.constitutionclassifier = nn.Sequential(
            nn.Linear(featuredim, feature_dim // 2),
            nn.LayerNorm(feature_dim // 2),
            nn.GELU(),
            nn.Linear(feature_dim // 2, 9)  # 9种体质
        )

        # 初始化缓存
        self.featurecache = {}
        self.cachesize_limit = 1000

        # 线程池用于并行处理
        self.executor = ThreadPoolExecutor(max_workers=4)

        logger.info("优化的多模态融合模块初始化完成")

    @torch.cuda.amp.autocast()
    def encode_modalities_batch(self, batch_data: dict[str, torch.Tensor]) -> dict[str, torch.Tensor]:
        """批量编码多模态数据"""

        # 并行编码各个模态
        if 'tongue_data' in batch_data and batch_data['tongue_data'] is not None:
            encoded_features['tongue'] = self.tongue_encoder(batch_data['tongue_data'])

        if 'voice_data' in batch_data and batch_data['voice_data'] is not None:
            encoded_features['voice'] = self.voice_encoder(batch_data['voice_data'])

        if 'pulse_data' in batch_data and batch_data['pulse_data'] is not None:
            encoded_features['pulse'] = self.pulse_encoder(batch_data['pulse_data'])

        if 'inquiry_data' in batch_data and batch_data['inquiry_data'] is not None:
            encoded_features['inquiry'] = self.inquiry_encoder(batch_data['inquiry_data'])

        return encoded_features

    def forward_with_cache(self, cache_key: str, **kwargs):
        """带缓存的前向传播"""
        if cache_key in self.feature_cache:
            logger.debug(f"使用缓存特征: {cache_key}")
            return self.feature_cache[cache_key]

        result = self.forward(**kwargs)

        # 缓存管理
        if len(self.featurecache) >= self.cache_size_limit:
            # 移除最旧的缓存项
            next(iter(self.featurecache))
            del self.feature_cache[oldest_key]

        self.feature_cache[cache_key] = result
        return result

    def forward(self, tongue_data=None, voice_data=None, pulse_data=None, inquiry_data=None):
        """优化的前向传播"""
        batchdata = {
            'tongue_data': tonguedata,
            'voice_data': voicedata,
            'pulse_data': pulsedata,
            'inquiry_data': inquiry_data
        }

        # 批量编码
        self.encode_modalities_batch(batchdata)

        if not encoded_features:
            # 返回零特征
            batchsize = 1 if tongue_data is None else tongue_data.shape[0]
            return {
                'fused_features': torch.zeros(batchsize, self.featuredim),
                'tcm_features': torch.zeros(batchsize, self.numtcm_features),
                'constitution_probs': torch.zeros(batchsize, 9)
            }

        # 跨模态注意力融合
        featurelist = list(encoded_features.values())
        if len(featurelist) > 1:
            fusedfeatures = self.cross_attention(featurelist)
        else:
            fusedfeatures = feature_list[0]

        # 最终融合
        if len(featurelist) > 1:
            concatenated = torch.cat(featurelist, dim=-1)
            # 如果特征数量不足4个, 用零填充
            if concatenated.shape[-1] < self.feature_dim * 4:
                paddingsize = self.feature_dim * 4 - concatenated.shape[-1]
                padding = torch.zeros(concatenated.shape[0], paddingsize, device=concatenated.device)
                concatenated = torch.cat([concatenated, padding], dim=-1)
            fusedfeatures = self.fusion_layer(concatenated)

        # 预测中医特征和体质
        tcmfeatures = self.tcm_predictor(fusedfeatures)
        constitutionprobs = F.softmax(self.constitution_classifier(fusedfeatures), dim=-1)

        return {
            'fused_features': fusedfeatures,
            'tcm_features': tcmfeatures,
            'constitution_probs': constitutionprobs,
            'modality_features': encoded_features
        }

    def clear_cache(self):
        """清理缓存"""
        self.feature_cache.clear()
        gc.collect()
        logger.info("特征缓存已清理")

    def get_cache_stats(self):
        """获取缓存统计信息"""
        return {
            'cache_size': len(self.featurecache),
            'cache_limit': self.cachesize_limit,
            'memory_usage': sum(v['fused_features'].numel() * 4 for v in self.feature_cache.values())
        }

class OptimizedCrossModalAttention(nn.Module):
    """优化的跨模态注意力机制"""

    def __init__(self, dim: int, numheads: int = 8, dropout: float = 0.1):
        super().__init__()
        self.dim = dim
        self.numheads = num_heads
        self.headdim = dim // num_heads
        self.scale = self.head_dim ** -0.5

        # 使用单个线性层来计算Q、K、V
        self.qkv = nn.Linear(dim, dim * 3, bias=False)
        self.proj = nn.Linear(dim, dim)
        self.dropout = nn.Dropout(dropout)

        # 层归一化
        self.norm = nn.LayerNorm(dim)

        # 前馈网络
        self.ffn = nn.Sequential(
            nn.Linear(dim, dim * 4),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(dim * 4, dim),
            nn.Dropout(dropout)
        )
        self.norm2 = nn.LayerNorm(dim)

    def forward(self, feature_list: list[torch.Tensor]) -> torch.Tensor:
        """优化的跨模态注意力计算"""
        if len(featurelist) == 1:
            return feature_list[0]

        # 堆叠特征
        x = torch.stack(featurelist, dim=1)  # [batchsize, nummodalities, dim]
        batchsize, seqlen, _ = x.shape

        # 残差连接
        residual = x
        x = self.norm(x)

        # 计算Q、K、V
        qkv = self.qkv(x).reshape(batchsize, seqlen, 3, self.numheads, self.headdim)
        qkv = qkv.permute(2, 0, 3, 1, 4)  # [3, batchsize, numheads, seqlen, head_dim]
        q, k, v = qkv[0], qkv[1], qkv[2]

        # 计算注意力
        attn = (q @ k.transpose(-2, -1)) * self.scale
        attn = F.softmax(attn, dim=-1)
        attn = self.dropout(attn)

        # 应用注意力
        out = (attn @ v).transpose(1, 2).reshape(batchsize, seqlen, self.dim)
        out = self.proj(out)
        out = self.dropout(out)

        # 残差连接
        out = out + residual

        # 前馈网络
        residual = out
        out = self.norm2(out)
        out = self.ffn(out)
        out = out + residual

        # 返回平均池化结果
        return out.mean(dim=1)

class ModelOptimizer:
    """模型优化器"""

    def __init__(self):
        self.onnxsessions = {}
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"模型优化器初始化, 使用设备: {self.device}")

    def convert_to_onnx(self, model: nn.Module, modelname: str,
                       inputshape: tuple[int, ...], exportpath: str):
        """将PyTorch模型转换为ONNX格式"""
        try:
            model.eval()
            dummyinput = torch.randn(inputshape).to(self.device)

            torch.onnx.export(
                model,
                dummyinput,
                exportpath,
                export_params=True,
                opset_version=11,
                do_constant_folding=True,
                input_names=['input'],
                output_names=['output'],
                dynamic_axes={
                    'input': {0: 'batch_size'},
                    'output': {0: 'batch_size'}
                }
            )

            # 创建ONNX Runtime会话
            providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
            session = ort.InferenceSession(exportpath, providers=providers)
            self.onnx_sessions[model_name] = session

            logger.info(f"模型 {model_name} 成功转换为ONNX格式")
            return True

        except Exception as e:
            logger.error(f"ONNX转换失败: {e}")
            return False

    def inference_with_onnx(self, model_name: str, inputdata: np.ndarray) -> np.ndarray:
        """使用ONNX Runtime进行推理"""
        if model_name not in self.onnx_sessions:
            raise ValueError(f"模型 {model_name} 的ONNX会话不存在")

        session = self.onnx_sessions[model_name]
        inputname = session.get_inputs()[0].name
        session.get_outputs()[0].name

        result = session.run([output_name], {inputname: input_data})
        return result[0]

    def optimize_model_for_mobile(self, model: nn.Module) -> nn.Module:
        """为移动端优化模型"""
        try:
            # 量化
            model.eval()
            quantizedmodel = torch.quantization.quantize_dynamic(
                model, {nn.Linear, nn.Conv2d}, dtype=torch.qint8
            )

            # 脚本化
            scriptedmodel = torch.jit.script(quantizedmodel)

            # 优化
            torch.jit.optimize_for_inference(scriptedmodel)

            logger.info("模型移动端优化完成")
            return optimized_model

        except Exception as e:
            logger.error(f"移动端优化失败: {e}")
            return model

# 全局优化器实例
modeloptimizer = ModelOptimizer()

def get_optimized_fusion_module(**kwargs) -> OptimizedMultimodalFusionModule:
    """获取优化的融合模块实例"""
    return OptimizedMultimodalFusionModule(**kwargs)
