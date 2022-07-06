import numpy as np
# from time import time 
from Pythogen import cells, model, signals

#tstart = time()

meanCellRadius, meanPDRadius = 25, 5e-3

cell_params = cells.Cells(meanCellRadius, meanPDRadius, cellSizeGradientPC=0.5)

defSignal = signals.Signal(300, 0, 'defenceSignal')


def init_func(signal, G, names):
    idx = np.random.randint(G.number_of_nodes())
    G.nodes(data=True)[idx]['defenceSignal'] = 1


defSignal.add_onAdd_function(init_func)

mdl = model.Model('rectangle', NCellsY=25, NCellsX=25)
mdl.add_cell_features(cell_params)
mdl.add_signal(defSignal)

mdl.run(100)

df = mdl.to_pd()
print(df.sort_values(by='radius', ascending=False).head())

#print(f"Took: {time()-tstart} s to run")