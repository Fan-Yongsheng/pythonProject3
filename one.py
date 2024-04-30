import requests
from bs4 import BeautifulSoup
import pandas as pd



def get_links(url, root_url, visited, max_links, parent=None):
    # 检查是否达到了链接数量的限制
    if len(visited) >= max_links:
        return []

    # 检查URL是否已被访问
    if url in visited:
        return []
    print(f"Visiting {url}")
    visited.add(url)


    try:
        content = requests.get(url).text
    except requests.RequestException as e:
        print(f"Error visiting {url}: {e}")
        return []


    soup = BeautifulSoup(content, 'html.parser')
    page_links = []

    # 遍历页面中的所有链接
    for link in soup.find_all('a'):
        href = link.get('href')
        if href:
            # 完整的URL
            if not href.startswith('http'):
                href = requests.compat.urljoin(url, href)
            if 'www.hs-hannover.de' in href and href not in visited:

                page_links.append((href, url))

                if len(visited) < max_links:
                    page_links.extend(get_links(href, root_url, visited, max_links, url))

    return page_links


# 根URL
root_url = 'http://www.hs-hannover.de'
# www, / , gleiche LINK,

visited_links = set()
max_links = 10  # 最大爬取链接数量

links_with_parents = get_links(root_url, root_url, visited_links, max_links)


df_links = pd.DataFrame(links_with_parents, columns=['URL', 'Parent URL'])


excel_file_name = 'hs_hannover_links.xlsx'


df_links.to_excel(excel_file_name, index=False)

import networkx as nx
import matplotlib.pyplot as plt



from pyvis.network import Network
import pandas as pd

df_links = pd.DataFrame(links_with_parents, columns=['URL', 'Parent URL'])
net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white", notebook=True)

# 添加节点和边
for index, row in df_links.iterrows():
    src = row['Parent URL'] if row['Parent URL'] else 'Root'
    dst = row['URL']

    # 直接添加节点，不检查是否已存在
    net.add_node(src, label=src, title=src, color="#f7bb42")
    net.add_node(dst, label=dst, title=dst, color="#dd4b39")
    net.add_edge(src, dst)

net.set_options("""
    {
      "physics": {
        "forceAtlas2Based": {
          "gravitationalConstant": -200,
          "centralGravity": 0.002,
          "springLength": 100,
          "springConstant": 0.05,
          "avoidOverlap": 1
        },
        "solver": "forceAtlas2Based",
        "timestep": 0.35,
        "stabilization": {
          "iterations": 150
        }
      },
      "nodes": {
        "scaling": {
          "min": 10,
          "max": 30,
          "label": {
            "enabled": true
          }
        }
      }
    }
    """)

net.show("hs_hannover_network.html")
