# from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import NoSuchElementException
import datetime
import pause
import argparse
import requests
from datetime import date
from dateutil.relativedelta import relativedelta
from seleniumwire import webdriver
import json
import brotli


HEADERS = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                         "Chrome/88.0.4324.190 Safari/537.36"}


def get_server_delay():
    diffsum = datetime.timedelta(0)
    diff_list = list()
    cycle = 6
    pc_ahead = 0
    for cycle in range(cycle):
        diff, pc_flag = get_server_clock_diff()
        diffsum += diff
        pc_ahead += pc_flag
        diff_list.append(diff)
    min_diff = min(diff_list)
    average_diff = diffsum / cycle
    if pc_ahead == 0:
        print("Server is ahead of PC")
        server_adjustment = 0
        server_leading = 1
    elif pc_ahead == 6:
        print("PC is always ahead of Server")
        server_adjustment = 1
        server_leading = 0
    else:
        print("PC and Server alternate clock lead, no adjustment being made")
        server_adjustment = 0
        server_leading = 0
    print("Average difference in PC clock from Ontario Parks Server clock (including latency) is", average_diff)
    print("Minimum difference in PC clock from Ontario Parks Server clock (including latency) is", min_diff)

    return min_diff, server_adjustment, server_leading


def get_private_info(args):
    with open(args.file) as ifile:
        contents = ifile.readlines()
    username = contents[0]
    password = contents[1]
    return username.strip(), password.strip()


def make_reservation(args, driver):
    desired_site = args.site
    dt = datetime.datetime(args.earliest_booking.year,
                           args.earliest_booking.month,
                           args.earliest_booking.day, 7, 0, 0, 0)
    rooturl = "https://reservations.ontarioparks.com"
    username, password = get_private_info(args)

    bookingurl = f"{rooturl}/create-booking/results?" \
                 f"resourceLocationId={args.park_tuple[1]}" \
                 f"&mapId={args.campground_tuple[0]}" \
                 f"&searchTabGroupId=0" \
                 f"&bookingCategoryId=0" \
                 f"&startDate={args.arrival_date}" \
                 f"&endDate={args.departure_date}" \
                 f"&nights={args.nights}&isReserving=true" \
                 f"&equipmentId=-32768&subEquipmentId={args.equipment_code}&partySize=6"
    print(f"The program will endeavour to get your site #{args.site} in {args.campground_tuple[1]} at "
          f"{args.park_tuple[0]} at exactly 7AM.")
    # pause_time = dt - datetime.timedelta(minutes=15)
    # print(f"The program will now pause until {pause_time} before continuing the final stage...")
    # pause.until(pause_time)
    # driver = webdriver.Firefox()
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
    login_submit = driver.find_element_by_xpath("/html/body/app-root/mat-sidenav-container/mat-sidenav-content/div[2]/"
                                                "main/app-login/div/div[2]/div/form/div/div[1]/button")
    login_submit.click()

    driver.get(bookingurl)

    listview = wait.until(ec.element_to_be_clickable((By.ID, "list-view-button")))
    acknowledge = driver.find_element_by_id('acknowledgement')
    acknowledge.click()
    listview.click()

    site_list = wait.until(ec.visibility_of_element_located((By.TAG_NAME, "app-list-view")))
    wait.until(ec.visibility_of_element_located((By.TAG_NAME, "mat-expansion-panel")))
    # longwait = WebDriverWait(driver, 60*60*24)
    # fastwait = WebDriverWait(driver, 180, poll_frequency=0.001)

    # TODO: Add logic for handling VIEW MORE button loading remainder of available sites
    loadmore = 1
    while loadmore == 1:
        try:
            lm_button = driver.find_element_by_id("loadMoreButton")
        except NoSuchElementException:
            loadmore = 0
            continue
        lm_button.click()
        driver.implicitly_wait(5)
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
                    print("Reservation Queued. Pausing until 5 minutes before site availability...")
                    # TODO: change to warning box removal instead of reserve button clickable
                    # min_delay, server_adjustment, server_leading = get_server_delay()

                    """if server_leading == 1:
                        if server_adjustment == 0:
                            nt = dt - min_delay
                            # reservation = wait.until(ec.invisibility_of_element((By.TAG_NAME,
                            # f"app-restrictive-messages")))
                            pause.until(nt)
                        else:
                            nt = dt - min_delay
                            pause.until(nt)
                    else:
                        if server_adjustment == 1:
                            nt = dt + min_delay
                            pause.until(nt)
                        else:
                            nt = dt - min_delay
                            pause.until(nt)"""
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


