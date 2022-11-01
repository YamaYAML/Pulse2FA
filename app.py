import pywinauto
import time
import pyperclip
import subprocess
from pywinauto import Desktop
from datetime import datetime
import warnings
import mintotp

"""
== THIS HACKFIX IS TO BE USED WITH CAUTION! ==

    - It is not in line with security guidelines, a connectivity solution has to be found.
    - Code is very simple, undocumented en definately not secure by design
    - My personal auth token is in this file...

== HOW TO USE: ==

    1. In case pip is not installed, run from extracted folder: python get-pip.py
    2. Install dependencies: 
    - python -m pip install pywinauto
    - python -m pip install mintotp
    3. Make sure Pulse Client is running (see URL below)
    4. Run app.py, prefably in background (python app.py &)

== WHY ==

    ACS LAB environment is currently not available from 
    test automation VM due to Connectra VPN not being used anymore.

    Pulse Secure is used instead. Mirror:
    https://www.edpnet.nl/assets/files/support/installation-usage/ps-pulse-win-9.1r13.0-b11723-64bit-installer.zip

    As the time-out of any VPN session is now set to 12 hours, this hackfix has been created.

First login/client setup has to be done by Jesse Lautenbach

"""



authToken = "IUZEQWKSIJLECQK2JNCUOVSDJQ"

warnings.simplefilter('ignore', category=UserWarning)  # Ignore pywinauto warnings
# https://github.com/pywinauto/pywinauto/issues/530

def check_if_VPN_is_connected():
    cmdout = subprocess.Popen(["ipconfig"], stdout = subprocess.PIPE, shell=True).communicate()[0]
    if "Connection-specific DNS Suffix  . : upclabs.com" in str(cmdout):
        print("Already connected. Checking again in 30 minutes.")
        return True
    return False


def cancel_and_connect_to_VPN(app):
    try:
        app['Pulse Secure']['Cancel'].click()
        time.sleep(5)
        print("Application canceled, clicking Connect...")
        app['Pulse Secure']['Connect'].click()
    except pywinauto.MatchError as me:
        print("Cancel/Connect button not found. Clicking Proceed")
        app['Pulse Secure']['Connect'].click()
        time.sleep(2)
        app.top_window().type_keys('{ENTER}')
        time.sleep(2)
    return 1
        
def get_pulse_secure_app(path_to_ps_app):
    try:
        app = pywinauto.Application().connect(path=path_to_ps_app)
        print("Application exists, Cancelling session")
    except pywinauto.application.ProcessNotFoundError as ex:
        print("Application not running. Launching it...")
        pywinauto.Application().start(path_to_ps_app)
        app = pywinauto.Application().connect(path=path_to_ps_app)
        time.sleep(5) 
    return app


def cancel_software_update_dialog():
    print("Canceling the upgrade...")
    app4 = pywinauto.Application().connect(title="Software Upgrade for: <COMPANY>")
    app4['Software Upgrade for: <COMPANY>']['Cancel'].click()
    print("Done!")


def print_elements_in_window():
    print("Element/app not found. Printing all available elements: ")
    windows = Desktop(backend="uia").windows()
    print([w.window_text() for w in windows])


def paste_2_factor_code():
    app3 = pywinauto.Application(backend="uia").connect(title_re="Connect to: <COMPANY>")
    tempKey = pyperclip.copy(mintotp.totp(authToken))
    app3.top_window().type_keys(tempKey)
    app3.top_window().type_keys('{ENTER}') 
    time.sleep(5) 


while True:
    print(datetime.now())
    path_to_ps_app = "C:\Program Files (x86)\Common Files\Pulse Secure\JamUI\Pulse.exe"
    if not check_if_VPN_is_connected():
        pulse_secure_app = get_pulse_secure_app(path_to_ps_app=path_to_ps_app)
        cancel_and_connect_to_VPN(pulse_secure_app)
        print("Generating the 2-factor key...")
        pulse_secure_app.top_window().type_keys('{ENTER}')
        tempKey = mintotp.totp(authToken)
        pyperclip.copy(tempKey)
        print(tempKey)
        time.sleep(5) 
        pulse_secure_app.top_window().type_keys(pyperclip.paste()).type_keys('{ENTER}')
        print("Pasting the 2-factor key...")
        pulse_secure_app.top_window().type_keys(tempKey)
        pulse_secure_app.top_window().type_keys('{ENTER}')
        print("Sleeping for 10 minutes to check if connection is still up.")
        time.sleep(1200)
                