from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import os
import time

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

output_folder = r"D:\pcdata\Py\mbti"  # 指定保存的文件夹

try:
    driver.get('https://styx.personality-database.com/personality?_gl=1*18b7blj*_ga*MTg1ODU5Njc4OC4xNzE0NzI4MzA2*_ga_8S3H6J5GSR*MTcxNDcyODMwNS4xLjEuMTcxNDcyODUyOS40MC4wLjA')
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".index_item__N5Geu"))
    )

    items = driver.find_elements(By.CSS_SELECTOR, ".index_item__N5Geu")
    total_items = len(items[:16])  # 限制为前16个元素
    for index in range(total_items):
        try:
            # 重新获取元素以防止过时的元素引用
            items = driver.find_elements(By.CSS_SELECTOR, ".index_item__N5Geu")
            items[index].click()
            time.sleep(5)  # 等待页面加载

            # 获取新页面的内容
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            text_content = soup.find('div', class_='index_root_content__V8loD').text

            # 确保目标文件夹存在，如果不存在则创建
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)

            # 保存到指定的文件夹
            with open(os.path.join(output_folder, f'output_{index + 1}.txt'), 'w', encoding='utf-8') as file:
                file.write(text_content)

            driver.back()
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".index_item__N5Geu"))
            )
        except StaleElementReferenceException:
            print(f"Stale element encountered at index {index}, retrying...")
            continue  # 如果遇到过时的元素引用错误，跳过当前循环的剩余部分并重试
except TimeoutException as e:
    print(f"Timeout error: {e}")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    driver.quit()