def parse_args():
    print("This program requires some information from the user.\n\n"
          "Please type 'sitesnipe.py --help' for instructions")
    print("if any of your variables have a space in them, for example a campground/park with two words, "
          "YOU MUST ENCLOSE IN QUOTATION MARKS SO THE PROGRAM DOESN'T BREAK!!!")
    print("i.e. --campground 'LUNDY SOUTH' or -c ""middle creek""")

    default_arrival = date.today() + relativedelta(months=+5, days=+1)
    default_arrival_iso = f"{default_arrival.year}-{default_arrival.month:02}-{default_arrival.day:02}"
    default_departure = default_arrival + relativedelta(days=+6)
    default_departure_iso = f"{default_departure.year}-{default_departure.month:02}-{default_departure.day:02}"
    parser = argparse.ArgumentParser(description='Firefox Remote control to snipe Ontario Parks campsites.')
    parser.add_argument('-f', '--file', type=str, required=True,
                        help='Your username/password file, i.e. -f privateinfo.txt')
    parser.add_argument('-a', '--arrival_date', type=datetime.date.fromisoformat, required=True,
                        default=default_arrival_iso,
                        help=f'Date you arrive to the campground, format YYYY-MM-DD, i.e. -a {default_arrival_iso}')
    parser.add_argument('-d', '--departure_date', type=datetime.date.fromisoformat, required=True,
                        default=default_departure_iso,
                        help=f'Date you leave the campground, format YYYY-MM-DD, i.e. -d {default_arrival_iso}')
    parser.add_argument('-e', '--equipment', default=4, choices=['1', '2', '3', '4', '5', '6', '7'], required=True,
                        help='Please enter a number 1 through 7 corresponding with one of the following options '
                             'for your equipment type. The default is 6, trailer up to 32 feet (i.e. -e 6):\n'
                             '1 - Single Tent\n'
                             '2 - 2 Tents\n'
                             '3 - 3 Tents\n'
                             '4 - Trailer or RV up to 18ft (5.5m)\n'
                             '5 - Trailer or RV up to 25ft (7.6m)\n'
                             '6 - Trailer or RV up to 32ft (9.7m) [DEFAULT]\n'
                             '7 - Trailer or RV over 32ft (9.7m)\n')
    parser.add_argument('-p', '--park', type=str, required=True,
                        help=f'The park you wish to book, i.e. -p wheatley')
    parser.add_argument('-c', '--campground', type=str, required=True,
                        help=f'The park you wish to book, i.e. -c "Lumby South"')
    parser.add_argument('-s', '--site', type=str, required=True,
                        help=f'The site you wish to book, i.e. -s 302')
    args = parser.parse_args()
    earliest_booking = args.arrival_date - relativedelta(months=5)
    equipmentcodes = dict([('1', '-32768'),
                           ('2', '-32767'),
                           ('3', '-32766'),
                           ('4', '-32765'),
                           ('5', '-32764'),
                           ('6', '-32763'),
                           ('7', '-32762')])
    args.equipment_code = equipmentcodes[args.equipment]
    nights = args.departure_date - args.arrival_date
    args.nights = nights.days

    print(f"The earliest you can book for {args.arrival_date} is {earliest_booking} at 7AM")
    args.earliest_booking = earliest_booking
    return args


def determine_park(park_list, args):
    possible_parks = list()
    for park_tuple in park_list:
        park_name = park_tuple[0]
        given_name = args.park
        if given_name.lower() in park_name.lower():
            possible_parks.append(park_tuple)
    if len(possible_parks) == 1:
        print("We identified your campsite as being", possible_parks[0][0])
        print("If this is incorrect, press Ctrl-C and enter a more complete campsite name")
        args.park_tuple = possible_parks[0]
    else:
        print("We could not determine the campground you requested.  Please enter a more complete name")
        quit()
    return args


def determine_campground(big_dict, maps, args):
    possible_camps = list()
    given_name = args.campground
    loc_name = args.park_tuple[0]
    loc_id = args.park_tuple[1]
    loc_map = args.park_tuple[2]
    park_dict = maps['child_maps'][int(loc_map)]
    map_children = park_dict['children']
    for m_child in map_children.keys():
        cg_name = map_children[m_child]['title']
        if given_name.lower() in cg_name.lower():
            possible_camps.append((m_child, map_children[m_child]['title'], map_children[m_child]['description']))

    if len(possible_camps) == 1:
        print(f"You entered {args.campground} and from that I identified your campground as being",
              possible_camps[0][1])
        print("If this is incorrect, press Ctrl-C to stop the program...")
        args.campground_tuple = possible_camps[0]
    else:
        print("We could not determine the campground you requested.  Please enter a more complete name")
        quit()
    return args


