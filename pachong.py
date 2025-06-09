import os
import requests
from bs4 import BeautifulSoup
import urllib.parse
import time


def download_bing_images(keyword, count=30, save_dir='images'):
    """
    从必应图片下载指定关键词的图片

    :param keyword: 搜索关键词
    :param count: 需要下载的图片数量
    :param save_dir: 图片保存目录
    """
    # 创建保存目录
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # 必应图片搜索URL
    base_url = 'https://cn.bing.com/images/async?'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    downloaded = 0
    page_size = 30  # 每页图片数量
    offset = 0

    while downloaded < count:
        # 构造请求参数
        params = {
            'q': keyword,
            'first': offset,
            'count': page_size,
            'mmasync': '1'
        }

        try:
            # 发送请求
            response = requests.get(base_url, params=params, headers=headers)
            response.raise_for_status()

            # 解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            images = soup.find_all('a', class_='iusc')

            if not images:
                print("没有找到更多图片")
                break

            for img in images:
                if downloaded >= count:
                    break

                # 从JSON数据中提取图片URL
                img_data = img.get('m')
                if not img_data:
                    continue

                try:
                    import json
                    img_info = json.loads(img_data)
                    img_url = img_info.get('murl')

                    if not img_url:
                        continue

                    # 下载图片
                    try:
                        img_data = requests.get(img_url, headers=headers, timeout=10).content

                        # 生成文件名
                        filename = f"{keyword}_{downloaded + 1}.jpg"
                        filepath = os.path.join(save_dir, filename)

                        # 保存图片
                        with open(filepath, 'wb') as f:
                            f.write(img_data)

                        downloaded += 1
                        print(f"已下载 {downloaded}/{count}: {filename}")

                    except Exception as e:
                        print(f"下载图片失败: {img_url}, 错误: {e}")

                except json.JSONDecodeError:
                    continue

            offset += page_size
            time.sleep(1)  # 防止请求过于频繁

        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
            break

    print(f"下载完成，共下载 {downloaded} 张图片")


# 使用示例
if __name__ == '__main__':
    keyword = "葡萄花鸟纹银香囊"
    download_count = 20
    download_bing_images(keyword, download_count)