import pandas as pd
import glob
import os

path = './data/'
extension = 'csv'
os.chdir(path)
result = glob.glob('*.{}'.format(extension))

# this reorders the files chronologically
order = [1, 3, 4, 2, 0]
result = [result[i] for i in order]
print(result)

df = pd.DataFrame()
for i in result:
    df_test = pd.read_csv(f'{i}', sep=';', index_col=0, parse_dates=True)
    df = pd.concat([df, df_test])

print('hi!')