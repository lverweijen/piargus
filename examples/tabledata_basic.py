# Example data taken from https://github.com/InseeFrLab/rtauargus

import pandas as pd
import piargus as pa


def main():
    tau = pa.TauArgus()
    input_df = pd.read_csv("data/tabledata.csv")
    table = pa.TableData(input_df, ["activity", "size"], "val",
                         safety_rule={pa.frequency_rule(3, 10), pa.dominance_rule(1, 85)},
                         frequency="n_obs",
                         top_contributors=["max"],
                         suppress_method=pa.GHMITER)
    job = pa.Job(table, directory='tau', name='tabledata-example')
    result = tau.run(job)
    table_result = table.load_result()

    print(result)
    print(table_result)
    table_result.dataframe().to_csv('output/result_table.csv')


if __name__ == '__main__':
    main()
