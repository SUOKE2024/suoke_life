/**
 * 望诊服务模拟器 - 用于本地开发和测试
 */
const express = require('express');
const cors = require('cors');
const app = express();
const PORT = 3001;

// 中间件
app.use(cors());
app.use(express.json());

// 健康检查端点
app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'looking-diagnosis-mock' });
});

// 诊断接口
app.post('/diagnose', (req, res) => {
  console.log('收到望诊请求:', req.body);
  
  const { image, parameters } = req.body;
  
  // 模拟不同的诊断结果
  let result;
  const random = Math.random();
  
  if (random < 0.3) {
    result = {
      face_color: "偏红",
      face_characteristics: ["颧红", "眼睛明亮"],
      tongue_color: "淡红",
      tongue_coating: "薄白",
      diagnosis: "风热证",
      constitution_tendency: "阳虚质",
      recommendations: ["避免辛辣刺激食物", "保持情绪舒畅"]
    };
  } else if (random < 0.6) {
    result = {
      face_color: "偏白",
      face_characteristics: ["面色无华", "眼睑浮肿"],
      tongue_color: "淡白",
      tongue_coating: "白腻",
      diagnosis: "痰湿证",
      constitution_tendency: "痰湿质",
      recommendations: ["控制饮食", "增加运动"]
    };
  } else {
    result = {
      face_color: "偏黄",
      face_characteristics: ["黄褐斑", "眼睛疲惫"],
      tongue_color: "淡黄",
      tongue_coating: "薄黄",
      diagnosis: "脾虚证",
      constitution_tendency: "气虚质",
      recommendations: ["健脾益气", "规律作息"]
    };
  }
  
  // 模拟处理延迟
  setTimeout(() => {
    res.json({
      result,
      confidence: 0.85 + (Math.random() * 0.1)
    });
  }, 300 + Math.floor(Math.random() * 300));
});

// 启动服务器
app.listen(PORT, () => {
  console.log(`望诊服务模拟器运行在 http://localhost:${PORT}`);
}); 