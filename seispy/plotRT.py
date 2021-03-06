import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.lines import Line2D
from seispy.rfcorrect import SACStation
from seispy.rf import CfgParser
import argparse
import numpy as np
from os.path import join, realpath, basename, exists
import sys


def init_figure():
    h = plt.figure(figsize=(11.7, 8.3))
    gs = GridSpec(17, 3)
    gs.update(wspace=0.25)
    axr_sum = plt.subplot(gs[0, 0])
    axr_sum.grid(color='gray', linestyle='--', linewidth=0.4, axis='x')
    axr = plt.subplot(gs[1:, 0])
    axr.grid(color='gray', linestyle='--', linewidth=0.4, axis='x')
    axt_sum = plt.subplot(gs[0, 1])
    axt_sum.grid(color='gray', linestyle='--', linewidth=0.4, axis='x')
    axt = plt.subplot(gs[1:, 1])
    axt.grid(color='gray', linestyle='--', linewidth=0.4, axis='x')
    axb = plt.subplot(gs[1:, 2])
    axb.grid(color='gray', linestyle='--', linewidth=0.4, axis='x')
    return h, axr, axt, axb, axr_sum, axt_sum


def read_process_data(lst):
    stadata = SACStation(lst)
    idx = np.argsort(stadata.bazi)
    stadata.event = stadata.event[idx]
    stadata.bazi = stadata.bazi[idx]
    stadata.datar = stadata.datar[idx]
    stadata.datat = stadata.datat[idx]
    time_axis = np.arange(stadata.RFlength) * stadata.sampling - stadata.shift
    return stadata, time_axis


def plot_waves(axr, axt, axb, axr_sum, axt_sum, stadata, time_axis, enf=3):
    bound = np.zeros(stadata.RFlength)
    for i in range(stadata.ev_num):
        datar = stadata.datar[i] * enf + (i + 1)
        datat = stadata.datat[i] * enf + (i + 1)
        # axr.plot(time_axis, stadata.datar[i], linewidth=0.2, color='black')
        axr.fill_between(time_axis, datar, bound + i+1, where=datar > i+1, facecolor='red',
                         alpha=0.7)
        axr.fill_between(time_axis, datar, bound + i+1, where=datar < i+1, facecolor='blue',
                         alpha=0.7)
        # axt.plot(time_axis, stadata.datat[i], linewidth=0.2, color='black')
        axt.fill_between(time_axis, datat, bound + i + 1, where=datat > i+1, facecolor='red',
                         alpha=0.7)
        axt.fill_between(time_axis, datat, bound + i + 1, where=datat < i+1, facecolor='blue',
                         alpha=0.7)
    datar = np.mean(stadata.datar, axis=0)
    datar /= np.max(datar)
    datat = np.mean(stadata.datat, axis=0)
    datat /= np.max(datar)
    axr_sum.fill_between(time_axis, datar, bound, where=datar > 0, facecolor='red', alpha=0.7)
    axr_sum.fill_between(time_axis, datar, bound, where=datar < 0, facecolor='blue', alpha=0.7)
    axt_sum.fill_between(time_axis, datat, bound, where=datat > 0, facecolor='red', alpha=0.7)
    axt_sum.fill_between(time_axis, datat, bound, where=datat < 0, facecolor='blue', alpha=0.7)
    axb.scatter(stadata.bazi, np.arange(stadata.ev_num) + 1, s=7)


