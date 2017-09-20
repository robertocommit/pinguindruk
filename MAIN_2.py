from torrequest import TorRequest


def main():
    with TorRequest() as requests:
        cookies = requests.get('https://pinguindruck.de/shop/postkarten').cookies
        start_url = 'https://pinguindruck.de/data/get-print-product/format?type=json&ignore%5B%5D=paper&ignore%5B%5D=color&ignore%5B%5D=charge'
        start_response = requests.get(start_url, cookies=cookies)
        for format in start_response.json()['request']:
            format_id = str(format['format_id'])
            paper_url = 'https://pinguindruck.de/data/get-print-product/paper?type=json&format_id=' + format_id + '&width=0&height=0&ignore%5B%5D=color&ignore%5B%5D=charge'
            paper_response = requests.get(paper_url, cookies=cookies)
            for paper in paper_response.json()['request']:
                paper_id = str(paper['paper_id'])
                color_url = 'https://pinguindruck.de/data/get-print-product/color?type=json&paper_id=' + paper_id + '&ignore%5B%5D=charge'
                color_response = requests.get(color_url, cookies=cookies)
                for color in color_response.json()['request']:
                    color_id = str(color['color_id'])
                    page_url = 'https://pinguindruck.de/data/get-print-product/page?type=json&color_id=' + color_id + '&ignore%5B%5D=charge'
                    page_response = requests.get(page_url, cookies=cookies)
                    for page in page_response.json()['request']:
                        page_id = str(page['page_id'])
                        charge_url = 'https://pinguindruck.de/data/get-print-product/charge?type=json&page_id=' + page_id + '&exclude=price&ignore%5B%5D=charge'
                        charge_response = requests.get(charge_url, cookies=page_response.cookies).json()
                        combination_ids = '%2C'.join([elem['combination_id'] for elem in charge_response['request']][0:4])
                        price_url = 'https://pinguindruck.de/data/get-print-product/price?type=json&list=' + combination_ids
                        price_response = requests.get(price_url, cookies=cookies).json()
                        product_identifier = price_response['session']['item']['product']['identifier']
                        format_identifier = price_response['session']['item']['format']['identifier']
                        paper_identifier = price_response['session']['item']['paper']['identifier']
                        color_identifier = price_response['session']['item']['color']['identifier']
                        for charge in price_response['request']:
                            print product_identifier, format_identifier, paper_identifier, color_identifier, charge['charge_id'], charge['price']['taxexcl']
                        print ''


if __name__ == '__main__':
    main()
