from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables 
from RPA.PDF import PDF
from RPA.Archive import Archive

@task
def Order_Robots():

    open_robot_order_website()
    download_order_file()
    load_table_from_csv()
    archive_receipts()


def open_robot_order_website():
    browser.configure(
        slowmo=100
    )
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

def download_order_file():
    http = HTTP()
    http.download(url = "https://robotsparebinindustries.com/orders.csv", overwrite=True)

def load_table_from_csv():
    table= Tables()
    csvtable=table.read_table_from_csv("orders.csv")

    for row in csvtable:
        fill_form(row)

def fill_form(val):
    print("enter")
    print(val["Order number"])
    page = browser.page()
    page.click("//button[normalize-space()='Yep']")
    page.select_option("//select[@id='head']", val["Head"])
    page.click("//input[@id='id-body-"+val["Body"]+"']")
    page.fill("//input[@placeholder ='Enter the part number for the legs']",val["Legs"])
    page.fill("//input[@id='address']", val["Address"])
    
    while True:
        page.click("//button[@id='order']")
        order_another = page.query_selector("#order-another")
        if order_another:
            pdf_path = store_receipt_as_pdf(int(val["Order number"]))
            screenshot_path = screenshot_robot(int(val["Order number"]))
            embed_screenshot_to_receipt(screenshot_path, pdf_path)
            page.click("#order-another")
            print("exit")
            break



def store_receipt_as_pdf(order_number):
    page = browser.page()
    order_receipt_html = page.locator("#receipt").inner_html()
    pdf = PDF()
    pdf_path = f"output/receipts/{order_number}.pdf"
    pdf.html_to_pdf(order_receipt_html, pdf_path)
    return pdf_path


def screenshot_robot(order_number):
    page = browser.page()
    screenshot_path = f"output/screenshots/{order_number}.png"
    page.locator("#robot-preview-image").screenshot(path=screenshot_path)
    return screenshot_path

def embed_screenshot_to_receipt(screenshot, pdf_file):
    pdf = PDF()
    pdf.add_watermark_image_to_pdf(image_path=screenshot, 
                                   source_path=pdf_file, 
                                   output_path=pdf_file)
    

def archive_receipts():
    lib = Archive()
    lib.archive_folder_with_zip("./output/receipts", "./output/receipts.zip")