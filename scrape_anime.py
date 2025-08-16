import requests
from bs4 import BeautifulSoup
import json
import time
import random
import os
import sys
from datetime import datetime

BASE_URL = "https://4m.kamrix.shop"
HOMEPAGE_URL = f"{BASE_URL}/"
ANIME_LIST_URL = f"{BASE_URL}/%D9%82%D8%A7%D8%A6%D9%85%D8%A9-%D8%A7%D9%84%D8%A7%D9%86%D9%85%D9%8A/page/"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1"
]

# ملف حفظ التقدم
PROGRESS_FILE = "scraping_progress.json"
ANIME_DATA_FILE = "anime.json"

class AnimeScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "ar,en-US;q=0.7,en;q=0.3",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        })
        
    def random_sleep(self, min_delay=1.5, max_delay=3.5):
        """تأخير عشوائي بين الطلبات لتجنب الحظر"""
        delay = random.uniform(min_delay, max_delay)
        print(f"[انتظار] انتظار {delay:.1f} ثانية...")
        time.sleep(delay)
    
    def get_headers(self):
        """الحصول على headers عشوائية"""
        return {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "ar,en-US;q=0.7,en;q=0.3",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
    
    def load_progress(self):
        """تحميل التقدم المحفوظ"""
        if os.path.exists(PROGRESS_FILE):
            try:
                with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[تحذير] خطأ في تحميل التقدم: {e}")
        return {"completed_anime": [], "current_page": 1, "total_anime": 0}
    
    def save_progress(self, progress_data):
        """حفظ التقدم الحالي"""
        try:
            with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
                json.dump(progress_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[خطأ] في حفظ التقدم: {e}")
    
    def load_anime_data(self):
        """تحميل بيانات الأنميات الموجودة"""
        if os.path.exists(ANIME_DATA_FILE):
            try:
                with open(ANIME_DATA_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[تحذير] خطأ في تحميل بيانات الأنميات: {e}")
        return {}
    
    def save_anime_data(self, data):
        """حفظ بيانات الأنميات بدون نسخ احتياطية تلقائية"""
        try:
            # حفظ الملف الرئيسي فقط بدون نسخ احتياطية
            with open(ANIME_DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"[حفظ] تم حفظ البيانات في {ANIME_DATA_FILE}")
        except Exception as e:
            print(f"[خطأ] في حفظ البيانات: {e}")
    
    def get_all_anime_links(self, max_pages=None):
        """جلب جميع روابط الأنميات من جميع الصفحات"""
        print("[جمع] بدء جمع روابط الأنميات من جميع الصفحات...")
        anime_links = []
        page = 1
        
        while True:
            if max_pages and page > max_pages:
                break
                
            url = ANIME_LIST_URL + str(page) + "/"
            print(f"[صفحة {page}] جلب: {url}")
            
            try:
                resp = self.session.get(url, timeout=30)
                resp.encoding = 'utf-8'
                soup = BeautifulSoup(resp.text, "html.parser")
                
                # البحث عن روابط الأنميات
                anime_cards = soup.select(".anime-card-container .anime-card-title a")
                
                if not anime_cards:
                    print(f"[صفحة {page}] لا توجد أنميات في هذه الصفحة. تم جمع {len(anime_links)} أنمي.")
                    break
                
                page_anime_count = 0
                for card in anime_cards:
                    link = card.get("href")
                    if link and link.startswith("http"):
                        anime_links.append(link)
                        page_anime_count += 1
                
                print(f"[صفحة {page}] تم جمع {page_anime_count} أنمي. المجموع: {len(anime_links)}")
                
                if page_anime_count == 0:
                    break
                
                page += 1
                self.random_sleep(2, 4)
                
            except Exception as e:
                print(f"[خطأ] في جلب الصفحة {page}: {e}")
                break
        
        print(f"[جمع] تم جمع إجمالي {len(anime_links)} رابط أنمي.")
        return anime_links
    
    def clean_anime_name(self, raw_name):
        """تنظيف اسم الأنمي من الكلمات الزائدة"""
        remove_phrases = [
            "جميع حلقات انمي", "جميع حلقات", "مترجمة اون لاين", "مترجم اون لاين", 
            "مترجمة", "مترجم", "- Anime4up", "| Anime4up", "\u2013 Anime4up", "\u2014 Anime4up",
            "انمي", "anime", "مترجم", "مترجمة", "اون لاين", "online"
        ]
        name = raw_name
        for phrase in remove_phrases:
            name = name.replace(phrase, "")
        return name.strip(" -|\u2013\u2014").strip()
    
    def get_anime_details(self, anime_url, existing_data=None):
        """جلب تفاصيل الأنمي الكاملة"""
        print(f"[تفاصيل] جلب تفاصيل: {anime_url}")
        
        try:
            resp = self.session.get(anime_url, timeout=30)
            resp.encoding = 'utf-8'
            soup = BeautifulSoup(resp.text, "html.parser")
            
            # استخراج اسم الأنمي
            name = ""
            name_selectors = [
                "h1.anime-details-title",
                ".anime-title",
                ".anime-card-title h3",
                "h1",
                ".anime-name"
            ]
            
            for selector in name_selectors:
                element = soup.select_one(selector)
                if element:
                    name = element.text.strip()
                    break
            
            if not name and soup.title:
                name = soup.title.text.strip().split("|")[0]
            
            name = self.clean_anime_name(name)
            
            # صورة الغلاف
            image = ""
            image_selectors = [
                ".anime-cover img",
                ".anime-poster img",
                ".anime-image img",
                ".cover img"
            ]
            
            for selector in image_selectors:
                img = soup.select_one(selector)
                if img:
                    image = img.get("src", "")
                    if image.startswith("//"):
                        image = "https:" + image
                    break
            
            # القصة
            story = ""
            story_selectors = [
                ".anime-story p",
                ".anime-story",
                ".story p",
                ".description p",
                ".anime-description"
            ]
            
            for selector in story_selectors:
                element = soup.select_one(selector)
                if element:
                    story = element.text.strip()
                    break
            
            # التفاصيل الأخرى
            details = {
                "النوع": "غير متوفر",
                "الحالة": "غير متوفر", 
                "بداية العرض": "غير متوفر",
                "الموسم": "غير متوفر",
                "المصدر": "غير متوفر",
                "مدة الحلقة": "غير متوفر",
                "التقييم": "غير متوفر",
                "عدد الحلقات": "غير متوفر"
            }
            
            # جلب التفاصيل من عدة أنماط
            detail_selectors = [
                ".anime-details li",
                "div.anime-info",
                ".info-item",
                ".detail-item"
            ]
            
            for selector in detail_selectors:
                elements = soup.select(selector)
                for element in elements:
                    key_elem = element.select_one("span.detail-title, span")
                    if key_elem:
                        key = key_elem.text.strip().replace(":", "")
                        value_elem = element.select_one("span.detail-value, a")
                        if value_elem:
                            value = value_elem.text.strip()
                        else:
                            # البحث عن النص بعد span
                            value = ""
                            if key_elem.next_sibling:
                                value = key_elem.next_sibling.strip()
                            elif element.select_one("a"):
                                value = element.select_one("a").text.strip()
                        
                        if key in details:
                            details[key] = value
                        else:
                            details[key] = value
            
            # جلب الحلقات
            if existing_data and "episodes" in existing_data:
                episodes, new_count = self.check_and_add_new_episodes(anime_url, existing_data["episodes"])
                print(f"[حلقات] {name}: تم إضافة {new_count} حلقة جديدة. المجموع: {len(episodes)}")
            else:
                episodes = self.get_all_episodes(anime_url)
                print(f"[حلقات] {name}: تم جمع {len(episodes)} حلقة.")
            
            anime_data = {
                "name": name,
                "url": anime_url,
                "image": image,
                "story": story,
                "scraped_at": datetime.now().isoformat(),
                **details,
                "episodes": episodes
            }
            
            return name, anime_data
            
        except Exception as e:
            print(f"[خطأ] في جلب تفاصيل الأنمي: {e}")
            return None, None
    
    def check_and_add_new_episodes(self, anime_url, existing_episodes):
        """التحقق من الحلقات الجديدة وإضافتها"""
        print(f"[فحص] فحص الحلقات الجديدة...")
        
        existing_numbers = {ep["episode_number"] for ep in existing_episodes}
        print(f"[فحص] عدد الحلقات الموجودة: {len(existing_numbers)}")
        
        all_current_episodes = self.get_all_episodes(anime_url)
        
        new_episodes = []
        for episode in all_current_episodes:
            if episode["episode_number"] not in existing_numbers:
                new_episodes.append(episode)
                print(f"[جديد] حلقة جديدة: {episode['episode_number']}")
        
        if new_episodes:
            print(f"[جديد] تم العثور على {len(new_episodes)} حلقة جديدة")
            existing_episodes.extend(new_episodes)
            # ترتيب الحلقات
            try:
                existing_episodes.sort(key=lambda x: int(x["episode_number"]) if x["episode_number"].isdigit() else 0)
            except:
                pass
            return existing_episodes, len(new_episodes)
        else:
            print(f"[تخطي] لا توجد حلقات جديدة")
            return existing_episodes, 0
    
    def get_all_episodes(self, anime_url):
        """جلب جميع الحلقات مع التنقل بين الصفحات"""
        print(f"[حلقات] بدء جلب جميع الحلقات...")
        episodes = []
        page = 1
        processed_urls = set()
        max_pages = 2000  # زيادة الحد الأقصى
        
        while page <= max_pages:
            # بناء رابط صفحة الحلقات
            if page == 1:
                episodes_url = anime_url
            else:
                if anime_url.endswith('/'):
                    episodes_url = anime_url + f"page/{page}/"
                else:
                    episodes_url = anime_url + f"/page/{page}/"
            
            print(f"[حلقات] صفحة {page}: {episodes_url}")
            
            try:
                resp = self.session.get(episodes_url, timeout=30)
                resp.encoding = 'utf-8'
                soup = BeautifulSoup(resp.text, "html.parser")
                
                # البحث عن روابط الحلقات
                episode_links = soup.select(".episodes-card-title h3 a")
                
                # محاولة selectors بديلة
                if not episode_links:
                    alternative_selectors = [
                        ".episode-card a",
                        ".episodes-list a",
                        ".episode-item a", 
                        ".anime-episode a",
                        ".episode-title a",
                        ".episode-link a",
                        ".episode a"
                    ]
                    for selector in alternative_selectors:
                        episode_links = soup.select(selector)
                        if episode_links:
                            print(f"[حلقات] تم العثور على حلقات بـ: {selector}")
                            break
                
                if not episode_links:
                    print(f"[حلقات] لا توجد حلقات في صفحة {page}. المجموع: {len(episodes)}")
                    break
                
                print(f"[حلقات] تم العثور على {len(episode_links)} حلقة في صفحة {page}")
                
                # معالجة الحلقات
                for idx, ep_a in enumerate(episode_links, 1):
                    ep_url = ep_a.get("href")
                    ep_number = ep_a.text.strip()
                    
                    # تنظيف رقم الحلقة
                    ep_number = ep_number.replace("الحلقة الحلقة", "الحلقة").replace("حلقة حلقة", "حلقة").strip()
                    
                    if ep_url in processed_urls:
                        continue
                    
                    if ep_url and ep_url.startswith("http"):
                        processed_urls.add(ep_url)
                        print(f"[حلقة] ({idx}/{len(episode_links)}) جلب سيرفرات الحلقة {ep_number}...")
                        
                        try:
                            watch_servers = self.get_watch_servers(ep_url)
                            print(f"[حلقة] {ep_number}: {len(watch_servers)} سيرفر")
                            
                            episodes.append({
                                "episode_number": ep_number,
                                "episode_url": ep_url,
                                "watch_servers": watch_servers,
                                "scraped_at": datetime.now().isoformat()
                            })
                        except Exception as e:
                            print(f"[خطأ] في الحلقة {ep_number}: {e}")
                            episodes.append({
                                "episode_number": ep_number,
                                "episode_url": ep_url,
                                "watch_servers": [],
                                "error": str(e),
                                "scraped_at": datetime.now().isoformat()
                            })
                        
                        self.random_sleep(1, 2)
                
                # التحقق من الصفحة التالية
                next_page_url = self.find_next_page(soup, page)
                if next_page_url:
                    print(f"[حلقات] صفحة تالية: {next_page_url}")
                    episodes_url = next_page_url
                    page += 1
                else:
                    # اختبار الصفحة التالية
                    test_url = anime_url + f"/page/{page + 1}/" if not anime_url.endswith('/') else anime_url + f"page/{page + 1}/"
                    try:
                        test_resp = self.session.get(test_url, timeout=15)
                        test_soup = BeautifulSoup(test_resp.text, "html.parser")
                        test_episodes = test_soup.select(".episodes-card-title h3 a")
                        
                        if not test_episodes:
                            # محاولة selectors بديلة
                            found = False
                            for selector in [".episode-card a", ".episodes-list a", ".episode-item a"]:
                                if test_soup.select(selector):
                                    found = True
                                    break
                            
                            if not found:
                                print(f"[حلقات] لا توجد صفحات إضافية. المجموع: {len(episodes)}")
                                break
                    except:
                        print(f"[حلقات] لا توجد صفحات إضافية. المجموع: {len(episodes)}")
                        break
                
                page += 1
                self.random_sleep(2, 4)
                
            except Exception as e:
                print(f"[خطأ] في صفحة الحلقات {page}: {e}")
                if page == 1:
                    break
                page += 1
                continue
        
        print(f"[حلقات] تم جمع إجمالي {len(episodes)} حلقة")
        
        # ترتيب الحلقات
        try:
            episodes.sort(key=lambda x: int(x["episode_number"]) if x["episode_number"].isdigit() else 0)
        except:
            pass
        
        return episodes
    
    def find_next_page(self, soup, current_page):
        """البحث عن رابط الصفحة التالية"""
        pagination_selectors = [
            ".pagination a",
            ".episodes-pagination a",
            ".pagination-container a", 
            ".page-numbers a",
            ".episode-pagination a",
            ".pagination .page-numbers a",
            ".pagination .next a",
            ".pagination .prev a"
        ]
        
        for selector in pagination_selectors:
            pagination = soup.select(selector)
            if pagination:
                for link in pagination:
                    href = link.get("href", "")
                    text = link.text.strip().lower()
                    
                    if any(keyword in text for keyword in ["التالي", "next", ">", "التالي"]):
                        if href and href.startswith("http"):
                            return href
                    elif text.isdigit() and int(text) == current_page + 1:
                        if href and href.startswith("http"):
                            return href
                    elif any(keyword in str(link) for keyword in ["fa-chevron-right", "fa-arrow-right", "next"]):
                        if href and href.startswith("http"):
                            return href
        
        # البحث في جميع الروابط
        all_links = soup.find_all("a", href=True)
        for link in all_links:
            href = link.get("href", "")
            if f"page/{current_page + 1}" in href or f"/{current_page + 1}/" in href:
                if href.startswith("http"):
                    return href
        
        return None
    
    def get_watch_servers(self, episode_url):
        """جلب روابط المشاهدة للحلقة"""
        print(f"[سيرفر] جلب سيرفرات: {episode_url}")
        
        try:
            resp = self.session.get(episode_url, timeout=30)
            resp.encoding = 'utf-8'
            soup = BeautifulSoup(resp.text, "html.parser")
            servers = []
            
            # محاولة جلب السيرفرات
            server_selectors = [
                '.hardsub-content ul#episode-servers li a',
                '.episode-servers li a',
                '.servers-list li a',
                '.watch-servers a',
                '.server-item a',
                '.server a',
                '.episode-servers a'
            ]
            
            for selector in server_selectors:
                server_links = soup.select(selector)
                if server_links:
                    for btn in server_links:
                        link = btn.get('data-ep-url') or btn.get('href')
                        if link:
                            if link.startswith('//'):
                                link = 'https:' + link
                            elif link.startswith('/'):
                                link = BASE_URL + link
                            servers.append({
                                "url": link,
                                "name": btn.text.strip() or "سيرفر",
                                "scraped_at": datetime.now().isoformat()
                            })
                    break
            
            # البحث عن روابط فيديو مباشرة
            if not servers:
                video_selectors = [
                    'iframe[src]',
                    'video source[src]',
                    '.video-player iframe',
                    '.player iframe',
                    'video[src]'
                ]
                
                for selector in video_selectors:
                    videos = soup.select(selector)
                    for video in videos:
                        src = video.get('src')
                        if src:
                            if src.startswith('//'):
                                src = 'https:' + src
                            elif src.startswith('/'):
                                src = BASE_URL + src
                            servers.append({
                                "url": src,
                                "name": "فيديو مباشر",
                                "scraped_at": datetime.now().isoformat()
                            })
                    if servers:
                        break
            
            return servers[:5]  # تحديد 5 سيرفرات كحد أقصى
            
        except Exception as e:
            print(f"[خطأ] في جلب السيرفرات: {e}")
            return []
    
    def scrape_all_anime(self, max_pages=None, max_anime=None):
        """جلب جميع الأنميات مع حفظ التقدم"""
        print("[بدء] بدء عملية جلب جميع الأنميات...")
        
        # تحميل التقدم والبيانات الموجودة
        progress = self.load_progress()
        anime_data = self.load_anime_data()
        
        # جلب روابط الأنميات
        all_anime_links = self.get_all_anime_links(max_pages)
        
        if max_anime:
            all_anime_links = all_anime_links[:max_anime]
        
        progress["total_anime"] = len(all_anime_links)
        self.save_progress(progress)
        
        # إحصائيات
        total_anime = len(all_anime_links)
        completed = len(progress["completed_anime"])
        skipped = 0
        updated = 0
        new_anime = 0
        total_new_episodes = 0
        
        print(f"[إحصائيات] إجمالي الأنميات: {total_anime}, مكتمل: {completed}")
        
        for idx, anime_link in enumerate(all_anime_links, 1):
            try:
                print(f"\n[أنمي] ({idx}/{total_anime}) معالجة: {anime_link}")
                
                # التحقق من اكتمال هذا الأنمي
                if anime_link in progress["completed_anime"]:
                    print(f"[تخطي] الأنمي مكتمل مسبقاً")
                    skipped += 1
                    continue
                
                # التحقق من وجود الأنمي في البيانات
                existing_anime = None
                for name, data in anime_data.items():
                    if data.get('url') == anime_link:
                        existing_anime = data
                        break
                
                if existing_anime:
                    print(f"[تحديث] الأنمي موجود، فحص الحلقات الجديدة...")
                    name, updated_data = self.get_anime_details(anime_link, existing_anime)
                    if updated_data and updated_data["episodes"] != existing_anime["episodes"]:
                        anime_data[name] = updated_data
                        updated += 1
                        total_new_episodes += len(updated_data["episodes"]) - len(existing_anime["episodes"])
                        print(f"[تحديث] تم تحديث الأنمي مع {len(updated_data['episodes']) - len(existing_anime['episodes'])} حلقة جديدة")
                    else:
                        print(f"[تخطي] لا توجد تحديثات")
                        skipped += 1
                else:
                    print(f"[جديد] أنمي جديد، جلب جميع البيانات...")
                    name, anime_details = self.get_anime_details(anime_link)
                    if name and anime_details:
                        anime_data[name] = anime_details
                        new_anime += 1
                        total_new_episodes += len(anime_details["episodes"])
                        print(f"[جديد] تم إضافة أنمي جديد مع {len(anime_details['episodes'])} حلقة")
                    else:
                        print(f"[خطأ] فشل في جلب بيانات الأنمي")
                        continue
                
                # تحديث التقدم
                progress["completed_anime"].append(anime_link)
                self.save_progress(progress)
                
                # حفظ البيانات
                self.save_anime_data(anime_data)
                
                # عرض الإحصائيات
                print(f"[إحصائيات] مكتمل: {len(progress['completed_anime'])}, تخطي: {skipped}, تحديث: {updated}, جديد: {new_anime}, حلقات جديدة: {total_new_episodes}")
                
                # تأخير بين الأنميات
                self.random_sleep(3, 6)
                
            except KeyboardInterrupt:
                print(f"\n[إيقاف] تم إيقاف العملية بواسطة المستخدم")
                print(f"[حفظ] حفظ التقدم والبيانات...")
                self.save_progress(progress)
                self.save_anime_data(anime_data)
                return
            except Exception as e:
                print(f"[خطأ] في معالجة {anime_link}: {e}")
                # تسجيل الخطأ
                with open("errors.log", "a", encoding="utf-8") as f:
                    f.write(f"{datetime.now()}: {anime_link} | {e}\n")
                continue
        
        print(f"\n[انتهاء] تم الانتهاء من جلب جميع الأنميات!")
        print(f"[إحصائيات نهائية]")
        print(f"  - إجمالي الأنميات: {len(anime_data)}")
        print(f"  - تم تخطي: {skipped}")
        print(f"  - تم تحديث: {updated}")
        print(f"  - أنميات جديدة: {new_anime}")
        print(f"  - حلقات جديدة: {total_new_episodes}")
        print(f"  - تم حفظ البيانات في: {ANIME_DATA_FILE}")

def main():
    scraper = AnimeScraper()
    
    # معالجة المعاملات
    if len(sys.argv) > 1:
        if sys.argv[1] == "--test":
            # اختبار على أنمي واحد
            test_url = "https://4m.kamrix.shop/anime/one-piece/"
            print(f"[اختبار] اختبار على: {test_url}")
            name, data = scraper.get_anime_details(test_url)
            if name and data:
                anime_data = {name: data}
                scraper.save_anime_data(anime_data)
                print(f"[اختبار] تم حفظ بيانات الاختبار")
        elif sys.argv[1] == "--max-pages" and len(sys.argv) > 2:
            max_pages = int(sys.argv[2])
            scraper.scrape_all_anime(max_pages=max_pages)
        elif sys.argv[1] == "--max-anime" and len(sys.argv) > 2:
            max_anime = int(sys.argv[2])
            scraper.scrape_all_anime(max_anime=max_anime)
        elif sys.argv[1] == "--resume":
            print("[استئناف] استئناف العملية من آخر نقطة...")
            scraper.scrape_all_anime()
        else:
            print("الاستخدام:")
            print("  python scrape_anime.py                    # جلب جميع الأنميات")
            print("  python scrape_anime.py --test             # اختبار على أنمي واحد")
            print("  python scrape_anime.py --max-pages 10     # تحديد عدد الصفحات")
            print("  python scrape_anime.py --max-anime 50     # تحديد عدد الأنميات")
            print("  python scrape_anime.py --resume           # استئناف العملية")
    else:
        # العملية العادية
        scraper.scrape_all_anime()

if __name__ == "__main__":
    main() 