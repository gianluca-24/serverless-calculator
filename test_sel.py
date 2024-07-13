from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import threading

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

def upload_test():
    # Set up Chrome options for headless mode
    driver = webdriver.Chrome(options=chrome_options)
    driver.get("http://127.0.0.1:5500/frontend.html")
    # upload an image
    driver.find_element(By.ID, 'imageUpload').send_keys("/Users/gianluca/Desktop/university/magistrale/primo anno/Secondo semestre/CLC/final project/images/eq10x3.jpeg")
    # click on the submit button
    driver.find_element(By.CSS_SELECTOR,"input[type='submit']").click()
    # start timer
    start = time.time()
    # wait for the result to be displayed
    while True:
        try:
            result = driver.find_element(By.CLASS_NAME,"solution-text")
            # end timer
            end = time.time()
            break
        except:
            pass
    # print(end - start)
    times.append(end - start)
    # close the browser
    driver.quit()
# Number of concurrent users to simulate
num_users = 50 # 2,5,10,25,30,50
# Create and start threads
threads = []
times = []
for _ in range(num_users):
    thread = threading.Thread(target=upload_test)
    threads.append(thread)
    thread.start()
# Wait for all threads to complete
for thread in threads:
    thread.join()
print(times)
print("Average time taken for", num_users, "users:", sum(times) / len(times))