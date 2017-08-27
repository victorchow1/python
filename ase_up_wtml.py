#! /usr/bin/env python

#   Usage: enter a python shell
#       execfile('ase_up_wtml.py') OR run ase_up_wtml.py
#       mainfunc()
#       open up Arubapedia: https://arubapedia.arubanetworks.com/arubapedia/index.php/Aruba_Solution_Exchange_(ASE)
#       click edit, and paste output into the wiki html format

import json
import datetime, urllib2

# global info

today = datetime.date.today()
today_lmonth = today.replace(day=1) - datetime.timedelta(days=1)

# modifies html output functions
# simple 1 will output basic text on command line for troubleshooting
# simple 0 will output full html
simple=0
print_debug=False

data = json.load(urllib2.urlopen('https://ase.arubanetworks.com/api/solutions/'))





def load_two():
    cs_list = get_lmonth('created')
    ms_list = get_lmonth('modified')
    return (cs_list, ms_list)

def get_date(datetime_str):
    date_str = '-'.join(datetime_str.split('T')[:-1])
    return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()

def format_dateobj(date_obj):
    return date_obj.strftime('%A, %B %d')


def get_title_link(sol_id, sol_title):
    h_link = 'https://ase.arubanetworks.com/solutions/id/' + str(sol_id)
    h_ref = '[' + h_link + ' ' + sol_title + ']'
    return h_ref

# returns sorted list (selected fields) of last month's solutions
def get_lmonth(modified_or_created):
    m_list=[]
    m_cby = modified_or_created + '_by'
    for sol in data:
        date_obj = get_date(sol[modified_or_created])
        if today_lmonth.year == date_obj.year and today_lmonth.month == date_obj.month:
            prod_list=[]
            for prod in sol['products_details']:
                prod_list.append(prod['acronym'])
            products = '] ['.join(prod_list)
            products = '[' + products + ']'
            m_list.append( [sol[modified_or_created], sol['title'], sol['id'], products, sol['description'], sol[m_cby]['handle'], format_dateobj(date_obj)] )
    return sorted(m_list, key=lambda tup: tup[0])

def filter_lm(json_ldata, modified_or_created):
        m_list=[]
        for sol in json_ldata:
            date_obj = get_date(sol[modified_or_created])
            if today_lmonth.year == date_obj.year and today_lmonth.month == date_obj.month:
                m_list.append(sol)
        return m_list

def get_msol_hist(sol_id):
    l_hist = []
    j_link = 'https://ase.arubanetworks.com/api/solutions/' + str(sol_id) +'/'
    ji_data = json.load(urllib2.urlopen(j_link))
    hist_daterange = filter_lm(ji_data['history'], 'modified')
    for sol_item in hist_daterange:
        sol_item_date = format_dateobj(get_date(sol_item['modified']))
        #hist_list = [sol_item['created'], sol_item['id'], sol_item['change_message'], sol_item['created_by']['handle'], sol_item_date]
        hist_list = [sol_item['modified'], sol_item['created_by']['handle'], sol_item_date, sol_item['change_message']]
        hist_list = sorted(hist_list, key=lambda tup: hist_list[0], reverse=True)
        hist_list = [str(x) for x in hist_list[1:]]
        l_hist.append(hist_list)
    return l_hist

def proc_mfields(l_item):
    for item in l_item:
        rec_dt = item.pop(0)
        h_title = item.pop(0)
        h_id = item.pop(0)
        item.pop()
        item.pop()
        h_ref = get_title_link(h_id, h_title)
        item.insert(0, h_ref)
        lvar = get_msol_hist(h_id)
        if (print_debug==True):
            for hl_item in lvar:
                print hl_item
            print '------------'
        item.append(lvar)

def proc_cfields(l_item):
    for item in l_item:
        rec_dt = item.pop(0)
        h_title = item.pop(0)
        h_id = item.pop(0)
        h_ref = get_title_link(h_id, h_title)
        if print_debug==True: print h_ref
        item.insert(0, h_ref)

def print_header():
#    first = today.replace(day=1)
#    p_mo = first - datetime.timedelta(days=1)
    sp_mo = today_lmonth.strftime('%B-%Y')
    print '== ASE updates for the month of ' + sp_mo + '<br/> ==' + '\n'


def html_create_tab(l_item):
    #simple = 0
    print "'''Created Solutions'''<br/>" + '\n'
    print '{| class="wikitable"'
    print '|-'
    print '! scope="col" | Solution Title<br/>'
    print '! scope="col" | Products'
    print '! scope="col" | Description'
    print '! scope="col" | Created By'
    print '! scope="col" | Created'
    for item in l_item:
        if simple == 0:
            print '|-'
            print '| scope="row" | '
            print item[0]
            for field in item[1:]:
                print '| | ' + field
        else:
            for field in item:
                print field
    print '|}' + '\n'


def html_mod_tab(l_item):
    #simple = 0
    print "'''Modified Solutions'''<br/>" + '\n'
    print '{| class="wikitable"'
    print '|-'
    print '! scope="col" | Solution Title<br/>'
    print '! scope="col" | Products'
    print '! scope="col" | Description'
    print '! scope="col" | Changes'
    for item in l_item:
        if simple == 0:
            print '|-'
            print '| scope="row" | '
            print item[0]
            for field in item[1:-1]:
                print '| | ' + field
            print '| style="color: black;  padding: 0 5px;  width: 600px" |'
            print '{| class="wikitable"'
            print '! scope="col" | Handle\n! scope="col" | Date\n! scope="col" | Change log'
            for mfield in item[-1]:
                print '|-'
                print '|style="color: black;  padding: 0 10px;  width: 40px" | ' + mfield[0]
                print '|style="color: black;  padding: 0 10px;  width: 60px" | ' + mfield[1]
                print '|style="color: black;  padding: 0 10px;  width: 500px" | ' + mfield[2]
            print '|}' + '\n'
        else:
            for field in item:
                print field
    print '|}' + '\n'

def mainfunc():
    # loads the two main datastructures used throughout
    (cs_list, ms_list) = load_two()
    # mutates lists to get desired fields/format
    proc_cfields(cs_list)
    proc_mfields(ms_list)
    #html output
    print_header()
    html_create_tab(cs_list)
    html_mod_tab(ms_list)


mainfunc()
#   will output MediaWiki HTML to stdout
