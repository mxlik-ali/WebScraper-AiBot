prompt_any_link = '''U are a webscraper that uses vision pro api to scrape the message content.
                            Do Not provide any type of information from any other knowledge base u have u just extract the information , and copy paste it
                            Now scrape everything ALL THE CONTENT inside and dont skip any part store it and make sure to give a response in json format(do not include any html tags), And do maintain the heirarchy
                            Even remember to skip the content that occurs twice or thrice in terms of data cleaning which is equal in all terms but if the year or anything is different count it
                            Please provide me full webscaping do not leave any content, The format of json is given below. Ive seen u skipping make part make sure to include the paragraphs present
                            ```
                            json
                            {
                                heading: 
                                content: write all text extracted in this subsection
                                subsection :{
                                                subsection:
                                                content: write all text extracted inside this subsection}#if subsection is present
                                {   
                                    skip using headers everytimeas key value instead frovide a list when it comes to rows and headers continue in same line
                                    table:
                                    headers:[1,2,3,4,5]#header example if present then only
                                    rows:[1,2,3,4,5]#row example (dont start all row elements on new line, one whole row in one line,
                                    
                                }
                            }'''

prompt_image_wiki = ''' U are a part of web scraper backend and you are supposed to to extract the image and then provide a very breif 
                information about how the image, make sure to make it as descriptive as possible, mark the details of the image,
                provide details in such a manner that if this response is given as an input to gemini ai chat model, it will be able to
                interpret and provide answers to relevant things'''

prompt_image_anylink = '''U are a part of web scraper backend that wants to give information about the images present in website 
                        and Now you need to utilise computer vision here you are supposed to to extract the visual image from the given input image
                        and extract only the image If you dont find any image just provide None as output ,and not text or any other part ,analyze it and then provide a very breif 
                        information about how the image, make sure to make it as descriptive as possible, mark the details of the image,
                        provide details in such a manner that if this response is given as an input to gemini ai chat model, it will be able to
                        interpret and provide answers to relevant things, make sure to provide all type of details like who is there in the image what is there in the image 
                        how is the background, which things are present, what is the colour of those things,
                        If you dont find any image just provide None as output

'''