import re
from datetime import datetime
from urllib.parse import urlparse
import jdatetime


def is_georgian_date(date):
    try:
        return bool(datetime.strptime(date, "%Y/%m/%d"))
    except ValueError:
        return False


def validate_mobile_number(number):
    """
    Validates an Iran mobile number in the format 09XXXXXXXXX.
    Returns True if the number is valid, False otherwise.
    """
    pattern = r"^09\d{9}$"
    return bool(re.match(pattern, number))


def validate_city_phone_number(number):
    """
        Validates an Iran city phone number in the format 0XX-XXXXXXXX.
        Returns True if the number is valid, False otherwise.
        """
    pattern = r'^(0[1-9][1-9]\d{8})$'
    return bool(re.match(pattern, number))


def is_persian(string):
    pattern = r'^[آ-ی]+$'
    return bool(re.match(pattern, string))


def is_english(string):
    pattern = r'^[a-zA-Z]+$'
    return bool(re.match(pattern, string))


def is_jalali_date(date):
    try:
        jdatetime.datetime.strptime(date, '%Y/%m/%d')
        return True
    except ValueError:
        return False


def is_numeric(string):
    pattern = '^[0-9]+$'
    return bool(re.match(pattern, string))


def validate_email(email):
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return bool(re.match(pattern, email))


def option_in_html_tag_validator(options_list: list, option_text):
    print(options_list)
    for option in options_list:
        no_tag = re.sub(r'<[^>]+>', '', option)
        if no_tag == option_text:
            return True
    return False


def tag_remover(string):
    return re.sub(r'<[^>]+>', '', string)


def url_validator(url):
    url = url.replace('https://', '')
    url = url.replace('http://', '')
    url = url.replace('www.', '')
    url = 'https://' + url
    result = urlparse(url)
    print(result.scheme)
    print(result.netloc)
    spurl = url.split('.')
    return bool(((result.scheme and result.netloc) or result.netloc) and len(spurl) > 1 and spurl[-1] in ['com', 'ir', 'org', 'net', 'edu', 'gov', 'co', 'info', 'me', 'biz', 'mobi', 'tv', 'name', 'us', 'cc', 'ws', 'bz', 'mn', 'co.uk', 'org.uk', 'me.uk', 'uk.com', 'uk.net', 'gb.com', 'gb.net', 'eu.com', 'eu.net', 'de.com', 'qc.com', 'ae.org', 'kr.com', 'us.com', 'ar.com', 'br.com', 'cn.com', 'hu.com', 'no.com', 'ru.com', 'sa.com', 'se.com', 'se.net', 'uy.com', 'za.com', 'co.jp', 'jp.net', 'jpn.com', 'de', 'fr', 'it', 'nl', 'se', 'es', 'xxx', 'pw', 'tk', 'ml', 'cf', 'ga', 'gq', 'cm', 'dj', 'com.de', 'com.se', 'net.se', 'org.se', 'eu', 'com.au', 'net.au', 'org.au', 'co.nz', 'net.nz', 'org.nz', 'com.tw', 'idv.tw', 'org.tw', 'game.tw', 'ebiz.tw', 'club.tw', 'tw', 'com.cn', 'net.cn', 'org.cn', 'gov.cn', 'ac.cn', 'bj.cn', 'sh.cn', 'tj.cn', 'cq.cn', 'he.cn', 'nm.cn', 'ln.cn', 'jl.cn', 'hl.cn', 'js.cn', 'zj.cn', 'ah.cn', 'fj.cn', 'jx.cn', 'sd.cn', 'ha.cn', 'hb.cn', 'hn.cn', 'gd.cn', 'gx.cn', 'hi.cn', 'sc.cn', 'gz.cn', 'yn.cn', 'xz.cn', 'sn.cn', 'gs.cn', 'qh.cn', 'nx.cn', 'xj.cn', 'tw.cn', 'hk.cn', 'mo.cn', 'asia', 'biz', 'cc', 'cn', 'co', 'com', 'info', 'me', 'mobi', 'name', 'net', 'org', 'pro', 'tel', 'tv', 'us'])