def get_server_clock_diff():
    servertime_url = "https://reservations.ontarioparks.com/api/transactionlocation/servertime"
    st = requests.get(servertime_url, headers=HEADERS)
    pctime = datetime.datetime.now(datetime.timezone.utc)  # tz=tzlocal()
    st_string = st.text
    st_string = st_string.replace('"', '')
    st_main, st_micro = st_string.split('.')
    st_micro = st_micro.split('Z')[0]
    st_micro = f"{int(st_micro):07}"
    st_string = f"{st_main}.{st_micro[:6]}"
    st_string = f"{st_string}+00:00"
    servertime = datetime.datetime.fromisoformat(st_string)
    diff = pctime - servertime
    pc_ahead = 1
    if diff.days < 0:
        diff = servertime - pctime
        pc_ahead = 0
    print(f"PC time: {pctime}   Server Time: {servertime}    Variation: {diff}")
    return diff, pc_ahead


def get_cookies(cookiedriver):
    rooturl = "https://reservations.ontarioparks.com/create-booking/results?mapId=-2147483464&searchTabGroupId=0&bookingCategoryId=0"

    wait = WebDriverWait(cookiedriver, 1800)
    cookiedriver.get(rooturl)
    # cookiedriver.maximize_window()
    wait.until(ec.visibility_of_element_located((By.CLASS_NAME, 'map-legend')))
    cookies = cookiedriver.get_cookies()
    cookie_requests = cookiedriver.requests
    req_list = list()
    resp_dict = dict()
    rm = None
    maps = None
    for cr in cookie_requests:
        url = cr.url
        if url.startswith('https://reservations.ontarioparks.com'):
            req_list.append(cr)
            cr_resp = cr.response
            if cr_resp is not None:
                cr_resp = cr_resp.body
                try:
                    resp_decompress = brotli.decompress(cr_resp)
                except brotli.brotli.Error:
                    continue
                resp_str = resp_decompress.decode()
                try:
                    resp_json = json.loads(resp_str)
                except json.decoder.JSONDecodeError:
                    resp_json = resp_str

                if url.startswith('https://reservations.ontarioparks.com/api/resourcelocation/rootmaps'):
                    rm = resp_json
                elif url == 'https://reservations.ontarioparks.com/api/maps':
                    maps = resp_json
                elif url.startswith('https://reservations.ontarioparks.com/api/'):
                    resp_dict[url] = resp_json

    return cookies, req_list, rm, resp_dict, maps


def write_files(maps, cgjson):
    with open('maps.json', 'w') as ofile:
        json.dump(maps, ofile)
    with open('parks.json', 'w') as cfile:
        json.dump(cgjson, cfile)
    parklist = list()
    for cg in cgjson:
        loc_id = cg['resourceLocationId']
        if loc_id is None:
            continue
        loc_map = cg['mapId']
        loc_name = cg['resourceLocationLocalizedValues']['en-CA']
        parklist.append((loc_name, loc_id, loc_map))
    parklist.sort()
    with open('parklist.txt', 'w') as gfile:
        gfile.writelines([f"{x[0]}\t{x[1]}\t{x[2]}\n" for x in parklist])
    return parklist


