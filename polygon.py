
import re
import bs4
import requests
import datetime

BASE_URL = "http://www.polygon.com"
SEARCH_GAME_REVIEW_URL_TEMPLATE = BASE_URL + "/search?q=%s review"

class PolygonScraper(object):
    def __init__(self):
        return

    def _get_page_soup(self, url):
        response = requests.get(url)
        soup = bs4.BeautifulSoup(response.text)
        return soup

    def _get_name(self, soup):
        header_container_divs = [header_container_div for header_container_div in soup.select("div.header-container")]
        if not header_container_divs:
            return None
        header_container_div = header_container_divs[0]
        full_title = header_container_div.select('h1')[0].text
        return full_title.lower().split('review:')[0].strip()

    def _get_global_score(self, soup):
        score_div = [review_score for review_score in soup.select("div.review_score")]
        if not score_div:
            return None
        score_div = score_div[0]
        div_classes = [div_class for div_class in score_div.get('class') if div_class != "review_score"]
        if not div_classes:
            return None
        score_text = div_classes[0].replace('score_', '')
        return score_text

    def _get_score_by_platform(self, soup):
        score_by_platform = {}
        scores_div = soup.select("div.review_scores")
        if not scores_div:
            return None
        scores_div = scores_div[0]
        platform_scores_divs = [platform_score_div for platform_score_div in scores_div.select("div.score")]
        for platform_scores_div in platform_scores_divs:
            platform_score, platform_name = list(platform_scores_div.stripped_strings)
            if platform_name and platform_score:
                score_by_platform[platform_name] = platform_score
        return score_by_platform

    def _get_details(self, soup):
        game_details = {
            "name": self._get_name(soup),
            "score": self._get_global_score(soup),
            "score_by_platform": self._get_score_by_platform(soup)
        }
        return game_details

    def get_game_details_by_url(self, url):
        soup = self._get_page_soup(url)
        game_details = self._get_details(soup)
        return game_details

    def get_game_url(self, game_name):
        url = SEARCH_GAME_REVIEW_URL_TEMPLATE % game_name
        while True:
            soup = self._get_page_soup(url)
            text_to_url = {href.text.lower().strip(): href.get('href') for href in soup.select("div.meta a")}
            for link_name, game_url in text_to_url.items():
                if "review" in link_name:
                    link_game_name = link_name.lower().split('review:')[0].strip()
                    print link_game_name
                    if link_game_name.lower() == game_name.lower():
                        return game_url
            next_hrefs = [next_href for next_href in soup.select("span.vox-pagination-next a")]
            if not next_hrefs:
                break
            url = BASE_URL + next_hrefs[0].get('href')
        return None

    def get_game_details_by_name(self, game_name):
        game_url = self.get_game_url(game_name)
        if not game_url:
            return None
        game_details = self.get_game_details_by_url(game_url)
        return game_details
