import streamlit as st
import pandas as pd
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import time
import re

# Настройка страницы
st.set_page_config(page_title="Мониторинг цен", page_icon="💰", layout="wide")

st.title("💰 Мониторинг цен товаров")
st.markdown("---")

# Функция для парсинга Wildberries
def parse_wildberries(browser, search_query, url):
    """Парсинг товаров с Wildberries"""
    results = []
    try:
        page = browser.new_page()
        page.set_viewport_size({"width": 1920, "height": 1080})
        
        st.info(f"🔍 Открываю страницу: {url}")
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        time.sleep(3)  # Ждем загрузки контента
        
        # CSS-селекторы для Wildberries (обновлено для актуальной версии сайта)
        # ⚠️ ВАЖНО: Эти селекторы могут меняться! Проверяйте через DevTools браузера
        product_cards = page.query_selector_all('article.product-card')
        
        if not product_cards:
            st.warning("⚠️ Товары не найдены. Возможно, нужно обновить селекторы.")
            return results
        
        st.success(f"✅ Найдено карточек товаров: {len(product_cards)}")
        
        for card in product_cards[:20]:  # Берем первые 20 товаров
            try:
                # Название товара
                # 🔧 СЕЛЕКТОР ДЛЯ ИЗМЕНЕНИЯ: Измените селектор ниже для вашего сайта
                name_elem = card.query_selector('.product-card__name')
                name = name_elem.inner_text().strip() if name_elem else "Не указано"
                
                # Фильтрация по поисковому запросу
                if search_query.lower() not in name.lower():
                    continue
                
                # Артикул
                # 🔧 СЕЛЕКТОР ДЛЯ ИЗМЕНЕНИЯ
                article_elem = card.query_selector('.product-card__article')
                article = article_elem.inner_text().strip() if article_elem else "Не указан"
                
                # Цена
                # 🔧 СЕЛЕКТОР ДЛЯ ИЗМЕНЕНИЯ
                price_elem = card.query_selector('.price__lower-price')
                if price_elem:
                    price_text = price_elem.inner_text().strip()
                    # Извлекаем только цифры
                    price = re.sub(r'[^\d]', '', price_text)
                    price = f"{price} ₽" if price else "Не указана"
                else:
                    price = "Не указана"
                
                results.append({
                    "Название": name,
                    "Артикул": article,
                    "Цена": price,
                    "Источник": "Wildberries"
                })
                
            except Exception as e:
                st.warning(f"⚠️ Ошибка при обработке карточки: {str(e)}")
                continue
        
        page.close()
        
    except PlaywrightTimeout:
        st.error(f"❌ Превышено время ожидания загрузки страницы: {url}")
    except Exception as e:
        st.error(f"❌ Ошибка при парсинге {url}: {str(e)}")
    
    return results


# Функция для парсинга других сайтов (шаблон)
def parse_generic_site(browser, search_query, url):
    """
    Шаблон для парсинга других сайтов
    
    🔧 КАК АДАПТИРОВАТЬ ДЛЯ ДРУГОГО САЙТА:
    1. Откройте сайт в браузере Chrome/Edge
    2. Нажмите F12 (открыть DevTools)
    3. Нажмите Ctrl+Shift+C и наведите на элемент товара
    4. Найдите CSS-селекторы для: названия, артикула, цены
    5. Замените селекторы в коде ниже
    """
    results = []
    try:
        page = browser.new_page()
        page.set_viewport_size({"width": 1920, "height": 1080})
        
        st.info(f"🔍 Открываю страницу: {url}")
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        time.sleep(3)
        
        # 🔧 ЗАМЕНИТЕ СЕЛЕКТОРЫ НА АКТУАЛЬНЫЕ ДЛЯ ВАШЕГО САЙТА
        product_cards = page.query_selector_all('.product-item')  # Основной контейнер товара
        
        if not product_cards:
            st.warning("⚠️ Товары не найдены. Проверьте селектор '.product-item'")
            return results
        
        st.success(f"✅ Найдено карточек товаров: {len(product_cards)}")
        
        for card in product_cards[:20]:
            try:
                # 🔧 ЗАМЕНИТЕ на селектор названия товара
                name_elem = card.query_selector('.product-title')
                name = name_elem.inner_text().strip() if name_elem else "Не указано"
                
                if search_query.lower() not in name.lower():
                    continue
                
                # 🔧 ЗАМЕНИТЕ на селектор артикула
                article_elem = card.query_selector('.product-sku')
                article = article_elem.inner_text().strip() if article_elem else "Не указан"
                
                # 🔧 ЗАМЕНИТЕ на селектор цены
                price_elem = card.query_selector('.product-price')
                if price_elem:
                    price_text = price_elem.inner_text().strip()
                    price = re.sub(r'[^\d]', '', price_text)
                    price = f"{price} ₽" if price else "Не указана"
                else:
                    price = "Не указана"
                
                results.append({
                    "Название": name,
                    "Артикул": article,
                    "Цена": price,
                    "Источник": url
                })
                
            except Exception as e:
                continue
        
        page.close()
        
    except Exception as e:
        st.error(f"❌ Ошибка при парсинге {url}: {str(e)}")
    
    return results


