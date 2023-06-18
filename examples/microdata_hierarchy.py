import pandas as pd
import piargus as pa


def main():
    tau = pa.TauArgus(r'C:\Users\LVWN\Desktop\TauArgus4.2.0b5\TauArgus')
    input_df = pd.read_csv('data/microdata.csv')
    sbi_hierarchy = pa.Hierarchy(["A", "C"])
    regio_hierarchy = pa.Hierarchy({"Example": ["ExampleDam", "ExampleCity"]})
    input_data = pa.MicroData(
        input_df,
        hierarchies={'sbi': sbi_hierarchy, "regio": regio_hierarchy},
        total_codes={"sbi": "Industry", "regio": "Country"},
    )
    output_table = pa.Table(['sbi', 'regio'], 'income',
                            safety_rule={pa.dominance_rule(3, 70), pa.zero_rule(20)})
    job = pa.Job(input_data, [output_table], directory='tau', name='hierarchy-example')
    report = tau.run(job)
    table_result = output_table.load_result()

    print(report)
    print(table_result)
    table_result.dataframe().to_csv("output/result_hierarchy.csv")


if __name__ == '__main__':
    main()
