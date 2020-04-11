import baostock as bs
import os
import pandas as pd


def mkdir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


class Downloader(object):
    def __init__(self,
                 output_dir,stock_list=None,
                 date_start='2000-01-01',
                 date_end='2019-12-31'):
        self._bs = bs
        self._bs.login()
        self.date_start = date_start
        self.date_end = date_end
        self.output_dir = output_dir
        self.stock_list = stock_list
        self.fields = "date,code,open,high,low,close,volume,amount," \
                      "adjustflag,turn,tradestatus,pctChg,peTTM," \
                      "pbMRQ,psTTM,pcfNcfTTM,isST"

    def exit(self):
        bs.logout()

    def get_codes_by_date(self, date):
        print(date)
        stock_rs = bs.query_all_stock(date)
        stock_df = stock_rs.get_data()
        return stock_df

    def run(self):
        stock_df = self.get_codes_by_date(self.date_end)
        if not self.stock_list:
            for index, row in stock_df.iterrows():
                print('Downloading {} {}'.format(row["code"],row["code_name"]))
                df_code = bs.query_history_k_data_plus(row["code"], self.fields,
                                                       start_date=self.date_start,
                                                       end_date=self.date_end).get_data()
                df_code.to_csv('{}/{}.{}.csv'.format(self.output_dir,row["code"],row["code_name"].replace('*','T')), index=False)
        else:
            for index, row in stock_df.iterrows():
                if row["code"] in self.stock_list:
                    print('Downloading {} {}'.format(row["code"],row["code_name"]))
                    df_code = bs.query_history_k_data_plus(row["code"], self.fields,
                                                           start_date=self.date_start,
                                                           end_date=self.date_end).get_data()
                    df_code.to_csv('{}/{}.{}.csv'.format(self.output_dir,row["code"],row["code_name"].replace('*','T')), index=False)
                else:
                    continue
        self.exit()


if __name__ == '__main__':
    stock_list = ['sh.000001','sz.000002','sz.002371','sh.600004','sh.600030','sh.600036','sh.600276','sh.600519','sh.600900','sh.601318']
    mkdir('./train')
    downloader = Downloader('./train', stock_list, date_start='2000-01-01', date_end='2016-12-30')
    downloader.run()

    mkdir('./test')
    downloader = Downloader('./test', stock_list, date_start='2017-01-01', date_end='2019-12-31')
    downloader.run()

