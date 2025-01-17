import os
from pathlib import Path
import json
import pandas as pd
from openai import OpenAI
import base64
import argparse
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

image_dir_base = r"E:\App Dev\GitHub\chart_ocr\data"
image_dir = None 

# Logging function
def log_error(message):
    with open(image_dir / "Chatgpt_extraction_error_log.txt", "a") as log_file:
        log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

def parse_arguments():
    try:
        parser = argparse.ArgumentParser(description='Chart Screenshot Automation Tool')
        parser.add_argument('--image_dir', type=str, required=True,
                          help='Directory containing the images')        
        
        args = parser.parse_args()

        global image_dir
        image_dir = Path(image_dir_base) / args.image_dir       
        return args
    
    except ValueError as e:
        print(f"Value Error: {str(e)}")
        log_error(f"Value Error: {str(e)}")
        exit(1)
    except Exception as e:
        print(f"Unexpected error during argument parsing: {str(e)}")
        log_error(f"Unexpected error during argument parsing: {str(e)}")
        exit(1)

def encode_image(image_path):
    try:
        if not Path(image_path).exists():
            log_error(f"Image file not found: {image_path}")
            raise FileNotFoundError(f"Image file not found: {image_path}")
            
        if not Path(image_path).is_file():
            log_error(f"Path is not a file: {image_path}")
            raise ValueError(f"Path is not a file: {image_path}")
            
        if Path(image_path).suffix.lower() not in ['.jpg', '.jpeg', '.png']:
            log_error(f"Unsupported file format: {Path(image_path).suffix}")
            raise ValueError(f"Unsupported file format: {Path(image_path).suffix}")
            
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
            
    except (FileNotFoundError, ValueError) as e:
        log_error(f"Image encoding error: {str(e)}")
        print(f"Image encoding error: {str(e)}")
        raise
    except Exception as e:
        log_error(f"Unexpected error during image encoding: {str(e)}")
        print(f"Unexpected error during image encoding: {str(e)}")
        raise

def get_levels_from_gpt(image_path):
    print(image_path)
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    base64_image = encode_image(image_path)
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": 
                     
                     """You are a skilled assistant specialized in analyzing financial chart images and extracting reference levels extended to the right side of the market profile chart. Your task is to interpret the image, identify reference levels, and provide them as a list of [key, value] pairs.
                        Each reference level has a name ("VPoC", "V-PPoC", "PoorH", "PoorL", "SwingH", "SwingL", "ABPoorH", "ABPoorL", "SingleP", "pMon-Series-H", "pMon-Series-L", "pWk-Series-H", "pWk-Series-L"). VPoC and V-PPoC will have a corresponding numerical value. For other names, you have to interpret the numerical value based on the line of that level and the price index. 
                        If multiple levels are marked to a single value, (e.g., pMon-Series-L, SwingL, PoorL), consider that value for each of the reference levels. 
                        
                        Exclude any levels or markings not extended to the right of the chart or unrelated to the task.  Also ignore the red, green and blue numbers present in the price index. 
                         Focus only on solid yellow levels clearly extended to the right side near the price column. Ignore the dotted yellow lines. Ignore noise, labels, or annotations that do not match the specified format.
                        Output format:
                        {
                            [[\"VPoC\", 372], [\"VPoC\", 360], [\"PoorL\", 358], [\"PoorH\", 379], [\"SwingL\", 362], [\"SwingH\", 381], [\"ABPoorH\", 383], [\"ABPoorL\", 364], [\"SingleP\", 374], [\"SingleP\", 412], [\"pMon-Series-H\", 376], [\"pMon-Series-L\", 356], [\"pWk-Series-H\", 385], [\"pWk-Series-L\", 366]]
                        }
                        Don't add any additional sentences in the output. It has to strictly follow the Output format."""
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        max_tokens=300
    )
    
    try:
        response_text = response.choices[0].message.content.strip()
        # Print response for debugging
        #print(f"Raw response: {response_text}")
        
        #Remove the ```json at the start of the response_text
        response_text = response_text.replace("```json", "")
        response_text = response_text.replace("```plaintext", "")
        response_text = response_text.replace("```", "")
        #print(f"Raw response after correction: {response_text}")
        
        level_pairs = json.loads(response_text)
        # Convert list pairs to list of dictionaries
        results = []
        for key, value in level_pairs:
            results.append({'Key': key, 'Value': value})
        return results
        
    except json.JSONDecodeError as e:
        print(f"Invalid JSON response: {response_text}")
        log_error(f"Invalid JSON response: {response_text}")
        return {"error": "Invalid response format"}

def process_images_to_csv(output_csv):
    results = []
    
    for image_file in Path(image_dir).glob('*.jpg'):
        symbol = image_file.stem
        try:
            levels_list = get_levels_from_gpt(str(image_file))
            
            # Process each dictionary in the list
            for level in levels_list:
                results.append({
                    'Symbol': symbol,
                    'Key': level['Key'],
                    'Value': level['Value']
                })
                
        except Exception as e:
            print(f"Error processing {symbol}: {str(e)}")
            log_error(f"Error processing {symbol}: {str(e)}")
    
    # Create DataFrame with all entries
    df = pd.DataFrame(results)
    df = df.sort_values(by=['Symbol', 'Value'], ascending=[True, False])
    df.to_csv(output_csv, index=False)


def main():

    parse_arguments()
    
    output_csv = Path(image_dir) / "extracted_levels.csv"
    
    process_images_to_csv(output_csv)
    print(f"Processing complete. Results saved to {output_csv}")

if __name__ == "__main__":
    main()
