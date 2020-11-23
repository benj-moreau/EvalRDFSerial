from utils.DatasetGenerator import random_dataset
from utils import print_rdf_exporter, rdflib_rdf_exporter

NB_DATASETS = 20000


def main():
    datasets = []
    for i in range(1,2):
        datasets.append(random_dataset())
    results = rdflib_rdf_exporter.export(datasets)
    for res in results:


if __name__ == "__main__":
    main()
