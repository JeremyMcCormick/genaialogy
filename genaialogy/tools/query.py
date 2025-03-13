"""Engine for making genealogy queries on a document index."""

import textwrap

from llama_index.core.memory import ChatMemoryBuffer


class GenealogyQueryEngine:
    """Engine for making genealogy queries on a document index."""

    def __init__(
        self, index, format_response=True, top_k=100, max_tokens=1000, memory=True
    ):

        self.index = index
        self.format_response = format_response
        self.top_k = top_k

        self.memory = ChatMemoryBuffer(token_limit=1024) if memory else None

        self.query_engine = index.as_query_engine(
            memory=self.memory,
            max_tokens=max_tokens,
            system_prompt="You are an expert in genealogy."
            "Answer queries based on historical family records with accuracy.",
        )

    def _format_response(self, response):
        """
        Formats the response:
        - Wraps text to 80 characters per line.
        - Cleans up formatting inconsistencies.
        """
        response_str = str(response)
        response_str = response_str.encode().decode(
            "unicode_escape"
        )  # Convert encoded newlines safely
        return textwrap.fill(response_str, width=80)

    def query(self, question, keyword_filters=None, print_response=True, stream=False):
        """
        Queries the index with optional metadata filtering and streaming support.

        :param question: The query text.
        :param metadata_filters: A dictionary of metadata filters.
        :param print_response: Whether to print the response.
        :param stream: Whether to stream the response for large text output.
        """
        filters = {}
        if keyword_filters:
            if isinstance(keyword_filters, str):
                filters["keywords"] = [keyword_filters]
            elif isinstance(keyword_filters, list):
                filters["keywords"] = keyword_filters

        # Use query engine with memory (already set in __init__)
        response = self.query_engine.query(question)

        if self.format_response:
            response = self._format_response(response)

        if print_response:
            print(response)

    def get_relevant_documents(
        self, question, keyword_filters=None, metadata_filters={}
    ):
        """
        Retrieves relevant full documents by grouping relevant nodes.

        :param question: The query text.
        :param metadata_filters: Optional dictionary of metadata filters.
        :return: Dictionary of documents with metadata.
        """

        retrieved_nodes = self.get_relevant_nodes(question, metadata_filters)

        # Group by document source (use 'file_name' if 'source' is missing)
        documents = {}
        for node in retrieved_nodes:
            source = node["metadata"].get("source") or node["metadata"].get(
                "file_name", "Unknown Document"
            )

            if source not in documents:
                documents[source] = {"content": [], "metadata": node["metadata"]}

            documents[source]["content"].append(node["text"])

        # Combine text chunks for each document (limit size to prevent excessive output)
        for source in documents:
            combined_text = "\n\n".join(documents[source]["content"])
            documents[source]["content"] = combined_text[
                :5000
            ]  # Limit text to 5000 chars for readability

        return list(documents.keys())

    def get_relevant_nodes(self, question, metadata_filters=None):
        """
        Retrieves relevant document chunks (nodes) for a query.

        :param question: The query text.
        :param metadata_filters: Optional dictionary of metadata filters.
        :return: List of relevant nodes (chunks).
        """
        retriever = self.index.as_retriever(metadata_filters=metadata_filters)
        retrieved_nodes = retriever.retrieve(question)

        # Extract text and metadata from nodes
        relevant_nodes = [
            {"text": node.text, "metadata": node.metadata} for node in retrieved_nodes
        ]

        return relevant_nodes
