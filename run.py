from utils.DatasetGenerator import random_dataset
from utils import print_rdf_exporter, rdflib_rdf_exporter

NB_DATASETS = 20000


def main():
    datasets = []
    for i in range(1,NB_DATASETS):
        datasets.append(random_dataset())
    export = print_rdf_exporter.export(datasets)


if __name__ == "__main__":
    main()
