import seaborn as sns
import numpy as np

data = np.genfromtxt('floats.csv', delimiter=',')

sns.set_style('whitegrid')
sns.kdeplot(np.array(data), bw=0.5)
