import pandas as pd
import piargus as pa


def main():
    tau = pa.TauArgus(r'C:\Users\LVWN\Desktop\TauArgus4.2.0b5\TauArgus')
    input_df = pd.read_csv('data/microdata.csv')
    input_data = pa.MicroData(input_df, name='example')
    tables = [pa.Table(['sbi', 'regio'], '<freq>', cost=pa.UNITY, name='T5',
                       safety_rules={'FREQ(3,20)'},
                       suppress_method='OPT')]
    job = pa.Job(input_data, tables, directory='tau', name='response_example')
    report = tau.run(job)
    table_result = tables[0].load_result()

    print(report)
    print(table_result)
    table_result.dataframe().to_csv("output/result_response.csv")


if __name__ == '__main__':
    main()