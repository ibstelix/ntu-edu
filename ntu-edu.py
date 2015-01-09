#!/usr/bin/env python

######################################################################
# PURPOSE:
#
# Script to scrape data off of page
# https://wish.wis.ntu.edu.sg/webexe/owa/aus_subj_cont.main
#
# Retrieves all of the data in the iframe by selecting every option 
# in the second dropdown menu 
#
# Results written to *.html files in same directory as script
#
# USAGE: 
#   $ ./ntu-edu.py
######################################################################
import sys, signal
import mechanize, time

URL = 'https://wish.wis.ntu.edu.sg/webexe/owa/aus_subj_cont.main'
DELAY = 5

def sigint(signal, frame):
    sys.stderr.write('Exiting...\n')
    sys.exit(0)    

def select_form(form):
    '''
    Select the course display form
    '''
    return form.attrs.get('target', None) == 'subjects'

class NtuEduScraper:
    def __init__(self, url=URL, delay=DELAY):
        self.br = mechanize.Browser()
        self.url = url
        self.delay = delay

    def submit_form(self, item):
        '''
        Submit form using selection item.name and return the results
        '''
        maxtries = 3
        numtries = 0

        sys.stderr.write('Submitting form for item %s\n' % item.name)

        while numtries < maxtries:
            try:
                self.br.open(self.url)
                self.br.select_form(predicate=select_form)
                self.br.form['r_course_yr'] = [ item.name ]
                self.br.form.find_control('boption').readonly = False
                self.br.form['boption'] = 'CLoad'
                self.br.submit()
                break
            except (mechanize.HTTPError, mechanize.URLError) as e:
                if isinstance(e,mechanize.HTTPError):
                    print e.code
                else:
                    print e.reason.args

            numtries += 1
            time.sleep(numtries * self.delay)

        if numtries == maxtries:
            raise

        return self.br.response().read()

    def item_results_to_file(self, item, results):
        label = ' '.join([label.text for label in item.get_labels()])
        label = '-'.join(label.split())

        sys.stderr.write('Writing results for item %s to file %s.html\n' % (item.name, label))

        with open("%s.html" % label, 'w') as f:
            f.write(results)
            f.close()
        
    def get_items(self):
        '''
        Get the list of items in the second dropdown of the form
        '''
        sys.stderr.write('Generating list of items for form selection\n')

        self.br.open(self.url)
        self.br.select_form(predicate=select_form)

        items = self.br.form.find_control('r_course_yr').get_items()

        sys.stderr.write('Got %d items for form selection\n' % len(items))

        return items

    def scrape(self):
        '''
        Get the list of items in the second dropdown menu and submit the
        form for each item. Save the results to file.
        '''
        items = self.get_items()

        for item in items:
            # Skip invalid/blank item selections
            if len(item.name) < 1:
                continue

            results = self.submit_form(item)
            self.item_results_to_file(item, results)
            time.sleep(self.delay)
        
if __name__ == '__main__':
    signal.signal(signal.SIGINT, sigint)
    scraper = NtuEduScraper()
    scraper.scrape()
