import matplotlib.pyplot as plt


def generate_plot(print_times, rdflib_times):
    print_times.insert(0,0)
    rdflib_times.insert(0, 0)
    fig, ax = plt.subplots()
    x = []
    for i in range(0, len(print_times)):
        x.append(i*1000)
    ax.plot(x, print_times, label='XMLExporter')
    ax.plot(x, rdflib_times, label='RDFlib')
    ax.set_xlabel('catalog size (nb datasets)')
    ax.set_ylabel('time to export (s)')
    ax.legend()
    plt.show()
    return
