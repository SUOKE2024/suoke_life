#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from flask import Blueprint, request, jsonify, current_app, g
import json
from datetime import datetime

logger = logging.getLogger(__name__)

# 创建Blueprint
bp = Blueprint('medical_query', __name__)

@bp.route('/', methods=['POST'])
def submit_medical_query():
    """
    提交医疗查询
    
    处理用户提交的医疗查询请求，调用服务层生成回答
    
    Returns:
        JSON响应，包含查询ID和结果
    """
    try:
        # 获取请求数据
        data = request.json
        
        if not data:
            return jsonify({
                'error': '请求体不能为空',
                'status_code': 400
            }), 400
        
        # 验证必要字段
        required_fields = ['user_id', 'query_text']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'error': f'缺少必要字段: {field}',
                    'status_code': 400
                }), 400
        
        # 调用服务
        medical_query_service = current_app.services.get('medical_query_service')
        if not medical_query_service:
            return jsonify({
                'error': '服务未配置',
                'status_code': 500
            }), 500
        
        # 准备参数
        query_params = {
            'user_id': data['user_id'],
            'query_text': data['query_text'],
            'related_symptoms': data.get('related_symptoms', []),
            'related_conditions': data.get('related_conditions', []),
            'include_western_medicine': data.get('include_western_medicine', True),
            'include_tcm': data.get('include_tcm', True)
        }
        
        # 调用服务处理查询
        response = medical_query_service.submit_medical_query(**query_params)
        
        # 转换结果为REST响应
        result = {
            'response_id': response.id,
            'query_text': response.query_text,
            'answer': response.answer,
            'sources': [s.to_dict() for s in response.sources] if response.sources else [],
            'is_emergency_advice': response.is_emergency_advice,
            'disclaimer': response.disclaimer,
            'follow_up_questions': response.follow_up_questions
        }
        
        return jsonify(result), 201
        
    except Exception as e:
        logger.error(f"提交医疗查询失败: {str(e)}", exc_info=True)
        return jsonify({
            'error': f'处理查询失败: {str(e)}',
            'status_code': 500
        }), 500

@bp.route('/<query_id>', methods=['GET'])
def get_medical_query(query_id):
    """
    获取医疗查询记录
    
    根据ID检索特定的医疗查询记录
    
    Args:
        query_id: 查询ID
        
    Returns:
        JSON响应，包含查询记录
    """
    try:
        # 获取服务
        medical_query_service = current_app.services.get('medical_query_service')
        if not medical_query_service:
            return jsonify({
                'error': '服务未配置',
                'status_code': 500
            }), 500
        
        # 获取查询记录
        query = medical_query_service.get_query_by_id(query_id)
        
        if not query:
            return jsonify({
                'error': f'未找到ID为{query_id}的查询记录',
                'status_code': 404
            }), 404
        
        # 转换结果为REST响应
        result = {
            'response_id': query.id,
            'user_id': query.user_id,
            'query_text': query.query_text,
            'answer': query.answer,
            'sources': [s.to_dict() for s in query.sources] if query.sources else [],
            'is_emergency_advice': query.is_emergency_advice,
            'disclaimer': query.disclaimer,
            'follow_up_questions': query.follow_up_questions,
            'created_at': query.created_at.isoformat() if query.created_at else None,
            'updated_at': query.updated_at.isoformat() if query.updated_at else None
        }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"获取医疗查询记录失败: {str(e)}", exc_info=True)
        return jsonify({
            'error': f'获取查询记录失败: {str(e)}',
            'status_code': 500
        }), 500

@bp.route('/user/<user_id>', methods=['GET'])
def list_user_queries(user_id):
    """
    获取用户的医疗查询历史记录
    
    Args:
        user_id: 用户ID
        
    Returns:
        JSON响应，包含用户的查询历史记录列表
    """
    try:
        # 获取查询参数
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 10))
        keyword = request.args.get('keyword')
        
        # 页码和页大小不能小于1
        if page < 1:
            page = 1
        if page_size < 1:
            page_size = 10
        
        # 页大小不能超过100
        if page_size > 100:
            page_size = 100
        
        # 获取服务
        medical_query_service = current_app.services.get('medical_query_service')
        if not medical_query_service:
            return jsonify({
                'error': '服务未配置',
                'status_code': 500
            }), 500
        
        # 获取查询记录
        if keyword:
            queries = medical_query_service.search_queries(user_id, keyword, page_size, (page - 1) * page_size)
            total = medical_query_service.get_search_count(user_id, keyword)
        else:
            queries = medical_query_service.list_queries_by_user(user_id, page_size, (page - 1) * page_size)
            total = medical_query_service.get_query_count_by_user(user_id)
        
        # 转换结果为REST响应
        results = []
        for query in queries:
            results.append({
                'response_id': query.id,
                'query_text': query.query_text,
                'answer': query.answer,
                'is_emergency_advice': query.is_emergency_advice,
                'created_at': query.created_at.isoformat() if query.created_at else None
            })
        
        return jsonify({
            'queries': results,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size if total > 0 else 1
        })
        
    except Exception as e:
        logger.error(f"获取用户医疗查询历史记录失败: {str(e)}", exc_info=True)
        return jsonify({
            'error': f'获取查询历史记录失败: {str(e)}',
            'status_code': 500
        }), 500

@bp.route('/<query_id>', methods=['DELETE'])
def delete_medical_query(query_id):
    """
    删除医疗查询记录
    
    Args:
        query_id: 查询ID
        
    Returns:
        JSON响应，表示操作结果
    """
    try:
        # 获取服务
        medical_query_service = current_app.services.get('medical_query_service')
        if not medical_query_service:
            return jsonify({
                'error': '服务未配置',
                'status_code': 500
            }), 500
        
        # 删除查询记录
        success = medical_query_service.delete_query(query_id)
        
        if not success:
            return jsonify({
                'error': f'未找到ID为{query_id}的查询记录',
                'status_code': 404
            }), 404
        
        return '', 204  # 成功删除，返回204 No Content
        
    except Exception as e:
        logger.error(f"删除医疗查询记录失败: {str(e)}", exc_info=True)
        return jsonify({
            'error': f'删除查询记录失败: {str(e)}',
            'status_code': 500
        }), 500 