import streamlit as st
import pandas as pd
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import time
import re
from urllib.parse import quote

# Настройка страницы
st.set_page_config(page_title="Мониторинг цен косметики", page_icon="💄", layout="wide")

st.title("💄 Мониторинг цен косметики и парфюмерии")
st.markdown("---")


def parse_notino(page, search_query):
    """Парсинг товаров с Notino.pl"""
    results = []
    try:
        st.info(f"🔍 Notino.pl: Ищу товары...")
        
        search_url = f"https://www.notino.pl/search/{quote(search_query)}/"
        page.goto(search_url, wait_until="networkidle", timeout=30000)
        time.sleep(3)
        
        # Ждем загрузки товаров
        page.wait_for_selector('div[class*="styled__box"]', timeout=10000)
        
        # Прокрутка для загрузки всех товаров
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(2)
        
        # Получаем все карточки товаров
        products = page.query_selector_all('div[class*="styled__box"]')
        
        st.success(f"✅ Notino.pl: Найдено {len(products)} товаров")
        
        for product in products[:15]:
            try:
                # Название товара
                title_elem = product.query_selector('h3, div[class*="ProductTitle"]')
                if not title_elem:
                    continue
                    
                title = title_elem.inner_text().strip()
                
                # Бренд
                brand_elem = product.query_selector('span[class*="ProductBrand"]')
                brand = brand_elem.inner_text().strip() if brand_elem else ""
                
                # Цена
                price_elem = product.query_selector('span[class*="Price"]')
                price = price_elem.inner_text().strip() if price_elem else "Цена не указана"
                
                # Ссылка
                link_elem = product.query_selector('a[href]')
                link = ""
                if link_elem:
                    href = link_elem.get_attribute('href')
                    if href:
                        link = f"https://www.notino.pl{href}" if not href.startswith('http') else href
                
                results.append({
                    "Магазин": "Notino.pl",
                    "Бренд": brand,
                    "Название": title,
                    "Цена": price,
                    "Ссылка": link
                })
                
            except Exception as e:
                continue
                
    except PlaywrightTimeout:
        st.warning("⚠️ Notino.pl: Превышено время ожидания")
    except Exception as e:
        st.error(f"❌ Notino.pl: Ошибка - {str(e)}")
    
    return results


def parse_makeup_ua(page, search_query):
    """Парсинг товаров с Makeup.com.ua"""
    results = []
    try:
        st.info(f"🔍 Makeup.com.ua: Ищу товары...")
        
        search_url = f"https://makeup.com.ua/ua/search/?q={quote(search_query)}"
        page.goto(search_url, wait_until="networkidle", timeout=30000)
        time.sleep(3)
        
        # Ждем карточки товаров
        page.wait_for_selector('div.catalog-item', timeout=10000)
        
        products = page.query_selector_all('div.catalog-item')
        
        st.success(f"✅ Makeup.com.ua: Найдено {len(products)} товаров")
        
        for product in products[:15]:
            try:
                # Название
                title_elem = product.query_selector('a.catalog-item__name')
                if not title_elem:
                    continue
                    
                title = title_elem.inner_text().strip()
                
                # Бренд
                brand_elem = product.query_selector('span.catalog-item__brand')
                brand = brand_elem.inner_text().strip() if brand_elem else ""
                
                # Цена
                price_elem = product.query_selector('span[data-price]')
                price = price_elem.inner_text().strip() if price_elem else "Цена не указана"
                
                # Ссылка
                link = ""
                if title_elem:
                    href = title_elem.get_attribute('href')
                    if href:
                        link = f"https://makeup.com.ua{href}" if not href.startswith('http') else href
                
                results.append({
                    "Магазин": "Makeup.com.ua",
                    "Бренд": brand,
                    "Название": title,
                    "Цена": price,
                    "Ссылка": link
                })
                
            except Exception as e:
                continue
                
    except PlaywrightTimeout:
        st.warning("⚠️ Makeup.com.ua: Превышено время ожидания")
    except Exception as e:
        st.error(f"❌ Makeup.com.ua: Ошибка - {str(e)}")
    
    return results


