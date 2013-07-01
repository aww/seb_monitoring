#!/usr/bin/env python

import math
import datetime
from array import array

import getpass
import gdata.docs
import gdata.docs.service
import gdata.spreadsheet.service
import pickle

import matplotlib.pyplot as plt
import matplotlib.patches
from matplotlib.dates import MONDAY
from matplotlib.dates import MonthLocator, WeekdayLocator, DateFormatter


# We use minor ticks every Monday
mondays   = WeekdayLocator(MONDAY)
# And major ticks every [interval] month
months    = MonthLocator(range(1,13), bymonthday=1, interval=1)
monthsFmt = DateFormatter("%b '%y")

birth_datetime     = datetime.datetime.strptime('6/28/2012 9:40:00', '%m/%d/%Y %H:%M:%S')
initial_datetime   = datetime.datetime.strptime('1/1/0001 0:00:00', '%m/%d/%Y %H:%M:%S')
birth_rel_to_epoch = birth_datetime - initial_datetime
birth_in_days_after_epoch = birth_rel_to_epoch.days + birth_rel_to_epoch.seconds / 60. / 60. / 24.

def getGData():
    pickle_filename = 'sebastians_growth.pickle'
    rows = None
    try:
        cache_file = open(pickle_filename, 'rb')
        print "Loading data from", pickle_filename
        rows = pickle.load(cache_file)
        cache_file.close()
    except:
        rows = None
    
    if not rows:
        google_pw = getpass.getpass()
        # Connect to Google
        gd_client = gdata.spreadsheet.service.SpreadsheetsService()
        gd_client.email = 'alan.w.wilson@gmail.com'
        gd_client.password = google_pw
        gd_client.source = 'payne.org-example-1'
        try:
            gd_client.ProgrammaticLogin()
        except gdata.service.BadAuthentication:
            print "Error: BadAuthentication"
            return None
        q = gdata.spreadsheet.service.DocumentQuery()
        q['title'] = "Sebastian's growth"
        q['title-exact'] = 'true'
        feed = gd_client.GetSpreadsheetsFeed(query=q)
        spreadsheet_id = feed.entry[0].id.text.rsplit('/',1)[1]
        feed = gd_client.GetWorksheetsFeed(spreadsheet_id)
        worksheet_id = feed.entry[0].id.text.rsplit('/',1)[1]
    
        rows = gd_client.GetListFeed(spreadsheet_id, worksheet_id).entry
    
        cache_file = open(pickle_filename, 'wb')
        print "Writing data to", pickle_filename
        pickle.dump(rows, cache_file)
        cache_file.close()

    return rows

def getData(axis, weight_key, rows, scale_factor=1.):
    data_time = []
    data_weight = []

    time_key = 'dateandtime'
    for row in rows:
    #    for key in row.custom:
    #        print " %s: %s" % (key, row.custom[key].text)
    #    print
        if time_key in row.custom and weight_key in row.custom and row.custom[time_key].text and row.custom[weight_key].text:
            #print row.custom[time_key].text, row.custom[weight_key].text
            weight = float(row.custom[weight_key].text)
            weight *= scale_factor
            time = datetime.datetime.strptime(row.custom[time_key].text, '%m/%d/%Y %H:%M:%S')
            delta = time - initial_datetime
            days = delta.days + delta.seconds / 60. / 60. / 24.
            #stdDev = computeStdDev(days, weight, result)
            data_time.append(days)
            data_weight.append(weight)

    data_time_array   = array('f', data_time)
    data_weight_array = array('f', data_weight)
    return data_time_array, data_weight_array

# data_graph = ROOT.TGraph(len(data_time_array), data_time_array, data_weight_array)

# data_graph.SetMarkerStyle(20)
# data_graph.SetMarkerColor(ROOT.kBlack)
# data_graph.SetLineWidth(2)
# data_graph.Draw("pl")

# legend = ROOT.TLegend(.14, .9, .5, .7)
# legend.AddEntry(data_graph,    "Sebastian",                 "pl")
# legend.AddEntry(one_sig_graph, "WHO baby growth standards", "fl")
# legend.SetFillStyle(0)
# legend.SetBorderSize(0)
# legend.Draw()

# canvas.Update()




# Get baby weight mean +/-1,2,3 sigma data from
# http://www.who.int/childgrowth/standards/wfa_boys_z_exp.txt

