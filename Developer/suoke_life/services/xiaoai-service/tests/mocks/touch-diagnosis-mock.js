/**
 * 切诊服务模拟器 - 用于本地开发和测试
 */
const express = require('express');
const cors = require('cors');
const app = express();
const PORT = 3004;

// 中间件
app.use(cors());
app.use(express.json());

// 健康检查端点
app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'touch-diagnosis-mock' });
});

// 诊断接口
app.post('/diagnose', (req, res) => {
  console.log('收到切诊请求:', req.body);
  
  const { pulse_data, skin_data } = req.body;
  
  // 模拟不同的诊断结果
  let result;
  const random = Math.random();
  
  if (random < 0.3) {
    result = {
      pulse_type: "弦脉",
      pulse_characteristics: ["有力", "长而直"],
      skin_condition: "偏干",
      temperature: "微热",
      diagnosis: "肝气郁结",
      constitution_type: "木郁体质",
      treatment_principles: ["疏肝解郁", "理气活血"]
    };
  } else if (random < 0.6) {
    result = {
      pulse_type: "濡脉",
      pulse_characteristics: ["柔软", "缓慢无力"],
      skin_condition: "湿润",
      temperature: "微凉",
      diagnosis: "脾胃虚弱",
      constitution_type: "脾虚湿盛体质",
      treatment_principles: ["健脾益气", "化湿利水"]
    };
  } else {
    result = {
      pulse_type: "数脉",
      pulse_characteristics: ["急促", "跳动快"],
      skin_condition: "干燥",
      temperature: "发热",
      diagnosis: "阴虚内热",
      constitution_type: "阴虚火旺体质",
      treatment_principles: ["滋阴降火", "清热除烦"]
    };
  }
  
  // 模拟处理延迟
  setTimeout(() => {
    res.json({
      result,
      confidence: 0.75 + (Math.random() * 0.15)
    });
  }, 180 + Math.floor(Math.random() * 250));
});

// 启动服务器
app.listen(PORT, () => {
  console.log(`切诊服务模拟器运行在 http://localhost:${PORT}`);
});