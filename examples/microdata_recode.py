import pandas as pd
import piargus as pa


def main():
    tau = pa.TauArgus()
    symbol_hierarchy = pa.TreeHierarchy(["A", "C"], total_code="Industry")
    regio_hierarchy = pa.TreeHierarchy(
        [
            pa.Node("Example", [pa.Node("ExampleDam"), pa.Node("ExampleCity")]),
            pa.Node("Empty", []),
        ], total_code="Country"
    )

    input_df = pd.read_csv('data/microdata.csv')
    input_data = pa.MicroData(
        input_df,
        hierarchies={'symbol': symbol_hierarchy, "regio": regio_hierarchy},
    )
    output_table = pa.Table(['symbol', 'regio'], 'income',
                            safety_rule={pa.p_rule(3)},
                            recode={"regio": ["Example", "Empty"], "symbol": 1})

    job = pa.Job(input_data, [output_table], directory='tau', name='recode-example')
    report = tau.run(job)
    table_result = output_table.load_result()

    print(report)
    print(table_result)
    table_result.dataframe().to_csv("output/result_recode.csv")


if __name__ == '__main__':
    main()
