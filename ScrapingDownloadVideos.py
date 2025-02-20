'''
Cosas que hay que hacer antes de correr el script:
1. Instalar Dependencias
2. Cambiar el path de descarga en la linea 79
3. este script puede tener muchos problemas usar con precaución
'''

import os
import logging
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def leer_enlaces(archivo):
    with open(archivo, 'r', encoding='utf-8') as file:
        content = file.read()
    return [enlace.strip() for enlace in content.split('\n') if enlace.strip()]

def configurar_driver():
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')  # Ejecutar en modo headless (sin interfaz gráfica)
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def obtener_enlace_descarga(driver, enlace):
    pageDownload = 'https://getof.net/#url=' + enlace
    driver.get(pageDownload)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'downloadBtn')))
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    download_button = soup.find('button', {'id': 'downloadBtn'})
    
    if download_button:
        driver.find_element(By.ID, 'downloadBtn').click()
        logging.info(f'Descargando video desde: {enlace}')
        
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div/div/div[1]/div/div[2]/a')))
        reference_link_id = driver.find_element(By.XPATH, '/html/body/div[2]/div/div/div[1]/div/div[2]/a')
        return reference_link_id.get_attribute('href')
    else:
        logging.warning(f'Botón de descarga no encontrado para: {enlace}')
        return None

def esperar_descarga(download_dir):
    initial_files = set(os.listdir(download_dir))
    while True:
        current_files = set(os.listdir(download_dir))
        new_files = current_files - initial_files
        if any(file.endswith('.mp4') for file in new_files):
            return new_files
        time.sleep(1)

def renombrar_archivo(download_dir, new_files, name_archive):
    new_file = max(new_files, key=lambda f: os.path.getctime(os.path.join(download_dir, f)))
    if new_file.endswith('.mp4'):
        old_path = os.path.join(download_dir, new_file)
        new_path = os.path.join(download_dir, f'{name_archive}.mp4')
        os.rename(old_path, new_path)
        logging.info(f'Archivo renombrado a: {new_path}')
        return new_path
    return None

def mover_archivo(new_path, name_archive):
    destination_dir = r'C:\Users\zorro\Downloads\videos test 20-2'
    if not os.path.exists(destination_dir):
        print('No existe la carpeta')
        os.makedirs(destination_dir)
    
    final_path = os.path.join(destination_dir, f'{name_archive}.mp4')
    base_name = name_archive
    counter = 1
    
    # Si el archivo ya existe, agregar un diferenciador
    while os.path.exists(final_path):
        final_path = os.path.join(destination_dir, f'{base_name}_{counter}.mp4')
        counter += 1
    
    os.rename(new_path, final_path)
    logging.info(f'Archivo movido a: {final_path}')
    return final_path

def descargar_video(enlace, download_dir, name_archive):
    driver = configurar_driver()
    
    try:
        logging.info(f'\033[93mIniciando Descarga ...\033[0m')
        link_download = obtener_enlace_descarga(driver, enlace)
        
        if link_download:
            logging.info(f'Enlace de descarga: {link_download}')
            driver.execute_script("window.open(arguments[0], '_blank');", link_download)
            driver.switch_to.window(driver.window_handles[-1])
            
            logging.info(f'\033[93mDescargando archivo ...\033[0m')
            new_files = esperar_descarga(download_dir)
            new_path = renombrar_archivo(download_dir, new_files, name_archive)
            
            if new_path:
                mover_archivo(new_path, name_archive)
            
            mover_enlaces_procesados('completado')
            
            # Cerrar la pestaña actual y volver a la pestaña principal
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
        else:
            logging.warning(f'Enlace de descarga no encontrado para: {enlace}')
    except Exception as e:
        logging.error(f'Error al descargar el video desde {enlace}: {e}')
        mover_enlaces_procesados('error')
    finally:
        driver.quit()

def obtener_titulo(driver, enlace):
    driver.get(enlace)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'meta')))
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    meta_tag = soup.find('meta', property='og:title')
    
    driver.close()
    if meta_tag:
        title = meta_tag.get('content', '').strip()
        return title
    else:
        logging.warning(f'Título no encontrado para: {enlace}')
        return 'titulo_desconocido'
    
def mover_enlaces_procesados(estado):
    
    with open('enlaces_for_download.txt', 'r', encoding='utf-8') as file:
        primer_enlace = file.readline().strip()
    
    if (estado == 'completado'):
        with open('enlaces_download.txt', 'a', encoding='utf-8') as file:
            file.write(f'{primer_enlace}\n')
        with open('enlaces_for_download.txt', 'r', encoding='utf-8') as file:
            lines = file.readlines()
        with open('enlaces_for_download.txt', 'w', encoding='utf-8') as file:
            file.writelines(lines[1:])
            
    if (estado == 'error'):
        with open('enlaces_error_download.txt', 'a', encoding='utf-8') as file:
            file.write(f'{primer_enlace}\n')
    
    logging.info(f'Enlace {primer_enlace} movido a procesados con estado: {estado}')

def main():
    enlaces = leer_enlaces('enlaces_for_download.txt')
    download_dir = r'C:\Users\zorro\Downloads'
        
    for enlace in enlaces:
        
        name_archive = obtener_titulo(configurar_driver(), enlace)
        descargar_video(enlace, download_dir, name_archive)
    
    logging.info('Proceso completado :)')

if __name__ == '__main__':
    main()