def drawBands(axis, filename, limit=0):
    f = open(filename, 'r')
    lineNumber = 0
    daySigmasValueArray = []
    for line in f:
        values = line.split()
        lineNumber += 1
        if lineNumber > limit+1:
            break
        if len(values) == 10 and lineNumber != 1:
            #'Day   SD4neg  SD3neg  SD2neg  SD1neg  SD0     SD1     SD2     SD3     SD4'
            daySigmaValue = (
                int(values.pop(0)),
                float(values.pop(0)),
                float(values.pop(0)),
                float(values.pop(0)),
                float(values.pop(0)),
                float(values.pop(0)),
                float(values.pop(0)),
                float(values.pop(0)),
                float(values.pop(0)),
                float(values.pop(0)),
                )
            daySigmasValueArray.append(daySigmaValue)
    f.close()

    t = array('f', [ vec[0] + birth_in_days_after_epoch for vec in daySigmasValueArray ] )
    sigma = { -4: array('f', [ vec[1] for vec in daySigmasValueArray ] ),
              -3: array('f', [ vec[2] for vec in daySigmasValueArray ] ),
              -2: array('f', [ vec[3] for vec in daySigmasValueArray ] ),
              -1: array('f', [ vec[4] for vec in daySigmasValueArray ] ),
               0: array('f', [ vec[5] for vec in daySigmasValueArray ] ),
               1: array('f', [ vec[6] for vec in daySigmasValueArray ] ),
               2: array('f', [ vec[7] for vec in daySigmasValueArray ] ),
               3: array('f', [ vec[8] for vec in daySigmasValueArray ] ),
               4: array('f', [ vec[9] for vec in daySigmasValueArray ] ),
            }

    graph = {}
    #color = ['g', 'y', '#FFFF00', 'r']
    color = ['#48DD00', '#FFFD00', '#FFB400', 'r']
    trans = [.3,  .3,  .3,  .15]
    #axis.plot(t, sigma[ 3], color=color[2])
    #axis.fill_between(t, sigma[ 4], sigma[ 3], facecolor=color[3], alpha=trans[3], linewidth=0) # in ROOT I used kAzure - 4
    axis.fill_between(t, sigma[ 3], sigma[ 2], facecolor=color[2], alpha=trans[2], linewidth=0, label='WHO 2-3 sigma, boys') # in ROOT I used kCyan - 4
    axis.fill_between(t, sigma[ 2], sigma[ 1], facecolor=color[1], alpha=trans[1], linewidth=0, label='WHO 1-2 sigma, boys')
    axis.fill_between(t, sigma[ 1], sigma[ 0], facecolor=color[0], alpha=trans[0], linewidth=0, label='WHO 0-1 sigma, boys')
    axis.fill_between(t, sigma[ 0], sigma[-1], facecolor=color[0], alpha=trans[0], linewidth=0)
    axis.fill_between(t, sigma[-1], sigma[-2], facecolor=color[1], alpha=trans[1], linewidth=0)
    axis.fill_between(t, sigma[-2], sigma[-3], facecolor=color[2], alpha=trans[2], linewidth=0)
    #axis.fill_between(t, sigma[-3], sigma[-4], facecolor=color[3], alpha=trans[3], linewidth=0)
    #axis.plot(t, sigma[-3], color=color[2])
    graph[0] = axis.plot(t,sigma[0], 'k--')

    graph[1] = matplotlib.patches.Rectangle((0,0), 1, 1, fc=color[0], alpha=trans[0])
    graph[2] = matplotlib.patches.Rectangle((0,0), 1, 1, fc=color[1], alpha=trans[1])
    graph[3] = matplotlib.patches.Rectangle((0,0), 1, 1, fc=color[2], alpha=trans[2])
    graph[4] = matplotlib.patches.Rectangle((0,0), 1, 1, fc=color[3], alpha=trans[3])

    # sigma_labels = ROOT.TLatex()
    # sigma_labels.SetTextAlign(12)
    # sigma_labels.SetTextColor(sigma4_color)
    # sigma_labels.DrawLatex(result[-1][0], result[-1][9], "+4 SD")
    # sigma_labels.DrawLatex(result[-1][0], result[-1][1], "-4 SD")
    # sigma_labels.SetTextColor(sigma3_color)
    # sigma_labels.DrawLatex(result[-1][0], result[-1][8], "+3 SD")
    # sigma_labels.DrawLatex(result[-1][0], result[-1][2], "-3 SD")
    # sigma_labels.SetTextColor(sigma2_color)
    # sigma_labels.DrawLatex(result[-1][0], result[-1][7], "+2 SD")
    # sigma_labels.DrawLatex(result[-1][0], result[-1][3], "-2 SD")
    # sigma_labels.SetTextColor(sigma1_color)
    # sigma_labels.DrawLatex(result[-1][0], result[-1][6], "+1 SD")
    # sigma_labels.DrawLatex(result[-1][0], result[-1][4], "-1 SD")

    return graph

