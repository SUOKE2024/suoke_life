/**
 * 问诊服务模拟器 - 用于本地开发和测试
 */
const express = require('express');
const cors = require('cors');
const app = express();
const PORT = 3002;

// 中间件
app.use(cors());
app.use(express.json());

// 健康检查端点
app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'inquiry-diagnosis-mock' });
});

// 诊断接口
app.post('/diagnose', (req, res) => {
  console.log('收到问诊请求:', req.body);
  
  const { symptoms, history, questions } = req.body;
  
  // 模拟不同的诊断结果
  let result;
  const random = Math.random();
  
  if (random < 0.3) {
    result = {
      main_symptoms: ["头痛", "发热", "怕冷"],
      secondary_symptoms: ["鼻塞", "咳嗽", "咽痛"],
      diagnosis: "外感风寒",
      constitution_analysis: "偏阳虚体质",
      treatment_suggestions: ["疏风散寒", "及时保暖"],
      health_advice: ["避免生冷食物", "多喝热水", "保证充足休息"]
    };
  } else if (random < 0.6) {
    result = {
      main_symptoms: ["腹痛", "腹泻", "消化不良"],
      secondary_symptoms: ["口苦", "嗳气", "食欲不振"],
      diagnosis: "脾胃湿热",
      constitution_analysis: "湿热体质",
      treatment_suggestions: ["清热利湿", "健脾和胃"],
      health_advice: ["清淡饮食", "规律作息", "避免过度劳累"]
    };
  } else {
    result = {
      main_symptoms: ["心悸", "失眠", "多梦"],
      secondary_symptoms: ["健忘", "疲乏", "心烦"],
      diagnosis: "心脾两虚",
      constitution_analysis: "气血不足",
      treatment_suggestions: ["补心安神", "健脾益气"],
      health_advice: ["保持情绪稳定", "饮食规律", "适当运动"]
    };
  }
  
  // 模拟处理延迟
  setTimeout(() => {
    res.json({
      result,
      confidence: 0.78 + (Math.random() * 0.15)
    });
  }, 200 + Math.floor(Math.random() * 300));
});

// 启动服务器
app.listen(PORT, () => {
  console.log(`问诊服务模拟器运行在 http://localhost:${PORT}`);
}); 