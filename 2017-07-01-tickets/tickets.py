#!/usr/bin/env ptyhon3
# -*- coding: utf-8 -*-

""" 命令行火车票查看器

Usage:
    tickets [-gdtkz] <from> <to> <date>

Options:
    -h, --help  显示帮助菜单
    -g          高铁
    -d          动车
    -t          特快
    -k          快速
    -z          直达

Example:
    tickets 北京 上海 2017-07-01
    tickets -dg 深圳北 广州南 2017-07-01
"""

from docopt import docopt
from prettytable import PrettyTable
from colorama import init, Fore
import requests

from stations import stations

init() # 初始化colorma

class TrainsCollection:

    header = '车次 车站 时间 历时 特等 一等 二等 高级软卧 软卧 动卧 硬卧 软座 硬座 无座 其他'.split()

    def __init__(self, available_trains, available_place, options):
        """ 查询到的火车班次集合

         :param available_trains: 列表，包含可获得的火车班次，每个班次为字典
         :param available_place: 站点名称
         :param options: 查询的选项
        """
        self.available_trains = available_trains
        self.available_place = available_place
        self.options = options
    
    def _get_duration(self, raw_trains):
        duration = raw_trains[10].replace(':', '时') + '分'
        if duration.startswith('00'):
            return duration[4:]
        if duration.startswith('0'):
            return duration[1:]
    
    @property
    def trains(self):
        for raw_train in self.available_trains:
            raw_train_list = raw_train.split('|')
            train_no = raw_train_list[3]
            initial = train_no[0].lower()
            if not self.options or initial in self.options:
                train = [
                    train_no,
                    '\n'.join([Fore.GREEN + self.available_place[raw_train_list[6]] + Fore.RESET, Fore.RED + self.available_place[raw_train_list[7]] + Fore.RESET]),
                    '\n'.join([Fore.GREEN + raw_train_list[8] + Fore.RESET, Fore.RED + raw_train_list[9] + Fore.RESET]),
                    self._get_duration(raw_train_list),
                    raw_train_list[-4],
                    raw_train_list[-5],
                    raw_train_list[-6],
                    raw_train_list[-15],
                    raw_train_list[-13],
                    raw_train_list[-3],
                    raw_train_list[-8],
                    raw_train_list[-11],
                    raw_train_list[-7],
                    raw_train_list[-10],
                    raw_train_list[-14]
                    ]
                yield train

    def pretty_print(self):
        pt = PrettyTable()
        pt._set_field_names(self.header)
        for train in self.trains:
            pt.add_row(train)
        print(pt)

def cli():
    """command-line interface"""
    arguments = docopt(__doc__)
    from_station = stations.get(arguments['<from>'])
    to_station = stations.get(arguments['<to>'])
    date = arguments['<date>']

    # 构建URL
    url = 'https://kyfw.12306.cn/otn/leftTicket/query?leftTicketDTO.train_date={0}&leftTicketDTO.from_station={1}&leftTicketDTO.to_station={2}&purpose_codes=ADULT'.format(date, from_station, to_station)
    options = ''.join([key for key, value in arguments.items() if value is True])
    # 不验证证书
    r = requests.get(url, verify=False)
    available_trains = r.json()['data']['result']
    available_place = r.json()['data']['map']
    TrainsCollection(available_trains, available_place, options).pretty_print()

if __name__ == '__main__':
    cli()

    # "0|1|2|3 G149|4|5|6|7|8 16:25|9 22:22|10 05:57|11|12|13 20170701|14|15|16|17|18|19|20|-15 高级软卧|-14 其他|-13 软卧|-12|-11 |-10 无座|-9|-8 硬卧|-7 硬座|-6 二等|-5 一等|-4 特等|-3 动卧|-2|-1