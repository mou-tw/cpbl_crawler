from hitter_parser import hitter_parse_tocsv

import time


if __name__ == '__main__':
    st= time.time()

    # parse hitter and concat the return dataframe
    with open('undone_url.txt') as f:
        urls = f.readlines()

    for url in urls:
        hitter_parse_tocsv(url)

    print('done parsing hitter!')
    print (f' time cost :{time.time()-st} sec')
