import numpy as np
import matplotlib.pyplot as plt; plt.ion()
import matplotlib.patches as patches
import copy
class Points(object):
    """
    https://stackoverflow.com/questions/21654008/matplotlib-drag-overlapping-points-interactively
    """
    def __init__(self, artists, tolerance=5):
        for artist in artists:
            artist.set_picker(tolerance)
        self.artists = artists
        self.currently_dragging = False
        self.current_artist = None
        self.offset = (0, 0)

        for canvas in set(artist.figure.canvas for artist in self.artists):
            canvas.mpl_connect('button_press_event', self.on_press)
            canvas.mpl_connect('button_release_event', self.on_release)
            canvas.mpl_connect('pick_event', self.on_pick)
            canvas.mpl_connect('motion_notify_event', self.on_motion)

    def on_press(self, event):
        self.currently_dragging = True

    def on_release(self, event):
        self.currently_dragging = False
        self.current_artist = None

    def on_pick(self, event):
        # print 'yay'
        if self.current_artist is None:
            self.current_artist = event.artist
            x0, y0 = event.artist.center
            x1, y1 = event.mouseevent.xdata, event.mouseevent.ydata
            self.offset = (x0 - x1), (y0 - y1)

    def on_motion(self, event):
        if not self.currently_dragging:
            return
        if self.current_artist is None:
            return
        dx, dy = self.offset
        self.current_artist.center = event.xdata + dx, event.ydata + dy
        self.current_artist.figure.canvas.draw()


class GridPoints(Points):

    def on_release(self, event):

        # move artist to nearest grid point
        x0, y0 = self.current_artist.center
        x0 = np.int(np.round(x0))
        y0 = np.int(np.round(y0))
        self.current_artist.center = x0, y0
        self.current_artist.figure.canvas.draw()

        Points.on_release(self, event)


class GridPointsWithGhosts(GridPoints):

    def on_release(self, event):
        self.ghost_artist.remove()
        GridPoints.on_release(self, event)
        # for artist in self.artists:
        #     print artist.center

    def on_pick(self, event):
        if self.current_artist is None:

            # create 'ghost' of current artist
            self.ghost_artist = copy.copy(event.artist)
            # self.ghost_artist.set_alpha(0.1)
            event.artist.axes.add_patch(self.ghost_artist)

            GridPoints.on_pick(self, event)


def demo_points():

    fig, ax = plt.subplots()
    ax.set(xlim=[-5, 5], ylim=[-5, 5])

    circles = [patches.Circle((1.0, 1.0), 0.5, fc='r', alpha=0.5),
               patches.Circle((0.0, 0.0), 0.5, fc='b', alpha=0.5)]
    for circle in circles:
        ax.add_patch(circle)

    dr = GridPointsWithGhosts(circles)

    return dr

