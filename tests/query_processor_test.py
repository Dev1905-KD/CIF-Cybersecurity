from rag.query_processor import process_query


query = input("Enter your query: ")

result = process_query(query)

print(result)