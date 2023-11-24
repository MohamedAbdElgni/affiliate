import requests
from bs4 import BeautifulSoup
from .utils import scrap_item
from .models import Script, Category
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseNotFound
from django.template import loader
import random


HEADERS = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
    'referrer': 'https://google.com',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'Keep-Alive': '999',
    'Connection': 'keep-alive',
    'Cookie': 'PHPSESSID=r2t5uvjq435r4q7ib3vtdjq120',
    'Pragma': 'no-cache'
}
main_cat = [{'Wordpress': ['add-ons', 'advertising', 'calendars', 'ecommerce', 'forms', 'forums', 'galleries','interface-elements', 'media', 'membership', 'newsletters', 'seo', 'social-networking', 'utilities', 'widgets', 'miscellaneous']},
            {'Javascript': ['animated-svgs', 'calendars', 'countdowns', 'database-abstractions', 'forms', 'images-and-media', 'loaders-and-uploaders', 'media', 'navigation', 'news-tickers', 'project-management-tools', 'ratings-and-charts', 'shopping-carts', 'sliders', 'social-networks', 'miscellaneous']},
            {'Mobile': ['android', 'flutter', 'ios', 'native-web', 'titanium']},
            {'HTML5': ['3d', 'ad-templates', 'canvas', 'charts-and-graphs', 'forms', 'games', 'libraries', 'media', 'presentations', 'sliders', 'storage', 'templates', 'miscellaneous']},
            {'AI': ['content', 'image', 'chat']},
            {'Plugins': ['concrete5', 'drupal', 'expressionengine', 'joomla', 'magento-extensions', 'muse-widgets', 'opencart', 'oscommerce', 'prestashop', 'ubercart', 'virtuemart', 'zen-cart', 'miscellaneous']},
            {'Apps': ['windows', 'mac']}
            ]

def index(request):
    cat_menu = Category.objects.all()
    most_downloaded_scripts = Script.objects.all().order_by('-salesCount')[:18]
    most_rated_scripts = Script.objects.all().order_by('-ratingCount')[:18]
    
    context = {
        'cat_menu': cat_menu,
        'most_downloaded_scripts': most_downloaded_scripts,
        'most_rated_scripts': most_rated_scripts,
        'main_cat': main_cat
    }

    return render(request, 'index.html', context)


def search_view(request):
    cat_menu = Category.objects.all()

    current_page = 1

    if request.method == 'POST':
        searched = request.POST.get('search')
        searched = searched.strip().replace(' ', '%')
        request.session['search'] = searched

        BASE_URL = 'https://codecanyon.net/category/php-scripts?term='
        url = BASE_URL + searched

        response = requests.get(url, headers=HEADERS, timeout=5, verify=False)
        soup = BeautifulSoup(response.text, 'html.parser')

        # scraping and saving the data to the database
        scripts = []
        containers = soup.findAll(
            "div",
            {"class": "shared-item_cards-list-image_card_component__contentWrapper"}
        )
        if not containers:
            BASE_URL = 'https://codecanyon.net/search/'
            url = BASE_URL + searched
            response = requests.get(url, headers=HEADERS, timeout=5, verify=False)
            soup = BeautifulSoup(response.text, 'html.parser')
            containers = soup.findAll(
                "div",
                {"class": "shared-item_cards-list-image_card_component__contentWrapper"}
            )

        flag = True if containers else False

        for container in containers:
            scrap_item(container, scripts)

        pages = []
        urls = []

        paging = soup.find_all(
            'a',
            {'class': 'search-controls-pagination_nav_component__pageLink'}
        )

        if paging:
            for page in paging:
                pages.append(int(page.text))
                urls.append(page['href'])

        last_page = pages[-1] if pages else 0
        if scripts:
            sample_script = scripts[0]
        else:
            sample_script = None
        context = {
            'searched': searched,
            'scripts': scripts,
            'sample_script': sample_script,
            'flag': flag,
            'pages': pages,
            'urls': urls,
            'current_page': current_page,
            'cat_menu': cat_menu,
            'last_page': last_page,
            'main_cat': main_cat
        }

        return render(request, 'result.html', context)


