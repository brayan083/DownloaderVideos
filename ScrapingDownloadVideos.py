'''
Cosas que hay que hacer antes de correr el script:
1. Instalar Dependencias
2. Cambiar el path de descarga en la linea 79
3. este script puede tener muchos problemas usar con precaución
'''

import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

with open('enlaces.txt', 'r', encoding='utf-8') as file:
    content = file.read()

content_str = str(content)

enlaces = content_str.split('\n')
enlaces = [enlace.strip() for enlace in enlaces if enlace.strip()]


for enlace in enlaces:    
    # Configurar Selenium
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Ejecutar en modo headless (sin interfaz gráfica)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    pageDownload = 'https://getof.net/#url=' + enlace
    name_archive = enlace.split('/')[-1].split('?')[0] + '.mp4'
    
    driver.get(pageDownload)
    
    # Esperar a que la página cargue completamente
    time.sleep(5)
    
    # Usar BeautifulSoup para analizar el HTML de la página
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    # Encontrar el botón de descarga (ajusta el selector según sea necesario)
    download_button = soup.find('button', {'id': 'downloadBtn'})  # Ajusta el selector según el HTML de la página
    
    
    if download_button:
        # Hacer clic en el botón de descarga usando Selenium
        driver.find_element(By.ID, 'downloadBtn').click()
        print(f'Descargando video desde: {enlace}')
        
        # Esperar a que el enlace de descarga aparezca
        time.sleep(5)
        
        # Volver a analizar el HTML de la página
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Encontrar el enlace de descarga
        reference_link_id = driver.find_element(By.XPATH, '/html/body/div[2]/div/div/div[1]/div/div[2]/a')
        link_download = reference_link_id.get_attribute('href')
        
        if link_download:
            print(f'Enlace de descarga: {link_download}')
            
            # Abrir el enlace de descarga en una nueva pestaña
            driver.execute_script("window.open(arguments[0], '_blank');", link_download)
            
            # Cambiar a la nueva pestaña
            driver.switch_to.window(driver.window_handles[-1])
            
            # Esperar a que la página cargue completamente
            time.sleep(5)
            
            # Esperar hasta que la descarga haya terminado
            download_dir = r'C:\Users\zorro\Downloads'  # Cambia esto a tu directorio de descargas
            initial_files = set(os.listdir(download_dir))
            file_path = os.path.join(download_dir, name_archive)
            print(f'Esperando a que se complete la descarga en: {name_archive}')
            
            while True:
                current_files = set(os.listdir(download_dir))
                new_files = current_files - initial_files
                if new_files:
                    latest_file = max(new_files, key=lambda f: os.path.getctime(os.path.join(download_dir, f)))
                    if latest_file.endswith('.mp4'):
                        file_path = os.path.join(download_dir, latest_file)
                        break
                time.sleep(1)
            
            print(f'Descarga completada: {file_path}')
            
            # Cerrar la nueva pestaña
            driver.close()
            
            # Volver a la pestaña original
            driver.switch_to.window(driver.window_handles[0])
            
        else:
            print(f'Enlace de descarga no encontrado para: {enlace}')
        
    else:
        print(f'Botón de descarga no encontrado para: {enlace}')

    # Cerrar el navegador
    driver.quit()


print('Proceso completado :)')