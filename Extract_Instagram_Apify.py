import pandas as pd
import requests
import os
from apify_client import ApifyClient

class ExtractData():
    def __init__(self,client,excel_data,img_dir,txt_dir):
        self.client=client
        self.excel_data=excel_data
        self.img_dir=img_dir
        self.txt_dir=txt_dir
    
    def get_url_list(self):
        df=pd.read_excel(self.excel_data)
        url_list=df['url'].to_list()
        type_list=df['type'].to_list()

        new_url=[]
        for i in range(len(type_list)):
            if type_list[i] in ['Image','Sidecar']:
                new_url.append(url_list[i])
            else:
                pass
        return new_url

    def get_insta_data(self,url_list):
        # Prepare the Actor input
        try:
            run_input = {
                "directUrls": url_list,
                "resultsType": "details",
                "resultsLimit": 2,
                "searchType": "hashtag",
                "searchLimit": 1,
                "extendOutputFunction": """async ({ data, item, helpers, page, customData, label }) => {
            return item;
            }""",
                "extendScraperFunction": """async ({ page, request, label, response, helpers, requestQueue, logins, addProfile, addPost, addLocation, addHashtag, doRequest, customData, Apify }) => {
            
            }""",
                "customData": {},
            }

            # Run the Actor and wait for it to finish
            run = self.client.actor("shu8hvrXbJbY3Eb9W").call(run_input=run_input)

            # Fetch and print Actor results from the run's dataset (if there are any)
            item_list=[]
            for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
                item_list.append(item)
            
            return item_list
        except Exception as e:
            print("An error occurred:", e)
    
    def download_images(self,item,y,save_dir_image,save_dir_txt):
        filename=str(y)+'.jpg'
        txtname=str(y)+'.txt'

        try:    
            data_display_url=item['displayUrl']
            data_url=item['url']
            data_type=item['type']

            response = requests.get(data_display_url)
            if response.status_code == 200:
                image_data = response.content
                txt_data=data_url+'\n'+data_type+'\n'+data_display_url
                save_path_img = os.path.join(save_dir_image, filename)
                with open(save_path_img, 'wb') as file:
                    file.write(image_data)
                save_path_txt = os.path.join(save_dir_txt, txtname)
                with open(save_path_txt, 'w') as file:
                    file.write(txt_data)
            else:
                print('failed')
        except Exception as e:
            print("An error occurred:", e)
    
def main():
    api_key="Your_Apify_token" #put you api token from Apify
    client = ApifyClient(api_key) 

    excel='Your_Excel_file.xlsx' #put your excel file 
    out_img_dir="output_img_location" #put output image location
    out_txt_dir="output_text_location"#put output text location

    def divide_list(input_list, n):
        part_size = len(input_list) // n
        divided_list = []
        for i in range(0, len(input_list), part_size):
            part = input_list[i:i + part_size]
            divided_list.append(part)
        return divided_list

    extract=ExtractData(client,excel,out_img_dir,out_txt_dir)
    
    print("Please have patience this will take time!!!")
    urls=extract.get_url_list()
    start_count=0 #put your start count of images #if 4000 images was downloded before than start with 4001
                  # but you have to manually remove other images url from excel file which was downloaded from xlsx file
    divided_urls=divide_list(urls,200)
    
    for j in range(len(divided_urls)):
        items=extract.get_insta_data(divided_urls[j])
        for element in items:
            extract.download_images(element,start_count,out_img_dir,out_txt_dir)
            print(start_count,'.jpg saved')
            start_count+=1
        
if __name__=='__main__':
    main()


        
