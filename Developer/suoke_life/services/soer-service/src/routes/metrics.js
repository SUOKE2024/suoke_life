'use strict';

/**
 * 指标路由
 * 提供服务监控和性能指标的端点
 */
module.exports = async function (fastify, opts) {
  // 实现一个简单的指标收集器
  const metrics = {
    http_requests_total: 0,
    http_request_duration_seconds: [],
    active_users: new Set(),
    inference_requests_total: 0,
    health_insights_generated_total: 0,
    recommendation_requests_total: 0,
    environment_sensing_requests_total: 0,
    multimodal_sensing_requests_total: 0,
    errors_total: 0,
    uptime_seconds: 0
  };
  
  // 启动时间
  const startTime = Date.now();
  
  // 添加请求拦截器，用于收集指标
  fastify.addHook('onRequest', (request, reply, done) => {
    // 增加请求计数
    metrics.http_requests_total++;
    
    // 记录请求开始时间
    request.metrics = {
      startTime: process.hrtime()
    };
    
    done();
  });
  
  // 请求完成时收集指标
  fastify.addHook('onResponse', (request, reply, done) => {
    // 计算请求持续时间
    const hrTime = process.hrtime(request.metrics.startTime);
    const durationInSeconds = hrTime[0] + (hrTime[1] / 1e9);
    
    // 记录持续时间
    metrics.http_request_duration_seconds.push({
      path: request.routerPath || request.url,
      method: request.method,
      status: reply.statusCode,
      duration: durationInSeconds
    });
    
    // 只保留最近1000个请求的持续时间
    if (metrics.http_request_duration_seconds.length > 1000) {
      metrics.http_request_duration_seconds.shift();
    }
    
    // 如果是用户相关请求，记录活跃用户
    if (request.params.userId) {
      metrics.active_users.add(request.params.userId);
    }
    
    // 根据请求路径更新特定指标
    const url = request.url;
    
    if (url.includes('/api/v1/agent/message')) {
      metrics.inference_requests_total++;
    } else if (url.includes('/api/v1/insights')) {
      metrics.health_insights_generated_total++;
    } else if (url.includes('/api/v1/recommendations')) {
      metrics.recommendation_requests_total++;
    } else if (url.includes('/api/v1/sensing/environment')) {
      metrics.environment_sensing_requests_total++;
    } else if (url.includes('/api/v1/sensing/multimodal')) {
      metrics.multimodal_sensing_requests_total++;
    }
    
    // 如果是错误响应，增加错误计数
    if (reply.statusCode >= 400) {
      metrics.errors_total++;
    }
    
    done();
  });
  
  // 指标端点
  fastify.get('/', async (request, reply) => {
    // 计算运行时间
    metrics.uptime_seconds = Math.floor((Date.now() - startTime) / 1000);
    
    // 格式化指标为Prometheus文本格式
    let output = '';
    
    // HTTP请求总数
    output += '# HELP soer_http_requests_total 索儿服务处理的HTTP请求总数\n';
    output += '# TYPE soer_http_requests_total counter\n';
    output += `soer_http_requests_total ${metrics.http_requests_total}\n`;
    
    // 错误总数
    output += '# HELP soer_errors_total 索儿服务发生的错误总数\n';
    output += '# TYPE soer_errors_total counter\n';
    output += `soer_errors_total ${metrics.errors_total}\n`;
    
    // 活跃用户数
    output += '# HELP soer_active_users 索儿服务的活跃用户数\n';
    output += '# TYPE soer_active_users gauge\n';
    output += `soer_active_users ${metrics.active_users.size}\n`;
    
    // 推理请求总数
    output += '# HELP soer_inference_requests_total 索儿服务处理的推理请求总数\n';
    output += '# TYPE soer_inference_requests_total counter\n';
    output += `soer_inference_requests_total ${metrics.inference_requests_total}\n`;
    
    // 健康洞察生成总数
    output += '# HELP soer_health_insights_generated_total 索儿服务生成的健康洞察总数\n';
    output += '# TYPE soer_health_insights_generated_total counter\n';
    output += `soer_health_insights_generated_total ${metrics.health_insights_generated_total}\n`;
    
    // 推荐请求总数
    output += '# HELP soer_recommendation_requests_total 索儿服务处理的推荐请求总数\n';
    output += '# TYPE soer_recommendation_requests_total counter\n';
    output += `soer_recommendation_requests_total ${metrics.recommendation_requests_total}\n`;
    
    // 环境感知请求总数
    output += '# HELP soer_environment_sensing_requests_total 索儿服务处理的环境感知请求总数\n';
    output += '# TYPE soer_environment_sensing_requests_total counter\n';
    output += `soer_environment_sensing_requests_total ${metrics.environment_sensing_requests_total}\n`;
    
    // 多模态感知请求总数
    output += '# HELP soer_multimodal_sensing_requests_total 索儿服务处理的多模态感知请求总数\n';
    output += '# TYPE soer_multimodal_sensing_requests_total counter\n';
    output += `soer_multimodal_sensing_requests_total ${metrics.multimodal_sensing_requests_total}\n`;
    
    // 运行时间
    output += '# HELP soer_uptime_seconds 索儿服务的运行时间（秒）\n';
    output += '# TYPE soer_uptime_seconds gauge\n';
    output += `soer_uptime_seconds ${metrics.uptime_seconds}\n`;
    
    // 请求持续时间分布
    output += '# HELP soer_request_duration_seconds 索儿服务请求处理时间（秒）\n';
    output += '# TYPE soer_request_duration_seconds histogram\n';
    
    // 计算请求持续时间分布
    const durationBuckets = [0.01, 0.05, 0.1, 0.5, 1, 2, 5, 10];
    const pathCounts = {};
    
    // 初始化桶
    metrics.http_request_duration_seconds.forEach(req => {
      const path = req.path || 'unknown';
      const method = req.method;
      const status = Math.floor(req.status / 100) + 'xx';
      const key = `${method}:${path}:${status}`;
      
      if (!pathCounts[key]) {
        pathCounts[key] = {
          count: 0,
          sum: 0,
          buckets: {}
        };
        
        durationBuckets.forEach(bucket => {
          pathCounts[key].buckets[bucket] = 0;
        });
      }
      
      pathCounts[key].count++;
      pathCounts[key].sum += req.duration;
      
      // 填充桶
      for (const bucket of durationBuckets) {
        if (req.duration <= bucket) {
          pathCounts[key].buckets[bucket]++;
        }
      }
    });
    
    // 生成直方图指标
    for (const [key, data] of Object.entries(pathCounts)) {
      const [method, path, status] = key.split(':');
      
      // 桶计数
      for (const [bucket, count] of Object.entries(data.buckets)) {
        output += `soer_request_duration_seconds_bucket{method="${method}",path="${path}",status="${status}",le="${bucket}"} ${count}\n`;
      }
      
      // 无穷大桶
      output += `soer_request_duration_seconds_bucket{method="${method}",path="${path}",status="${status}",le="+Inf"} ${data.count}\n`;
      
      // 总计数和总和
      output += `soer_request_duration_seconds_count{method="${method}",path="${path}",status="${status}"} ${data.count}\n`;
      output += `soer_request_duration_seconds_sum{method="${method}",path="${path}",status="${status}"} ${data.sum.toFixed(6)}\n`;
    }
    
    // 模型状态指标
    output += '# HELP soer_model_status 索儿服务模型状态\n';
    output += '# TYPE soer_model_status gauge\n';
    
    // 获取模型状态
    const agentStatus = await fastify.agentService.getStatus();
    
    for (const [name, model] of Object.entries(agentStatus.models)) {
      output += `soer_model_status{name="${name}",type="${model.type}"} ${model.loaded ? 1 : 0}\n`;
    }
    
    // 设置响应类型为Prometheus文本格式
    reply.header('Content-Type', 'text/plain; version=0.0.4');
    
    return output;
  });
};