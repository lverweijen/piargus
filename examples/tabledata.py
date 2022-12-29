# Example data taken from https://github.com/InseeFrLab/rtauargus

import pandas as pd
import piargus as pa


def main():
    tau = pa.TauArgus(r'C:\Users\LVWN\Desktop\TauArgus4.2.0b5\TauArgus')
    input_df = pd.read_csv("data/tabledata.csv")
    table = pa.TableData(input_df, ["activity", "size"], "val",
                         name='T2',
                         safety_rules={"FREQ(3,10)", "NK(1,85)"},
                         frequency="n_obs",
                         top_contributors=["max"],
                         suppress_method='GH')

    job = pa.Job(table, directory='tau', name='tabledata_example')
    result = tau.run(job)
    table_result = table.load_result()

    print(result)
    print(table_result)
    table_result.dataframe().to_csv('output/result_table.csv')


if __name__ == '__main__':
    main()
