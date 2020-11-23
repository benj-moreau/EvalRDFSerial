from utils.DatasetGenerator import random_dataset
from utils import print_rdf_exporter, rdflib_rdf_exporter
from utils.PlotGenerator import generate_plot
import time

NB_DATASETS = 20000


def main():
    datasets = []
    for i in range(1, NB_DATASETS):
        datasets.append(random_dataset())
    # print serializer
    start_time = time.time()
    cpt = 0
    print_times = []
    for i, line in enumerate(print_rdf_exporter.export(datasets)):
        if cpt > 5001:
            cpt = 0
            print_times.append(time.time() - start_time)
        cpt += 1
        pass
    # rdflib serializer
    start_time = time.time()
    rdflib_times = []
    cpt = 0
    for i, dataset in enumerate(rdflib_rdf_exporter.export(datasets)):
        if cpt > 2001:
            cpt = 0
            rdflib_times.append(time.time() - start_time)
        cpt += 1
        pass
    generate_plot(print_times, rdflib_times)


if __name__ == "__main__":
    main()