def parse_makeup_pl(page, search_query):
    """Парсинг товаров с Makeup.pl"""
    results = []
    try:
        st.info(f"🔍 Makeup.pl: Ищу товары...")
        
        search_url = f"https://makeup.pl/search/?q={quote(search_query)}"
        page.goto(search_url, wait_until="networkidle", timeout=30000)
        time.sleep(3)
        
        page.wait_for_selector('div.catalog-item', timeout=10000)
        
        products = page.query_selector_all('div.catalog-item')
        
        st.success(f"✅ Makeup.pl: Найдено {len(products)} товаров")
        
        for product in products[:15]:
            try:
                title_elem = product.query_selector('a.catalog-item__name')
                if not title_elem:
                    continue
                    
                title = title_elem.inner_text().strip()
                
                brand_elem = product.query_selector('span.catalog-item__brand')
                brand = brand_elem.inner_text().strip() if brand_elem else ""
                
                price_elem = product.query_selector('span[data-price]')
                price = price_elem.inner_text().strip() if price_elem else "Цена не указана"
                
                link = ""
                if title_elem:
                    href = title_elem.get_attribute('href')
                    if href:
                        link = f"https://makeup.pl{href}" if not href.startswith('http') else href
                
                results.append({
                    "Магазин": "Makeup.pl",
                    "Бренд": brand,
                    "Название": title,
                    "Цена": price,
                    "Ссылка": link
                })
                
            except Exception as e:
                continue
                
    except PlaywrightTimeout:
        st.warning("⚠️ Makeup.pl: Превышено время ожидания")
    except Exception as e:
        st.error(f"❌ Makeup.pl: Ошибка - {str(e)}")
    
    return results


def parse_sephora(page, search_query):
    """Парсинг товаров с Sephora.pl"""
    results = []
    try:
        st.info(f"🔍 Sephora.pl: Ищу товары...")
        
        search_url = f"https://www.sephora.pl/search?q={quote(search_query)}"
        page.goto(search_url, wait_until="networkidle", timeout=30000)
        time.sleep(4)
        
        # Прокрутка для загрузки товаров
        page.evaluate("window.scrollTo(0, 1000)")
        time.sleep(2)
        
        # Пытаемся найти товары по разным селекторам
        products = page.query_selector_all('div[data-at="product_tile"]')
        if not products:
            products = page.query_selector_all('article[data-comp*="ProductTile"]')
        if not products:
            products = page.query_selector_all('div[class*="ProductTile"]')
        
        st.success(f"✅ Sephora.pl: Найдено {len(products)} товаров")
        
        for product in products[:15]:
            try:
                # Название
                title_elem = product.query_selector('span[data-at="sku_name"], div[class*="ProductName"]')
                if not title_elem:
                    continue
                    
                title = title_elem.inner_text().strip()
                
                # Бренд
                brand_elem = product.query_selector('span[data-at="brand_name"], span[class*="Brand"]')
                brand = brand_elem.inner_text().strip() if brand_elem else ""
                
                # Цена
                price_elem = product.query_selector('span[data-at="price"], span[class*="Price"]')
                price = price_elem.inner_text().strip() if price_elem else "Цена не указана"
                
                # Ссылка
                link_elem = product.query_selector('a[href]')
                link = ""
                if link_elem:
                    href = link_elem.get_attribute('href')
                    if href:
                        link = f"https://www.sephora.pl{href}" if not href.startswith('http') else href
                
                results.append({
                    "Магазин": "Sephora.pl",
                    "Бренд": brand,
                    "Название": title,
                    "Цена": price,
                    "Ссылка": link
                })
                
            except Exception as e:
                continue
                
    except PlaywrightTimeout:
        st.warning("⚠️ Sephora.pl: Превышено время ожидания")
    except Exception as e:
        st.error(f"❌ Sephora.pl: Ошибка - {str(e)}")
    
    return results


def parse_douglas(page, search_query):
    """Парсинг товаров с Douglas.pl"""
    results = []
    try:
        st.info(f"🔍 Douglas.pl: Ищу товары...")
        
        search_url = f"https://www.douglas.pl/pl/search?text={quote(search_query)}"
        page.goto(search_url, wait_until="networkidle", timeout=30000)
        time.sleep(4)
        
        # Прокрутка
        page.evaluate("window.scrollTo(0, 1000)")
        time.sleep(2)
        
        products = page.query_selector_all('div[class*="product-tile"]')
        if not products:
            products = page.query_selector_all('div[data-testid*="product"]')
        
        st.success(f"✅ Douglas.pl: Найдено {len(products)} товаров")
        
        for product in products[:15]:
            try:
                title_elem = product.query_selector('span[class*="product-name"], div[class*="name"]')
                if not title_elem:
                    continue
                    
                title = title_elem.inner_text().strip()
                
                brand_elem = product.query_selector('span[class*="brand"]')
                brand = brand_elem.inner_text().strip() if brand_elem else ""
                
                price_elem = product.query_selector('span[class*="price"]')
                price = price_elem.inner_text().strip() if price_elem else "Цена не указана"
                
                link_elem = product.query_selector('a[href]')
                link = ""
                if link_elem:
                    href = link_elem.get_attribute('href')
                    if href:
                        link = f"https://www.douglas.pl{href}" if not href.startswith('http') else href
                
                results.append({
                    "Магазин": "Douglas.pl",
                    "Бренд": brand,
                    "Название": title,
                    "Цена": price,
                    "Ссылка": link
                })
                
            except Exception as e:
                continue
                
    except PlaywrightTimeout:
        st.warning("⚠️ Douglas.pl: Превышено время ожидания")
    except Exception as e:
        st.error(f"❌ Douglas.pl: Ошибка - {str(e)}")
    
    return results


