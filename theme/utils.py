from .models import Script, Category
from django.utils.text import slugify
from django.shortcuts import get_object_or_404


def scrap_item(container, scripts):
    try:
        title = container.find(
            "a",
            {"class": "shared-item_cards-item_name_component__itemNameLink"}).text

        image = container.find_all('img')[0]['src']
        try:
            preview = container.find(
                'a',
                {'class': 'shared-item_cards-preview_button_with_analytics_component__root'})['href']
        except:
            preview = '#'

        description = container.find_all(
            'li',
            {'class': 'shared-item_cards-attributes_component__attribute'})

        file_types = container.find(
            'div',
            {'class': 'shared-item_cards-included_files_component__root'})

        features = [li.text.strip() for li in description]
        features.append(file_types.text.strip() if file_types else "")

        slug = slugify(title)

        category = container.find_all(
            'a',
            {'class': 'shared-item_cards-author_category_component__link'})[1].text.strip()

        details_url = container.find_all(
            'a',
            {'class': 'shared-item_cards-item_name_component__itemNameLink'})[0]['href']

        # getting the rate and price
        price_container = container.find_all(
            'div',
            {'class': 'shared-item_cards-list-image_card_component__priceWrapper'})[0]

        price = price_container.find(
            'div',
            {'class': 'shared-item_cards-price_component__root'}).text.strip()

        try:
            rating_text = price_container.find(
                'span',
                {'class': 'shared-stars_rating_component__starRatingCount'}).text.strip()

            if rating_text:
                rating_count = int(rating_text[1:-1])

        except:
            rating_count = 0

        try:
            sales_text = price_container.find(
                'div',
                {'class': 'shared-item_cards-sales_component__root'}).text.strip()

            if sales_text:
                sales = sales_text[:-6]
                sales_count = int(
                    float(sales[:-1])) * 1000 if 'K' in sales else int(sales)

        except:
            sales_count = 0

        last_update = price_container.find(
            'div',
            {'class': 'shared-item_cards-list-image_card_component__lastUpdated'}).text.strip()

        try:
            has_half = False
            rating = price_container.find('div', {'class': 'shared-stars_rating_component__starRating'}).find(
                'span').find('svg').find('use')['xlink:href'][-3:]
            if int(float(rating)) != float(rating):
                has_half = True
            rating = float(rating)

        except:
            rating = 0

        script = {
            "title": title,
            "image": image,
            "preview_link": preview,
            "slug": slug,
            'category': category,
            "description": features,
            'price': price,
            'lastUpdate': last_update,
            'ratng': rating,
            'range': range(int(rating)),
            'has_half': has_half
        }

        scripts.append(script)

        if Script.objects.filter(title=title).exists():
            script = get_object_or_404(Script, title=title)
            script.category = category
            script.details_link = details_url
            script.price = price
            script.ratingCount = rating_count
            script.salesCount = sales_count
            script.lastUpdate = last_update
            script.rating = rating
            script.save()
            script_id = script.script_id
            elem = [x for x in scripts if x['title'] == title][0]

            elem['script_id'] = script_id

            return

        else:
            script = Script.objects.create(
                title=title,
                image=image,
                preview_link=preview,
                category=category,
                details_link=details_url,
                price=price,
                ratingCount=rating_count,
                salesCount=sales_count,
                rating=rating,
                lastUpdate=last_update
            )
            if not Category.objects.filter(name=category).exists():
                Category.objects.create(name=category)

            script_id = script.script_id

            elem = [x for x in scripts if x['title'] == title][0]
            elem['script_id'] = script_id

    except Exception as e:
        print('some error: ', e)
