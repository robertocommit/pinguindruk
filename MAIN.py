from torrequest import TorRequest
import pandas as pd

csv_output = 'CSV/OUTPUT.csv'

start_url = 'https://pinguindruck.de/shop/klappkarten'


def main():
    for item in extract_info():
        save_execution_status(item)


def extract_info():
    session.get(start_url)
    format_response = session.post('https://pinguindruck.de/data/get-print-product/closedformat?type=json')
    formats = format_response.json()['request']
    for s, format in enumerate(formats):
        print(str((len(formats) - s)) + ' formats to go')
        restart_session()
        format_id = str(format['closedformat_id']) + ' ' + str(format['size_x']) + 'x' + str(format['size_y'])
        session.post('https://pinguindruck.de/data/set-parameter?type=json&closedformat_id=%s' % format_id)
        closedformatfoldings_response = session.post('https://pinguindruck.de/data/get-print-product/closedformatfoldings?type=json')
        closedformatfoldings = closedformatfoldings_response.json()['request']['left']
        for i, closedformat in enumerate(closedformatfoldings):
            print('     ' + str((len(closedformatfoldings) - i)) + ' closedformatfoldings to go')
            process_id = closedformat['process_id']
            process_data = 'option1=' + closedformat['folding_code'] + ';option1=' + closedformat['folding_code'] + ';option1=' + closedformat['folding_code']
            process_info = 'option1=' + closedformat['notation']['identifier'] + ';option1=' + closedformat['notation']['identifier'] + ';option1=' + closedformat['notation']['identifier']
            folding_code = closedformat['folding_code']
            folding_name = closedformat['notation']['text']
            closedformat_id = closedformat['format_id']
            width = closedformat['user_x']
            height = closedformat['user_y']
            session.post('https://pinguindruck.de/data/set-parameter?type=json&process_id=%s&process_data=%s&process_info=%s&folding_code=%s&format_id=%s&width=%s&height=%s' % (process_id, process_data, process_info, folding_code, closedformat_id, width, height))
            paper_response = session.post('https://pinguindruck.de/data/get-print-product/paper?type=json&filter=prefill&closedformat_id=%s' % closedformat_id)
            papers = paper_response.json()['request']
            for x, paper in enumerate(papers):
                print('          ' + str((len(papers) - x)) + ' papers to go')
                paper_id = paper['paper_id']
                session.post('https://pinguindruck.de/data/set-parameter?type=json&paper_id=%s&process_id=%s&process_data=%s&process_info=%s' % (paper_id, process_id, process_data.split(';')[0], process_info.split(';')[0]))
                color_response = session.post('https://pinguindruck.de/data/get-print-product/color?type=json&paper_id=%s' % paper_id)
                colors = color_response.json()['request']
                for y, color in enumerate(colors):
                    print('               ' + str((len(colors) - y)) + ' colors to go')
                    color_id = color['color_id']
                    page_response = session.post('https://pinguindruck.de/data/get-print-product/page?type=json&color_id=%s' % color_id)
                    pages = page_response.json()['request']
                    for z, page in enumerate(pages):
                        print('                    ' + str((len(pages) - z)) + ' pages to go')
                        page_id = page['page_id']
                        charge_response = session.post('https://pinguindruck.de/data/get-print-product/charge?type=json&page_id=%s&exclude=price' % page_id)
                        combination_id = '%2C'.join([elem['combination_id'] for elem in charge_response.json()['request']])
                        prices_response = session.post('https://pinguindruck.de/data/get-print-product/price?type=json&list=%s' % combination_id)
                        yield generate_output(charge_response.json(), prices_response.json(), folding_name)


def restart_session():
    session.cookies.clear()
    session.get(start_url)


def generate_output(charge_response, price_response, folding_name):
    product_identifier = price_response['session']['item']['product']['identifier']
    format_identifier = price_response['session']['item']['format']['identifier']
    folding_identifier = folding_name
    paper_identifier = price_response['session']['item']['paper']['identifier']
    color_identifier = price_response['session']['item']['color']['identifier']
    temp_array = []
    for price in price_response['request']:
        try:
            price_express = price['price']['taxexcl']['1']
        except:
            price_express = '/'
        try:
            price_standard = price['price']['taxexcl']['3']
        except:
            price_standard = '/'
        try:
            price_economy = price['price']['taxexcl']['5']
        except:
            price_economy = '/'
        quantity = get_charge_quantity(charge_response, price['charge_id'])
        temp_array.append([product_identifier, format_identifier, folding_identifier, paper_identifier, color_identifier, quantity, price_express, price_standard, price_economy])
    return pd.DataFrame(temp_array, columns=['product', 'format', 'folding', 'paper', 'color', 'charge', 'price_express', 'price_standard', 'price_economy'])


def get_charge_quantity(charge_response, charge_id):
    for charge in charge_response['request']:
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
