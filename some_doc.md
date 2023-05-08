**Logic of choosing 'lxml' python library over 'xml'**

- 'xml' is a built-in library in Python that provides a simple API for parsing and working with XML documents. It uses the DOM (Document Object Model) approach, where the entire XML document is loaded into memory as a tree structure, and then nodes can be accessed, modified or deleted using various methods. This approach is useful for small to medium-sized XML documents, but it may become slow and memory-intensive for very large documents.

- On the other hand, 'lxml' is a third-party library that is built on top of libxml2 and libxslt libraries. It provides a more powerful and efficient API for parsing and working with XML and HTML documents. 'lxml' supports both the DOM approach (similar to xml), and also the SAX (Simple API for XML) approach, which is a stream-based parsing method that processes XML documents incrementally, without loading the entire document into memory. This makes it more suitable for large XML documents, as it can process them efficiently and without using too much memory.

- 'lxml' supports XPath expressions, which makes it easier to extract information from XML files.

- 'lxml' supports XSLT transformations, which can be used to transform XML documents into different formats or to extract specific information.

- 'lxml' also includes support for parsing HTML documents, which can be useful when working with web scraping or other web-related projects.
