import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

# cria a instância do driver do firefox
driver = webdriver.Firefox(executable_path=r'\\geckodriver-v0.32.2-win32\\geckodriver.exe')

# acessa a página de login
driver.get('https://brainly.com.br/login')

# insere as credenciais de login
username_input = driver.find_element(By.XPATH, '/html/body/div[3]/div/div[2]/div/div/div[1]/div/div[1]/div[4]/form/div[1]/div/input')
username_input.send_keys('YOUR-EMAIL')
password_input = driver.find_element(By.XPATH, '/html/body/div[3]/div/div[2]/div/div/div[1]/div/div[1]/div[4]/form/div[2]/div/input')
password_input.send_keys('YOUR-PASSWORD')

# envia o formulário de login
password_input.send_keys(Keys.ENTER)

# após o login, espera 1 segundos antes de prosseguir para o link da pergunta
time.sleep(1)

# carrega o arquivo pu.txt
with open('YOUR_QUESTIONS_FILE_LIST', 'r', encoding='utf-8') as f:
    urls = f.readlines()
    # percorre as urls
    for url in urls:
        # remove o texto precedente ao link usando expressões regulares
        link = re.sub(r'^Link para a pergunta da linha \d+: ', '', url.strip())
        
        time.sleep(5)

        # acessa a página da pergunta
        driver.get(link)

        # clica no botão
        button = driver.find_element(By.XPATH, "/html/body/div[6]/div/div[6]/div[1]/div[1]/article/div/div/div[3]/div/div/div/div/div/button")
        ActionChains(driver).move_to_element(button).click().perform()

        time.sleep(1)

        # seleciona o texto e exclui
        qa = driver.find_element(By.XPATH, '//*[@id="slate-editable"]')
        qa.send_keys(Keys.CONTROL + 'a')
        qa.send_keys(Keys.BACKSPACE)

        # espera até que o texto seja excluído
        while True:
            text = qa.text.strip()
            if len(text) == 0:
                break
            time.sleep(1)