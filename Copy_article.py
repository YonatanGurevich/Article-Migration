import urllib3
from bs4 import BeautifulSoup
import json

articles_url = "https://rt-ed.co.il/articles/"
# section = {"title":"section 1","content":["Sometext1","Sometext2","Sometext3"]}
# section2 = {"title":"section 2","content":["Sometext1","Sometext2","Sometext3"]}
# section3 = {"title":"section 3","content":["Sometext1","Sometext2","Sometext3"]}
# article = {"title":"Hello world!","excerpt":"Some description on the article","sections":[section,section2,section3]}

not_parsed_well = []
not_parsed = []


def get_all_article_links(url, links_list):
    """
    Iterates through article pages and saves all the article's links in provided links_list
    :param url: url of articles main page: https://rt-ed.co.il/articles/
    :param links_list: empty list to contain all links extracted by function
    """

    http = urllib3.PoolManager()
    response = http.request('GET', url)
    soup = BeautifulSoup(response.data, 'lxml')
    articles_page = soup.find("div", {"class": 'articles'})
    for div in articles_page.find_all("div", {"class": 'article'}):
        img_blog = div.find("div", {"class": 'img-blog'})
        a = img_blog.find("a")
        link = a['href']
        links_list.append(link)
    navigation = articles_page.find("div", {"wp-pagenavi"})
    try:
        next_page = navigation.find('a', {"class": "nextpostslink"})['href']
        get_all_article_links(next_page, links)
    except Exception:
        pass


def parse_article(url, i):
    """

    :param url: url of article to parse
    :param i: index of article in url_list - to name the json file uniquely
    """
    http = urllib3.PoolManager()
    response = http.request('GET', url)
    soup = BeautifulSoup(response.data, 'lxml')
    try:
        article_content = soup.find("div", {"class": "panel-body"})
        try:
            article_content.find("div", {"class": "toc_container"}).decompose()  # Remove irrelevant table of contents
        except Exception:
            pass
        article_contents = article_content.contents
        article_contents = [tag for tag in article_contents if tag.name is not None]
        # print(article_contents)
        mapped_headers = [index for index, tag in enumerate(article_contents) if tag.name in ("h2", "h3", "h4", "h5")]
        if len(mapped_headers) != 0:  # If article has headers (h2, h3, etc...) organize article by sections
            h2 = mapped_headers[0]
            if article_contents[h2].name != "h2":
                not_parsed_well.append(url)
            article_sections = []
            for index, header in enumerate(mapped_headers):
                section = {"title": article_contents[header].get_text(), "content": []}
                try:
                    for tag in article_contents[header + 1: mapped_headers[index + 1]]:
                        section["content"].append(str(tag))
                except IndexError:
                    for tag in article_contents[header + 1:]:
                        section["content"].append(str(tag))
                article_sections.append(section)
            if len(article_sections) == 0:
                not_parsed_well.append(url)
            else:
                article_obj = {"title": article_sections[0]["title"], "sections": article_sections}
                with open("jsons\\article_{}.json".format(str(i)), 'w') as json_file:
                    json.dump(article_obj, json_file)

        else:  # (len(mapped_headers) == 0)
            article_sections = []
            for tag in article_contents:
                section = {"title": "", "content": str(tag)}
                article_sections.append(section)

            article_obj = {"title": article_sections[0]["title"], "sections": article_sections}
            with open("jsons\\article_{}.json".format(str(i)), 'w') as json_file:
                json.dump(article_obj, json_file)
            not_parsed_well.append(url)

    except Exception:
        not_parsed.append(url)


if __name__ == '__main__':
    links = []
    get_all_article_links(articles_url, links)
    for i, link in enumerate(links):
        parse_article(link, i)
        print("article {} parsed".format(i + 1))
    # parse_article('', 10000)
    not_parsed_well = [url for url in not_parsed_well if url not in not_parsed]
    # print(not_parsed_well, "\n\n\n\n\n\n\n")
    # print(not_parsed)
