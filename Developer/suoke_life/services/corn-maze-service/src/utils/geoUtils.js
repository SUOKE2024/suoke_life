/**
 * 地理位置工具
 * 提供各种地理计算功能
 */

// 引入R树索引库
const RBush = require('rbush');

// 创建R树索引缓存
const polygonIndexCache = new Map();

/**
 * 计算两个坐标点之间的距离（哈弗辛公式）
 * @param {number} lat1 - 第一点纬度
 * @param {number} lon1 - 第一点经度
 * @param {number} lat2 - 第二点纬度
 * @param {number} lon2 - 第二点经度
 * @returns {number} - 返回距离（米）
 */
function calculateDistance(lat1, lon1, lat2, lon2) {
  const R = 6371e3; // 地球半径（米）
  const φ1 = lat1 * Math.PI / 180;
  const φ2 = lat2 * Math.PI / 180;
  const Δφ = (lat2 - lat1) * Math.PI / 180;
  const Δλ = (lon2 - lon1) * Math.PI / 180;

  const a = Math.sin(Δφ / 2) * Math.sin(Δφ / 2) +
            Math.cos(φ1) * Math.cos(φ2) *
            Math.sin(Δλ / 2) * Math.sin(Δλ / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

  return R * c;
}

/**
 * 为多边形创建R树索引
 * @param {Array} polygon - 多边形坐标数组 [[longitude, latitude], ...]
 * @returns {Object} - R树索引对象
 */
function createPolygonIndex(polygon) {
  // 生成多边形的唯一标识符
  const polygonId = JSON.stringify(polygon);
  
  // 检查缓存中是否已存在该多边形的索引
  if (polygonIndexCache.has(polygonId)) {
    return polygonIndexCache.get(polygonId);
  }
  
  // 创建新的R树索引
  const tree = new RBush();
  const items = [];
  
  // 为多边形的每条边创建边界框
  for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
    const xi = polygon[i][0];
    const yi = polygon[i][1];
    const xj = polygon[j][0];
    const yj = polygon[j][1];
    
    // 创建边界框
    items.push({
      minX: Math.min(xi, xj),
      minY: Math.min(yi, yj),
      maxX: Math.max(xi, xj),
      maxY: Math.max(yi, yj),
      edge: [i, j] // 存储边的索引
    });
  }
  
  // 批量插入边界框
  tree.load(items);
  
  // 创建索引对象
  const index = {
    tree,
    polygon
  };
  
  // 将索引存入缓存
  polygonIndexCache.set(polygonId, index);
  
  return index;
}

/**
 * 计算点是否在多边形内（优化版，使用R树索引）
 * @param {Array} point - 点坐标 [longitude, latitude]
 * @param {Array} polygon - 多边形坐标数组 [[longitude, latitude], ...]
 * @returns {boolean} - 返回点是否在多边形内
 */
function isPointInPolygon(point, polygon) {
  const x = point[0];
  const y = point[1];
  
  // 快速边界框检查
  const bbox = getPolygonBoundingBox(polygon);
  if (x < bbox.minLon || x > bbox.maxLon || y < bbox.minLat || y > bbox.maxLat) {
    return false;
  }
  
  // 获取多边形索引
  const index = createPolygonIndex(polygon);
  
  // 创建射线（向右无限延伸）
  const ray = {
    minX: x,
    minY: y,
    maxX: Infinity,
    maxY: y
  };
  
  // 查询与射线相交的边
  const intersections = index.tree.search(ray).filter(item => {
    const i = item.edge[0];
    const j = item.edge[1];
    const xi = polygon[i][0];
    const yi = polygon[i][1];
    const xj = polygon[j][0];
    const yj = polygon[j][1];
    
    // 检查边是否与射线相交
    return ((yi > y) !== (yj > y)) &&
           (x < (xj - xi) * (y - yi) / (yj - yi) + xi);
  });
  
  // 计算相交次数
  return intersections.length % 2 === 1;
}

/**
 * 获取多边形的边界框
 * @param {Array} polygon - 多边形坐标数组 [[longitude, latitude], ...]
 * @returns {Object} - 返回边界框 {minLon, minLat, maxLon, maxLat}
 */
