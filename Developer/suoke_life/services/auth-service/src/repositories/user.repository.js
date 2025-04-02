/**
 * 用户仓库
 */
const userRepository = {
  /**
   * 根据用户名获取用户
   * @param {string} username 
   * @returns {Promise<Object|null>}
   */
  getUserByUsername: async (username) => {
    // 这里是实际的数据库操作，测试中会被模拟
    throw new Error('需要在测试中被模拟');
  },

  /**
   * 根据邮箱获取用户
   * @param {string} email 
   * @returns {Promise<Object|null>}
   */
  getUserByEmail: async (email) => {
    // 这里是实际的数据库操作，测试中会被模拟
    throw new Error('需要在测试中被模拟');
  },

  /**
   * 创建用户
   * @param {Object} userData 
   * @returns {Promise<Object>}
   */
  createUser: async (userData) => {
    // 这里是实际的数据库操作，测试中会被模拟
    throw new Error('需要在测试中被模拟');
  }
};

module.exports = userRepository; 