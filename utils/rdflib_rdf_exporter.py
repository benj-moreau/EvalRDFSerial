from rdflib import Graph, URIRef, RDF, XSD, Literal

DATASET_TYPE = URIRef("http://www.w3.org/ns/dcat#Dataset")
DESCRIPTION = URIRef("http://purl.org/dc/elements/1.1/description")
ISSUED = URIRef("http://purl.org/dc/terms/issued")
MODIFIED = URIRef("http://purl.org/dc/terms/modified")
ACCRUAL = URIRef("http://purl.org/dc/terms/accrualPeriodicity")


class CatalogExporter():

    def export_results(self, datasets):
        self.start_document = None
        for n, dataset in enumerate(datasets):
            serialized_dataset = self.export_result(dataset)
            if n > 0:
                yield self.output_separator()
                serialized_dataset = serialized_dataset.replace(self.output_header(serialized_dataset), b'', 1)
            if self.output_footer():
                serialized_dataset = b''.join(serialized_dataset.rsplit(self.output_footer(), 1))
            yield serialized_dataset
        yield self.output_footer()

    def export_result(self, dataset):
        dataset_graph = Graph()
        metas = dataset.get("metas")
        dataset_title = metas.get('default').get('title')
        dataset_language = metas.get("default").get('language')
        description = metas.get("default").get("title")
        issued = metas.get("dcat").get("issued")
        modified = metas.get("dcat").get("modified")
        accrual = metas.get("dcat").get("accrualperiodicity")
        dataset_uri = URIRef(f"http://localhost:8000/dataset/{dataset_title}")
        dataset_graph.add((dataset_uri, RDF.type, DATASET_TYPE))
        dataset_graph.add((dataset_uri, DESCRIPTION, Literal(description, lang=dataset_language)))
        dataset_graph.add((dataset_uri, ISSUED, Literal(issued, datatype=XSD.date)))
        dataset_graph.add((dataset_uri, MODIFIED, Literal(modified, datatype=XSD.date)))
        dataset_graph.add((dataset_uri, ACCRUAL, Literal(accrual)))
        return self.serialize(dataset_graph)

    def serialize(self, graph):
        raise NotImplementedError

    def output_header(self, graph):
        return ''

    def output_footer(self):
        return ''

    def output_separator(self):
        return ''


class XMLRdfExporter(CatalogExporter):

    def serialize(self, graph):
        return graph.serialize(format="xml", encoding="utf-8")

    def output_header(self, graph):
        prefixes = graph.split(b'<?xml version="1.0" encoding="UTF-8"?>')[1].split(b'>')[0]
        self.start_document = b'<?xml version="1.0" encoding="UTF-8"?>%s>' % prefixes
        return self.start_document

    def output_footer(self):
        return b'\n</rdf:RDF>'

    def get_content_type(self):
        return b'application/rdf+xml'

    def get_file_extension(self):
        return "rdf"


def export(datasets):
    dcat_exporter = XMLRdfExporter()
    return dcat_exporter.export_results(datasets)