def parse_brocard(page, search_query):
    """Парсинг товаров с Brocard.ua"""
    results = []
    try:
        st.info(f"🔍 Brocard.ua: Ищу товары...")
        
        search_url = f"https://www.brocard.ua/ua/search/?q={quote(search_query)}"
        page.goto(search_url, wait_until="networkidle", timeout=30000)
        time.sleep(4)
        
        page.evaluate("window.scrollTo(0, 1000)")
        time.sleep(2)
        
        products = page.query_selector_all('div[class*="product-item"]')
        if not products:
            products = page.query_selector_all('article[class*="product"]')
        
        st.success(f"✅ Brocard.ua: Найдено {len(products)} товаров")
        
        for product in products[:15]:
            try:
                title_elem = product.query_selector('a[class*="product-name"], div[class*="name"]')
                if not title_elem:
                    continue
                    
                title = title_elem.inner_text().strip()
                
                brand_elem = product.query_selector('span[class*="brand"]')
                brand = brand_elem.inner_text().strip() if brand_elem else ""
                
                price_elem = product.query_selector('span[class*="price"]')
                price = price_elem.inner_text().strip() if price_elem else "Цена не указана"
                
                link = ""
                if hasattr(title_elem, 'get_attribute'):
                    href = title_elem.get_attribute('href')
                    if href:
                        link = f"https://www.brocard.ua{href}" if not href.startswith('http') else href
                
                results.append({
                    "Магазин": "Brocard.ua",
                    "Бренд": brand,
                    "Название": title,
                    "Цена": price,
                    "Ссылка": link
                })
                
            except Exception as e:
                continue
                
    except PlaywrightTimeout:
        st.warning("⚠️ Brocard.ua: Превышено время ожидания")
    except Exception as e:
        st.error(f"❌ Brocard.ua: Ошибка - {str(e)}")
    
    return results


def scrape_prices(search_query, sites_to_search):
    """Главная функция для сбора данных"""
    all_results = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-web-security'
            ]
        )
        
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
            locale='pl-PL'
        )
        
        page = context.new_page()
        
        # Парсим выбранные сайты
        if 'notino' in sites_to_search:
            results = parse_notino(page, search_query)
            all_results.extend(results)
        
        if 'makeup_ua' in sites_to_search:
            results = parse_makeup_ua(page, search_query)
            all_results.extend(results)
        
        if 'makeup_pl' in sites_to_search:
            results = parse_makeup_pl(page, search_query)
            all_results.extend(results)
        
        if 'sephora' in sites_to_search:
            results = parse_sephora(page, search_query)
            all_results.extend(results)
        
        if 'douglas' in sites_to_search:
            results = parse_douglas(page, search_query)
            all_results.extend(results)
        
        if 'brocard' in sites_to_search:
            results = parse_brocard(page, search_query)
            all_results.extend(results)
        
        page.close()
        context.close()
        browser.close()
    
    return all_results


# Интерфейс приложения
st.markdown("### 🔍 Поиск товара")
search_query = st.text_input(
    "Введите название товара или бренд",
    placeholder="Например: Dior Sauvage, Chanel No 5, тональный крем",
    help="Поиск будет выполнен по всем выбранным магазинам"
)

st.markdown("### 🏪 Выберите магазины для поиска")

col1, col2, col3 = st.columns(3)

with col1:
    notino = st.checkbox("🇵🇱 Notino.pl", value=True)
    makeup_ua = st.checkbox("🇺🇦 Makeup.com.ua", value=True)

with col2:
    makeup_pl = st.checkbox("🇵🇱 Makeup.pl", value=True)
    sephora = st.checkbox("🇵🇱 Sephora.pl", value=True)

with col3:
    douglas = st.checkbox("🇵🇱 Douglas.pl", value=True)
    brocard = st.checkbox("🇺🇦 Brocard.ua", value=True)

