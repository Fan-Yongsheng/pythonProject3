import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import pandas as pd

def normalize_url(url):
    parsed_url = urlparse(url)
    normalized_url = parsed_url._replace(path=parsed_url.path.rstrip('/'))
    return normalized_url.geturl()

def get_links(url, root_url, visited, links_info, current_id, max_links, url_to_id):
    # 标准化URL
    url = normalize_url(url)

    # 检查是否达到了链接数量的限制
    if len(url_to_id) >= max_links:
        return current_id

    # 如果URL已被访问，直接返回其ID
    if url in url_to_id:
        return current_id

    # 将当前URL标记为已访问，并分配ID
    url_to_id[url] = current_id
    visited.add(url)
    print(f"Visiting {url} as ID {current_id}")

    try:
        content = requests.get(url).text
    except requests.RequestException as e:
        print(f"Error visiting {url}: {e}")
        return current_id

    soup = BeautifulSoup(content, 'html.parser')
    child_links = []

    # 遍历页面中的所有链接
    for link in soup.find_all('a'):
        href = link.get('href')
        if href:
            # 生成完整的URL
            if not href.startswith('http'):
                href = urljoin(url, href)
            href = normalize_url(href)
            if 'www.hs-hannover.de' in href:
                child_links.append(href)

    # 存储当前链接及其子链接
    links_info.append((current_id, url, child_links))

    # 分配ID并递归爬取子链接
    for child in child_links:
        if child not in url_to_id:
            current_id += 1
            current_id = get_links(child, root_url, visited, links_info, current_id, max_links, url_to_id)

    return current_id

def create_excel(links_info, url_to_id):
    data = []
    seen_ids = set()  # 记录已经输出的ID
    for id, url, children in links_info:
        if id not in seen_ids:
            parent_link = f"{id}: {url}"
            data.append([parent_link, ""])  # Add parent link
            seen_ids.add(id)
        for child in children:
            child_id = url_to_id[child]
            if child_id not in seen_ids:
                child_link = f"{child_id}: {child}"
                data.append(["", child_link])  # Add child link
                seen_ids.add(child_id)

    df = pd.DataFrame(data, columns=["Parent Link (ID URL)", "Child Link (ID URL)"])
    excel_file_name = 'hs_hannover_links.xlsx'
    df.to_excel(excel_file_name, index=False)
    print("Excel file created at:", excel_file_name)

# 根URL
root_url = 'http://www.hs-hannover.de'

visited_links = set()
links_info = []
url_to_id = {}
max_links = 50  # 最大爬取链接数量
current_id = 1  # 初始链接编号

get_links(root_url, root_url, visited_links, links_info, current_id, max_links, url_to_id)

# 保存到Excel文件
create_excel(links_info, url_to_id)