def read_json():
    big_dict = dict()
    big_dict['resourceLocationId'] = dict()
    big_dict['name'] = dict()
    big_dict['mapId'] = dict()
    big_dict['resourceCategoryIds'] = dict()
    with open('parks.json', 'rb') as cfile:
        cg = json.load(cfile)
    for park in cg:
        if park['resourceLocationId'] is None:
            continue
        c_res_loc_id = park['resourceLocationId']
        c_resource_location_localized_values = park['resourceLocationLocalizedValues']['en-CA']
        c_name = c_resource_location_localized_values.split('(')[0].strip()
        c_name = c_name.lower()
        c_map_id = park['mapId']

        c_res_cat_id_list = park['resourceCategoryIds']
        if c_name not in big_dict['name'].keys():
            big_dict['name'][c_name] = dict()
        else:
            print("Duplicate park name:", c_name)
            c_name = park['resourceLocationLocalizedValues']['en-CA']
            c_name = c_name.replace('(', '- ').replace(')', '').lower()
            if c_name not in big_dict['name'].keys():
                big_dict['name'][c_name] = dict()
            else:
                quit()
        big_dict['name'][c_name]['mapId'] = c_map_id
        big_dict['name'][c_name]['resourceLocationId'] = c_res_loc_id
        big_dict['name'][c_name]['resourceCategoryIds'] = c_res_cat_id_list
        for cat_id in c_res_cat_id_list:
            if cat_id not in big_dict['resourceCategoryIds'].keys():
                big_dict['resourceCategoryIds'][cat_id] = dict()
                big_dict['resourceCategoryIds'][cat_id]['name'] = list()
                big_dict['resourceCategoryIds'][cat_id]['mapId'] = list()
                big_dict['resourceCategoryIds'][cat_id]['resourceLocationId'] = list()
            big_dict['resourceCategoryIds'][cat_id]['name'].append(c_name)
            big_dict['resourceCategoryIds'][cat_id]['mapId'].append(c_map_id)
            big_dict['resourceCategoryIds'][cat_id]['resourceLocationId'].append(c_res_loc_id)
        try:
            big_dict['resourceLocationId'][c_res_loc_id] = dict()
        except KeyError:
            continue
        if c_res_loc_id not in big_dict['resourceLocationId'].keys():
            big_dict['resourceLocationId'][c_res_loc_id] = dict()
        big_dict['resourceLocationId'][c_res_loc_id]['name'] = c_name
        big_dict['resourceLocationId'][c_res_loc_id]['mapId'] = c_map_id
        big_dict['resourceLocationId'][c_res_loc_id]['resourceCategoryIds'] = c_res_cat_id_list
        if c_map_id not in big_dict['mapId'].keys():
            big_dict['mapId'][c_map_id] = dict()
        big_dict['mapId'][c_map_id]['name'] = c_name
        big_dict['mapId'][c_map_id]['resourceLocationId'] = c_res_loc_id
        big_dict['mapId'][c_map_id]['resourceCategoryIds'] = c_res_cat_id_list
    with open('maps.json', 'rb') as mfile:
        maps = json.load(mfile)
    with open('parklist.txt', 'r') as lfile:
        park_list = list()
        p_list = lfile.readlines()
        for p_line in p_list:
            p_chunks = p_line.rstrip().split('\t')
            park_list.append(tuple(p_chunks))
        other_park_list = [x.strip() for x in p_list]
    map_dict = dict()
    map_dict['mapId'] = dict()
    for mp in maps:
        m_map_id = mp['mapId']
        if m_map_id not in map_dict.keys():
            map_dict['mapId'][m_map_id] = dict()
        m_parent_maps = mp['parentMaps']
        if len(m_parent_maps) == 1:
            map_dict['mapId'][m_map_id]['parent_map'] = m_parent_maps[0]
        else:
            map_dict['mapId'][m_map_id]['parent_map'] = 'MULTIPLE_PARENTS'
        map_dict['mapId'][m_map_id]['parentMaps'] = m_parent_maps
        m_title = mp['localizedValues'][0]['title']
        map_dict['mapId'][m_map_id]['title'] = m_title
        m_description = mp['localizedValues'][0]['description']
        map_dict['mapId'][m_map_id]['description'] = m_description
    map_dict['child_maps'] = dict()
    for child_map_id in map_dict['mapId'].keys():
        mp = map_dict['mapId'][child_map_id]
        child_title = mp['title']
        child_desc = mp['description']
        parent_map = mp['parent_map']
        if parent_map is not None:
            if parent_map not in map_dict['child_maps'].keys():
                map_dict['child_maps'][parent_map] = dict()
                map_dict['child_maps'][parent_map]['children'] = dict()
                try:
                    map_dict['child_maps'][parent_map] = map_dict['mapId'][parent_map]
                except KeyError:
                    map_dict['child_maps'][parent_map] = dict()
                    map_dict['child_maps'][parent_map]['title'] = None
                    map_dict['child_maps'][parent_map]['description'] = None
            if 'children' not in map_dict['child_maps'][parent_map].keys():
                map_dict['child_maps'][parent_map]['children'] = dict()
            if child_map_id not in map_dict['child_maps'][parent_map]['children'].keys():
                map_dict['child_maps'][parent_map]['children'][child_map_id] = dict()
                map_dict['child_maps'][parent_map]['children'][child_map_id]['title'] = child_title
                map_dict['child_maps'][parent_map]['children'][child_map_id]['description'] = child_desc
            # else:

    return big_dict, map_dict, park_list


def main():
    """try:
        big_dict, maps, cg_list = read_json()
    except json.JSONDecodeError:
        pass"""
    with webdriver.Firefox(timeout=120) as maindriver:
        cookie_list, request_list, cgjson, response_dict, maps = get_cookies(maindriver)
        try:
            big_dict, maps, park_list = read_json()
        except (json.JSONDecodeError, FileNotFoundError):
            write_files(maps, cgjson)
            big_dict, maps, park_list = read_json()

        args = parse_args()
        args = determine_park(park_list, args)
        args = determine_campground(big_dict, maps, args)

        make_reservation(args, maindriver)


if __name__ == '__main__':
    main()
