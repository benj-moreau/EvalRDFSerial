from django.utils import html
import six
from six import StringIO
import datetime

DT_DATETIME = "http://www.w3.org/2001/XMLSchema#dateTime"


class XMLExporter(object):

    def __init__(self):
        self.buff = StringIO()
        self.escape_html = False

    def startDocument(self):
        return '<?xml version="1.0" encoding="UTF-8"?>'

    def addQuickElement(self, name, contents=None, attrs=None, disable_escape_html=False):
        if attrs is None:
            attrs = {}
        self.startElement(name, attrs)
        if contents is not None:
            self.characters(contents, disable_escape_html=disable_escape_html)
            return self.endElement(name)

        return self.flush() + '\n'

    def flush(self):
        self.buff.seek(0)
        data = self.buff.getvalue()
        self.buff.seek(0)
        self.buff.truncate()

        return data

    def startElement(self, name, attrs=None, self_closing=False):
        if attrs is None:
            attrs = {}
        self.buff.write(u'<' + name)
        for (name, value) in list(attrs.items()):
            self.buff.write(u' %s="%s"' % (name, value))
        if self_closing:
            self.buff.write(u' />')
        else:
            self.buff.write(u'>')

    def characters(self, content, disable_escape_html=False):
        if self.escape_html and not disable_escape_html:
            escaped_content = html.escape(content)
        else:
            escaped_content = content
        self.buff.write(six.text_type(escaped_content))

    def endElement(self, name):
        self.buff.write(u'</%s>' % name)
        return self.flush() + '\n'


