from netmiko import ConnectHandler
from netmiko.exceptions import NetMikoTimeoutException
from netmiko.exceptions import SSHException
from netmiko.exceptions import AuthenticationException
from github import Github



import time


# here is list of switch ip address
ip_list = []
# '10.70.100.51'
addresses = str(input("Введите адреса через запятую без пробела: "))
split_addresses = addresses.split(",")
for i in split_addresses:
    ip_list.append(i)
print(ip_list)

while True:
    time.sleep(1)
    print('Working...')
    break

# clearing the old data from the CSV file and writing the headers
f = open("login_issues.csv", "w+")
f.write("IP Address, Status")
f.write("\n")
f.close()

f = open("conf.csv", 'w').close()


def error_mes(mes):
    o = open("conf.csv", "a")
    o.write("\n\n----------------------IP_ADDRESS: ", )
    o.write(ip)
    o.write("----------------------")
    o.write("\n")
    o.write(mes)
    o.write("\n\n")
    o.close()


# loop all ip addresses in ip_list
for ip in ip_list:
    eltex = {
        'device_type': 'eltex',
        'ip': ip,
        'username': 'admin',  # ssh username
        'password': 'admin',  # ssh password
        'secret': 'password',  # ssh_enable_password
        'ssh_strict': False,
        'fast_cli': False,
    }

    # handling exceptions errors

    try:
        net_connect = ConnectHandler(**eltex)

    except NetMikoTimeoutException:
        f = open("login_issues.csv", "a")
        f.write(ip + "," + "Device Unreachable/SSH not enabled")
        f.write("\n")
        f.close()
        error_mes("Device Unreachable/SSH not enabled")
        continue

    except AuthenticationException:
        f = open("login_issues.csv", "a")
        f.write(ip + "," + "Authentication Failure")
        f.write("\n")
        f.close()
        error_mes("Authentication Failure")
        continue
    except SSHException:
        f = open("login_issues.csv", "a")
        f.write(ip + "," + "SSH not enabled")
        f.write("\n")
        f.close()
        error_mes("SSH not enabled")
        continue

    try:
        net_connect.enable()
        f = open("login_issues.csv", "a")
        f.write(ip + "," + " Connected")
        f.write("\n")
        f.close()

    # handling exceptions errors
    except ValueError:
        f = open("login_issues.csv", "a")
        f.write(ip + "," + "Could be SSH Enable Password issue")
        f.write("\n")
        f.close()
        error_mes("Could be SSH Enable Password issue")
        continue

    sh_run_output = net_connect.send_command('show run')
    # print(sh_run_output)

    sh_tr7_output = net_connect.send_command('show interfaces counters gi1/0/7')
    sh_tr8_output = net_connect.send_command('show interfaces counters gi1/0/8')
    sh_lldp_output = net_connect.send_command('show lldp neighbors')

    config = net_connect.send_command(
        command_string="configure",
        expect_string=r"#",
        strip_prompt=False,
        strip_command=False
    )
    sh_ver_output = net_connect.send_command('do show version')
    # print(sh_ver_output)

    f = open("conf.csv", "a")
    f.write("\n\n----------------------IP_ADDRESS: ", )
    f.write(ip)
    f.write("----------------------")
    f.write("\n\n")
    f.write("-----version info-----")
    f.write(sh_ver_output)
    f.write("\n\n")
    f.write("-----interfaces counters info-----")
    f.write(sh_tr7_output)
    f.write(sh_tr8_output)
    f.write("\n\n")
    f.write("-----lldp neighbors info-----")
    f.write(sh_lldp_output)
    f.write("\n\n")
    f.write("-----configuration info-----")
    f.write(sh_run_output)


token = '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'
g = Github(token)

repo = g.get_user().get_repo('project')

all_files = []
contents = repo.get_contents("")

while contents:
    file_content = contents.pop(0)
    if file_content.type == "dir":
        contents.extend(repo.get_contents(file_content.path))
    else:
        file = file_content
        all_files.append(str(file).replace('ContentFile(path="', '').replace('")', '').replace('("', ''))


f = open("conf.csv", "r")
content = f.read()
print(content)
git_file = f'conf.csv'


if git_file in all_files:
    contents = repo.get_contents(git_file)
    repo.update_file(contents.path, f"committing conf.csv", content, contents.sha, branch="main")
    print(git_file + ' UPDATED')
else:
    repo.create_file(git_file, f"committing conf.csv", content, branch="main")
    print(git_file + ' CREATED')










# # , private_token='glpat-naqV-moQf6EyjLuPiez1'

input('Press <ENTER> to exit')