def set_fig(axr, axt, axb, axr_sum, axt_sum, stadata, station, xmin=-2, xmax=30):
    y_range = np.arange(stadata.ev_num) + 1
    x_range = np.arange(0, xmax+2, 2)
    space = 2

    # set axr
    axr.set_xlim(xmin, xmax)
    axr.set_xticks(x_range)
    axr.set_xticklabels(x_range, fontsize=8)
    axr.set_ylim(0, stadata.ev_num + space)
    axr.set_yticks(y_range)
    axr.set_yticklabels(stadata.event, fontsize=5)
    axr.set_xlabel('Time after P (s)', fontsize=13)
    axr.set_ylabel('Event', fontsize=13)
    axr.add_line(Line2D([0, 0], axr.get_ylim(), color='black'))

    # set axr_sum
    axr_sum.set_title('R components ({})'.format(station), fontsize=16)
    axr_sum.set_xlim(xmin, xmax)
    axr_sum.set_xticks(x_range)
    axr_sum.set_xticklabels([])
    axr_sum.set_ylim(-0.5, 1.25)
    axr_sum.set_yticks([0.375])
    axr_sum.set_yticklabels(['Sum'], fontsize=8)
    axr_sum.tick_params(axis='y', left=False)
    axr_sum.add_line(Line2D([0, 0], axr_sum.get_ylim(), color='black'))

    # set axt
    axt.set_xlim(xmin, xmax)
    axt.set_xticks(x_range)
    axt.set_xticklabels(x_range, fontsize=8)
    axt.set_ylim(0, stadata.ev_num + space)
    axt.set_yticks(y_range)
    bazi = ['{:.1f}'.format(ba) for ba in stadata.bazi]
    axt.set_yticklabels(bazi, fontsize=5)
    axt.set_xlabel('Time after P (s)', fontsize=13)
    axt.set_ylabel(r'Back-azimuth ($\circ$)', fontsize=13)
    axt.add_line(Line2D([0, 0], axt.get_ylim(), color='black'))

    # set axt_sum
    axt_sum.set_title('T components ({})'.format(station), fontsize=16)
    axt_sum.set_xlim(xmin, xmax)
    axt_sum.set_xticks(x_range)
    axt_sum.set_xticklabels([])
    axt_sum.set_ylim(-0.5, 1.25)
    axt_sum.set_yticks([0.375])
    axt_sum.set_yticklabels(['Sum'], fontsize=8)
    axt_sum.tick_params(axis='y', left=False)
    axt_sum.add_line(Line2D([0, 0], axt_sum.get_ylim(), color='black'))

    # set axb
    axb.set_xlim(0, 360)
    axb.set_xticks(np.linspace(0, 360, 7))
    axb.set_xticklabels(np.linspace(0, 360, 7, dtype='i'), fontsize=8)
    axb.set_ylim(0, stadata.ev_num + space)
    axb.set_yticks(y_range)
    axb.set_yticklabels(y_range, fontsize=5)
    axb.set_xlabel(r'Back-azimuth ($\circ$)', fontsize=13)


def plotrt(rfpath, enf=3, out_path='./'):
    station = basename(rfpath)
    lst = join(rfpath, station+'finallist.dat')
    if not exists(lst):
        raise FileExistsError('No such a final list as {}'.format(lst))
    if not exists(out_path):
        raise FileExistsError('The output path {} not exists'.format(out_path))
    h, axr, axt, axb, axr_sum, axt_sum = init_figure()
    stadata, time_axis = read_process_data(lst)
    plot_waves(axr, axt, axb, axr_sum, axt_sum, stadata, time_axis, enf=enf)
    set_fig(axr, axt, axb, axr_sum, axt_sum, stadata, station)
    h.savefig(join(out_path, station+'_RT_bazorder_{:.1f}.pdf'.format(stadata.f0[0])), format='pdf')


def main():
    parser = argparse.ArgumentParser(description="Plot R&T components for P receiver functions (PRFs)")
    parser.add_argument('path', help='Path to PRFs with a \'finallist.dat\' in it', type=str, default=None)
    parser.add_argument('-e', help='Enlargement factor default is 3', dest='enf', type=int, default=3)
    parser.add_argument('-o', help='Output path without file name', dest='output', default='./', type=str)
    arg = parser.parse_args()
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    plotrt(rfpath=arg.path, enf=arg.enf, out_path=arg.output)


if __name__ == '__main__':
    # plotrt('XHL01')
    pass
