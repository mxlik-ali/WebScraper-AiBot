import json
from typing import List, Dict
from langchain.text_splitter import CharacterTextSplitter

def convert_to_chunks(page_structure: Dict) -> List[str]:
    """
    Converts the page structure into text chunks.

    Args:
        page_structure (Dict): The structure of the page in dictionary format.

    Returns:
        List[str]: List of text chunks.
    """
    try:
        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = text_splitter.split_text(page_structure)
        return chunks
    except Exception as e:
        print(f"An error occurred while converting page structure to chunks: {e}")
        return []

# Example usage
# page_structure = {...}  # Replace with actual page structure dictionary
# chunks = convert_to_chunks(page_structure)
# if chunks:
#     print("Text Chunks:")
#     for idx, chunk in enumerate(chunks, 1):
#         print(f"Chunk {idx}: {chunk}")
# else:
#     print("No text chunks generated.")
