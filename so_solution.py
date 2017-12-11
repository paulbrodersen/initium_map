"""
https://stackoverflow.com/questions/47293499/window-select-multiple-artists-and-drag-them-on-canvas/47312637#47312637
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

class WindowSelect(object):

    def __init__(self, artists):
        self.artists = artists
        self.colors = [a.get_facecolor() for a in self.artists]
        # assume all artists are in the same figure, otherwise selection is meaningless
        self.fig = self.artists[0].figure
        self.ax = self.artists[0].axes

        self.fig.canvas.mpl_connect('button_press_event', self.on_press)
        self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)

        self.currently_selecting = False
        self.currently_dragging = False
        self.selected_artists = []
        self.offset = np.zeros((1,2))
        self.rect = plt.Rectangle((0,0),1,1, linestyle="--",
                                  edgecolor="crimson", fill=False)
        self.ax.add_patch(self.rect)
        self.rect.set_visible(False)

        self.x0 = 0
        self.y0 = 0
        self.x1 = 0
        self.y1 = 0

    def on_press(self, event):
        # is the press over some artist
        isonartist = False
        for artist in self.artists:
            if artist.contains(event)[0]:
                isonartist = artist
        self.x0 = event.xdata
        self.y0 = event.ydata
        if isonartist:
            # add clicked artist to selection
            self.select_artist(isonartist)
            # start dragging
            self.currently_dragging = True
            ac = np.array([a.center for a in self.selected_artists])
            ec = np.array([event.xdata, event.ydata])
            self.offset = ac - ec
        else:
            #start selecting
            self.currently_selecting = True
            self.deseclect_artists()

    def on_release(self, event):
        if self.currently_selecting:
            for artist in self.artists:
                if self.is_inside_rect(*artist.center):
                    self.select_artist(artist)
            self.fig.canvas.draw_idle()
            self.currently_selecting = False
            self.rect.set_visible(False)

        elif self.currently_dragging:
            self.currently_dragging = False

    def on_motion(self, event):
        if self.currently_dragging:
            newcenters = np.array([event.xdata, event.ydata])+self.offset
            for i, artist in enumerate(self.selected_artists):
                artist.center = newcenters[i]
            self.fig.canvas.draw_idle()
        elif self.currently_selecting:
            self.x1 = event.xdata
            self.y1 = event.ydata
            #add rectangle for selection here
            self.selector_on()
            self.fig.canvas.draw_idle()

    def is_inside_rect(self, x, y):
        xlim = np.sort([self.x0, self.x1])
        ylim = np.sort([self.y0, self.y1])
        if (xlim[0]<=x) and (x<xlim[1]) and (ylim[0]<=y) and (y<ylim[1]):
            return True
        else:
            return False

    def select_artist(self, artist):
        artist.set_color('k')
        if artist not in self.selected_artists:
            self.selected_artists.append(artist)

    def deseclect_artists(self):
        for artist,color in zip(self.artists, self.colors):
            artist.set_color(color)
        self.selected_artists = []

    def selector_on(self):
        self.rect.set_visible(True)
        xlim = np.sort([self.x0, self.x1])
        ylim = np.sort([self.y0, self.y1])
        self.rect.set_xy((xlim[0],ylim[0] ) )
        self.rect.set_width(np.diff(xlim))
        self.rect.set_height(np.diff(ylim))


def demo():

    fig, ax = plt.subplots(1,1)
    xlim = [-5, 5]
    ylim = [-5, 5]
    ax.set(xlim=xlim, ylim=ylim)

    circles = [patches.Circle((3.0, 3.0), 0.5, fc='r', alpha=1.0),
               patches.Circle((0.0, 0.0), 0.5, fc='b', alpha=1.0),
               patches.Circle((0.0, 3.0), 0.5, fc='g', alpha=1.0)]

    for circle in circles:
        ax.add_patch(circle)

    w = WindowSelect(circles)
    plt.show()

if __name__ == '__main__':
    demo()
