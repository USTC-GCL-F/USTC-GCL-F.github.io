import requests
from bs4 import BeautifulSoup
import urllib.parse
import time


def search_homepage(researcher, institution):
    # 创建搜索查询，明确表达查找主页的意图
    query = f"{researcher} {institution} official homepage"
    query = urllib.parse.quote(query)

    # 发送请求到Google搜索
    url = f"https://www.google.com/search?q={query}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    # 定义优先级高的域名
    preferred_domains = [".edu", ".ac.", ".edu.cn", ".org", "university", ".ac.jp"]

    best_match = None
    best_score = -1

    # 提取所有搜索结果中的链接
    for g in soup.find_all("div", class_="g"):
        link = g.find("a")["href"]
        if "http" not in link:
            continue
        if (
            "dl.acm.org" in link
            or "siggraph.org" in link
            or "pg2022.org" in link
            or "ieeevr.org" in link
            or "intel.com" in link
            or "academia.edu" in link
            or ".pdf" in link
            or "wikipedia.org" in link
            or "swap.stanford.edu" in link
            or "paperdigest.org" in link
            or len(link) > 30
        ):
            continue

        # 计算该链接的相关性得分
        score = 0
        for domain in preferred_domains:
            if domain in link:
                score += 1

        # 检查描述文本中是否包含关键字
        description = g.find("span", class_="aCOpRe")
        if description and (
            "homepage" in description.text.lower()
            or researcher.lower() in description.text.lower()
        ):
            score += 1

        # 如果当前链接的得分更高，则更新最佳匹配
        if score > best_score:
            best_score = score
            best_match = link

    return best_match


def main():
    # 读取txt文件中的数据
    with open(
        "./public/file/PG2024ProgramCommittee.txt", "r", encoding="utf-8"
    ) as file:
        lines = file.readlines()

    results = []

    # 遍历研究者名单
    for line in lines:
        parts = line.split(",")
        researcher = parts[0].strip()
        institution = parts[1].strip()
        homepage = parts[2].strip()
        if len(homepage) != 0:
            results.append(f"{researcher},{institution},{homepage}")
            continue
        print(f"Searching for: {researcher}, {institution}")

        # 搜索主页
        homepage = search_homepage(researcher, institution)
        if homepage:
            print(f"Found homepage: {homepage}")
            results.append(f"{researcher},{institution},{homepage}")
        else:
            print("No homepage found.")
            results.append(f"{researcher},{institution},")

        # 避免发送过多请求导致被封IP，添加适当的延时
        time.sleep(2)

    # 保存结果到文件
    with open("researchers_homepages.txt", "w", encoding="utf-8") as output_file:
        for result in results:
            output_file.write(result + "\n")


if __name__ == "__main__":
    main()