def search_in_pages(request, page):
    cat_menu = Category.objects.all()
    searched = request.session['search']
    current_page = page

    url = f"https://codecanyon.net/category/php-scripts?page={page}&term={searched}#content"
    response = requests.get(url, headers=HEADERS, timeout=5, verify=False)
    soup = BeautifulSoup(response.text, 'html.parser')

    # scraping and saving the data to the database
    containers = soup.findAll(
        "div",
        {"class": "shared-item_cards-list-image_card_component__contentWrapper"})

    scripts = []
    flag = True if containers else False
    if not containers:
        url = f'https://codecanyon.net/search/{searched}?page={page}#content'
        response = requests.get(url, headers=HEADERS, timeout=5, verify=False)
        soup = BeautifulSoup(response.text, 'html.parser')
        containers = soup.findAll(
            "div",
            {"class": "shared-item_cards-list-image_card_component__contentWrapper"})
        # print('her', containers)


    for container in containers:
        scrap_item(container, scripts)

    paging = soup.find_all(
        'a',
        {'class': 'search-controls-pagination_nav_component__pageLink'})

    pages = [int(page.text) for page in paging]

    last_page = pages[-1] if pages else 0
    # print('scripts', scripts)
    
    if scripts:
        sample_script = scripts[0]
    else:
        sample_script = None
    context = {
        'searched': searched,
        'scripts': scripts,
        'sample_script': sample_script,
        'flag': flag,
        'pages': pages,
        'current_page': current_page,
        'cat_menu': cat_menu,
        'last_page': last_page,
        'main_cat': main_cat
    }

    return render(request, 'result.html', context)

def main_category(request, cat, sub_cat):
    cat = cat.lower()
    cat_menu = Category.objects.all()
    cats = [cat, sub_cat]
    current_page = 1
    url = f'https://codecanyon.net/category/{cat}/{sub_cat}'
    if cat == 'ai':
        url = f'https://codecanyon.net/search/ai%20{sub_cat}'
    response = requests.get(url, headers=HEADERS, timeout=5, verify=False)
    soup = BeautifulSoup(response.text, 'html.parser')

    # scraping and saving the data to the database
    scripts = []
    containers = soup.findAll(
        "div",
        {"class": "shared-item_cards-list-image_card_component__contentWrapper"}
    )
    
    if not containers:
        all_scripts = soup.findAll('a', {'class': 'category-categories_with_count_block_component__browseLink'})
        if all_scripts:
            new_url = all_scripts[1]['href']
            new_url = 'https://codecanyon.net' + new_url
            response2 = requests.get(new_url, headers=HEADERS, timeout=5, verify=False)
            soup = BeautifulSoup(response2.text, 'html.parser')
            containers = soup.findAll(
            "div",
            {"class": "shared-item_cards-list-image_card_component__contentWrapper"}
            )
            
    pages = []
    urls = []
    paging = soup.find_all(
        'a',
        {'class': 'search-controls-pagination_nav_component__pageLink'}
    )

    if paging:
        for page in paging:
            pages.append(int(page.text))
            urls.append(page['href'])

    last_page = pages[-1] if pages else 0

    flag = True if containers else False

    for container in containers:
        scrap_item(container, scripts)
    if scripts:
        sample_script = scripts[0]
    else:
        sample_script = None
    context = {
        'scripts': scripts,
        'sample_script': sample_script,
        'flag': flag,
        'pages': pages,
        'urls': urls,
        'current_page': current_page,
        'cat_menu': cat_menu,
        'last_page': last_page,
        'main_cat': main_cat,
        'cats': cats
    }
    return render(request, 'cat_result.html', context)

def main_category_in_pages(request, cat, sub_cat, page):
    cat = cat.lower()
    cat_menu = Category.objects.all()
    cats = [cat, sub_cat]
    current_page = page
    url = f'https://codecanyon.net/category/{cat}/{sub_cat}?page={page}#content'
    if cat == 'ai':
        url = f'https://codecanyon.net/search/ai%20{sub_cat}?page={page}#content'
    response = requests.get(url, headers=HEADERS, timeout=5, verify=False)
    soup = BeautifulSoup(response.text, 'html.parser')
    # scraping and saving the data to the database
    scripts = []
    containers = soup.findAll(
        "div",
        {"class": "shared-item_cards-list-image_card_component__contentWrapper"}
    )
    
    flag = True if containers else False

    for container in containers:
        scrap_item(container, scripts)

    pages = []
    urls = []

    paging = soup.find_all(
        'a',
        {'class': 'search-controls-pagination_nav_component__pageLink'}
    )

    if paging:
        for page in paging:
            pages.append(int(page.text))
            urls.append(page['href'])

    last_page = pages[-1] if pages else 0
    if scripts:
        sample_script = scripts[0]
    else:
        sample_script = None
    context = {
        'scripts': scripts,
        'sample_script': sample_script,
        'flag': flag,
        'pages': pages,
        'urls': urls,
        'current_page': current_page,
        'cat_menu': cat_menu,
        'last_page': last_page,
        'main_cat': main_cat,
        'cats': cats
    }
    return render(request, 'cat_result.html', context)


def category_list(request, cats):
    flag = False
    page_obj = None
    pages = None
    # print('her')
    cat_menu = Category.objects.all()
    queryset = Script.objects.filter(category=cats).order_by('-id')
    if queryset:
        flag = True
        paginator = Paginator(queryset, 30)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        pages = list(range(1, paginator.num_pages+1))

    cat = Category.objects.filter(name=cats)

    # getting the rating range and if it's has half

    rating_range = {}
    has_half = {}

    if page_obj:
        for script in page_obj:
            half = False
            the_range = range(int(float(script.rating)))
            if int(float(script.rating)) != float(script.rating):
                half = True
            rating_range[script.id] = the_range
            has_half[script.id] = half

    context = {
        'cats': cats,
        'cat': cat,
        'page_obj': page_obj,
        'pages': pages,
        'flag': flag,
        'cat_menu': cat_menu,
        'rating_range': rating_range,
        "has_half": has_half,
        'main_cat': main_cat
    }
    return render(request, 'categories.html', context)


