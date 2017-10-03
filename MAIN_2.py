from torrequest import TorRequest
import pandas as pd

csv_output = 'CSV/OUTPUT.csv'

start_url = 'https://pinguindruck.de/shop/postkarten'
format_url = 'https://pinguindruck.de/data/get-print-product/format?type=json'
paper_url = 'https://pinguindruck.de/data/get-print-product/paper?type=json&format_id=%s&width=0&height=0'
color_url = 'https://pinguindruck.de/data/get-print-product/color?type=json&paper_id=%s'
page_url = 'https://pinguindruck.de/data/get-print-product/page?type=json&color_id=%s'
charge_url = 'https://pinguindruck.de/data/get-print-product/charge?type=json&page_id=%s&exclude=price'
price_url = 'https://pinguindruck.de/data/get-print-product/price?type=json&list=%s'


def main():
    for item in extract_info():
        save_execution_status(item)


def extract_info():
    session.get(start_url)
    formats = get_response(format_url, '', '')
    for index_format, format in enumerate(formats):
        print(str((len(formats) - index_format)) + ' formats to go')
        papers = get_response(paper_url, format, 'format_id')
        for index_paper, paper in enumerate(papers):
            print('     ' + str((len(papers) - index_paper)) + ' papers to go')
            colors = get_response(color_url, paper, 'paper_id')
            for index_color, color in enumerate(colors):
                print('          ' + str((len(colors) - index_color)) + ' colors to go')
                pages = get_response(page_url, color, 'color_id')
                for index_page, page in enumerate(pages):
                    print('               ' + str((len(pages) - index_page)) + ' pages to go')
                    charge_response = get_response(charge_url, page, 'page_id')
                    price_response = get_price_response(charge_response)
                    yield generate_output(charge_response, price_response.json())


def get_response(url, dict, key):
    if dict == '':
        url_complete = url
    else:
        url_complete = url % str(dict[key])
    response = session.get(url_complete).json()
    return response['request']


def get_price_response(charge_response):
    url = '%2C'.join([elem['combination_id'] for elem in charge_response])
    return session.get(price_url % url)


def generate_output(charge_response, price_response):
    product_identifier = price_response['session']['item']['product']['identifier']
    format_identifier = price_response['session']['item']['format']['identifier']
    paper_identifier = price_response['session']['item']['paper']['identifier']
    color_identifier = price_response['session']['item']['color']['identifier']
    temp_array = []
    for price in price_response['request']:
        price_express, price_standard, price_economy = price['price']['taxexcl']['1'], price['price']['taxexcl']['3'], price['price']['taxexcl']['5']
        quantity = get_charge_quantity(charge_response, price['charge_id'])
        temp_array.append([product_identifier, format_identifier, paper_identifier, color_identifier, quantity, price_express, price_standard, price_economy])
    return pd.DataFrame(temp_array, columns=['product', 'format', 'paper', 'color', 'charge', 'price_express', 'price_standard', 'price_economy'])


def get_charge_quantity(charge_response, charge_id):
    for charge in charge_response:
        if charge['charge_id'] == charge_id:
            return charge['count']


def save_execution_status(df):
    with open(csv_output, 'a') as f:
        df.to_csv(f, header=False, index=False, encoding='utf-8')


if __name__ == '__main__':
    with TorRequest() as tor:
        session = tor.session
        session.headers.update({'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'})
        main()
