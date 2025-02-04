from datetime import datetime
from pytz import timezone
import os


def updateSitemap():
    timestamp = datetime.now(timezone('Asia/Seoul'))
    timestamp = timestamp.replace(microsecond=0)
    with open(os.path.join(os.path.dirname(__file__), r"../../sitemap.xml"), mode="w") as file:
        file.write(f"""---
layout: null
---
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9 http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd" xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://labwons.com</loc>
    <lastmod>{timestamp.isoformat()}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://labwons.com/rank</loc>
    <lastmod>{timestamp.isoformat()}</lastmod>
    <changefreq>daily</changefreq>
    <priority>0.5</priority>
  </url>
</urlset>""")
    return
  

def updateRSS():
    timestamp = datetime.now(timezone('Asia/Seoul'))
    timestamp = timestamp.strftime('%a, %d %b %Y %H:%M:%S %z')
    with open(os.path.join(os.path.dirname(__file__), r"../../feed.xml"), mode="w") as file:
        file.write(f"""---
layout: null
---
<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>LAB￦ONS</title>
    <description>SNO￦BALL YOUR ASSET</description>
    <link>https://labwons.com/</link>
    <atom:link href="https://labwons.com/feed.xml" rel="self" type="application/rss+xml"/>
    <pubDate>Fri, 26 Jul 2024 12:00:00 +0900</pubDate>
    <lastBuildDate>{timestamp}</lastBuildDate>
    <generator>Custom Python Script 1.0</generator>
    <item>
      <title>시장 지도</title>
      <description>시장 지도</description>
      <author>snob.labwons@gmail.com</author>
      <pubDate>{timestamp}</pubDate>
      <link>https://labwons.com/</link>
      <guid isPermaLink="true">https://labwons.com/</guid>
    </item>
    <item>
      <title>수익률 순위</title>
      <description>수익률 순위</description>
      <author>snob.labwons@gmail.com</author>
      <pubDate>{timestamp}</pubDate>
      <link>https://labwons.com/rank/</link>
      <guid isPermaLink="true">https://labwons.com/rank/</guid>
    </item>
  </channel>
</rss>""")
    return