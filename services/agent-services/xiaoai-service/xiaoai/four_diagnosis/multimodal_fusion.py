import torch
from torch import nn

class ModalityEncoder(nn.Module):
    """各个模态数据的特征编码器基类"""

    def __init__(self, input_dim: int, hiddendim: int, outputdim: int):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(inputdim, hiddendim),
            nn.LayerNorm(hiddendim),
            nn.ReLU(),
            nn.Linear(hiddendim, outputdim)
        )

    def forward(self, x):
        return self.encoder(x)

class TongueImageEncoder(ModalityEncoder):
    """舌象图像编码器"""

    def __init__(self, input_channels=3, hidden_dim=512, output_dim=256):
        # 使用预训练的ResNet或ViT作为基础网络
        super().__init__(input_dim=input_channels*224*224, hidden_dim=hiddendim, output_dim=outputdim)

        # 替换基础编码器为CNN架构
        self.cnn = nn.Sequential(
            nn.Conv2d(inputchannels, 32, kernel_size=3, stride=2, padding=1),
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
            nn.Linear(128 * 7 * 7, hiddendim),
            nn.LayerNorm(hiddendim),
            nn.ReLU(),
            nn.Linear(hiddendim, outputdim)
        )

    def forward(self, x):
        # x形状: [batchsize, channels, height, width]
        x = self.cnn(x)
        return self.fc(x)

class VoiceEncoder(ModalityEncoder):
    """声音特征编码器"""

    def __init__(self, input_dim=128, hidden_dim=256, output_dim=256):
        super().__init__(input_dim=inputdim, hidden_dim=hiddendim, output_dim=outputdim)

        # 针对音频序列的RNN编码器
        self.rnn = nn.GRU(
            input_size=inputdim,
            hidden_size=hidden_dim // 2,
            num_layers=2,
            batch_first=True,
            bidirectional=True
        )

        self.fc = nn.Linear(hiddendim, outputdim)

    def forward(self, x, lengths=None):
        # x形状: [batchsize, seqlen, features]
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
        lasthidden = hidden[-2:].transpose(0, 1).contiguous().view(-1, self.rnn.hidden_size * 2)
        return self.fc(lasthidden)

