import pandas as pd
import piargus as pa


def main():
    tau = pa.TauArgus(r'C:\Users\LVWN\Desktop\TauArgus4.2.0b5\TauArgus')
    input_data = pa.MicroData(pd.read_csv('data/microdata.csv'))
    output_table = pa.Table(['symbol', 'regio'], 'income',
                            safety_rule=pa.percent_rule(p=10),
                            suppress_method=pa.OPTIMAL)
    job = pa.Job(input_data, [output_table], directory='tau', name='basic-example')
    report = tau.run(job)
    table_result = output_table.load_result()

    print(report)
    print(table_result)
    table_result.dataframe().to_csv("output/result_microdata.csv")


if __name__ == '__main__':
    main()
