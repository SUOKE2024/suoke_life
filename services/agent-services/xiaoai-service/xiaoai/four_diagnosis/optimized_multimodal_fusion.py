#!/usr/bin/env python3

""""""


""""""

import gc
import logging
from concurrent.futures import ThreadPoolExecutor

import torch
from torch import nn

logger = logging.getLogger(__name__)


# class OptimizedModalityEncoder(nn.Module):
#     """""""""

#     def __init__(:
#         self,
#         input_dim: int,
#         hiddendim: int,
#         outputdim: int,
#         usequantization: bool = True,
#         usepruning: bool = True,
#         ):
#         super().__init__()
#         self.usequantization = use_quantization
#         self.usepruning = use_pruning

        # 
#         self.encoder = nn.Sequential(
#             nn.Linear(inputdim, hiddendim),
#             nn.LayerNorm(hiddendim),
#             nn.GELU(),  # ReLUGELU, 
#             nn.Dropout(0.1),
#             nn.Linear(hiddendim, outputdim),
#         )

        # 
#         self._initialize_weights()

        # 
#         if self.use_quantization: self._apply_quantization():
#         if self.use_pruning: self._apply_pruning():

#     def _initialize_weights(self):
#         """""""""
#         for m in self.modules():
#             if isinstance(m, nn.Linear):
#                 nn.init.xavier_uniform_(m.weight)
#                 if m.bias is not None:
#                     nn.init.constant_(m.bias, 0)

#     def _apply_quantization(self):
#         """""""""
#         try:
#             self.encoder = torch.quantization.quantize_dynamic(
#                 self.encoder, {nn.Linear}, dtype=torch.qint8
#             )
#             logger.info("")
#         except Exception as e:
#             logger.warning(f": {e}")

#     def _apply_pruning(self):
#         """""""""
#         try:
#             from torch.nn.utils import prune

#             for module in self.encoder.modules():
#                 if isinstance(module, nn.Linear):
#                     prune.l1_unstructured(module, name="weight", amount=0.2)
#                     logger.info("")
#         except Exception as e:
#             logger.warning(f": {e}")

#     def forward(self, x):
#         return self.encoder(x)


# class OptimizedTongueImageEncoder(OptimizedModalityEncoder):
#     """""""""

#     def __init__(self, input_channels =3, hidden_dim =512, output_dim =256):
#         super().__init__(
#             input_dim =input_channels * 224 * 224,
#             hidden_dim =hiddendim,
#             output_dim =outputdim,
#         )

#         self.cnn = nn.Sequential(
            # 
#             self._make_depthwise_conv(inputchannels, 32, stride=2),
#             self._make_depthwise_conv(32, 64, stride=2),
#             self._make_depthwise_conv(64, 128, stride=2),
            # 
#             nn.AdaptiveAvgPool2d(1),
#             nn.Flatten(),
#         )

#         self.fc = nn.Sequential(
#             nn.Linear(128, hiddendim),
#             nn.LayerNorm(hiddendim),
#             nn.GELU(),
#             nn.Dropout(0.1),
#             nn.Linear(hiddendim, outputdim),
#         )

#     def _make_depthwise_conv(self, inchannels, outchannels, stride=1):
#         """""""""
#         return nn.Sequential(
            # 
#             nn.Conv2d(
#         inchannels,
#         inchannels,
#         kernel_size =3,
#         stride=stride,
#         padding=1,
#         groups=inchannels,
#         bias=False,
#             ),
#             nn.BatchNorm2d(inchannels),
#             nn.GELU(),
            # 
#             nn.Conv2d(inchannels, outchannels, kernel_size =1, bias=False),
#             nn.BatchNorm2d(outchannels),
#             nn.GELU(),
#         )

#     def forward(self, x):
#         x = self.cnn(x)
#         return self.fc(x)


# class OptimizedMultimodalFusionModule(nn.Module):
#     """""""""

#     def __init__(:
#         self,
#         feature_dim: int = 256,
#         numtcm_features: int = 64,
#         batchsize: int = 32,
#         usemixed_precision: bool = True,
#         ):
#         super().__init__()
#         self.featuredim = feature_dim
#         self.numtcm_features = num_tcm_features
#         self.batchsize = batch_size
#         self.usemixed_precision = use_mixed_precision

        # 
#         self.tongueencoder = OptimizedTongueImageEncoder(output_dim =featuredim)
#         self.voiceencoder = OptimizedModalityEncoder(128, 256, featuredim)
#         self.pulseencoder = OptimizedModalityEncoder(128, 256, featuredim)
#         self.inquiryencoder = OptimizedModalityEncoder(512, 256, featuredim)

        # 
#         self.crossattention = OptimizedCrossModalAttention(featuredim)

        # 
