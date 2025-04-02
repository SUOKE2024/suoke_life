/**
 * 地理工具函数性能基准测试
 * 测试R树优化前后的性能差异
 */

const Benchmark = require('benchmark');
const geoUtils = require('../../src/utils/geoUtils');

// 创建基准测试套件
const suite = new Benchmark.Suite();

// 测试多边形 - 模拟迷宫边界
const testPolygon = [
  [116.310, 39.910], // 西北
  [116.340, 39.910], // 东北
  [116.340, 39.900], // 东南
  [116.310, 39.900]  // 西南
];

// 测试点 - 在多边形内部
const insidePoint = [116.325, 39.905];

// 测试点 - 在多边形外部
const outsidePoint = [116.300, 39.920];

// 生成多个随机点用于批量测试
function generateRandomPoints(count) {
  const points = [];
  for (let i = 0; i < count; i++) {
    const lon = 116.300 + Math.random() * 0.050;
    const lat = 39.890 + Math.random() * 0.030;
    points.push([lon, lat]);
  }
  return points;
}

// 生成复杂多边形用于测试性能
function generateComplexPolygon(vertexCount) {
  const polygon = [];
  const centerLon = 116.325;
  const centerLat = 39.905;
  const radius = 0.020;
  
  for (let i = 0; i < vertexCount; i++) {
    const angle = (i / vertexCount) * Math.PI * 2;
    // 添加一些随机性使多边形更不规则
    const r = radius * (0.8 + Math.random() * 0.4);
    const lon = centerLon + r * Math.cos(angle);
    const lat = centerLat + r * Math.sin(angle);
    polygon.push([lon, lat]);
  }
  
  return polygon;
}

// 测试数据
const randomPoints1000 = generateRandomPoints(1000);
const complexPolygon = generateComplexPolygon(50);

// 清除R树索引缓存函数（如果存在）
function clearCache() {
  if (typeof geoUtils.clearPolygonIndexCache === 'function') {
    geoUtils.clearPolygonIndexCache();
  }
}

// 单点测试 - 多边形内
suite.add('isPointInPolygon - 单点内部', function() {
  clearCache();
  geoUtils.isPointInPolygon(insidePoint, testPolygon);
});

// 单点测试 - 多边形外
suite.add('isPointInPolygon - 单点外部', function() {
  clearCache();
  geoUtils.isPointInPolygon(outsidePoint, testPolygon);
});

// 缓存预热后测试 - 同一多边形连续测试
suite.add('isPointInPolygon - 缓存预热后', function() {
  // 不清除缓存，让R树索引被复用
  geoUtils.isPointInPolygon(insidePoint, testPolygon);
});

// 批量点测试 - 同一多边形
suite.add('isPointInPolygon - 1000点批量测试', function() {
  clearCache();
  for (const point of randomPoints1000) {
    geoUtils.isPointInPolygon(point, testPolygon);
  }
});

// 复杂多边形测试
suite.add('isPointInPolygon - 复杂多边形(50顶点)', function() {
  clearCache();
  for (let i = 0; i < 100; i++) {
    const point = randomPoints1000[i];
    geoUtils.isPointInPolygon(point, complexPolygon);
  }
});

// 添加完成事件处理
suite
  .on('cycle', function(event) {
    console.log(String(event.target));
  })
  .on('complete', function() {
    console.log('最快测试: ' + this.filter('fastest').map('name'));
    console.log('最慢测试: ' + this.filter('slowest').map('name'));
    
    // 输出性能比较分析
    const results = {};
    this.forEach(benchmark => {
      results[benchmark.name] = {
        hz: benchmark.hz,
        rme: benchmark.stats.rme,
        mean: benchmark.stats.mean
      };
    });
    
    console.log('\n性能分析结果:');
    console.log('==============================');
    console.log('每秒操作次数越高越好，相对误差(rme)越低越好\n');
    
    Object.keys(results).forEach(name => {
      const { hz, rme, mean } = results[name];
      console.log(`${name}:`);
      console.log(`  每秒操作次数: ${Math.round(hz).toLocaleString()} ops/sec`);
      console.log(`  平均执行时间: ${(mean * 1000).toFixed(4)} ms`);
      console.log(`  相对误差: ±${rme.toFixed(2)}%`);
      console.log('------------------------------');
    });
  })
  .run({ 'async': true });

console.log('正在运行性能基准测试...\n');