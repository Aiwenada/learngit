#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2015  Data Enlighten Technology (Beijing) Co.,Ltd


__author__ = 'ada'

import zgy.connectiontest as conntest

if __name__ == '__main__':
    conn = conntest.PostgreSQLConnector()
    conn.connection("local")

    li_type = conn.execute("SELECT DISTINCT t1.type FROM public.mj_pr_repository as t1 ")
    li = li_type[1]
    li_vin_prlist = conn.execute("SELECT t1.vin,t1.pr_list FROM public.mj_pr_repository as t1 WHERE t1.type='%s'",li[0])


    if(len(li_vin_prlist)>=2):
        pr_list_resutl = []
        pr_list_temp1=li_vin_prlist[0][1].split('|')
        pr_list_temp2=li_vin_prlist[1][1].split('|')
        for pr_list_temp_iter in pr_list_temp1:
            if pr_list_temp_iter in pr_list_temp2:
                pr_list_resutl.append(pr_list_temp_iter)
        if(len(li_vin_prlist)>2):
            n=2
            while( n < len(li_vin_prlist)):
                pr_list_temp=li_vin_prlist[n][1].split('|')
                print(pr_list_temp)
                for pr_list_temp_iter in pr_list_resutl:
                    if pr_list_temp_iter in pr_list_temp:
                        pass
                    else:
                        pr_list_resutl.remove(pr_list_temp_iter)
                n=n+1

    for li_vin_prlist_temp in pr_list_resutl:
        n=0
        while(n < len(li_vin_prlist)):
            temp = li_vin_prlist[n][1]
            temp += '|'
            if li_vin_prlist_temp in temp:
    print(pr_list_resutl)

    result_list =[]
    print(result_list)