class DcatApCatalogExporter(XMLExporter):
    dcat_profile = ''
    namespaces = {
        "dc": "http://purl.org/dc/elements/1.1/",
        "dct": "http://purl.org/dc/terms/",  # sometimes 'dcterms' ns is used. these two ns should be consistent  (?)
        "dcat": "http://www.w3.org/ns/dcat#",
        "foaf": "http://xmlns.com/foaf/0.1/",
        "odrs": "http://schema.theodi.org/odrs#",
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
        "schema": "http://schema.org/",
        "vcard": "http://www.w3.org/2006/vcard/ns#",
        "xsd": "http://www.w3.org/2001/XMLSchema#"
    }
    additional_namespaces = {}
    additional_root_attrs = {}
    custom_parameters = {}
    formats_base = {
        "json": "application/json",
        "csv": "text/csv"
    }
    formats_geo = {
        "geojson": "application/json",
        "shp": "application/zip"
    }

    def __init__(self):
        super(DcatApCatalogExporter, self).__init__()
        self.tag_stack = []
        self.ns_keys = list(self.namespaces.keys()) + list(self.additional_namespaces.keys())
        self.escape_html = True
        self.nodes = {}

    def _load_catalog_metadata(self):
        """ Load dcat catalog metadata from the domain.properties' 'domain_catalog_metadata' field. """
        return {}

    def force_download(self):
        return False

    def get_buffer(self):
        return self.flush() + '\n'

    def enter_element(self, name, attributes=None):
        self.tag_stack.append(name)
        self.startElement(name, attributes)

    def exit_element(self, expected_element=None):
        last_element = self.tag_stack.pop()
        if expected_element and last_element != expected_element:
            raise ValueError("Expected: %s, got: %s" % (expected_element, last_element))
        self.buff.write(u'</%s>' % last_element)

    def addEmptyElement(self, name, attrs=None):
        if attrs is None:
            attrs = {}
        self.startElement(name, attrs, self_closing=True)
        return self.flush() + '\n'

    def addQuickCdataElementWithLang(self, name, contents, attributes=None, language=None):
        escaped_content = contents.replace("]]>", "]]]]><![CDATA[>")  # proper escaping of CDATA end string
        escaped_content = "<![CDATA[%s]]>" % escaped_content
        return self.addQuickElementWithLang(name, escaped_content, attributes, disable_escape_html=True, language=language)

    def addQuickCdataElement(self, name, contents, attributes=None):
        escaped_content = contents.replace("]]>", "]]]]><![CDATA[>")  # proper escaping of CDATA end string
        escaped_content = "<![CDATA[%s]]>" % escaped_content
        return self.addQuickElement(name, escaped_content, attributes, disable_escape_html=True)

    def addQuickElementWithLang(self, name, contents=None, attributes=None, disable_escape_html=False, language=None):
        attrs = attributes.copy() if attributes else {}
        if language is not None:
            attrs.update({"xml:lang": language})
            return self.addQuickElement(name, contents, attrs, disable_escape_html)
        else:
            raise ValueError("Expected: language, got: %s" % language)

    def dataset_generator(self, dataset, catalog_metas):
        metas, dataset_title, dataset_language, description, issued, contact_name, contact_email = self.load_dataset_generator_params(dataset)

        self.enter_element("dcat:Dataset")
        yield self.addQuickCdataElementWithLang("dc:description", description, language=dataset_language)
        yield self.addQuickElement("dct:issued", issued, {"rdf:datatype": DT_DATETIME})
        yield self.addQuickElement("dct:modified", issued, {"rdf:datatype": DT_DATETIME})
        yield self.addEmptyElement("rdf:type", {"rdf:resource": "http://www.w3.org/ns/dcat#Dataset"})

        if metas.get('dcat.accrualperiodicity'):
             yield self.addEmptyElement("dct:accrualPeriodicity", {'rdf:resource': metas.get('dcat.accrualperiodicity')})

        if 'vcard' in self.ns_keys and (contact_name or contact_email):
            node_id = self.add_node(self.generate_dataset_contact_elem, contact_name=contact_name, contact_email=contact_email)
            yield self.addEmptyElement('dcat:contactPoint', {'rdf:nodeID': node_id})

        # closing the dataset object
            self.exit_element("dcat:Dataset")
        yield self.get_buffer()

    def load_dataset_generator_params(self, dataset):
        metas = dataset.get("metas")
        dataset_title = metas.get('default').get('title')
        dataset_language = metas.get("default").get('language')
        description = metas.get("default").get("title")
        issued = metas.get("dcat").get("issued")

        contact_name = metas.get("dcat").get("contact_name")
        contact_email = metas.get("dcat").get("contact_email")

        return metas, dataset_title, dataset_language, description, issued, contact_name, contact_email

    def catalog_generator(self, datasets):
        catalog_metas, catalog_lang, ns_attrs = self.load_catalog_generator_params()

        self.enter_element("dcat:Catalog", ns_attrs)

        for dataset in datasets:
            for line in self.dataset_generator(dataset, catalog_metas):
                yield line

        self.exit_element("dcat:Catalog")
        yield self.get_buffer()

    def load_catalog_generator_params(self):
        catalog_metas = self._load_catalog_metadata()
        catalog_lang = catalog_metas.get('language', '')

        ns_attrs = {'xmlns:'+k: v for k, v in list(self.namespaces.items())}
        ns_attrs.update({'xmlns:'+k: v for k, v in list(self.additional_namespaces.items())})
        ns_attrs.update({k: v for k, v in list(self.additional_root_attrs.items())})

        return catalog_metas, catalog_lang, ns_attrs

    def export_results(self, datasets):
        """ Catalog generator. """
        yield self.startDocument()

        for line in self.catalog_generator(datasets):
            yield line

    def add_node(self, gen_method, **kwargs):
        for node, node_values in list(self.nodes.items()):
            if node_values['args'] == kwargs:
                return node
        cur_node_id = '_n{}'.format(len(self.nodes))
        self.nodes[cur_node_id] = {
            'gen_method': gen_method,
            'args': kwargs
        }
        return cur_node_id

    def generate_dataset_contact_elem(self, contact_name):
        self.enter_element("dcat:contactPoint")
        if contact_name:
            yield self.addQuickElement("vcard:fn", contact_name)
        self.exit_element()
        yield self.get_buffer()


def export(datasets):
    dcat_exporter = DcatApCatalogExporter()
    return dcat_exporter.export_results(datasets)