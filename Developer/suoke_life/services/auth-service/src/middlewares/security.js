const rateLimit = require('express-rate-limit');
const helmet = require('helmet');

// 建议添加的防护措施：
app.use(rateLimit({
  windowMs: 15 * 60 * 1000, // 15分钟
  max: 100 // 每个IP限制100次请求
}));

app.use(helmet()); // 添加安全头 