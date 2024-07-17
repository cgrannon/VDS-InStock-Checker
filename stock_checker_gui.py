import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import tkinter as tk
from tkinter import messagebox
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def check_stock(url):
    # Show loading message
    status_label.config(text="Loading...", fg="blue", font=("Helvetica", 14, "bold"))
    status_bar.config(bg="blue")
    root.update_idletasks()
    
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    service = Service(executable_path='/usr/local/bin/chromedriver')  # Path to chromedriver
    driver = webdriver.Chrome(service=service, options=options)

    driver.get(url)
    time.sleep(5)  # Wait for the page to load

    try:
        stock_status_element = driver.find_element(By.XPATH, '//*[@id="app"]/div[1]/div[2]/div[2]/form/div/div/div[1]/div[1]/div[2]/button[3]/div[3]/div')
        stock_status = stock_status_element.text.strip()
        print(f"Stock status: {stock_status}")
        if 'In Stock' in stock_status:
            send_notification(url)
            status_label.config(text="Stock Status: In Stock", fg="green", font=("Helvetica", 14, "bold"))
            status_bar.config(bg="green")
        else:
            status_label.config(text="Stock Status: Out of Stock", fg="red", font=("Helvetica", 14, "bold"))
            status_bar.config(bg="red")
    except Exception as e:
        print(f"Error finding stock status element: {e}")
        status_label.config(text="Stock Status: Error", fg="orange", font=("Helvetica", 14, "bold"))
        status_bar.config(bg="orange")

    driver.quit()

def send_notification(url):
    sender_email = "cgrannon@gmail.com"
    receiver_email = "cgrannon@gmail.com"
    subject = "Product Back in Stock!"
    body = f"The product is back in stock! Check it out here: {url}"

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender_email, 'dypv ptme vavm sthx')  # Replace 'your_app_password' with the 16-character App Password
    text = msg.as_string()
    server.sendmail(sender_email, receiver_email, text)
    server.quit()

def start_checking(url, interval_ms):
    if url:
        check_stock(url)
        start_countdown(interval_ms)
        root.after(interval_ms, lambda: start_checking(url, interval_ms))  # Check stock at the specified interval
    else:
        messagebox.showerror("Error", "Please enter a URL")

def start_countdown(interval_ms):
    countdown_time = interval_ms // 1000
    update_timer(countdown_time)

def update_timer(countdown_time):
    minutes, seconds = divmod(countdown_time, 60)
    timer_label.config(text=f"Next Check In: {minutes:02}:{seconds:02}")
    if countdown_time > 0:
        root.after(1000, update_timer, countdown_time - 1)

def interval_to_ms(interval):
    interval_map = {
        "1 minute": 60000,
        "5 minutes": 300000,
        "10 minutes": 600000,
        "30 minutes": 1800000,
        "1 hour": 3600000
    }
    return interval_map.get(interval, 600000)  # Default to 10 minutes if not found

# GUI setup
root = tk.Tk()
root.title("Stock Checker")
root.geometry("400x320")
root.configure(bg='#f0f0f0')

# Add status bar
status_bar = tk.Frame(root, height=45, bg="gray")
status_bar.pack(fill=tk.X)

# Add label for countdown timer
timer_label = tk.Label(root, text="Next Check In: --:--", font=("Helvetica", 14), bg='#f0f0f0')
timer_label.pack(pady=10)

# Add label for displaying stock status
status_text_label = tk.Label(root, text="Stock Status:", font=("Helvetica", 14, "bold"), bg='#f0f0f0')
status_text_label.pack(pady=5)
status_label = tk.Label(root, text="Unknown", font=("Helvetica", 14), bg='#f0f0f0')
status_label.pack(pady=5)

# Dropdown for interval selection
interval_var = tk.StringVar(root)
interval_var.set("10 minutes")  # Default value
interval_menu = tk.OptionMenu(root, interval_var, "1 minute", "5 minutes", "10 minutes", "30 minutes", "1 hour")
interval_menu.configure(bg='#ffffff', font=("Helvetica", 12))
interval_menu.pack(pady=10)

# Cherry Server buttons
cherry_server_url = "https://portal.cherryservers.com/deployment?plan=805&cycle=3&tags=up_to_16"
cherry_instant_button = tk.Button(root, text="Cherry Instant", command=lambda: check_stock(cherry_server_url), bg='#ffffff', font=("Helvetica", 12))
cherry_instant_button.pack(pady=10)

cherry_recurring_button = tk.Button(root, text="Cherry Recurring", command=lambda: start_checking(cherry_server_url, interval_to_ms(interval_var.get())), bg='#ffffff', font=("Helvetica", 12))
cherry_recurring_button.pack(pady=10)

# Add static text disclosure
disclosure_label = tk.Label(root, text="Please allow a few seconds for the status check to complete.", font=("Helvetica", 10), bg='#f0f0f0')
disclosure_label.pack(pady=10)

root.mainloop()