import numpy as np
import matplotlib.pyplot as plt; plt.ion()
import matplotlib.patches as patches
import copy
import netgraph; reload(netgraph)


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

        # move artist to nearest integer point
        x0, y0 = self.current_artist.center
        x0 = np.int(np.round(x0))
        y0 = np.int(np.round(y0))
        self.current_artist.center = x0, y0
        self.current_artist.figure.canvas.draw()
        Points.on_release(self, event)


class Graph(object):
    """
    Essentially a wrapper around netgraph, making netgraph drawing
    functions methods of a class such that the plot of a network can
    be updated in response to mouse events on the plot canvas.
    """

    def __init__(self, adjacency_matrix, node_positions,
                 node_labels=None,
                 edge_labels=None,
                 draw_nodes_kwargs={},
                 draw_edges_kwargs={},
                 draw_node_labels_kwargs={},
                 draw_edge_labels_kwargs={},
                 ax=None,
                 point_class=Points):
        """
        See netgraph
            .draw_nodes()
            .draw_edges()
            .draw_node_labels()
            .draw_edge_labels()
        for details on keyword arguments.
        """

        # retain input
        self.adjacency_matrix        = adjacency_matrix
        self.node_positions          = node_positions
        self.node_labels             = node_labels
        self.edge_labels             = edge_labels
        self.draw_nodes_kwargs       = draw_nodes_kwargs
        self.draw_edges_kwargs       = draw_edges_kwargs
        self.draw_node_labels_kwargs = draw_node_labels_kwargs
        self.draw_edge_labels_kwargs = draw_edge_labels_kwargs
        self.point_class = point_class

        # set sensible defaults if None are given
        if ax is None:
            self.axis = plt.gca()
        else:
            self.axis = ax
        self.axis.set_aspect('equal')

        if 'node_size' in draw_nodes_kwargs:
            self.node_size = draw_nodes_kwargs['node_size']
        else:
            self.node_size = 3

        # cache some intermediate computations
        self.total_nodes = len(node_positions)

        # initialise graph
        self.draw()

        # keep axis limits constant
        self.xlim = self.axis.get_xlim()
        self.ylim = self.axis.get_ylim()

        # hook up mouse button release to re-draw, etc
        self.axis.get_figure().canvas.mpl_connect('button_release_event', self.on_release)

    def on_release(self, event):
        # TODO: should really only remove artists, such that axis properties are not cleared;
        self.update_node_positions()
        self.update_axis()
        self.draw()

    def update_axis(self):
        self.axis.cla()
        self.axis.set_xlim(self.xlim)
        self.axis.set_ylim(self.ylim)

    def update_node_positions(self):
        self.node_positions = np.array([artist.center for artist in self.draggable.artists])

    def draw(self):

        node_artists = netgraph.draw_nodes(self.node_positions,
                                           ax=self.axis, **self.draw_nodes_kwargs)

        netgraph.draw_edges(self.adjacency_matrix, self.node_positions,
                            ax=self.axis, **self.draw_edges_kwargs)

        if self.node_labels:
            netgraph.draw_node_labels(self.node_positions, self.node_labels,
                                      ax=self.axis, **self.draw_node_labels_kwargs)

        if self.edge_labels:
            netgraph.draw_edge_labels(self.adjaceny_matrix, self.node_positions,
                                      self.edge_labels, ax=self.axis, **self.draw_edge_labels_kwargs)

        # make nodes artists draggable
        node_faces = [node_artists[(ii, 'face')] for ii in range(self.total_nodes)]
        draggable = self.point_class(node_faces)
        # draggable points need to be a member of the class;
        # otherwise, reference to them will be garbage collected once the graph is redrawn,
        # and then nothing will be actually draggable
        self.draggable = draggable

        # update figure
        self.axis.get_figure().canvas.draw()


def demo_points():

    fig, ax = plt.subplots()
    ax.set(xlim=[-5, 5], ylim=[-5, 5])

    circles = [patches.Circle((1.0, 1.0), 0.5, fc='r', alpha=0.5),
               patches.Circle((0.0, 0.0), 0.5, fc='b', alpha=0.5)]
    for circle in circles:
        ax.add_patch(circle)

    dr = GridPoints(circles)

    return dr


def demo_graph():

    n = 4
    adj = np.ones((n,n))
    adj = np.triu(adj, 1)
    adj[adj==0] = np.nan
    # pos = np.random.rand(n,2)
    pos = np.random.rand(n,2)
    pos[:,0] *= 10
    pos[:,1] *= 5

    fig, ax = plt.subplots()
    ax.set(xlim=[0, 10], ylim=[0, 5])
    g = Graph(adj, pos, ax=ax,
              draw_nodes_kwargs=dict(node_color='r', node_size=0.25, node_edge_width=-0.01),
              draw_edges_kwargs=dict(edge_width=0.05, draw_arrows=False), point_class=GridPoints)

    return g


if __name__ == '__main__':

    # out = demo_points()
    out = demo_graph()