def plotOn(rows, axis, params, doLegend=False):
    time, data = getData(axis, params['gkey'], rows, params['scale_factor'])
    from_birth = datetime.datetime.now() - birth_datetime
    #days = math.ceil(from_birth.days + from_birth.seconds / 60. / 60. / 24.)
    days = 365. + 30.
    #print "Days since birth", days
    who_bands = drawBands(axis, params['who_filename'], days)
    seb_plot = axis.plot(time, data, label='Sebastian',
                         linestyle='-', linewidth=3,
                         marker='|', markersize=10,
                         color='blue')
    if doLegend:
        leg = axis.legend((seb_plot[0], who_bands[0][0], who_bands[1], who_bands[2], who_bands[3]),
                          ('Sebastian',
                           'Median for boys',
                           '0-1$\sigma$ for boys',
                           '1-2$\sigma$ for boys',
                           '2-3$\sigma$ for boys'),
                          loc='upper left',
                          labelspacing=.2, )
        for t in leg.get_texts():
            t.set_fontsize('x-small')
    axis.set_ylabel(params['yaxis'])
    axis.set_yticks(axis.get_yticks()[1:-1])
    axis.xaxis.set_major_locator(months)
    axis.xaxis.set_major_formatter(monthsFmt)
    axis.xaxis.set_minor_locator(mondays)

params = {
    'weight' : {
        'scale_factor': 0.001,
        'title' : "Baby weight",
        'yaxis' : "Weight (kg)",
        'gkey'  : "nakedweight",
        'who_filename' : 'WHO_wfa_boys_z_exp.txt',
        },
    'height' : {
        'scale_factor' : 1.0,
        'title' : "Baby height",
        'yaxis' : "Height (cm)",
        'gkey'   : 'height',
        'who_filename' : 'WHO_lhfa_boys_z_exp.txt',
        },
    'head' : {
        'scale_factor' : 1.0,
        'title' : "Baby head diameter",
        'yaxis' : "Head circumference (cm)",
        'gkey' : 'headcircumference',
        'who_filename' : 'WHO_hcfa_boys_z_exp.txt',
        },
    }

if __name__ == "__main__":
    axis_min_x = 0.1
    axis_width = 0.85

    rows = getGData()

    fig = plt.figure(figsize=(5.6,7.)) # 7 x 8in

    # From bottom, up
    ax1 = fig.add_axes([axis_min_x, 0.65, axis_width, 0.3])
    ax2 = fig.add_axes([axis_min_x, 0.35, axis_width, 0.3])
    ax3 = fig.add_axes([axis_min_x, 0.05, axis_width, 0.3])

    ax1.grid(True)
    ax2.grid(True)
    ax3.grid(True)

    # ax1r = ax1.twinx()
    # ax2r = ax2.twinx()
    # ax3r = ax3.twinx()
    # ax1r.set_ylabel("Weight (lb)")
    # ax2r.set_ylabel("Height (in)")
    # ax3r.set_ylabel("Head circumference (in)")
    # def update_ax1r(ax1):
    #     y1,y2 = ax1.get_ylim()
    #     ax1r.set_ylim(y1 * 2.2, y2 * 2.2)
    #     ax1r.figure.canvas.draw()
    # def update_ax2r(ax2):
    #     y1,y2 = ax2.get_ylim()
    #     ax2r.set_ylim(y1 / 2.54, y2 / 2.54)
    #     ax2r.figure.canvas.draw()
    # def update_ax3r(ax3):
    #     y1,y2 = ax3.get_ylim()
    #     ax3r.set_ylim(y1 / 2.54, y2 / 2.54)
    #     ax3r.figure.canvas.draw()    
    # ax1.callbacks.connect("ylim_changed", update_ax1r)
    # ax2.callbacks.connect("ylim_changed", update_ax2r)
    # ax3.callbacks.connect("ylim_changed", update_ax3r)
    
    plotOn(rows, ax1, params['weight'], doLegend=True)
    plotOn(rows, ax2, params['height'])
    plotOn(rows, ax3, params['head'])

    num_major_ranges=6
    ax1.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(nbins=num_major_ranges))
    ax2.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(nbins=num_major_ranges))
    ax3.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(nbins=num_major_ranges))
    ax1.get_xaxis().set_ticklabels([])
    ax2.get_xaxis().set_ticklabels([])
    #ax3.set_xticklabels()
    #print ax3.xaxis.get_majorticklocs()
    #print ax3.xaxis.get_majorticklabels()[1]
    #print ax3.xaxis.get_minorticklabels()[1]
    
    outfilename = "seb_monitoring.png"
    plt.savefig(outfilename)
    print "Wrote", outfilename
    #plt.show()
