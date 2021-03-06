import numpy as np
from networkx import shortest_path_length
from tqdm import tqdm

from .nx import attr_to_arr, custom_shape, generate_shape, get_centre_node
from .utility import G_to_pd


class Model:
    def __init__(self,
                 shape,
                 NCells=100,
                 NCellsY=None,
                 NCellsX=None,
                 custom=None,
                 custom_cut=0, 
                 unique_seed=True):
        if unique_seed:
            np.random.seed()
        self.shape = shape
        if custom is not None:
            self.G = custom_shape(custom, cut_center=custom_cut)
        elif NCellsY is not None and NCellsX is not None:
            self.G = generate_shape(self.shape, n=NCellsX, m=NCellsY)
        else:
            self.G = generate_shape(self.shape,
                                    n=int(np.sqrt(NCells)),
                                    m=int(np.sqrt(NCells)))
        self.apply_neighbours_to_data()
        self.apply_dist_from_centre()
        self.Cells = None
        self.signals = []

    def apply_neighbours_to_data(self):
        for idx, n in self.G.nodes(data=True):
            n['neighbours'] = list(self.G.neighbors(idx))
            n['num_neighbours'] = len(n['neighbours'])

    def apply_f_to_G(self, f):
        for idx, n in self.G.nodes(data=True):
            f(n)

    def add_cell_features(self, Cells, overwrite=False):
        Cells.run_onAdd(self.G)
        self.apply_cell_radii(Cells, overwrite=overwrite)
        self.Cells = Cells

    def add_signal(self, signal):
        self.signals.append(signal)

        signal.onAdd(self.G)

    def run(self, seconds, dt=1, seconds_per_update=1, progress_bar=False):
        dfs = []
        epochs = int(seconds_per_update / dt)
        dx = attr_to_arr(self.G, 'radius')
        for signal in self.signals:
            signal.set_Deff(self.G)

        if progress_bar:
            for update in tqdm(range(int(seconds / seconds_per_update))):
                self.run_update(seconds_per_update, dt, dx, epochs, update, dfs)
        else:
            for update in range(int(seconds / seconds_per_update)):
                self.run_update(seconds_per_update, dt, dx, epochs, update, dfs)
        return dfs

    def run_update(self, seconds_per_update, dt, dx, epochs, update, dfs):
            for signal in  self.signals:
                signal.set_Deff(self.G)
                signal.run_diffuse(self.G, dt, dx, epochs)
                signal.interact(self.G)
                signal.run_decay(self.G)
                signal.run_production(self.G)
                #signal.flatten(self.G)
            df = self.to_pd()
            df['time'] = (update + 1) * seconds_per_update
            dfs.append(df)

    def apply_cell_radii(self, Cells, overwrite=False):
        Ys = attr_to_arr(self.G, 'y')
        maxY = max(Ys)
        for k, c in self.G.nodes(data=True):
            r_noise = np.random.normal(
                Cells.meanCellRadius,
                Cells.cellRadiusVariationPC * Cells.meanCellRadius)

            # TODO: this needs adjusting to maintain mean size
            r = lambda: abs(r_noise * (1 + c['y'] / maxY * Cells.cellSizeGradientPC))
            
            pdr = lambda : abs(
                np.random.normal(
                    Cells.meanPDRadius,
                    Cells.PDRadiusVariationPC * Cells.meanPDRadius))

            num_pd = lambda: abs(
                np.random.normal(Cells.meanPDNum,
                                 Cells.meanPDNum * Cells.PDNumVariationPC))

            
            c['radius'] = r() if ('radius' not in c
                                or overwrite) else c['radius']

            c['radius_ep_original'] = pdr() if (
                'radius_ep_original' not in c
                or overwrite) else c['radius_ep_original']

            c['radius_ep'] = c['radius_ep_original']

            c['num_pd'] = num_pd() if ('num_pd' not in c
                                     or overwrite) else c['num_pd']

    def apply_dist_from_centre(self):
        centre = get_centre_node(self.G, voronoi=(True if 'voronoi' in self.shape else False))
        for n, d in self.G.nodes(data=True):
            d['distCentre'] = shortest_path_length(self.G, n, centre)

    def to_pd(self):
        return G_to_pd(self.G, self.shape)
