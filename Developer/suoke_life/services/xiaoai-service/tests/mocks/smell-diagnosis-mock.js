/**
 * 闻诊服务模拟器 - 用于本地开发和测试
 */
const express = require('express');
const cors = require('cors');
const app = express();
const PORT = 3003;

// 中间件
app.use(cors());
app.use(express.json());

// 健康检查端点
app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'smell-diagnosis-mock' });
});

// 诊断接口
app.post('/diagnose', (req, res) => {
  console.log('收到闻诊请求:', req.body);
  
  const { audio_data, descriptions } = req.body;
  
  // 模拟不同的诊断结果
  let result;
  const random = Math.random();
  
  if (random < 0.3) {
    result = {
      smell_characteristics: ["酸腐气味", "气息偏弱"],
      voice_analysis: ["声音低沉", "说话无力"],
      breath_pattern: "短而浅",
      diagnosis: "肝气郁结",
      related_organs: ["肝", "脾"],
      recommendations: ["疏肝理气", "调畅情志"]
    };
  } else if (random < 0.6) {
    result = {
      smell_characteristics: ["腥臭气味", "口气重"],
      voice_analysis: ["声音嘶哑", "语速缓慢"],
      breath_pattern: "粗而长",
      diagnosis: "热毒内蕴",
      related_organs: ["肺", "大肠"],
      recommendations: ["清热解毒", "调理肠胃"]
    };
  } else {
    result = {
      smell_characteristics: ["淡而无味", "汗液清淡"],
      voice_analysis: ["声音颤抖", "言语不清"],
      breath_pattern: "弱而不均",
      diagnosis: "脾肾阳虚",
      related_organs: ["脾", "肾"],
      recommendations: ["温补脾肾", "益气固表"]
    };
  }
  
  // 模拟处理延迟
  setTimeout(() => {
    res.json({
      result,
      confidence: 0.72 + (Math.random() * 0.12)
    });
  }, 150 + Math.floor(Math.random() * 200));
});

// 启动服务器
app.listen(PORT, () => {
  console.log(`闻诊服务模拟器运行在 http://localhost:${PORT}`);
});