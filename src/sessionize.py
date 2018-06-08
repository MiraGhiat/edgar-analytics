import pandas as pd


def generator_chunk_data(file_path, chunk_size=86400):
    """generator) to read a data reported every 24 hours
    chunk size: 86400(s) which is 24 hours."""

    if file_path:
        reader = pd.read_table(file_path, sep=',', header=0,
                               parse_dates=[['date', 'time']],
                               usecols=['ip','date','time','extention'],
                               chunksize=chunk_size)
        yield reader


def generator_values(pvt):
    for row in pvt.values:
        yield row


def write_output(pvt, inactivity_period):
    with open(r'\output\sessionize.txt', 'w') as f:
        for r_idx, row in enumerate(generator_values(pvt)):
            i = 0
            counter = 0
            while i < len(row):
                if row[i] != 0:
                    counter = row[i]
                    _save = counter
                    start_time = pvt.columns[i]
                    end_time = start_time
                    j = i+1
                    start_idx = i
                    while j < len(row):
                        if row[j] != 0:
                            if (pvt.columns[j].second - pvt.columns[start_idx].second) <= inactivity_period:
                                counter += row[j]
                                end_time = pvt.columns[j]
                                start_idx = j
                                j += 1
                                i = j
                            else:
                                # this for multiple request for the selected time frame
                                duration = end_time.second-start_time.second
                                end_time = end_time.strftime('%Y-%m-%d %H:%M:%S')
                                start_time = start_time.strftime('%Y-%m-%d %H:%M:%S')
                                l_out = [pvt.index[r_idx], start_time, end_time, str(duration),
                                             str(counter)]
                                f.write(','.join(l_out))
                                f.write('\n')

                                counter = 0
                                _save = 0
                                start_time = pvt.columns[j]
                                end_time = start_time
                                j += 1
                                i = j
                        else:
                            j += 1
                            i = j
                else:
                    i += 1
            # this is for case with one request per ip ex:[0 0 0 1 0 0]
            if counter == _save:
                start_time = start_time.strftime('%Y-%m-%d %H:%M:%S')
                l_out = [pvt.index[r_idx], start_time, start_time, '1',
                         str(counter)]
                f.write(','.join(l_out))
                f.write('\n')


if __name__ == '__main__':

    f = open(r'inactivity_period.txt', 'rb')
    inactivity_period = int(f.read())
    f.close()

    data_path = r'log.csv'
    gen_data = generator_chunk_data(data_path)

    for chunk in gen_data:
        df = chunk.get_chunk()
        pvt = pd.pivot_table(df, values='extention', index='ip', columns='date_time', aggfunc='count', fill_value=0)
        write_output(pvt, inactivity_period)