# Основная функция парсинга
def scrape_prices(search_query, urls):
    """Главная функция для сбора данных"""
    all_results = []
    
    with sync_playwright() as p:
        # Запуск браузера с эмуляцией реального пользователя
        browser = p.chromium.launch(
            headless=True,  # Измените на False, чтобы видеть браузер
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage'
            ]
        )
        
        # Устанавливаем реальный User-Agent
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
            locale='ru-RU'
        )
        
        for url in urls:
            url = url.strip()
            if not url:
                continue
            
            # Определяем тип сайта и используем соответствующий парсер
            if 'wildberries.ru' in url or 'wb.ru' in url:
                results = parse_wildberries(context, search_query, url)
            else:
                results = parse_generic_site(context, search_query, url)
            
            all_results.extend(results)
            time.sleep(2)  # Пауза между запросами
        
        context.close()
        browser.close()
    
    return all_results


# Интерфейс приложения
col1, col2 = st.columns([1, 1])

with col1:
    search_query = st.text_input(
        "🔍 Поисковый запрос (название товара)",
        placeholder="Например: смартфон samsung",
        help="Введите название товара для поиска"
    )

with col2:
    st.write("")  # Отступ для выравнивания

# Поле для ввода ссылок
st.markdown("### 🔗 Ссылки на страницы магазинов")
st.markdown("*Вставьте ссылки на категории или результаты поиска (каждая ссылка с новой строки)*")

urls_input = st.text_area(
    "URLs",
    height=150,
    placeholder="""https://www.wildberries.ru/catalog/elektronika/smartfony-i-telefony
https://www.wildberries.ru/catalog/elektronika/noutbuki-pereferiya""",
    label_visibility="collapsed"
)

# Примеры ссылок
with st.expander("📝 Примеры ссылок для тестирования"):
    st.code("""
# Wildberries - Смартфоны
https://www.wildberries.ru/catalog/elektronika/smartfony-i-telefony/smartfony

# Wildberries - Ноутбуки
https://www.wildberries.ru/catalog/elektronika/noutbuki-pereferiya/noutbuki-ultrabuki

# Для поиска конкретного товара используйте поиск на сайте и скопируйте URL
    """)

# Кнопка запуска
if st.button("🚀 Начать мониторинг", type="primary", use_container_width=True):
    if not search_query:
        st.error("❌ Введите поисковый запрос!")
    elif not urls_input.strip():
        st.error("❌ Добавьте хотя бы одну ссылку!")
    else:
        urls = [url for url in urls_input.split('\n') if url.strip()]
        
        with st.spinner(f"⏳ Ищу товары по запросу '{search_query}'..."):
            results = scrape_prices(search_query, urls)
        
        if results:
            st.success(f"✅ Найдено товаров: {len(results)}")
            
            # Создаем DataFrame
            df = pd.DataFrame(results)
            
            # Выводим таблицу
            st.markdown("### 📊 Результаты мониторинга")
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Название": st.column_config.TextColumn("Название товара", width="large"),
                    "Артикул": st.column_config.TextColumn("Артикул", width="medium"),
                    "Цена": st.column_config.TextColumn("Цена", width="small"),
                    "Источник": st.column_config.TextColumn("Магазин", width="medium")
                }
            )
            
            # Кнопка скачивания CSV
            csv = df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 Скачать результаты (CSV)",
                data=csv,
                file_name=f"price_monitoring_{search_query}.csv",
                mime="text/csv"
            )
        else:
            st.warning("⚠️ Товары не найдены. Попробуйте другой запрос или проверьте ссылки.")

# Инструкция по использованию
with st.expander("❓ Как использовать приложение"):
    st.markdown("""
    ### Пошаговая инструкция:
    
    1. **Введите название товара** в поле поиска (например: "смартфон samsung")
    
    2. **Добавьте ссылки** на страницы магазинов:
       - Откройте сайт магазина (например, Wildberries)
       - Перейдите в нужную категорию или используйте поиск на сайте
       - Скопируйте URL из адресной строки браузера
       - Вставьте ссылку в поле "Ссылки на страницы магазинов"
    
    3. **Нажмите "Начать мониторинг"** и дождитесь результатов
    
    4. **Сохраните результаты** в CSV-файл при необходимости
    
    ### 🔧 Адаптация под другие сайты:
    
    Чтобы добавить поддержку нового магазина:
    1. Откройте сайт в браузере Chrome/Edge
    2. Нажмите F12 (DevTools) → Выберите элемент (Ctrl+Shift+C)
    3. Наведите на карточку товара и найдите CSS-селекторы
    4. Откройте код и найдите функцию `parse_generic_site`
    5. Замените селекторы, помеченные 🔧
    """)

st.markdown("---")
st.markdown("*💡 Совет: Если приложение не находит товары, попробуйте обновить CSS-селекторы в коде*")
