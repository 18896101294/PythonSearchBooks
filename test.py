import requests
from bs4 import BeautifulSoup
import time
import random

def get_download_url(base_url, detail_url):

    cookie = '6b61badaf837d57e645781b1288425c1'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Edg/134.0.0.0',
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'cookie': f'siteLanguage=zh; remix_userkey={cookie}; remix_userid=42383395; domainsNotWorking=cnlib.icu%2Cz-lib.gs',
        'Referer': base_url + detail_url
    }

    try:
        # 发送请求
        response = requests.get(base_url + detail_url, headers=headers)
        response.raise_for_status()  # 检查请求是否成功

        # 解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # 查找具有特定 class 的 a 标签
        download_link = soup.find('a', class_='btn btn-default addDownloadedBook')
        
        if download_link and 'href' in download_link.attrs:
            download_url = download_link['href']
            # 如果是相对 URL，添加 base_url
            if download_url.startswith('/'):
                download_url = base_url + download_url
            # print(f"找到下载链接: {download_url}")
            return download_url
        else:
            print("未找到下载链接")
            return ''
    
    except requests.exceptions.RequestException as e:
        print(f"请求错误: {e}")
        return ''
    except Exception as e:
        print(f"解析错误: {e}")
        return ''

def search_book(book_name):
    """
    在 Z-Library 搜索指定书籍，返回评级最高的5条记录
    
    Args:
        book_name: 书籍名称
    
    Returns:
        搜索结果列表，每个元素包含书籍信息
    """
    base_url = "https://zh.z-library.sk"
    search_url = f"{base_url}/s/{book_name}"
    
    # 设置请求头，模拟浏览器访问
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Referer': base_url
    }
    
    try:
        # 发送请求
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()  # 检查请求是否成功
        # 解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找书籍列表
        book_items = soup.select('.book-item')[:5]
        
        results = []
        for i, item in enumerate(book_items):
            bookcard = item.find('z-bookcard')
            # 提取书籍标题
            title_elem = bookcard.find('div', {'slot': 'title'})
            if title_elem and book_name in title_elem.text:
                author_elem = bookcard.find('div', {'slot': 'author'})
                language = bookcard.get('language')
                publisher = bookcard.get('publisher')
                year = bookcard.get('year')
                extension = bookcard.get('extension')
                filesize = bookcard.get('filesize')
                rating = bookcard.get('rating')
                quality = bookcard.get('quality')
                detail_url = bookcard.get('href', 'N/A')
                download_url = get_download_url(base_url, detail_url) if detail_url else None

                book_info = {
                    'id': len(results) + 1,  # 使用列表长度作为ID
                    'title': title_elem.text.strip() if title_elem else 'Unknown',
                    'author': author_elem.text.strip() if author_elem else 'Unknown',
                    'publisher': publisher if publisher else 'Unknown',
                    'language': language if language else 'Unknown',
                    'extension': extension if extension else 'Unknown',
                    'filesize': filesize if filesize else 'Unknown',
                    'rating': float(rating) if rating and rating != 'Unknown' else 0,  # 转换为浮点数
                    'quality': quality if quality else 'Unknown',
                    'year': year if year else 'Unknown',
                    'detail_url': base_url + detail_url if detail_url else None,
                    'download_url': download_url if download_url else None
                }
                
                results.append(book_info)
        
        return results
    
    except requests.exceptions.RequestException as e:
        print(f"请求错误: {e}")
        return []
    except Exception as e:
        print(f"解析错误: {e}")
        return []

def download_book(download_url, filename=None):
    """
    下载书籍
    
    Args:
        download_url: 下载链接
        filename: 保存的文件名，如果为None则从URL中提取
    
    Returns:
        是否下载成功
    """
    if not download_url:
        print("下载链接无效")
        return False
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'https://zh.z-library.sk/'
    }
    
    try:
        # 发送请求获取下载页面
        response = requests.get(download_url, headers=headers)
        response.raise_for_status()
        
        # 解析下载页面，获取真实下载链接
        soup = BeautifulSoup(response.text, 'html.parser')
        download_button = soup.select_one('.dlButton')
        
        if not download_button or 'href' not in download_button.attrs:
            print("无法找到下载按钮")
            return False
        
        real_download_url = download_button['href']
        
        # 如果没有指定文件名，从URL中提取
        if not filename:
            filename = real_download_url.split('/')[-1]
            if '?' in filename:
                filename = filename.split('?')[0]
        
        # 下载文件
        print(f"正在下载 {filename}...")
        file_response = requests.get(real_download_url, headers=headers, stream=True)
        file_response.raise_for_status()
        
        with open(filename, 'wb') as f:
            for chunk in file_response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        print(f"下载完成: {filename}")
        return True
    
    except requests.exceptions.RequestException as e:
        print(f"下载错误: {e}")
        return False
    except Exception as e:
        print(f"处理错误: {e}")
        return False

def main():
    book_name = input("请输入要搜索的书籍名称: ")
    
    print(f"正在搜索 '{book_name}'...")
    results = search_book(book_name)
    
    if not results:
        print("未找到相关书籍")
        return
    
    print(f"找到 {len(results)} 本相关书籍:")
    for i, book in enumerate(results):
        print(f"\n{i+1}. {book['title']}")
        print(f"   序号: {book['id']}")
        print(f"   作者: {book['author']}")
        print(f"   出版社: {book['publisher']}")
        print(f"   语言: {book['language']}")
        print(f"   格式: {book['extension']}")
        print(f"   大小: {book['filesize']}")
        print(f"   图书评级: {book['rating']}")
        print(f"   文件质量: {book['quality']}")
        print(f"   详情地址: {book['detail_url']}")
        print(f"   下载地址: {book['download_url']}")
    
    while True:
        try:
            choice = int(input("\n请选择要下载的书籍编号 (0 退出): "))
            if choice == 0:
                break
            if 1 <= choice <= len(results):
                selected_book = results[choice-1]
                if selected_book['detail_url']:
                    print(f"正在获取下载链接...")
                    # 获取实际下载链接
                    download_url = get_download_url(selected_book['detail_url'])
                    
                    if download_url:
                        # 添加随机延迟，避免被检测为爬虫
                        delay = random.uniform(1, 3)
                        print(f"等待 {delay:.2f} 秒...")
                        time.sleep(delay)
                        
                        filename = f"{selected_book['title']}_{selected_book['author']}.{selected_book['extension'].lower()}"
                        filename = filename.replace('/', '_').replace('\\', '_').replace(':', '_')
                        download_book(download_url, filename)
                    else:
                        print("无法获取下载链接")
                else:
                    print("该书籍没有详情页链接")
            else:
                print("无效的选择")
        except ValueError:
            print("请输入有效的数字")
        except Exception as e:
            print(f"发生错误: {e}")

if __name__ == "__main__":
    main()