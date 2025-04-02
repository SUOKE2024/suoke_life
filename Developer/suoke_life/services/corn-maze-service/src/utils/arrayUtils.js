/**
 * 数组工具函数
 */

/**
 * 随机打乱数组
 * @param {Array} array - 要打乱的数组
 * @param {Function} randomFunc - 随机数生成函数，不提供则使用Math.random
 * @returns {Array} 打乱后的数组
 */
const shuffleArray = (array, randomFunc = Math.random) => {
  const result = [...array];
  for (let i = result.length - 1; i > 0; i--) {
    const j = Math.floor(randomFunc() * (i + 1));
    [result[i], result[j]] = [result[j], result[i]];
  }
  return result;
};

/**
 * 从数组中获取随机元素
 * @param {Array} array - 源数组
 * @param {Function} randomFunc - 随机数生成函数，不提供则使用Math.random
 * @returns {*} 随机元素
 */
const getRandomElement = (array, randomFunc = Math.random) => {
  if (!array.length) return null;
  const index = Math.floor(randomFunc() * array.length);
  return array[index];
};

/**
 * 二维数组深拷贝
 * @param {Array<Array>} array - 二维数组
 * @returns {Array<Array>} 拷贝后的数组
 */
const deepCopy2DArray = (array) => {
  return array.map(row => [...row]);
};

/**
 * 旋转二维数组90度
 * @param {Array<Array>} array - 二维数组
 * @param {number} times - 旋转次数(1=90度, 2=180度, 3=270度)
 * @returns {Array<Array>} 旋转后的数组
 */
const rotate2DArray = (array, times = 1) => {
  times = ((times % 4) + 4) % 4; // 规范化到0-3之间
  if (times === 0) return deepCopy2DArray(array);
  
  let result = array;
  for (let i = 0; i < times; i++) {
    result = rotateCW(result);
  }
  return result;
};

/**
 * 顺时针旋转二维数组90度
 * @param {Array<Array>} array - 二维数组
 * @returns {Array<Array>} 旋转后的数组
 */
const rotateCW = (array) => {
  const height = array.length;
  if (height === 0) return [];
  
  const width = array[0].length;
  const result = Array(width).fill().map(() => Array(height).fill(0));
  
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      result[x][height - 1 - y] = array[y][x];
    }
  }
  
  return result;
};

/**
 * 在二维数组中找到所有匹配条件的单元格
 * @param {Array<Array>} array - 二维数组
 * @param {Function} predicate - 判断函数，接收参数(value, x, y)
 * @returns {Array<Object>} 匹配的单元格坐标[{x, y, value}]
 */
const findAllInGrid = (array, predicate) => {
  const results = [];
  
  for (let y = 0; y < array.length; y++) {
    for (let x = 0; x < array[y].length; x++) {
      if (predicate(array[y][x], x, y)) {
        results.push({ x, y, value: array[y][x] });
      }
    }
  }
  
  return results;
};

/**
 * 比较两个二维数组是否相等
 * @param {Array<Array>} array1 - 第一个二维数组
 * @param {Array<Array>} array2 - 第二个二维数组
 * @returns {boolean} 是否相等
 */
const isEqual2DArray = (array1, array2) => {
  if (array1.length !== array2.length) return false;
  
  for (let y = 0; y < array1.length; y++) {
    if (array1[y].length !== array2[y].length) return false;
    
    for (let x = 0; x < array1[y].length; x++) {
      if (array1[y][x] !== array2[y][x]) return false;
    }
  }
  
  return true;
};

module.exports = {
  shuffleArray,
  getRandomElement,
  deepCopy2DArray,
  rotate2DArray,
  findAllInGrid,
  isEqual2DArray
}; 