def script_detail(request, slug):
    # scraping more detail
    try:
        script = get_object_or_404(Script, slug=slug)

        response = requests.get(
            script.details_link,
            headers=HEADERS,
            timeout=5,
            verify=False
        )
        dataModfied = script.lastUpdate.split(':')[-1]
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', {'class': 'meta-attributes__table'})

        all_rows = [
            [i.text.strip() for i in j.find_all('td')]
            for j in table.find_all('tr')
        ]

        detail_text = []
        containers = soup.findAll(
            "div",
            {"class": "user-html user-html__with-lazy-load"})

        for element in containers:
            p_tags = element.find_all('p')

        p_text = [x.text.strip() for x in p_tags]
        if p_text:
            while ('' in p_text):
                p_text.remove('')
            p_text.append('')
            p_text.append('')
            try:
                for i in range(3):
                    if len(p_text[i]) >= 90:
                        detail_text.append(p_text[i])
            except:
                pass

        features = script.description.all()

    except:
        return redirect('')

    has_half = False
    cat_menu = Category.objects.all()
    similar_scripts = list(Script.objects.all().exclude(slug=script.slug))
    similar_scripts = random.sample(similar_scripts, 18)
    
    try:
        if int(float(script.rating)) != float(script.rating):
            has_half = True
    except:
        pass

    context = {
        'script': script,
        'dataModfied': dataModfied,
        'similar_scripts': similar_scripts,
        'cat_menu': cat_menu,
        'all_rows': all_rows,
        'detail_text': detail_text,
        'range': range(int(script.rating)),
        'has_half': has_half,
        'main_cat': main_cat
    }

    return render(request, 'details.html', context)

def page404(request):
    #content = loader.render_to_string('404.html', {}, request)
    #return HttpResponseNotFound(content)
    return render(request, '404.html')

def dmca(request):
    cat_menu = Category.objects.all()
    context = {'cat_menu': cat_menu, 'main_cat': main_cat}
    return render(request, 'dmca.html', context)


def privacy(request):
    cat_menu = Category.objects.all()
    context = {'cat_menu': cat_menu, 'main_cat': main_cat}
    return render(request, 'privacy.html', context)

def download(request):
    cat_menu = Category.objects.all()
    context = {'cat_menu': cat_menu, 'main_cat': main_cat}
    return render(request, 'download.html', context)

def php_scripts(request):
    # if request.method == 'GET':
    #     cat_menu = Category.objects.all()
    #     scripts = Script.objects.filter(category='PHP Scripts')
    #     flag = True if scripts else False

    #     context = {
    #         'scripts': scripts,
    #         'cat_menu': cat_menu,
    #         'flag': flag
    #         # 'main_cat': main_cat
    #     }
    #     print('ter')
    cat_menu = Category.objects.all()
    current_page = 1
    searched = 'PHP Scritps'
    searched = searched.strip().replace(' ', '%')
    request.session['search'] = searched

    BASE_URL = 'https://codecanyon.net/category/php-scripts?term='
    url = BASE_URL + searched

    response = requests.get(url, headers=HEADERS, timeout=5, verify=False)
    soup = BeautifulSoup(response.text, 'html.parser')

    # scraping and saving the data to the database
    scripts = []
    containers = soup.findAll(
        "div",
        {"class": "shared-item_cards-list-image_card_component__contentWrapper"}
    )
    if not containers:
        BASE_URL = 'https://codecanyon.net/search/'
        url = BASE_URL + searched
        response = requests.get(url, headers=HEADERS, timeout=5, verify=False)
        soup = BeautifulSoup(response.text, 'html.parser')
        containers = soup.findAll(
            "div",
            {"class": "shared-item_cards-list-image_card_component__contentWrapper"}
        )

    flag = True if containers else False

    for container in containers:
        scrap_item(container, scripts)

    pages = []
    urls = []

    paging = soup.find_all(
        'a',
        {'class': 'search-controls-pagination_nav_component__pageLink'}
    )

    if paging:
        for page in paging:
            pages.append(int(page.text))
            urls.append(page['href'])

    last_page = pages[-1] if pages else 0
    if scripts:
        sample_script = scripts[0]
    else:
        sample_script = None
    context = {
        'searched': searched,
        'scripts': scripts,
        'sample_script': sample_script,
        'flag': flag,
        'pages': pages,
        'urls': urls,
        'current_page': current_page,
        'cat_menu': cat_menu,
        'last_page': last_page,
        'main_cat': main_cat
    }

    return render(request, 'result.html', context)
