import re

FILE_NAME = 'ResultsOfBenchmark_results_20161205.txt'

# Read File
class Parser(object):
    '''
    Class is used to parse lines
    '''

    def __init__(self, file_name):
        '''
        Constructor
        '''
        self.file_name = file_name

    def clean_record(self, record, counter):
        """
        un-clean record
        {'average_time_ms': '144.4669189453125',
        'min_scorel': '0.6',
        'times': '[145.1171875, 143.816650390625]',
        'search_string': 'search=M&minscore=0.6&bti=3&bde=6&bds=1&btg=1',
        'elasticsearch_on': 'True',
        'data_length': '10'}
        """
        clean_record = {}
        clean_record['id'] = counter
        clean_record['average_time_ms'] = float(record['average_time_ms'])

        try:
            clean_record['min_score'] = float(record['min_scorel'])
        except:
            clean_record['min_score'] = None
        # times
        temp1 = str(record['times']).strip('[]')
        temp2 = re.split('; |, ',temp1)


        clean_record['times_ms'] = [float(record) for record in temp2]


        clean_record['data_length'] = int(record['data_length'])

        clean_record['elasticsearch_on'] = bool(record['elasticsearch_on'])

        return clean_record

    def process(self):
        '''
        Function used to read file

        Args:
            file_path: path of the file
            process_line_callback: function for callback
            skip: If True skip first line of file

        Exceptions:
            IOError
        '''
        counter = 0
        with open(self.file_name , 'r') as f:
            for line in f.readlines():
                counter = counter + 1

                line_split_list = line.split('\t')
                if counter == 1:
                    line_split_list = [record.lower().replace(' ', '_').replace('(','').replace(')','').strip() for record in line_split_list]
                    self.header = line_split_list
                else:
                    line_split_list = [record.strip() for record in line_split_list]
                    temp_record = dict(zip(self.header, line_split_list))

                    clean_record = self.clean_record(temp_record, counter)
                    self._process_record(clean_record, counter)

    def _process_record(self, record, counter):
        '''
        Helper Function
        '''
        if counter % 10000 == 0:
            print(counter)
        #print(record)

        # print(counter)
        #
        # print(line_split_list)

if __name__ == "__main__":


    Parser(FILE_NAME).process()
