from flask import Flask, request, jsonify
from test import search_book, get_download_url, download_book
import os
import time
import random

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

@app.route('/api/download', methods=['POST'])
def download():
    """下载书籍API"""
    data = request.get_json()
    if not data or 'download_url' not in data:
        return jsonify({'error': '请提供下载链接'}), 400
    
    download_url = data['download_url']
    filename = data.get('filename')
    
    if not filename:
        # 从URL中提取文件名
        filename = download_url.split('/')[-1]
        if '?' in filename:
            filename = filename.split('?')[0]
    
    # 确保文件名安全
    filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_', '.'))
    filepath = os.path.join(DOWNLOAD_DIR, filename)
    
    # 添加随机延迟
    delay = random.uniform(1, 3)
    time.sleep(delay)
    
    success = download_book(download_url, filepath)
    
    if success:
        return jsonify({
            'status': 'success',
            'message': '下载成功',
            'filepath': filepath
        })
    else:
        return jsonify({'error': '下载失败'}), 500

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True) 