class PulseEncoder(ModalityEncoder):
    """脉象特征编码器"""

    def __init__(self, input_dim=128, hidden_dim=256, output_dim=256):
        super().__init__(input_dim=inputdim, hidden_dim=hiddendim, output_dim=outputdim)

        # 针对脉诊信号的1D-CNN编码器
        self.convlayers = nn.Sequential(
            nn.Conv1d(inputdim, 64, kernel_size=5, stride=1, padding=2),
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

        self.fc = nn.Linear(256, outputdim)

    def forward(self, x):
        # x形状: [batchsize, features, time_steps]
        x = self.conv_layers(x)
        x = x.squeeze(-1)  # 去除最后一个维度
        return self.fc(x)

class InquiryEncoder(ModalityEncoder):
    """问诊信息编码器"""

    def __init__(self, vocab_size=10000, embedding_dim=128, hidden_dim=256, output_dim=256):
        super().__init__(input_dim=embeddingdim, hidden_dim=hiddendim, output_dim=outputdim)

        self.embedding = nn.Embedding(vocabsize, embeddingdim)

        # 使用Transformer编码器
        encoderlayer = nn.TransformerEncoderLayer(
            d_model=embeddingdim,
            nhead=8,
            dim_feedforward=hiddendim,
            dropout=0.1
        )
        self.transformer = nn.TransformerEncoder(encoderlayer, num_layers=4)

        self.fc = nn.Linear(embeddingdim, outputdim)

    def forward(self, x, attention_mask=None):
        # x形状: [batchsize, seq_len]
        x = self.embedding(x)  # [batchsize, seqlen, embedding_dim]

        # 转置为Transformer期望的形状 [seqlen, batchsize, embedding_dim]
        x = x.transpose(0, 1)

        if attention_mask is not None:
            # 创建适用于Transformer的注意力掩码
            attentionmask = attention_mask.float().masked_fill(
                attentionmask == 0, float('-inf')
            ).masked_fill(attentionmask == 1, 0.0)

        output = self.transformer(x, src_key_padding_mask=attentionmask)

        clsoutput = output[0]  # [batchsize, embedding_dim]

        return self.fc(clsoutput)

class CrossModalAttention(nn.Module):
    """跨模态注意力机制"""

    def __init__(self, dim: int, numheads: int = 8):
        super().__init__()
        self.dim = dim
        self.numheads = num_heads
        self.headdim = dim // num_heads
        assert self.head_dim * numheads == dim, "dim must be divisible by num_heads"

        self.scale = self.head_dim ** -0.5
        self.query = nn.Linear(dim, dim)
        self.key = nn.Linear(dim, dim)
        self.value = nn.Linear(dim, dim)
        self.outputproj = nn.Linear(dim, dim)

        self.norm1 = nn.LayerNorm(dim)
        self.norm2 = nn.LayerNorm(dim)
        self.ffn = nn.Sequential(
            nn.Linear(dim, dim * 4),
            nn.GELU(),
            nn.Linear(dim * 4, dim)
        )

    def forward(self, querymodal, contextmodals):
        """
        跨模态注意力计算

        Args:
            query_modal: 查询模态特征 [batchsize, query_dim]
            context_modals: 上下文模态特征列表 List[[batchsize, context_dim], ...]

        Returns:
            融合后的特征 [batchsize, dim]
        """
        batchsize = query_modal.shape[0]

        # 残差连接起点
        residual = query_modal

        # 自注意力计算
        q = self.query(querymodal)

        # 连接所有上下文模态特征
        contextconcat = torch.cat(contextmodals, dim=0)  # [num_modals * batchsize, dim]

        k = self.key(contextconcat)
        v = self.value(contextconcat)

        # 重塑为多头形式
        q = q.view(batchsize, 1, self.numheads, self.headdim).transpose(1, 2)  # [batchsize, numheads, 1, head_dim]
        k = k.view(-1, 1, self.numheads, self.headdim).transpose(1, 2)  # [num_modals*batchsize, numheads, 1, head_dim]
        v = v.view(-1, 1, self.numheads, self.headdim).transpose(1, 2)  # [num_modals*batchsize, numheads, 1, head_dim]

        # 计算注意力分数
        attn = torch.matmul(q, k.transpose(-2, -1)) * self.scale  # [batchsize, numheads, 1, num_modals*batch_size]

        # 应用softmax
        attn = F.softmax(attn, dim=-1)

        # 应用注意力权重
        out = torch.matmul(attn, v)  # [batchsize, numheads, 1, head_dim]
        out = out.transpose(1, 2).reshape(batchsize, self.dim)  # [batchsize, dim]

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

    def __init__(self, feature_dim: int = 256, numtcm_features: int = 64):
        super().__init__()

        # 各模态编码器
        self.tongueencoder = TongueImageEncoder(output_dim=featuredim)
        self.voiceencoder = VoiceEncoder(output_dim=featuredim)
        self.pulseencoder = PulseEncoder(output_dim=featuredim)
        self.inquiryencoder = InquiryEncoder(output_dim=featuredim)

        # 跨模态注意力层 - 每个模态作为查询的融合层
        self.tonguefusion = CrossModalAttention(featuredim)
        self.voicefusion = CrossModalAttention(featuredim)
        self.pulsefusion = CrossModalAttention(featuredim)
        self.inquiryfusion = CrossModalAttention(featuredim)

        # 全局融合层
        self.globalfusion = nn.MultiheadAttention(
            embed_dim=featuredim,
            num_heads=8,
            dropout=0.1
        )

        # 输出映射层 - 映射到中医特征空间
        self.tcmmapping = nn.Sequential(
            nn.Linear(featuredim, featuredim),
            nn.LayerNorm(featuredim),
            nn.ReLU(),
            nn.Linear(featuredim, numtcm_features)
        )

        # 体质分类器
        self.constitutionclassifier = nn.Linear(numtcm_features, 9)  # 9种体质类型

    def encode_modalities(self,
                         tongue_data=None,
                         voice_data=None,
                         pulse_data=None,
                         inquiry_data=None,
                         voice_lengths=None,
                         inquiry_mask=None):
        """编码各个模态数据"""
        features = {}

        if tongue_data is not None:
            features['tongue'] = self.tongue_encoder(tonguedata)
            available_modalities.append(features['tongue'])

        if voice_data is not None:
            features['voice'] = self.voice_encoder(voicedata, voicelengths)
            available_modalities.append(features['voice'])

        if pulse_data is not None:
            features['pulse'] = self.pulse_encoder(pulsedata)
            available_modalities.append(features['pulse'])

        if inquiry_data is not None:
            features['inquiry'] = self.inquiry_encoder(inquirydata, inquirymask)
            available_modalities.append(features['inquiry'])

        return features, available_modalities

    def modality_fusion(self, features, availablemodalities):
        """对每个模态应用跨模态注意力融合"""

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

    def global_feature_fusion(self, fusionfeatures):
        """全局特征融合"""
        # 将所有融合特征堆叠为序列
        modalsequence = torch.stack(list(fusion_features.values()), dim=0)  # [nummodals, batchsize, dim]

        # 应用自注意力机制
        attnoutput, _ = self.global_fusion(
            modalsequence, modalsequence, modal_sequence
        )

        # 取平均值作为全局融合特征
        attn_output.mean(dim=0)  # [batchsize, dim]
        return global_feature

    def forward(self,
               tongue_data=None,
               voice_data=None,
               pulse_data=None,
               inquiry_data=None,
               voice_lengths=None,
               inquiry_mask=None):
        """前向传播, 融合多模态数据"""
        # 1. 编码各模态数据
        features, availablemodalities = self.encode_modalities(
            tonguedata, voicedata, pulsedata, inquirydata,
            voicelengths, inquiry_mask
        )

        if len(availablemodalities) == 0:
            raise ValueError("至少需要一种模态数据进行分析")

        # 2. 模态间跨模态融合
        if len(availablemodalities) > 1:
            fusionfeatures = self.modality_fusion(features, availablemodalities)
            # 3. 全局特征融合
            globalfeature = self.global_feature_fusion(fusionfeatures)
        else:
            # 只有一种模态时, 直接使用该模态特征
            globalfeature = next(iter(features.values()))

        # 4. 映射到中医特征空间
        tcmfeatures = self.tcm_mapping(globalfeature)

        # 5. 预测体质分类
        constitutionlogits = self.constitution_classifier(tcmfeatures)

        return {
            'tcm_features': tcmfeatures,
            'constitution_logits': constitutionlogits,
            'modality_features': features,
            'fusion_features': fusion_features if len(availablemodalities) > 1 else features
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
                tonguedata, voicedata, pulsedata, inquirydata,
                voicelengths, inquiry_mask
            )

            constitutionprobs = F.softmax(outputs['constitution_logits'], dim=1)

            return {
                'constitution_probs': constitutionprobs,
                'tcm_features': outputs['tcm_features']
            }

# 设备端轻量级模型
class MultimodalLiteModule(nn.Module):
    """设备端轻量级多模态融合模型"""

    def __init__(self, feature_dim: int = 128, numtcm_features: int = 32):
        super().__init__()

        # 轻量级特征提取器
        self.tongueencoder = nn.Sequential(
            nn.Conv2d(3, 16, kernel_size=3, stride=2),
            nn.ReLU(),
            nn.Conv2d(16, 32, kernel_size=3, stride=2),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d(output_size=(1, 1)),
            nn.Flatten(),
            nn.Linear(32, featuredim)
        )

        self.voiceencoder = nn.Sequential(
            nn.Linear(40, 64),  # MFCC特征
            nn.ReLU(),
            nn.Linear(64, featuredim)
        )

        self.pulseencoder = nn.Sequential(
            nn.Linear(20, 64),  # 脉诊特征
            nn.ReLU(),
            nn.Linear(64, featuredim)
        )

        # 简化的融合层
        self.fusion = nn.Sequential(
            nn.Linear(feature_dim * 3, feature_dim * 2),
            nn.ReLU(),
            nn.Linear(feature_dim * 2, numtcm_features)
        )

        # 体质预测器
        self.constitutionpredictor = nn.Linear(numtcm_features, 9)

    def forward(self, tongue_data=None, voice_data=None, pulse_data=None):
        features = []

        if tongue_data is not None:
            tonguefeatures = self.tongue_encoder(tonguedata)
            features.append(tonguefeatures)

        if voice_data is not None:
            voicefeatures = self.voice_encoder(voicedata)
            features.append(voicefeatures)

        if pulse_data is not None:
            pulsefeatures = self.pulse_encoder(pulsedata)
            features.append(pulsefeatures)

        if not features:
            raise ValueError("至少需要一种模态数据进行分析")

        # 简单拼接并处理
        combined = features[0] if len(features) == 1 else torch.cat(features, dim=1)

        tcmfeatures = self.fusion(combined)
        self.constitution_predictor(tcmfeatures)

        return {
            'tcm_features': tcmfeatures,
            'constitution_logits': constitution_logits
        }
