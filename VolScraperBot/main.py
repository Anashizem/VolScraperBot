import asyncio
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  # Set event loop policy explicitly for Windows

from twisted.internet import asyncioreactor
asyncioreactor.install()

from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
from spiders.NouvelairSpider import NouvelairSpider
from spiders.TunisairExpressSpider import TunisairExpressSpider
from spiders.AirfranceSpider import AirfranceSpider
from spiders.TunisairSpider import TunisairSpider


from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/search_flights', methods=['POST'])
def submit_form():
    data = request.json
    print(data)
    main(data)
    return jsonify({"message": "Form submitted successfully"})

def main(data):
    configure_logging()
    settings = get_project_settings()
    runner = CrawlerRunner(settings)

    def get_user_input(data):
        place_of_departure = data['from']
        place_of_arrival = data['to']
        travel_type = data['tripType']
        check_in_date = data['startDateRoundTrip'] if travel_type == 'aller-retour' else data['startDateOneWay']
        check_out_date = data['endDateValueRoundTrip'] if travel_type == 'aller-retour' else None

        return {
            'place_of_departure': place_of_departure,
            'place_of_arrival': place_of_arrival,
            'type': travel_type,
            'check_in_date': check_in_date,
            'check_out_date': check_out_date
        }

    @defer.inlineCallbacks
    def crawl():
        user_args = get_user_input(data) 
        # yield runner.crawl(AirfranceSpider, **user_args)
        yield runner.crawl(NouvelairSpider, **user_args)
        # yield runner.crawl(TunisairSpider, **user_args)
        # yield runner.crawl(TunisairExpressSpider, **user_args)

        reactor.stop()

    crawl()
    reactor.run()

if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=False, use_reloader=False)
