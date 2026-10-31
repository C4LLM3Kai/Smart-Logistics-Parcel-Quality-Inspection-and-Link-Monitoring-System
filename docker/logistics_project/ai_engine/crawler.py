from icrawler.builtin import BingImageCrawler
import os

# 使用说明:
# 如果不想用 Roboflow 的现成数据集，以此脚本体现“爬虫”能力
# 它会从 Bing 图片搜索中抓取图片到 dataset/raw 目录

def crawl_images():
    base_dir = "dataset/raw"
    
    # 1. 爬取“破损包裹”图片
    damaged_dir = os.path.join(base_dir, "damaged")
    google_crawler = BingImageCrawler(storage={'root_dir': damaged_dir})
    print("Crawling 'damaged cardboard box' images...")
    google_crawler.crawl(keyword='damaged cardboard box logistics', max_num=50)

    # 2. 爬取“正常包裹”图片
    normal_dir = os.path.join(base_dir, "normal")
    google_crawler = BingImageCrawler(storage={'root_dir': normal_dir})
    print("Crawling 'clean cardboard box' images...")
    google_crawler.crawl(keyword='clean cardboard box package', max_num=50)

    print("Crawling finished! Please inspect images and manually label/clean them.")

if __name__ == "__main__":
    crawl_images()
