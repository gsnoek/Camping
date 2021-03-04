from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import datetime
import pause

driver = webdriver.Firefox()


def get_private_info(filename):
    with open(filename, 'r') as ifile:
        contents = ifile.readlines()
    uname = contents[0]
    pword = contents[1]
    return uname.strip(), pword.strip()


desired_site = '5'
dt = datetime.datetime(2021, 3, 3, 7, 0, 0, 0)

rooturl = "https://reservations.ontarioparks.com"
startDate = '2021-08-03'
endDate = '2021-08-08'
nights = 4

bookingurl = f"{rooturl}/create-booking/results?resourceLocationId=-2147483607&mapId=-2147483457&searchTabGroupId=0" \
             f"&bookingCategoryId=0&startDate={startDate}&endDate={endDate}&nights={nights}&isReserving=true" \
             f"&equipmentId=-32768&subEquipmentId=-32765&partySize=6"

driver.get(rooturl)
wait = WebDriverWait(driver, 10)
login = wait.until(ec.element_to_be_clickable((By.ID, 'login')))
login.click()

consent = wait.until(ec.element_to_be_clickable((By.ID, 'consentButton')))
consent.click()

email = wait.until(ec.presence_of_element_located((By.ID, 'email')))
email.send_keys(username)
pwd = driver.find_element_by_id("password")
pwd.send_keys(password)
login_submit = driver.find_element_by_xpath("/html/body/app-root/mat-sidenav-container/mat-sidenav-content/div[2]/main/"
                                            "app-login/div/div[2]/div/form/div/div[1]/button")
login_submit.click()

driver.get(bookingurl)

listview = wait.until(ec.element_to_be_clickable((By.ID, "list-view-button")))
acknowledge = driver.find_element_by_id('acknowledgement')
acknowledge.click()
listview.click()

site_list = wait.until(ec.visibility_of_element_located((By.TAG_NAME, "app-list-view")))
actest = wait.until(ec.visibility_of_element_located((By.TAG_NAME, "mat-expansion-panel")))
accordian_sites = site_list.find_elements_by_tag_name("mat-expansion-panel")

for acc_idx, accordian_site in enumerate(accordian_sites):
    sitenumbers = accordian_site.find_elements_by_tag_name("h3")
    for sn in sitenumbers:
        site_text = sn.text
        if site_text.startswith("Site"):
            site_text = site_text.split("\n")[1]
            if site_text == desired_site:
                accordian_site.click()
                reservation = wait.until(ec.element_to_be_clickable((By.ID, f"reserveButton-{acc_idx}")))
                print("Reservation Queued. Waiting until trigger time...")
                pause.until(dt)
                reservation.click()

confirm_ac = wait.until(ec.presence_of_element_located((By.ID, "mat-checkbox-3")))
all_correct = confirm_ac.find_element_by_class_name("mat-checkbox-label")
all_correct.click()

confirm_ra = wait.until(ec.presence_of_element_located((By.ID, "mat-checkbox-4")))
read_ack = confirm_ra.find_element_by_class_name("mat-checkbox-label")
read_ack.click()

rb = wait.until(ec.element_to_be_clickable((By.ID, "confirmReservationDetails")))
rb.click()

print("Hopefully that worked!!!")
print("Reservation completed. holding open to checkout...")
pause.hours(2)
driver.close()
