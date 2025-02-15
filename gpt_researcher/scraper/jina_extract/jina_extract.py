from bs4 import BeautifulSoup
import os
from ..utils import get_relevant_images, extract_title
import requests
from urllib.parse import quote

class JinaExtract:
    def __init__(self, link, session=None):
        self.link = link
        self.session = session
        self.base_url = "https://s.jina.ai"
        self.headers = {
            'Authorization': f'Bearer {self.get_api_key()}',
            'X-Engine': 'direct',
            'X-Retain-Images': 'none'
        }

    def get_api_key(self) -> str:
        """
        Gets the Jina API key
        Returns:
            Api key (str)
        """
        try:
            api_key = os.environ["JINA_API_KEY"]
        except KeyError:
            raise Exception(
                "Jina API key not found. Please set the JINA_API_KEY environment variable."
            )
        return api_key

    def scrape(self) -> tuple:
        """
        This function extracts content from a specified link using the Jina API, the title and
        images from the link are extracted using the functions from `gpt_researcher/scraper/utils.py`.

        Returns:
            The `scrape` method returns a tuple containing the extracted content, a list of image URLs, and
            the title of the webpage specified by the `self.link` attribute. It uses the Jina API to
            extract content from the webpage. If any exception occurs during the process, an error
            message is printed and an empty result is returned.
        """
        try:
            # Encode the URL for the GET request
            encoded_url = quote(self.link)
            url = f"{self.base_url}/{encoded_url}"
            
            # Make request to Jina API
            response = requests.get(
                url,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()

            # Parse the HTML content of the response to create a BeautifulSoup object for the utility functions
            response_bs = self.session.get(self.link, timeout=4)
            soup = BeautifulSoup(
                response_bs.content, "lxml", from_encoding=response_bs.encoding
            )

            # Extract content from Jina response
            if response.headers.get('content-type') == 'application/json':
                data = response.json()
                content = data.get('content', '')
            else:
                content = response.text

            if not content.strip():
                return "", [], ""

            # Get relevant images using the utility function
            image_urls = get_relevant_images(soup, self.link)

            # Extract the title using the utility function
            title = extract_title(soup)

            return content, image_urls, title

        except Exception as e:
            print("Error! : " + str(e))
            return "", [], ""