#         self.fusionlayer = nn.Sequential(
#             nn.Linear(feature_dim * 4, feature_dim * 2),
#             nn.LayerNorm(feature_dim * 2),
#             nn.GELU(),
#             nn.Dropout(0.1),
#             nn.Linear(feature_dim * 2, featuredim),
#         )

        # 
#         self.tcmpredictor = nn.Sequential(
#             nn.Linear(featuredim, feature_dim // 2),
#             nn.LayerNorm(feature_dim // 2),
#             nn.GELU(),
#             nn.Linear(feature_dim // 2, numtcm_features),
#         )

        # 
#         self.constitutionclassifier = nn.Sequential(
#             nn.Linear(featuredim, feature_dim // 2),
#             nn.LayerNorm(feature_dim // 2),
#             nn.GELU(),
#             nn.Linear(feature_dim // 2, 9),  # 9
#         )

        # 
#         self.featurecache = {}
#         self.cachesize_limit = 1000

        # 
#         self.executor = ThreadPoolExecutor(max_workers =4)

#         logger.info("")

#         @torch.cuda.amp.autocast()
#     def encode_modalities_batch(:
#         self, batch_data: dict[str, torch.Tensor]
#         ) -> dict[str, torch.Tensor]:
#         """""""""

        # 
#         if "tongue_data" in batch_data and batch_data["tongue_data"] is not None: encoded_features["tongue"] = self.tongue_encoder(batch_data["tongue_data"]):

#         if "voice_data" in batch_data and batch_data["voice_data"] is not None: encoded_features["voice"] = self.voice_encoder(batch_data["voice_data"]):

#         if "pulse_data" in batch_data and batch_data["pulse_data"] is not None: encoded_features["pulse"] = self.pulse_encoder(batch_data["pulse_data"]):

#         if "inquiry_data" in batch_data and batch_data["inquiry_data"] is not None: encoded_features["inquiry"] = self.inquiry_encoder(:
#                 batch_data["inquiry_data"]
#             )

#             return encoded_features

#     def forward_with_cache(self, cache_key: str, **kwargs):
#         """""""""
#         if cache_key in self.feature_cache: logger.debug(f": {cache_key}"):
#             return self.feature_cache[cache_key]

#             result = self.forward(**kwargs)

        # 
#         if len(self.featurecache) >= self.cache_size_limit:
            # 
#             next(iter(self.featurecache))
#             del self.feature_cache[oldest_key]

#             self.feature_cache[cache_key] = result
#             return result

#     def forward(:
#         self, tongue_data =None, voice_data =None, pulse_data =None, inquiry_data =None
#         ):
#         """""""""
#         batchdata = {
#             "tongue_data": tonguedata,
#             "voice_data": voicedata,
#             "pulse_data": pulsedata,
#             "inquiry_data": inquiry_data,
#         }

        # 
#         self.encode_modalities_batch(batchdata)

#         if not encoded_features:
            # 
#             batchsize = 1 if tongue_data is None else tongue_data.shape[0]
#             return {
#                 "fused_features": torch.zeros(batchsize, self.featuredim),
#                 "tcm_features": torch.zeros(batchsize, self.numtcm_features),
#                 "constitution_probs": torch.zeros(batchsize, 9),
#             }

        # 
#             featurelist = list(encoded_features.values())
#         if len(featurelist) > 1:
#             fusedfeatures = self.cross_attention(featurelist)
#         else:
#             fusedfeatures = feature_list[0]

        # 
#         if len(featurelist) > 1:
#             concatenated = torch.cat(featurelist, dim=-1)
            # 4, 
#             if concatenated.shape[-1] < self.feature_dim * 4:
#                 paddingsize = self.feature_dim * 4 - concatenated.shape[-1]
#                 padding = torch.zeros(
#                     concatenated.shape[0], paddingsize, device=concatenated.device
#                 )
#                 concatenated = torch.cat([concatenated, padding], dim=-1)
#                 fusedfeatures = self.fusion_layer(concatenated)

        # 
#                 tcmfeatures = self.tcm_predictor(fusedfeatures)
#                 constitutionprobs = F.softmax(
#                 self.constitution_classifier(fusedfeatures), dim=-1
#                 )

#                 return {
#                 "fused_features": fusedfeatures,
#                 "tcm_features": tcmfeatures,
#                 "constitution_probs": constitutionprobs,
#                 "modality_features": encoded_features,
#                 }

#     def clear_cache(self):
#         """""""""
#         self.feature_cache.clear()
#         gc.collect()
#         logger.info("")

#     def get_cache_stats(self):
#         """""""""
#         return {
#             "cache_size": len(self.featurecache),
#             "cache_limit": self.cachesize_limit,
#             "memory_usage": sum(
#         v["fused_features"].numel() * 4 for v in self.feature_cache.values()
#             ),
#         }


