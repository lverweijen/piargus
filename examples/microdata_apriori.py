import pandas as pd
import piargus as pa


def main():
    tau = pa.TauArgus(r'C:\Users\LVWN\Desktop\TauArgus4.2.0b5\TauArgus')
    input_df = pd.read_csv('data/microdata.csv')
    input_data = pa.MicroData(input_df, name='example')

    apriori = pa.Apriori(expand_trivial=True)
    apriori.change_status(['A', 'ExampleDam'], pa.SAFE)
    apriori.change_status(['A', 'ExampleCity'], pa.SAFE)
    apriori.change_cost(['C', 'ExampleDam'], 10)
    apriori.change_protection_level(['C', 'ExampleCity'], 5)

    tables = [pa.Table(['sbi', 'regio'], 'income', name='T3',
                       safety_rules={'NK(3,70)', 'FREQ(3,20)', 'ZERO(20)'},
                       apriori=apriori,
                       suppress_method='OPT')]

    job = pa.Job(input_data, tables, directory='tau', name='apriori_example')
    report = tau.run(job)
    table_result = tables[0].load_result()

    print(report)
    print(table_result)
    table_result.dataframe().to_csv("output/result_microdata_apriori.csv")


if __name__ == '__main__':
    main()
