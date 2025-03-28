from flask import Flask, request, jsonify, send_file
from test import search_book, get_download_url, download_book
import os
import time
import random
import io
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# 创建下载目录
DOWNLOAD_DIR = "downloads"
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

@app.route('/api/search', methods=['GET'])
def search():
    """搜索书籍API"""
    book_name = request.args.get('q')
    if not book_name:
        return jsonify({'error': '请提供搜索关键词'}), 400
    
    results = search_book(book_name)
    return jsonify({
        'status': 'success',
        'count': len(results),
        'books': results
    })

@app.route('/api/download', methods=['GET'])
def download():
    """下载书籍API - 直接返回URL的二进制流"""
    download_url = request.args.get('url')
    if not download_url:
        return jsonify({'error': '请提供下载链接'}), 400
    
    cookie = '6b61badaf837d57e645781b1288425c1'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Edg/134.0.0.0',
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'cookie': f'siteLanguage=zh; remix_userkey={cookie}; remix_userid=42383395; domainsNotWorking=cnlib.icu%2Cz-lib.gs',
    }
    
    try:
        # 直接获取URL的二进制流
        response = requests.get(download_url, headers=headers, stream=True)
        response.raise_for_status()
        
        # 直接返回二进制流
        return response.content, 200, {
            'Content-Type': 'application/octet-stream',
            'Content-Disposition': 'attachment'
        }
    
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'下载错误: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'处理错误: {str(e)}'}), 500

@app.route('/api/get_download_url', methods=['GET'])
def get_download():
    """获取下载链接API"""
    detail_url = request.args.get('url')
    if not detail_url:
        return jsonify({'error': '请提供详情页URL'}), 400
    
    base_url = "https://zh.z-library.sk"
    download_url = get_download_url(base_url, detail_url)
    
    if download_url:
        return jsonify({
            'status': 'success',
            'download_url': download_url
        })
    else:
        return jsonify({'error': '无法获取下载链接'}), 404

@app.route('/api/feishu/token', methods=['POST'])
def get_feishu_token():
    """获取飞书 tenant_access_token"""
    try:
        # 飞书API配置
        FEISHU_API_URL = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        
        # 固定的请求参数
        payload = {
            "app_id": "cli_a33d4ad126b8100e",
            "app_secret": "fLQlPwLDHSzxVFL76FHDSbvN5ow4fS87"
        }
        
        # 设置请求头
        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'User-Agent': 'Apifox/1.0.0 (https://www.apifox.cn)',
            'Accept': '*/*',
            'Host': 'open.feishu.cn',
            'Connection': 'keep-alive'
        }
        
        # 发送请求
        response = requests.post(FEISHU_API_URL, headers=headers, json=payload)
        response.raise_for_status()  # 检查请求是否成功
        
        # 获取响应数据
        response_data = response.json()
        
        # 检查响应状态
        if response_data.get('code') == 0:
            return response_data.get('tenant_access_token')
        else:
            return jsonify(response_data.get('msg', '获取token失败')), 500
        
    except requests.exceptions.RequestException as e:
        return jsonify(f'请求飞书API失败: {str(e)}'), 500
    except Exception as e:
        return jsonify(f'服务器内部错误: {str(e)}'), 500

@app.route('/api/feishu/upload', methods=['POST'])
def upload_to_feishu():
    """上传文件到飞书"""
    try:
        # 获取请求参数
        data = request.get_json()
        if not data or 'file_name' not in data or 'file_url' not in data:
            return jsonify('缺少必要参数'), 400
        
        file_name = data['file_name']
        file_url = data['file_url']
        
        # 1. 获取飞书token
        token_response = requests.post('http://localhost:5001/api/feishu/token')
        if token_response.status_code != 200:
            return jsonify('获取token失败'), 500
        token = token_response.text
        
        # 2. 下载文件
        download_response = requests.get(f'http://localhost:5001/api/download?url={file_url}')
        if download_response.status_code != 200:
            return jsonify('下载文件失败'), 500
        file_content = download_response.content
        
        # 获取文件大小
        file_size = len(file_content)
        
        # 3. 上传到飞书
        FEISHU_UPLOAD_URL = "https://open.feishu.cn/open-apis/drive/v1/medias/upload_all"
        
        # 准备文件数据
        files = {
            'file': (file_name, file_content, 'application/octet-stream')
        }
        
        # 准备表单数据
        form_data = {
            'file_name': file_name,
            'parent_type': 'bitable_file',
            'parent_node': 'T3F1bvJ7paQzoFsvaiicDkiInxg',
            'size': str(file_size)
        }
        
        # 设置请求头
        headers = {
            'Authorization': f'Bearer {token}',
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
            'Accept': '*/*',
            'Host': 'open.feishu.cn',
            'Connection': 'keep-alive'
        }
        
        # 发送请求
        response = requests.post(FEISHU_UPLOAD_URL, headers=headers, files=files, data=form_data)
        response.raise_for_status()
        
        # 获取响应数据
        response_data = response.json()
        
        # 检查响应状态并返回file_token
        if response_data.get('code') == 0:
            return response_data.get('data', {}).get('file_token')
        else:
            return jsonify(response_data.get('msg', '上传失败')), 500
        
    except requests.exceptions.RequestException as e:
        return jsonify(f'请求飞书API失败: {str(e)}'), 500
    except Exception as e:
        return jsonify(f'服务器内部错误: {str(e)}'), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True) 