# class OptimizedCrossModalAttention(nn.Module):
#     """""""""

#     def __init__(self, dim: int, numheads: int = 8, dropout: float = 0.1):
#         super().__init__()
#         self.dim = dim
#         self.numheads = num_heads
#         self.headdim = dim // num_heads
#         self.scale = self.head_dim**-0.5

        # QKV
#         self.qkv = nn.Linear(dim, dim * 3, bias=False)
#         self.proj = nn.Linear(dim, dim)
#         self.dropout = nn.Dropout(dropout)

        # 
#         self.norm = nn.LayerNorm(dim)

        # 
#         self.ffn = nn.Sequential(
#             nn.Linear(dim, dim * 4),
#             nn.GELU(),
#             nn.Dropout(dropout),
#             nn.Linear(dim * 4, dim),
#             nn.Dropout(dropout),
#         )
#         self.norm2 = nn.LayerNorm(dim)

#     def forward(self, feature_list: list[torch.Tensor]) -> torch.Tensor:
#         """""""""
#         if len(featurelist) == 1:
#             return feature_list[0]

        # 
#             x = torch.stack(featurelist, dim=1)  # [batchsize, nummodalities, dim]
#             batchsize, seqlen, _ = x.shape

        # 
#             residual = x
#             x = self.norm(x)

        # QKV
#             qkv = self.qkv(x).reshape(batchsize, seqlen, 3, self.numheads, self.headdim)
#             qkv = qkv.permute(2, 0, 3, 1, 4)  # [3, batchsize, numheads, seqlen, head_dim]
#             q, k, v = qkv[0], qkv[1], qkv[2]

        # 
#             attn = (q @ k.transpose(-2, -1)) * self.scale
#             attn = F.softmax(attn, dim=-1)
#             attn = self.dropout(attn)

        # 
#             out = (attn @ v).transpose(1, 2).reshape(batchsize, seqlen, self.dim)
#             out = self.proj(out)
#             out = self.dropout(out)

        # 
#             out = out + residual

        # 
#             residual = out
#             out = self.norm2(out)
#             out = self.ffn(out)
#             out = out + residual

        # 
#             return out.mean(dim=1)


# class ModelOptimizer:
#     """""""""

#     def __init__(self):
#         self.onnxsessions = {}
#         self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
#         logger.info(f", : {self.device}")

#     def convert_to_onnx(:
#         self,
#         model: nn.Module,
#         modelname: str,
#         inputshape: tuple[int, ...],
#         exportpath: str,
#         ):
#         """PyTorchONNX""""""
#         try:
#             model.eval()
#             dummyinput = torch.randn(inputshape).to(self.device)

#             torch.onnx.export(
#                 model,
#                 dummyinput,
#                 exportpath,
#                 export_params =True,
#                 opset_version =11,
#                 do_constant_folding =True,
#                 input_names =["input"],
#                 output_names =["output"],
#                 dynamic_axes ={"input": {0: "batch_size"}, "output": {0: "batch_size"}},
#             )

            # ONNX Runtime
#             providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]
#             session = ort.InferenceSession(exportpath, providers=providers)
#             self.onnx_sessions[model_name] = session

#             logger.info(f" {model_name} ONNX")
#             return True

#         except Exception as e:
#             logger.error(f"ONNX: {e}")
#             return False

#     def inference_with_onnx(self, model_name: str, inputdata: np.ndarray) -> np.ndarray:
#         """ONNX Runtime""""""
#         if model_name not in self.onnx_sessions: raise ValueError(f" {model_name} ONNX"):

#             session = self.onnx_sessions[model_name]
#             inputname = session.get_inputs()[0].name
#             session.get_outputs()[0].name

#             result = session.run([output_name], {inputname: input_data})
#             return result[0]

#     def optimize_model_for_mobile(self, model: nn.Module) -> nn.Module:
#         """""""""
#         try:
            # 
#             model.eval()
#             quantizedmodel = torch.quantization.quantize_dynamic(
#                 model, {nn.Linear, nn.Conv2d}, dtype=torch.qint8
#             )

            # 
#             scriptedmodel = torch.jit.script(quantizedmodel)

            # 
#             torch.jit.optimize_for_inference(scriptedmodel)

#             logger.info("")
#             return optimized_model

#         except Exception as e:
#             logger.error(f": {e}")
#             return model


# 
#             modeloptimizer = ModelOptimizer()


# def get_optimized_fusion_module(**kwargs) -> OptimizedMultimodalFusionModule:
#     """""""""
#     return OptimizedMultimodalFusionModule(**kwargs)
