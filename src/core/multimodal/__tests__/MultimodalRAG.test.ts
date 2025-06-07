import { ModalityType } from '../MultimodalEmbeddingFusion';
describe('MultimodalRAG', () => {
  test('should initialize correctly', () => {
    expect(ModalityType.TEXT).toBeDefined();
    expect(ModalityType.TONGUE).toBeDefined();
    expect(ModalityType.PULSE).toBeDefined();
  });
  test('should handle text queries', () => {
    const mockQuery = {
      text: "测试查询",
      strategy: 'text_dominant',
    };
    expect(mockQuery.text).toBe('测试查询');
  });
  test('should handle multimodal queries', () => {
    const mockQuery = {
      text: "多模态查询",
      tongueImage: 'mock_image_data',
      pulseSignal: [1, 2, 3, 4, 5],
      strategy: 'tcm_diagnosis',
    };
    expect(mockQuery.text).toBe('多模态查询');
    expect(mockQuery.pulseSignal).toHaveLength(5);
  });
});
