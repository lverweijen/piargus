import pandas as pd
import piargus as pa


def main():
    tau = pa.TauArgus(r'C:\Users\LVWN\Desktop\TauArgus4.2.0b5\TauArgus')
    input_data = pa.MicroData(pd.read_csv('data/microdata.csv'))

    sbi_table = pa.Table(['symbol'], 'income',
                         safety_rule=pa.percent_rule(p=10),
                         suppress_method=pa.MODULAR)
    sbi_regio_table = pa.Table(['symbol', 'regio'], 'income',
                               safety_rule=pa.percent_rule(p=10),
                               suppress_method=pa.MODULAR)
    tables = {
        "sbi": sbi_table,
        "sbi x regio": sbi_regio_table,
    }

    job = pa.Job(input_data, tables, directory='tau', name='microdata-linked',
                 linked_suppress_method=pa.MODULAR)
    report = tau.run(job)

    print(report)
    for name, table in tables.items():
        table_result = table.load_result()
        print("Table", name)
        print(table_result)
        print()


if __name__ == '__main__':
    main()