# Кнопка запуска
st.markdown("---")
if st.button("🚀 Начать поиск", type="primary", use_container_width=True):
    if not search_query.strip():
        st.error("❌ Введите название товара!")
    else:
        # Собираем выбранные сайты
        sites = []
        if notino: sites.append('notino')
        if makeup_ua: sites.append('makeup_ua')
        if makeup_pl: sites.append('makeup_pl')
        if sephora: sites.append('sephora')
        if douglas: sites.append('douglas')
        if brocard: sites.append('brocard')
        
        if not sites:
            st.error("❌ Выберите хотя бы один магазин!")
        else:
            with st.spinner(f"⏳ Ищу '{search_query}' в {len(sites)} магазинах... Это может занять несколько минут."):
                results = scrape_prices(search_query, sites)
            
            if results:
                st.success(f"✅ Найдено товаров: {len(results)}")
                
                df = pd.DataFrame(results)
                
                # Статистика
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Всего товаров", len(results))
                with col2:
                    st.metric("Магазинов", df['Магазин'].nunique())
                with col3:
                    brands_count = len(df[df['Бренд'].str.strip() != '']['Бренд'].unique())
                    st.metric("Брендов", brands_count)
                
                st.markdown("### 📊 Результаты поиска")
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Магазин": st.column_config.TextColumn("Магазин", width="small"),
                        "Бренд": st.column_config.TextColumn("Бренд", width="medium"),
                        "Название": st.column_config.TextColumn("Товар", width="large"),
                        "Цена": st.column_config.TextColumn("Цена", width="small"),
                        "Ссылка": st.column_config.LinkColumn("Ссылка", width="small")
                    }
                )
                
                # Скачивание
                csv = df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📥 Скачать результаты (CSV)",
                    data=csv,
                    file_name=f"cosmetics_{search_query.replace(' ', '_')}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("⚠️ Товары не найдены. Попробуйте:\n- Изменить поисковый запрос\n- Использовать более общее название\n- Проверить правильность написания")

# Инструкция
with st.expander("❓ Как использовать приложение"):
    st.markdown("""
    ### 📝 Инструкция:
    
    1. **Введите название товара** (например: "Dior Sauvage", "помада Maybelline")
    2. **Выберите магазины**, где нужно искать (по умолчанию все)
    3. **Нажмите "Начать поиск"** и подождите 2-5 минут
    4. **Просмотрите результаты** в таблице
    5. **Скачайте CSV** при необходимости
    
    ### 💡 Советы для лучших результатов:
    
    - ✅ **Хорошие запросы**: "Chanel Coco", "крем Nivea", "тушь Maybelline"
    - ❌ **Плохие запросы**: "крем" (слишком общее), "123456" (артикул может не работать)
    - 🔍 Используйте **название бренда + тип товара** для точности
    - 🌍 Учитывайте язык: польские сайты лучше искать на польском/английском
    
    ### 🔧 Поддерживаемые магазины:
    
    - 🇵🇱 **Notino.pl** - парфюмерия, косметика, уход
    - 🇺🇦 **Makeup.com.ua** - косметика, уход за кожей
    - 🇵🇱 **Makeup.pl** - польская версия Makeup
    - 🇵🇱 **Sephora.pl** - премиум косметика и парфюмерия
    - 🇵🇱 **Douglas.pl** - косметика, парфюмерия, уход
    - 🇺🇦 **Brocard.ua** - парфюмерия и косметика
    
    ### ⚠️ Важные замечания:
    
    - ⏱️ Поиск может занять **2-5 минут** в зависимости от количества магазинов
    - 🔄 Селекторы обновляются, но могут устареть при изменении дизайна сайта
    - 🛡️ Некоторые сайты могут иметь защиту от автоматического парсинга
    - 📊 Результаты зависят от наличия товара и работы поиска на сайте
    - 💱 Цены в разных валютах: PLN (польский злотый), UAH (украинская гривна)
    
    ### 🐛 Если что-то не работает:
    
    1. Проверьте интернет-соединение
    2. Попробуйте другой поисковый запрос
    3. Выберите меньше магазинов для тестирования
    4. Убедитесь, что Playwright установлен корректно
    """)

with st.expander("🔧 Техническая информация"):
    st.markdown("""
    ### Используемые селекторы:
    
    **Notino.pl:**
    - Карточки: `div[class*="styled__box"]`
    - Название: `h3, div[class*="ProductTitle"]`
    - Бренд: `span[class*="ProductBrand"]`
    - Цена: `span[class*="Price"]`
    
    **Makeup (UA/PL):**
    - Карточки: `div.catalog-item`
    - Название: `a.catalog-item__name`
    - Бренд: `span.catalog-item__brand`
    - Цена: `span[data-price]`
    
    **Sephora.pl:**
    - Карточки: `div[data-at="product_tile"]`
    - Название: `span[data-at="sku_name"]`
    - Бренд: `span[data-at="brand_name"]`
    - Цена: `span[data-at="price"]`
    
    **Douglas.pl:**
    - Карточки: `div[class*="product-tile"]`
    - Название: `span[class*="product-name"]`
    - Цена: `span[class*="price"]`
    
    **Brocard.ua:**
    - Карточки: `div[class*="product-item"]`
    - Название: `a[class*="product-name"]`
    - Цена: `span[class*="price"]`
    
    *Селекторы актуальны на момент создания (декабрь 2024)*
    """)

st.markdown("---")
st.markdown("*💄 Приложение для мониторинга цен косметики и парфюмерии | Версия 2.0*")
