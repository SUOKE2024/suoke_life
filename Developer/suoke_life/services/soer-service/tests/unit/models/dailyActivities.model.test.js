/**
 * 日常活动模型单元测试
 */
const {
  formatActivityForDb,
  formatActivityForApi,
} = require('../../../src/models/dailyActivities.model');

describe('日常活动模型', () => {
  describe('formatActivityForDb', () => {
    test('应正确转换API格式到数据库格式', () => {
      // 准备测试数据
      const apiActivity = {
        userId: 'user123',
        type: 'walking',
        typeLabel: '步行',
        description: '早上散步',
        duration: 30,
        distance: 2.5,
        calories: 120,
        startTime: '2023-04-01T08:00:00Z',
        endTime: '2023-04-01T08:30:00Z',
        locationName: '人民公园',
        locationCoordinates: { latitude: 31.23, longitude: 121.47 },
        heartRate: { average: 110, max: 125, min: 95 },
        tags: ['晨练', '户外'],
        mood: '轻松',
        notes: '天气很好',
        data: { steps: 3500 }
      };

      // 执行转换
      const dbActivity = formatActivityForDb(apiActivity);

      // 验证结果
      expect(dbActivity).toHaveProperty('user_id', 'user123');
      expect(dbActivity).not.toHaveProperty('userId');
      
      expect(dbActivity).toHaveProperty('type_label', '步行');
      expect(dbActivity).not.toHaveProperty('typeLabel');
      
      expect(dbActivity).toHaveProperty('start_time', '2023-04-01T08:00:00Z');
      expect(dbActivity).not.toHaveProperty('startTime');
      
      expect(dbActivity).toHaveProperty('end_time', '2023-04-01T08:30:00Z');
      expect(dbActivity).not.toHaveProperty('endTime');
      
      expect(dbActivity).toHaveProperty('location_name', '人民公园');
      expect(dbActivity).not.toHaveProperty('locationName');
      
      // 验证JSON字段
      expect(dbActivity).toHaveProperty('location_coordinates');
      expect(typeof dbActivity.location_coordinates).toBe('string');
      expect(JSON.parse(dbActivity.location_coordinates)).toEqual({ latitude: 31.23, longitude: 121.47 });
      
      expect(dbActivity).toHaveProperty('heart_rate');
      expect(typeof dbActivity.heart_rate).toBe('string');
      expect(JSON.parse(dbActivity.heart_rate)).toEqual({ average: 110, max: 125, min: 95 });
      
      expect(dbActivity).toHaveProperty('tags');
      expect(typeof dbActivity.tags).toBe('string');
      expect(JSON.parse(dbActivity.tags)).toEqual(['晨练', '户外']);
      
      expect(dbActivity).toHaveProperty('data');
      expect(typeof dbActivity.data).toBe('string');
      expect(JSON.parse(dbActivity.data)).toEqual({ steps: 3500 });
      
      // 验证未更改的字段
      expect(dbActivity).toHaveProperty('type', 'walking');
      expect(dbActivity).toHaveProperty('description', '早上散步');
      expect(dbActivity).toHaveProperty('duration', 30);
      expect(dbActivity).toHaveProperty('distance', 2.5);
      expect(dbActivity).toHaveProperty('calories', 120);
      expect(dbActivity).toHaveProperty('mood', '轻松');
      expect(dbActivity).toHaveProperty('notes', '天气很好');
    });

    test('应处理缺少可选字段的情况', () => {
      // 只包含必要字段的活动
      const minimalActivity = {
        userId: 'user123',
        type: 'walking',
        description: '散步',
        duration: 20
      };

      const dbActivity = formatActivityForDb(minimalActivity);

      expect(dbActivity).toHaveProperty('user_id', 'user123');
      expect(dbActivity).toHaveProperty('type', 'walking');
      expect(dbActivity).toHaveProperty('description', '散步');
      expect(dbActivity).toHaveProperty('duration', 20);
      expect(dbActivity).not.toHaveProperty('userId');
    });
  });

  describe('formatActivityForApi', () => {
    test('应正确转换数据库格式到API格式', () => {
      // 准备测试数据
      const dbActivity = {
        id: 'act123',
        user_id: 'user123',
        type: 'walking',
        type_label: '步行',
        description: '早上散步',
        duration: 30,
        distance: 2.5,
        calories: 120,
        start_time: '2023-04-01T08:00:00Z',
        end_time: '2023-04-01T08:30:00Z',
        location_name: '人民公园',
        location_coordinates: JSON.stringify({ latitude: 31.23, longitude: 121.47 }),
        heart_rate: JSON.stringify({ average: 110, max: 125, min: 95 }),
        tags: JSON.stringify(['晨练', '户外']),
        mood: '轻松',
        notes: '天气很好',
        data: JSON.stringify({ steps: 3500 }),
        created_at: '2023-04-01T08:35:00Z',
        updated_at: '2023-04-01T08:35:00Z'
      };

      // 执行转换
      const apiActivity = formatActivityForApi(dbActivity);

      // 验证结果
      expect(apiActivity).toHaveProperty('userId', 'user123');
      expect(apiActivity).not.toHaveProperty('user_id');
      
      expect(apiActivity).toHaveProperty('typeLabel', '步行');
      expect(apiActivity).not.toHaveProperty('type_label');
      
      expect(apiActivity).toHaveProperty('startTime', '2023-04-01T08:00:00Z');
      expect(apiActivity).not.toHaveProperty('start_time');
      
      expect(apiActivity).toHaveProperty('endTime', '2023-04-01T08:30:00Z');
      expect(apiActivity).not.toHaveProperty('end_time');
      
      expect(apiActivity).toHaveProperty('locationName', '人民公园');
      expect(apiActivity).not.toHaveProperty('location_name');
      
      // 验证JSON字段解析
      expect(apiActivity).toHaveProperty('locationCoordinates');
      expect(typeof apiActivity.locationCoordinates).toBe('object');
      expect(apiActivity.locationCoordinates).toEqual({ latitude: 31.23, longitude: 121.47 });
      
      expect(apiActivity).toHaveProperty('heartRate');
      expect(typeof apiActivity.heartRate).toBe('object');
      expect(apiActivity.heartRate).toEqual({ average: 110, max: 125, min: 95 });
      
      expect(apiActivity).toHaveProperty('tags');
      expect(Array.isArray(apiActivity.tags)).toBe(true);
      expect(apiActivity.tags).toEqual(['晨练', '户外']);
      
      expect(apiActivity).toHaveProperty('data');
      expect(typeof apiActivity.data).toBe('object');
      expect(apiActivity.data).toEqual({ steps: 3500 });
      
      // 验证未更改的字段
      expect(apiActivity).toHaveProperty('id', 'act123');
      expect(apiActivity).toHaveProperty('type', 'walking');
      expect(apiActivity).toHaveProperty('description', '早上散步');
      expect(apiActivity).toHaveProperty('duration', 30);
      expect(apiActivity).toHaveProperty('distance', 2.5);
      expect(apiActivity).toHaveProperty('calories', 120);
      expect(apiActivity).toHaveProperty('mood', '轻松');
      expect(apiActivity).toHaveProperty('notes', '天气很好');
      expect(apiActivity).toHaveProperty('created_at', '2023-04-01T08:35:00Z');
      expect(apiActivity).toHaveProperty('updated_at', '2023-04-01T08:35:00Z');
    });

    test('应处理无效的JSON字段', () => {
      const dbActivity = {
        id: 'act123',
        user_id: 'user123',
        type: 'walking',
        description: '散步',
        duration: 20,
        location_coordinates: '无效JSON',
        heart_rate: '{不是有效JSON}',
        tags: 'also not json',
        data: 'invalid data'
      };

      const apiActivity = formatActivityForApi(dbActivity);

      expect(apiActivity).toHaveProperty('userId', 'user123');
      expect(apiActivity).toHaveProperty('locationCoordinates', '无效JSON');
      expect(apiActivity).toHaveProperty('heartRate', '{不是有效JSON}');
      expect(apiActivity).toHaveProperty('tags', 'also not json');
      expect(apiActivity).toHaveProperty('data', 'invalid data');
    });
  });
}); 