function getPolygonBoundingBox(polygon) {
  let minLon = Infinity;
  let minLat = Infinity;
  let maxLon = -Infinity;
  let maxLat = -Infinity;
  
  for (const point of polygon) {
    const lon = point[0];
    const lat = point[1];
    
    minLon = Math.min(minLon, lon);
    minLat = Math.min(minLat, lat);
    maxLon = Math.max(maxLon, lon);
    maxLat = Math.max(maxLat, lat);
  }
  
  return { minLon, minLat, maxLon, maxLat };
}

/**
 * 清除多边形索引缓存
 * @param {Array} polygon - 可选，特定多边形坐标数组
 */
function clearPolygonIndexCache(polygon) {
  if (polygon) {
    const polygonId = JSON.stringify(polygon);
    polygonIndexCache.delete(polygonId);
  } else {
    polygonIndexCache.clear();
  }
}

/**
 * 生成指定距离内的随机点
 * @param {Array} center - 中心点坐标 [longitude, latitude]
 * @param {number} maxDistance - 最大距离（米）
 * @returns {Array} - 返回随机点坐标 [longitude, latitude]
 */
function generateRandomPointNearby(center, maxDistance) {
  const centerLon = center[0];
  const centerLat = center[1];
  
  // 地球半径（米）
  const R = 6371e3;
  
  // 随机距离和方向
  const distance = Math.random() * maxDistance;
  const bearing = Math.random() * Math.PI * 2;
  
  // 计算经纬度偏移
  const distRatio = distance / R;
  const lat1 = centerLat * Math.PI / 180;
  const lon1 = centerLon * Math.PI / 180;
  
  const lat2 = Math.asin(Math.sin(lat1) * Math.cos(distRatio) +
                         Math.cos(lat1) * Math.sin(distRatio) * Math.cos(bearing));
  const lon2 = lon1 + Math.atan2(Math.sin(bearing) * Math.sin(distRatio) * Math.cos(lat1),
                                 Math.cos(distRatio) - Math.sin(lat1) * Math.sin(lat2));
  
  // 转换回角度
  const newLat = lat2 * 180 / Math.PI;
  const newLon = lon2 * 180 / Math.PI;
  
  return [newLon, newLat];
}

/**
 * 将边界框转换为GeoJSON多边形
 * @param {Object} bbox - 边界框 {minLon, minLat, maxLon, maxLat}
 * @returns {Object} - 返回GeoJSON多边形
 */
function bboxToGeoJSONPolygon(bbox) {
  const { minLon, minLat, maxLon, maxLat } = bbox;
  
  return {
    type: 'Polygon',
    coordinates: [[
      [minLon, minLat],
      [maxLon, minLat],
      [maxLon, maxLat],
      [minLon, maxLat],
      [minLon, minLat]
    ]]
  };
}

/**
 * 计算路径的总长度
 * @param {Array} path - 路径点数组 [[longitude, latitude], ...]
 * @returns {number} - 返回路径总长度（米）
 */
function calculatePathLength(path) {
  let totalDistance = 0;
  
  for (let i = 0; i < path.length - 1; i++) {
    const point1 = path[i];
    const point2 = path[i + 1];
    
    totalDistance += calculateDistance(
      point1[1], point1[0],
      point2[1], point2[0]
    );
  }
  
  return totalDistance;
}

/**
 * 格式化坐标为固定精度的字符串
 * @param {Array} coordinates - 坐标 [longitude, latitude]
 * @param {number} precision - 精度（小数位数）
 * @returns {string} - 返回格式化后的坐标字符串
 */
function formatCoordinates(coordinates, precision = 6) {
  return `${coordinates[1].toFixed(precision)},${coordinates[0].toFixed(precision)}`;
}

module.exports = {
  calculateDistance,
  isPointInPolygon,
  getPolygonBoundingBox,
  generateRandomPointNearby,
  bboxToGeoJSONPolygon,
  calculatePathLength,
  formatCoordinates,
  clearPolygonIndexCache
}; 