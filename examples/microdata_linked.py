import pandas as pd
import piargus as pa


def main():
    argus = r"C:\Users\LVWN\Desktop\TauArgus4.2.4b2\TauArgus.exe"

    tau = pa.TauArgus(argus)
    input_data = pa.MicroData(pd.read_csv('data/microdata.csv'))

    sbi_table = pa.Table(['symbol'], 'income',
                         safety_rule=pa.dominance_rule(2, 80),
                         # suppress_method=pa.MODULAR)
                         suppress_method=None)
    sbi_regio_table = pa.Table(['symbol', 'regio'], 'income',
                               safety_rule=pa.dominance_rule(2, 80),
                               # suppress_method=pa.MODULAR)
                               suppress_method=None)
    tables = {
        "sbi": sbi_table,
        "sbi x regio": sbi_regio_table,
    }

    job = pa.Job(input_data, tables, directory='tau', name='microdata-linked-together',
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
