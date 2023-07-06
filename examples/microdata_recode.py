import pandas as pd
import piargus as pa


def main():
    tau = pa.TauArgus(r'C:\Users\LVWN\Desktop\TauArgus4.2.4b2\TauArgus')
    input_df = pd.read_csv('data/microdata.csv')
    symbol_hierarchy = pa.Hierarchy(["A", "C"])
    regio_hierarchy = pa.Hierarchy({"Example": ["ExampleDam", "ExampleCity"]})
    input_data = pa.MicroData(
        input_df,
        hierarchies={'symbol': symbol_hierarchy, "regio": regio_hierarchy},
        total_codes={"symbol": "Industry", "regio": "Country"},
    )
    output_table = pa.Table(['symbol', 'regio'], 'income',
                            safety_rule={pa.p_rule(3)},
                            recodes={"regio": ["Example"], "symbol": 1})
    job = pa.Job(input_data, [output_table], directory='tau', name='recode-example')
    report = tau.run(job)
    table_result = output_table.load_result()

    print(report)
    print(table_result)
    table_result.dataframe().to_csv("output/result_recode.csv")


if __name__ == '__main__':
    main()
