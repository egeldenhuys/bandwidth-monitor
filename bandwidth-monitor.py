import requests
import sys
import hashlib
import time
import locale
import getpass

def main():
    locale.setlocale(locale.LC_ALL, '')

    username = 'admin'

    hashed = False

    timeDiff = 5
    rateScale = 1024
    rateScaleStr = 'KiB'

    totalScale = 1048576
    totalScaleStr = 'MiB'

    if (len(sys.argv) > 1):
        if (sys.argv[1] == '-h' or sys.argv[1] == '--help'):
            print('Description: Displays the amount of bandwidth passing through the router\n')
            print('Usage: bandwidth-monitor [passwordHash] [interval]\n')
            print('passwordHash : MD5 Hash of the admin password')
            print('interval     : Seconds between polling the router for stats')
            exit()

    if (len(sys.argv) > 1):
        if (sys.argv[1] != ''):
            hashed = True
            password = sys.argv[1]

    if (len(sys.argv) > 2):
        if (sys.argv[2] != ''):
            timeDiff = int(sys.argv[2])

    s = requests.Session()

    if (not hashed):
        password = getpass.getpass('Password: ')

    authenticate(username, password, s, hashed)

    statsOld = getStatistics(s)

    while (True):
        statsNew = getStatistics(s)

        statsDiff = [statsNew[0] - statsOld[0], statsNew[1] - statsOld[1]]
        statsRate = [statsDiff[0] / timeDiff, statsDiff[1] / timeDiff]

        down = [statsNew[0] / totalScale, statsRate[0] / rateScale]
        up = [statsNew[1] / totalScale, statsRate[1] / rateScale]

        sys.stdout.write('Total Down ({0}): {1} ({2} {3}/s)\n'.format(totalScaleStr, down[0], down[1], rateScaleStr))
        sys.stdout.write('Total Up ({0}): {1} ({2} {3}/s)\n\n'.format(totalScaleStr, up[0], up[1], rateScaleStr))
        sys.stdout.flush()

        statsOld = statsNew

        time.sleep(timeDiff)

    return

def authenticate(username, password, session, alreadyHashed = False):
    #print('Authenticate...')

    m = hashlib.md5()
    m.update(username)
    usernameHash = m.hexdigest()

    if (alreadyHashed == False):
        m = hashlib.md5()
        m.update(password)
        passwordHash = m.hexdigest()
    else:
        passwordHash = password

    url = 'http://192.168.1.1/Forms/login_security_1'

    session.headers = {
        'Host': '192.168.1.1',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:46.0) Gecko/20100101 Firefox/46.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Referer': 'http://192.168.1.1/login_security.html',
        'Connection': 'keep-alive'
    }

    data = {
        'tipsFlag': '0',
        'timevalue': '0',
        'Login_Name': username,
        'Login_Pwd': 'Ha2S+eOKqmzA6nrlmTeh7w==',
        'uiWebLoginhiddenUsername': usernameHash,
        'uiWebLoginhiddenPassword': passwordHash
        }

    try:
        r = session.post(url, data=data, allow_redirects=False, timeout=5)
    except requests.ConnectionError as e:
        print(e.response)
        session.close()
        sys.stdout.flush()
        exit(1)


    #print(r.text)
    #print(r.headers)
    #print(r.cookies.keys())

    if (r.cookies['C1'] == '%00'):
        print('Incorrect password!')
        sys.stdout.flush()
        session.close()
        exit(1)


    #print('%s - %s' % (r.status_code, r.reason))

    return

def extractValue(indexString, content):
    index = content.find(indexString)

    if (index == -1):
        raise ValueError('String not found!', indexString)

    index += len(indexString) + 1

    numberStr = '';
    number = 0

    while (content[index] != '<'):
        if (content[index] != ','):
            numberStr += content[index]

        index = index + 1

    number = int(numberStr)
    return number

def getStatistics(session):
    #print('Get statistics...')

    downUp = [-1, -1]

    url = 'http://192.168.1.1/Forms/status_statistics_1'
    session.headers['Referer'] = 'http://192.168.1.1/status/status_statistics.htm'
    data = {
        'Stat_Radio': 'Zero',
        'StatRefresh': 'REFRESH'
    }

    try:
        r = session.post(url, data=data, allow_redirects=True, timeout=5)
    except requests.Timeout as e:
        print(e.message)
        return downUp
    except requests.ConnectionError as e:
        print(e.message)
        return downUp


    #print(r.url)
    #print('%s - %s' % (r.status_code, r.reason))

    searchString = '<font color="#000000">Transmit total Bytes</font></td><td class="tabdata"><div align=center>'
    downUp[0] = extractValue(searchString, r.text)

    searchString = '<font color="#000000">Receive total Bytes</font></td><td class="tabdata"><div align=center>'
    downUp[1] = extractValue(searchString, r.text)

    downUp[0] = downUp[0]
    downUp[1] = downUp[1]

    return downUp

main()
