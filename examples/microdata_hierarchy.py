import pandas as pd
import piargus as pa


def main():
    tau = pa.TauArgus()
    input_df = pd.read_csv('data/microdata.csv')

    # Use LevelHierarchy if the code itself is hierarchical (e.g. nace-codes)
    sbi_hierarchy = pa.LevelHierarchy([2, 1, 1], total_code="TTTT")

    # Use a TreeHierarchy to have more control about how the codes are nested
    # Can also be stored and loaded as hrc-format.
    regio_hierarchy = pa.TreeHierarchy([
        pa.Node("ExampleProvince", children=[
            pa.Node("ExampleDam"),
            pa.Node("ExampleCity"),
        ]),
        pa.Node("EmptyProvince")
    ], total_code="CountryTotal")

    print(f"Using the following hierarchy for sbi:\n{sbi_hierarchy}")
    print(f"Using the following hierarchy for regio:\n{regio_hierarchy}")
    # regio_hierarchy.to_image().show()  # If graphviz and Pillow are installed

    input_data = pa.MicroData(
        input_df,
        hierarchies={'sbi': sbi_hierarchy, "regio": regio_hierarchy},
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
