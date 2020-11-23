from utils.DatasetGenerator import random_dataset
from utils import print_rdf_exporter, rdflib_rdf_exporter
import time

NB_DATASETS = 20000


def main():
    datasets = []
    for i in range(1,NB_DATASETS):
        datasets.append(random_dataset())
    # print serializer
    start_time = time.time()
    for line in print_rdf_exporter.export(datasets):
        pass
    print(f"--- {time.time() - start_time} seconds ---")
    # rdflib serializer
    start_time = time.time()
    for line in rdflib_rdf_exporter.export(datasets):
        pass
    print(f"--- {time.time() - start_time} seconds ---")


if __name__ == "__main__":
    main()
