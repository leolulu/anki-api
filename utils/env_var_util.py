import os
import winreg


def set_user_environment_variable(name, value):
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_ALL_ACCESS)
    winreg.SetValueEx(key, name, 0, winreg.REG_EXPAND_SZ, value)
    winreg.CloseKey(key)
    os.system(f'setx {name} "{value}"')
    print(f"Environment variable '{name}' set to '{value}' successfully.")
    return value


def read_user_environment_variable(name):
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_ALL_ACCESS)
    try:
        value, _ = winreg.QueryValueEx(key, name)
    except:
        value = None
    winreg.CloseKey(key)
    return value
