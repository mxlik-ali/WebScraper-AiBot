from utils.web_scraper import scrape_wikipedia_page
from utils.chunks import convert_to_chunks
from utils.vector_db import vector_db, get_conversational_chain
from api_config.vision import *
from api_config.vision_scrape import *
from api_config.prompt import *


import google.generativeai as genai
from dotenv import load_dotenv


from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.chains import create_qa_with_sources_chain, LLMChain
from langchain.prompts import PromptTemplate
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain_google_genai import ChatGoogleGenerativeAI

import os
import json
import glob
import time
import gradio
import streamlit as st
from urllib.parse import urlparse
# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

def existence(path):
    """
    Check if the given path exists.
    
    Parameters:
    path (str): The path to be checked.

    Returns:
    bool: True if the path exists, False otherwise.
    """
    try:
        return os.path.exists(path)
    except Exception as e:
        print(f"An error occurred while checking the existence of the path: {e}")
        return False


def is_wikipedia_url(url):
    """
    Check if the given URL belongs to Wikipedia.
    
    Parameters:
    url (str): The URL to be checked.

    Returns:
    bool: True if the URL belongs to Wikipedia, False otherwise.
    """
    try:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        return domain.endswith('wikipedia.org')
    except Exception as e:
        print(f"An error occurred while parsing the URL: {e}")
        return False


def query_model(query, new_db):
    """
    Query the vector database and get the response.

    Parameters:
    query (str): The query string to search for.
    new_db (object): The database object to query.

    Returns:
    dict: The response from the database query or None if an error occurs.
    """
    try:
        if new_db:
            docs = new_db.similarity_search(query)
            chain = get_conversational_chain()
            response = chain.invoke(
                {"input_documents": docs, "question": query},
                return_only_outputs=True
            )
            print(response)
            return response
        else:
            print("Database not available for querying.")
            return None
    except Exception as e:
        print(f"An error occurred while querying the database: {e}")
        return None


def get_all_jpg_files(folder_path):
    """
    Get all .jpg files in the specified folder(image_saves).
    
    Parameters:
    folder_path (str): The path to the folder.

    Returns:
    list: A list of paths to .jpg files in the folder.

    Raises:
    ValueError: If the folder does not exist.
    """
    try:
        # Ensure the folder path exists
        if not os.path.isdir(folder_path):
            raise ValueError(f"Folder {folder_path} does not exist")
        
        # Get all .jpg files in the folder
        jpg_files = glob.glob(os.path.join(folder_path, "*.jpg"))
        
        return jpg_files
    except Exception as e:
        print(f"An error occurred while retrieving JPG files: {e}")
        return []

def wait_for_images(folder_path, expected_count, max_wait_time=60, check_interval=2):
    """
    Wait for a specified number of images to appear in a folder (retrived from computer vision) within a maximum wait time.
    
    Parameters:
    folder_path (str): The path to the folder.
    expected_count (int): The number of expected image files.
    max_wait_time (int, optional): Maximum wait time in seconds. Default is 60 seconds.
    check_interval (int, optional): Interval in seconds to check the folder. Default is 2 seconds.

    Returns:
    list: A list of paths to .jpg files in the folder.

    Raises:
    ValueError: If the folder does not exist.
    """
    try:
        elapsed_time = 0
        while elapsed_time < max_wait_time:
            jpg_files = get_all_jpg_files(folder_path)
            if len(jpg_files) >= expected_count:
                return jpg_files
            time.sleep(check_interval)
            elapsed_time += check_interval
            print(f"Waiting for images... {elapsed_time}/{max_wait_time} seconds elapsed")
        return jpg_files
    except Exception as e:
        print(f"An error occurred while waiting for images: {e}")
        return []
    
def main():

    """
    Main function to execute the workflow.

    Returns:
        FAISS: The FAISS index containing vectorized embeddings of the Wikipedia page content.
    """
    # Paths for files
    url = os.getenv('URL')
    sitemap_path = './scrape/sitemap.json'
    faiss_index_path = "./faiss_index"
    prompt = prompt_any_link
    path_list = image_path_list
    
    try:
        sitemap_exists = existence(sitemap_path)
        print(f'Site map exists : {sitemap_exists}')
        


        if not sitemap_exists:
            # URL of the Wikipedia page
            print('webscraping')
            link_type = is_wikipedia_url(url)
            if link_type:
                page_structure = scrape_wikipedia_page(url)
                with open(sitemap_path, 'w', encoding='utf-8') as f:
                    json.dump(page_structure, f, ensure_ascii=False, indent=4)


            else:
                print('Link provided in not of Wikipedia')


            input_for_vision = scraper_main(url)
            folder_path = './image_saves'
            expected_image_count = 2  # Adjust based on your expected count
            jpg_files = wait_for_images(folder_path, expected_image_count)



            # Debugging print to check if jpg_files list is populated
            print(f"Extracted files from the website in jpg form: {jpg_files}")

            if not jpg_files:
                raise ValueError("No jpg files found in the scrape folder.")
            vision_page_structure = []
            image_description_list = []
            image_description = {}
            i = 0
            for files in jpg_files:
                b64_image = image_b64('./image_saves/screenshot1.jpg')
                print(f'Processing the {i+1} generated images')
                response = gen_vision(b64_image,prompt=prompt)
                vision_page_structure.append(response)
                i+=1
            
            i = 0
            for image_url in image_path_list:
                image_description = {}
                print(f'Processing the {i+1} image extracted')
                image_description['contents'] = f'here it contains all the description of the image{image_url}'
                response = gen_vision_for_image(image_url=image_url,prompt=prompt_any_link)
                image_description[image_url] = response
                image_description_list.append(image_description)
                
                i+=1
            
            image_description_list.append(f'Number of images present in the website is {i}')
            

            with open(sitemap_path, 'a', encoding='utf-8') as f:
                json.dump(vision_page_structure, f, ensure_ascii=False, indent=4)

            with open(sitemap_path, 'a', encoding='utf-8') as f:
                json.dump(image_description_list, f, ensure_ascii=False, indent=4)
            print('Webcraping using vision api done')
            # with open('html.txt', 'w', encoding='utf-8') as f:
            #     f.write(str(page_structure))

        faiss_exists = existence(faiss_index_path)
        print(f'faiss-index database exists :{faiss_exists}')
        if not faiss_exists:
            # Load the sitemap from file
            if  sitemap_exists:
                with open(sitemap_path, 'r', encoding='utf-8') as f:
                    page_structure = json.load(f)
                    print('opened sitemap')

            chunks = convert_to_chunks(str(page_structure))
            with open('./test/chunks.txt', 'w', encoding='utf-8') as f:
                f.write(str(chunks))

            # Create and save FAISS index
            vectorized_embedding = vector_db(chunks)
            new_db = FAISS.load_local("faiss_index",embeddings,allow_dangerous_deserialization=True)
        

        else:
            # Load the FAISS index
            new_db = FAISS.load_local("faiss_index",embeddings,allow_dangerous_deserialization=True)
        
        return new_db
    except Exception as e:
        print(f"An error occurred: {e}")





if __name__ == "__main__":
    main()
    print('Webscraping process completed , Run app.py to access the Chatbot !!!')


# Example Usage
# query = 'Who is luke skywalker'     
# obtain_db = main()
# query_model(query,obtain_db)
