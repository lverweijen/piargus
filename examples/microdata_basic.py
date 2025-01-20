import pandas as pd
import piargus as pa


def main():
    input_data = pa.MicroData(pd.read_csv('data/microdata.csv'))
    input_data['symbol'].total_code = 'Total'
    input_data['regio'].total_code = 'NL'

    output_table = pa.Table(['symbol', 'regio'], 'income')
    output_table.safety_rule = pa.percent_rule(p=10)
    output_table.suppress_method = pa.OPTIMAL

    tau = pa.TauArgus()
    job = pa.Job(input_data, [output_table], directory='tau-new', name='basic-example-new')
    report = tau.run(job)
    table_result = output_table.load_result()

    print(report)
    print(table_result)
    table_result.dataframe().to_csv("output/result_microdata.csv")


if __name__ == '__main__':
    main()
