from datetime import datetime, timezone, timedelta
import os
import xml.etree.ElementTree as ET
import xml.dom.minidom


def sitemap(root: str, domain: str, save:str="") -> str:
    """
    특정 루트 경로에서 index.html이 포함된 하위 디렉토리를 찾아 사이트맵(XML) 문자열로 반환.

    :param root: 파일 시스템 내 검색할 루트 디렉토리
    :param domain: 사이트의 기본 URL (예: "https://www.example.com")
    :param save: 저장 경로
    :return: XML 사이트맵 문자열
    """
    urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

    for dirpath, _, filenames in os.walk(root):
        if "index.html" in filenames:
            index_path = os.path.join(dirpath, "index.html")
            last_modified_timestamp = os.path.getmtime(index_path)
            last_modified_dt = datetime.fromtimestamp(last_modified_timestamp, timezone(timedelta(hours=9)))
            last_modified_str = last_modified_dt.strftime("%Y-%m-%dT%H:%M:%S%z")
            last_modified_str = last_modified_str[:-2] + ":" + last_modified_str[-2:]  # +0900 → +09:00 변환

            relative_path = os.path.relpath(dirpath, root)
            path = f"{domain}/{relative_path.replace(os.sep, '/')}" if relative_path != '.' else domain

            url_element = ET.SubElement(urlset, "url")
            loc = ET.SubElement(url_element, "loc")
            loc.text = path
            lastmod = ET.SubElement(url_element, "lastmod")
            lastmod.text = last_modified_str
            freq = ET.SubElement(url_element, "changefreq")
            freq.text = "daily"
            priority = ET.SubElement(url_element, "priority")
            priority.text = "1.0" if path.count('/') < 3 else "0.9" if path.count("/") < 4 else "0.8"

    string = ET.tostring(urlset, encoding="utf-8", method="xml").decode("utf-8")
    if save:
        dom = xml.dom.minidom.parseString(string)
        with open(save, "w", encoding="utf-8") as file:
            file.write(f'''---
layout:null
---
{dom.toprettyxml(indent="  ").replace(
'<?xml version="1.0" ?>', '<?xml version="1.0" encoding="UTF-8"?>'
)}''')
    return string


# 예제 실행
if __name__ == "__main__":
    from src.common.path import PATH

    domain = "https://www.labwons.com"
    print(sitemap(PATH.DOCS, domain))
