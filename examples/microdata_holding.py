import pandas as pd
import piargus as pa


def main():
    tau = pa.TauArgus(r'C:\Users\LVWN\Desktop\TauArgus4.2.0b5\TauArgus')
    input_df = pd.read_csv('data/microdata.csv')
    input_data = pa.MicroData(input_df, name='example', holding='holding')
    tables = [pa.Table(['sbi', 'regio'], 'income',
                       name='T4',
                       safety_rules={pa.dominance_rule(2, 20), pa.frequency_rule(1, 20)},
                       safety_rules_holding={pa.dominance_rule(1, 90), pa.p_rule(1, 30)},
                       suppress_method=pa.OPTIMAL)]
    job = pa.Job(input_data, tables, directory='tau', name='holding_example')
    report = tau.run(job)
    table_result = tables[0].load_result()

    print(report)
    print(table_result)
    table_result.dataframe().to_csv("output/result_microdata_holding.csv")


if __name__ == '__main__':
    main()
