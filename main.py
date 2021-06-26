from hitter_parser import hitter_parse_tocsv
from multiprocessing import Process
import time


if __name__ == '__main__':
    st= time.time()

    # parse hitter and concat the return dataframe
    with open('doc_file/url_lst.txt') as f:
        urls = f.readlines()

    for i in range(int(len(urls)/5) +1 ):
        print(i)
        p_list = []
        for url in urls[5 * i  : 5 * (i+1)]:
            # print(url)
            p = Process( target=hitter_parse_tocsv, args=(url,) )
            p_list.append(p)
            p.start()
        [p.join() for p in p_list]

    print('done parsing hitter!')
    print (f' time cost :{time.time()-st} sec')
